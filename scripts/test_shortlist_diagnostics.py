"""Allowlisted, credential-redacted API diagnostics; no network calls."""
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from requests.structures import CaseInsensitiveDict

import run_shortlist_job as runner
import test_shortlist_runner as fixtures
from shortlist_model import ModelError, ResponsesModel, api_error_diagnostics


class DiagnosticTests(unittest.TestCase):
    def response(self, code="rate_limit_exceeded"):
        response = Mock(status_code=429, headers=CaseInsensitiveDict({
            "Retry-After": "12", "X-Request-ID": "req-test-429",
            "X-RateLimit-Limit-Requests": "100", "x-ratelimit-limit-tokens": "50000",
            "x-ratelimit-remaining-requests": "0", "x-ratelimit-remaining-tokens": "0",
            "x-ratelimit-reset-requests": "2s", "x-ratelimit-reset-tokens": "12s",
            "Set-Cookie": "SECRET_COOKIE", "Authorization": "Bearer SECRET_TOKEN",
            "unrelated-header": "SECRET_OTHER"}))
        response.json.return_value = {"error": {"code": code, "type": "requests",
            "message": "Request limit reached; wait before retrying.", "payload": "SECRET_PAYLOAD"},
            "request": "SECRET_REQUEST"}
        return response

    def test_429_classification_headers_and_retry_behavior_preserved(self):
        for code in ("rate_limit_exceeded", "insufficient_quota"):
            response = self.response(code)
            with self.subTest(code=code), patch("shortlist_model.requests.post", return_value=response), self.assertRaises(ModelError) as caught:
                ResponsesModel("test", api_key="test-key").complete(stage="test", instructions="JSON", context={}, output_schema={})
            exc = caught.exception
            self.assertTrue(exc.transient)  # Classification logging does not change retry policy.
            self.assertEqual(exc.retry_after, 12)
            self.assertEqual(exc.diagnostics["error"], {
                "code": code, "type": "requests", "message": "Request limit reached; wait before retrying."})
            self.assertEqual(exc.diagnostics["retry_after"], "12")
            self.assertEqual(exc.diagnostics["request_id"], "req-test-429")
            self.assertEqual(len(exc.diagnostics["rate_limit_headers"]), 6)
            self.assertNotIn("SECRET", json.dumps(exc.diagnostics))

    def test_credentials_redacted_in_all_allowlisted_fields(self):
        response = self.response()
        response.json.return_value["error"] = {
            "code": "my-real-api-key", "type": "Bearer secret-token",
            "message": 'Invalid key my-real-api-key; sk-proj-anothersecret; password="hidden value"; api_key=othersecret\nNext line\x1b'}
        response.headers["X-Request-ID"] = "my-real-api-key"
        response.headers["x-ratelimit-limit-tokens"] = "sk-othersecret"
        data = api_error_diagnostics(response, "my-real-api-key")
        serialized = json.dumps(data)
        for secret in ("my-real-api-key", "secret-token", "sk-proj-anothersecret", "hidden value", "othersecret"):
            self.assertNotIn(secret, serialized)
        self.assertNotIn("\n", data["error"]["message"])
        self.assertNotIn("\x1b", data["error"]["message"])
        self.assertIn("[REDACTED]", serialized)

    def test_missing_or_non_json_body_does_not_replace_http_error(self):
        for body in (None, [], {"error": "text"}, {"error": {"code": {"secret": "value"}}}):
            response = Mock(status_code=429, headers={})
            response.json.return_value = body
            with self.subTest(body=body):
                data = api_error_diagnostics(response, "test-key")
                self.assertEqual(data["error"], {"code": None, "type": None, "message": None})
                self.assertIsNone(data["request_id"])
                self.assertIsNone(data["retry_after"])
        response.json.side_effect = ValueError("SECRET RAW BODY")
        with patch("shortlist_model.requests.post", return_value=response), self.assertRaises(ModelError) as caught:
            ResponsesModel("test", api_key="test-key").complete(stage="test", instructions="JSON", context={}, output_schema={})
        self.assertEqual(caught.exception.error_type, "HTTP 429")
        self.assertNotIn("SECRET", json.dumps(caught.exception.diagnostics))


class DiagnosticPersistenceTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    execute = fixtures.RunnerTests.execute

    def test_error_retry_history_and_progress_retain_safe_diagnostics(self):
        response = DiagnosticTests().response()
        diagnostics = api_error_diagnostics(response, "test-key")
        def fail(stage, output):
            if stage == "shortlist_decision":
                raise ModelError("HTTP 429", error_type="HTTP 429", transient=True,
                                 retry_after=12, diagnostics=diagnostics)
        with patch("run_shortlist_job.time.sleep") as sleep, self.assertRaises(runner.RunError) as caught:
            self.execute(fixtures.FakeModel(fail))
        directory = caught.exception.run_dir
        artifact = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        attempts = [e for e in artifact["history"] if e["event"] == "request_failed"]
        self.assertEqual(len(attempts), 4)
        self.assertTrue(all(e["api_diagnostics"] == diagnostics for e in attempts))
        self.assertEqual(artifact["error"]["api_diagnostics"], diagnostics)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [12, 12, 12])
        log = (directory / "progress.log").read_text(encoding="utf-8")
        self.assertEqual(log.count("req-test-429"), 4)
        self.assertNotIn("SECRET", log)
        runner.resume_job(directory, fixtures.FakeModel(), candidate_root=self.root)
        final = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        resumed = next(e for e in final["history"] if e["event"] == "resume")
        self.assertEqual(resumed["previous_error"]["api_diagnostics"], diagnostics)

    def test_progress_permission_error_after_stage_commit_does_not_fail_run(self):
        original_open = Path.open
        progress_appends = 0

        def one_locked_append(path, *args, **kwargs):
            nonlocal progress_appends
            mode = args[0] if args else kwargs.get("mode", "r")
            if path.name == "progress.log" and "a" in mode:
                progress_appends += 1
                if progress_appends == 6:  # Role-completed message, after its durable stage save.
                    raise PermissionError(13, "Synthetic OneDrive lock")
            return original_open(path, *args, **kwargs)

        with patch("pathlib.Path.open", new=one_locked_append):
            directory, artifact, model = self.execute()
        self.assertEqual(artifact["status"], "accepted")
        self.assertEqual(artifact["completed_stages"], list(runner.STAGES))
        self.assertEqual([call["stage"] for call in model.calls], list(runner.STAGES))
        role_events = [event for event in artifact["history"]
                       if event.get("event") == "stage_completed" and
                       event.get("stage") == "role_understanding"]
        self.assertEqual(len(role_events), 1)
        self.assertIn("role_understanding", artifact["stage_outputs"])
        self.assertTrue(any(warning["channel"] == "progress.log" and
                            warning["type"] == "PermissionError"
                            for warning in artifact["diagnostic_warnings"]))
        self.assertTrue((directory / "shortlist_state.json").is_file())

    def test_genuine_model_refusal_remains_a_model_error(self):
        class RefusingModel(fixtures.FakeModel):
            def complete(self, **request):
                self.calls.append(request)
                raise ModelError("Model refused the stage; no decision fabricated",
                                 error_type="Refusal", transient=False)

        with self.assertRaises(runner.RunError) as caught:
            self.execute(RefusingModel())
        artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["completed_stages"], [])
        self.assertEqual(artifact["error"]["type"], "ModelError")
        self.assertEqual(artifact["error"]["message"],
                         "Model refused the stage; no decision fabricated")
        self.assertNotEqual(artifact["error"]["type"], "PermissionError")

    def test_local_permission_error_message_is_specific(self):
        message = runner._execution_error_message(PermissionError(13, "locked"), "[1/4] Role Understanding")
        self.assertIn("Local filesystem permission denied", message)
        self.assertNotIn("no result accepted", message)


if __name__ == "__main__":
    unittest.main()
