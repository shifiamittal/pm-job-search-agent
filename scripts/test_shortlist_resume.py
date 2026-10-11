"""Offline checkpoint compatibility and bounded transient retry tests."""
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
import json
import unittest
from unittest.mock import Mock, patch

import requests
import run_shortlist_job as runner
from shortlist_model import ModelError, ResponsesModel, retry_after_seconds
import test_shortlist_runner as fixtures

FakeModel = fixtures.FakeModel


class ResumeTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    execute = fixtures.RunnerTests.execute

    def failed_run(self, stage="shortlist_decision", error=None):
        def fail(name, output):
            if name == stage:
                raise error or ModelError("Model request returned HTTP 429", error_type="HTTP 429")
        with self.assertRaises(runner.RunError) as caught:
            self.execute(FakeModel(fail))
        directory = caught.exception.run_dir
        return directory, json.loads((directory / "job_state.json").read_text(encoding="utf-8"))

    def test_resume_reuses_two_stages_and_preserves_original_failure(self):
        directory, before = self.failed_run()
        model = FakeModel()
        self.assertEqual(runner.resume_job(directory, model, candidate_root=self.root), directory)
        after = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual([call["stage"] for call in model.calls], list(runner.STAGES[2:]))
        self.assertEqual(after["completed_stages"], list(runner.STAGES))
        self.assertEqual(after["status"], "accepted")
        self.assertEqual(after["model_calls"][:2], before["model_calls"])
        for stage in runner.STAGES[:2]:
            self.assertEqual(after["stage_outputs"][stage], before["stage_outputs"][stage])
        event = next(e for e in after["history"] if e["event"] == "resume")
        snapshot = json.loads((directory / event["snapshot"]).read_text(encoding="utf-8"))
        self.assertEqual(snapshot, before)
        self.assertEqual(event["previous_error"], before["error"])
        self.assertTrue((directory / "shortlist_state.json").is_file())
        self.assertTrue((directory / "review.md").is_file())
        self.assertFalse((directory / "resume.lock").exists())

    def test_legacy_checkpoint_uses_saved_request_fingerprints(self):
        directory, artifact = self.failed_run()
        for key in ("model_settings", "input_sha256", "prompt_hashes", "history"):
            artifact.pop(key)
        for call in artifact["model_calls"]:
            call.pop("output_sha256")
            call["response"]["max_output_tokens"] = 12000
        (directory / "job_state.json").write_text(runner._json(artifact), encoding="utf-8")
        model = FakeModel()
        runner.resume_job(directory, model, candidate_root=self.root)
        self.assertEqual([c["stage"] for c in model.calls], list(runner.STAGES[2:]))

    def test_stale_hashes_and_settings_block_without_calls_or_mutation(self):
        for kind in ("job", "spec", "prompt", "candidate", "model", "tokens", "timeout", "output"):
            with self.subTest(kind=kind):
                directory, artifact = self.failed_run()
                model = FakeModel()
                if kind == "job":
                    artifact["input_job"]["title"] = "Changed title"
                elif kind == "spec":
                    artifact["contract_hashes"][runner.CONTRACT_FILES[0]] = "stale"
                elif kind == "prompt":
                    artifact["prompt_hashes"][runner.STAGES[0]] = "stale"
                elif kind == "candidate":
                    artifact["candidate_context"][runner.CANDIDATE_FILES[0]]["sha256"] = "stale"
                elif kind == "model":
                    model.model = "different-model"
                elif kind == "tokens":
                    model.max_output_tokens = 99
                elif kind == "timeout":
                    model.timeout = 99
                else:
                    artifact["stage_outputs"]["career_requirements_mapping"]["evidence_provenance"] = []
                path = directory / "job_state.json"
                path.write_text(runner._json(artifact), encoding="utf-8")
                original = path.read_bytes()
                with self.assertRaisesRegex(ValueError, "Resume blocked:.*rerun stale stage"):
                    runner.resume_job(directory, model, candidate_root=self.root)
                self.assertEqual(model.calls, [])
                self.assertEqual(path.read_bytes(), original)
                self.assertFalse(list(directory.glob("before-resume-*")))

    def test_changed_candidate_file_blocks_reuse(self):
        directory, _ = self.failed_run()
        path = self.root / "profile/candidate_confirmed_facts.md"
        path.write_text("Different confirmation", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "candidate-context hash changed"):
            runner.resume_job(directory, FakeModel(), candidate_root=self.root)

    def test_resume_controller_only_after_decision_success(self):
        directory, before = self.failed_run("controller_validation")
        model = FakeModel()
        runner.resume_job(directory, model, candidate_root=self.root)
        self.assertEqual([c["stage"] for c in model.calls], ["controller_validation"])
        after = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(after["stage_outputs"]["shortlist_decision"], before["stage_outputs"]["shortlist_decision"])

    def test_resume_recovers_persisted_decision_after_location_normalization_fix(self):
        job = fixtures.input_job()
        job["location"] = "Redmond"
        def enrich_location(stage, output):
            if stage == "shortlist_decision":
                output["location_work_model"]["location"] = "Redmond, Washington"
        with patch("shortlist_contract.locations_equivalent", return_value=False), \
             self.assertRaises(runner.RunError) as caught:
            self.execute(FakeModel(enrich_location), job=job)
        directory = caught.exception.run_dir
        before = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(before["completed_stages"], list(runner.STAGES[:2]))
        saved_decision = before["stage_outputs"]["shortlist_decision"]

        resumed = FakeModel()
        runner.resume_job(directory, resumed, candidate_root=self.root)
        after = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual([call["stage"] for call in resumed.calls], ["controller_validation"])
        self.assertEqual(after["stage_outputs"]["shortlist_decision"], saved_decision)
        self.assertEqual(after["completed_stages"], list(runner.STAGES))
        recovered = [event for event in after["history"]
                     if event.get("stage") == "shortlist_decision" and
                     event.get("recovered_from_persisted_output")]
        self.assertEqual(len(recovered), 1)
        resume = [event for event in after["history"] if event["event"] == "resume"][-1]
        self.assertEqual(resume["initial_resume_at"], "shortlist_decision")
        self.assertEqual(resume["recovered_stage"], "shortlist_decision")
        self.assertEqual(resume["resume_at"], "controller_validation")

    def test_429_retries_only_failed_stage_then_runs_controller(self):
        failures = 0
        def rate_limit(stage, output):
            nonlocal failures
            if stage == "shortlist_decision" and failures < 2:
                failures += 1
                raise ModelError("HTTP 429", error_type="HTTP 429", transient=True, retry_after=7)
        with patch("run_shortlist_job.time.sleep") as sleep:
            _, artifact, model = self.execute(FakeModel(rate_limit))
        self.assertEqual([c["stage"] for c in model.calls], [*runner.STAGES[:2], *(["shortlist_decision"] * 3), "controller_validation"])
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [7, 7])
        self.assertEqual(artifact["status"], "accepted")
        self.assertEqual(len([e for e in artifact["history"] if e["event"] == "request_failed"]), 2)

    def test_bounded_retry_exhaustion_keeps_completed_stages(self):
        error = ModelError("HTTP 503", error_type="HTTP 503", transient=True)
        with patch("run_shortlist_job.time.sleep") as sleep:
            _, artifact = self.failed_run(error=error)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4, 8])
        self.assertEqual(artifact["completed_stages"], list(runner.STAGES[:2]))
        self.assertEqual(len([e for e in artifact["history"] if e["event"] == "request_failed"]), 4)

    def test_retry_during_resume_never_recalls_saved_stages(self):
        directory, _ = self.failed_run()
        failures = 0
        def rate_limit(stage, output):
            nonlocal failures
            if stage == "shortlist_decision" and failures == 0:
                failures += 1
                raise ModelError("HTTP 429", error_type="HTTP 429", transient=True)
        model = FakeModel(rate_limit)
        with patch("run_shortlist_job.time.sleep") as sleep, patch("run_shortlist_job.random.uniform", return_value=0):
            runner.resume_job(directory, model, candidate_root=self.root)
        self.assertEqual([c["stage"] for c in model.calls], ["shortlist_decision", "shortlist_decision", "controller_validation"])
        sleep.assert_called_once_with(15)

    def test_429_missing_retry_after_uses_slow_jittered_bounded_backoff(self):
        error = ModelError("HTTP 429", error_type="HTTP 429", transient=True)
        with patch("run_shortlist_job.time.sleep") as sleep, \
             patch("run_shortlist_job.random.uniform", side_effect=[1, 2, 3, 0]):
            directory, artifact = self.failed_run(error=error)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [16, 32, 63])
        attempts = [e for e in artifact["history"] if e["event"] == "request_failed"]
        self.assertEqual([e["delay_seconds"] for e in attempts], [16, 32, 63, None])
        self.assertEqual(artifact["completed_stages"], list(runner.STAGES[:2]))
        self.assertIn("retry 3/3 in 63.0s", (directory / "progress.log").read_text(encoding="utf-8"))

    def test_429_server_delay_overrides_fallback_without_jitter(self):
        for delay in (0, 1, 12, 90):
            error = ModelError("HTTP 429", error_type="HTTP 429", transient=True, retry_after=delay)
            with self.subTest(delay=delay), patch("run_shortlist_job.random.uniform") as jitter:
                self.assertEqual(runner._retry_delay(error, 2), delay)
                jitter.assert_not_called()

    def test_429_fallback_jitter_stays_within_twenty_percent(self):
        error = ModelError("HTTP 429", error_type="HTTP 429", transient=True)
        for attempt, base in enumerate((15, 30, 60)):
            delay = runner._retry_delay(error, attempt)
            self.assertGreaterEqual(delay, base)
            self.assertLessEqual(delay, base * 1.2)

    def test_concurrent_resume_lock_blocks_execution(self):
        directory, _ = self.failed_run()
        (directory / "resume.lock").write_text("other process", encoding="utf-8")
        model = FakeModel()
        with self.assertRaisesRegex(ValueError, "already locked"):
            runner.resume_job(directory, model, candidate_root=self.root)
        self.assertEqual(model.calls, [])
        self.assertEqual((directory / "resume.lock").read_text(), "other process")

    def test_long_retry_after_stops_instead_of_retrying_early(self):
        with patch("run_shortlist_job.time.sleep") as sleep:
            _, artifact = self.failed_run(error=ModelError("HTTP 429", transient=True, retry_after=301))
        sleep.assert_not_called()
        self.assertEqual(artifact["status"], "failed")

    def test_schema_failure_is_not_retried(self):
        def invalid(stage, output):
            if stage == "shortlist_decision":
                output.clear()
        model = FakeModel(invalid)
        with patch("run_shortlist_job.time.sleep") as sleep, self.assertRaises(runner.RunError):
            self.execute(model)
        self.assertEqual(len(model.calls), 3)
        sleep.assert_not_called()

    def test_cli_resume_uses_saved_settings_and_no_input(self):
        directory, _ = self.failed_run()
        model = FakeModel()
        real_resume = runner.resume_job
        with patch("sys.argv", ["run_shortlist_job.py", "--resume-run", directory.name,
                               "--output-root", str(directory.parent)]), \
             patch("run_shortlist_job.ResponsesModel", return_value=model), \
             patch("run_shortlist_job.resume_job", side_effect=lambda path, m, **kwargs: real_resume(
                 path, m, candidate_root=self.root, **kwargs)):
            runner.main()
        self.assertEqual([c["stage"] for c in model.calls], list(runner.STAGES[2:]))


class RetryTransportTests(unittest.TestCase):
    def test_retry_after_seconds_and_http_date(self):
        self.assertEqual(retry_after_seconds("12"), 12)
        future = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=60))
        self.assertGreater(retry_after_seconds(future), 58)
        for value in (None, "invalid", "NaN", "inf"):
            self.assertIsNone(retry_after_seconds(value))

    def test_http_transience_and_retry_header(self):
        for code in (400, 401, 403, 408, 429, 500, 502, 503, 504):
            response = Mock(status_code=code, headers={"Retry-After": "9"})
            with self.subTest(code=code), patch("shortlist_model.requests.post", return_value=response), self.assertRaises(ModelError) as caught:
                ResponsesModel("test", api_key="secret").complete(stage="test", instructions="JSON", context={}, output_schema={})
            self.assertEqual(caught.exception.transient, code in (408, 429, 500, 502, 503, 504))
            self.assertEqual(caught.exception.retry_after, 9)

    def test_timeout_is_transient_without_exposing_payload(self):
        with patch("shortlist_model.requests.post", side_effect=requests.Timeout("SECRET")), self.assertRaises(ModelError) as caught:
            ResponsesModel("test", api_key="secret").complete(stage="test", instructions="JSON", context={}, output_schema={})
        self.assertTrue(caught.exception.transient)
        self.assertNotIn("SECRET", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
