"""Offline provenance, technical retry and judge transport regressions."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import unittest
from unittest.mock import Mock, patch

from jsonschema import Draft202012Validator
import eval_shortlist as ev
import run_shortlist_job as runner
from shortlist_model import ModelError, ResponsesModel
import test_shortlist_runner as fixtures
import test_shortlist_eval as eval_fixtures


class TransportTests(unittest.TestCase):
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}},
              "required": ["ok"], "additionalProperties": False}

    def invoke(self, body, schema=None, stage="role_understanding", status=200):
        response = Mock(status_code=status, headers={})
        response.json.return_value = body
        with patch("shortlist_model.requests.post", return_value=response):
            return ResponsesModel("gpt-6-sol", api_key="not-a-real-key").complete(
                stage=stage, instructions="Return JSON", context={}, output_schema=schema or self.schema)

    def test_incomplete_preserves_reason_usage_and_retry_classification(self):
        with self.assertRaises(ModelError) as caught:
            self.invoke({"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"},
                         "usage": {"input_tokens": 100, "output_tokens": 12000}})
        error = caught.exception
        self.assertTrue(error.structural)
        self.assertEqual(error.diagnostics["incomplete_reason"], "max_output_tokens")
        self.assertEqual(error.response_metadata["usage"]["output_tokens"], 12000)

    def test_malformed_json_and_missing_required_field_are_technical(self):
        for text, kind in [('{"ok":', "MalformedJSON"), ('{}', "StructuredOutputSchema")]:
            with self.subTest(text=text), self.assertRaises(ModelError) as caught:
                self.invoke({"status": "completed", "usage": {"input_tokens": 5, "output_tokens": 4},
                    "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]})
            self.assertEqual(caught.exception.error_type, kind)
            self.assertTrue(caught.exception.structural)

    def test_refusal_and_content_filter_are_not_retryable(self):
        for body in [{"status": "incomplete", "incomplete_details": {"reason": "content_filter"}},
                     {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]}]:
            with self.assertRaises(ModelError) as caught: self.invoke(body)
            self.assertFalse(caught.exception.structural or caught.exception.transient)

    def test_judge_uses_strict_schema_same_transport_and_preserves_valid_fail(self):
        model = ResponsesModel("gpt-6-sol", api_key="not-a-real-key")
        payload, cache = model.build_payload(stage="shortlist_golden_judge", instructions=ev.JUDGE_INSTRUCTIONS,
            context={"exact_evaluated_source": "Synthetic JD"}, output_schema=ev.JUDGE_SCHEMA)
        fmt = payload["text"]["format"]
        self.assertEqual(fmt["type"], "json_schema"); self.assertTrue(fmt["strict"])
        self.assertEqual(payload["model"], "gpt-6-sol")
        self.assertFalse(payload["store"]); self.assertEqual(payload["truncation"], "disabled")
        self.assertLessEqual(len(fmt["name"]), 64)
        self.assertIsNone(cache)
        self.assertNotIn("prompt_cache_options", payload)
        Draft202012Validator.check_schema(fmt["schema"])
        value = eval_fixtures.response()
        for row in value.values(): row.update(status="FAIL", could_change_decision=True,
            material_discrepancy="Synthetic unsupported claim", failure_kind="unsupported_career_claim")
        Draft202012Validator(fmt["schema"]).validate(value)
        out, _ = self.invoke({"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(value)}]}]}, ev.JUDGE_SCHEMA, "shortlist_golden_judge")
        self.assertEqual(out, value)


class RunnerReliabilityTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    execute = fixtures.RunnerTests.execute

    def test_exact_span_and_grounded_derived_limitation_are_separate(self):
        def mapping(stage, out):
            if stage == "career_requirements_mapping":
                out[stage]["criteria"][0]["limitation_or_difference"] = "Derived interpretation: reusable deployment ownership does not establish fleet-scale operations."
        with redirect_stdout(io.StringIO()): _, artifact, model = self.execute(fixtures.FakeModel(mapping))
        row = artifact["stage_outputs"]["career_requirements_mapping"]["evidence_provenance"][0]["sources"][0]
        self.assertEqual(row["quote"], fixtures.CAPABILITY)
        self.assertIn("never a paraphrase", model.calls[1]["instructions"])

    def test_paraphrase_cannot_masquerade_as_quote(self):
        for quote in ("Owned deployment workflows and kept releases safe.", "Invented personal ownership."):
            def mapping(stage, out):
                if stage == "career_requirements_mapping": out["evidence_provenance"][0]["sources"][0]["quote"] = quote
            model = fixtures.FakeModel(mapping)
            with redirect_stdout(io.StringIO()), self.assertRaises(runner.RunError): self.execute(model)
            self.assertEqual(len(model.calls), 2)  # Grounding failure is not technical retry.

    def test_incomplete_retries_once_and_usage_includes_failed_attempt(self):
        model = fixtures.FakeModel(); complete = model.complete; attempts = []
        def request(**kwargs):
            attempts.append(kwargs["stage"])
            if len(attempts) == 2:
                raise ModelError("Truncated", structural=True, error_type="IncompleteResponse",
                    response_metadata={"usage": {"input_tokens": 7, "output_tokens": 9}})
            return complete(**kwargs)
        model.complete = request
        with patch("run_shortlist_job.time.sleep"), redirect_stdout(io.StringIO()):
            _, artifact, _ = self.execute(model)
        self.assertEqual(attempts.count("career_requirements_mapping"), 2)
        self.assertEqual(artifact["completed_stages"], list(runner.STAGES))
        self.assertEqual(len(artifact["model_calls"]), 4)
        self.assertEqual(artifact["usage_summary"]["totals"]["input_tokens"], 407)
        self.assertEqual(sum(x["input_tokens"] for x in ev.agent_telemetry(artifact)), 407)

    def test_second_incomplete_is_terminal_without_duplicate_state(self):
        model = fixtures.FakeModel(); complete = model.complete; attempts = []
        def request(**kwargs):
            attempts.append(kwargs["stage"])
            if kwargs["stage"] == "career_requirements_mapping": raise ModelError("Incomplete", structural=True)
            return complete(**kwargs)
        model.complete = request
        with patch("run_shortlist_job.time.sleep"), redirect_stdout(io.StringIO()), self.assertRaises(runner.RunError) as caught:
            self.execute(model)
        artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(attempts.count("career_requirements_mapping"), 2)
        self.assertEqual(artifact["completed_stages"], ["role_understanding"])
        self.assertEqual(artifact["status"], "failed")

    def test_controller_rejection_never_retries(self):
        def reject(stage, out):
            if stage == "controller_validation":
                out["validation"] = {k: False for k in out["validation"]}
                out["issues"] = [dict(stage="career_requirements_mapping", description="Unsupported claim", required_action="Review evidence")]
        with redirect_stdout(io.StringIO()): _, artifact, model = self.execute(fixtures.FakeModel(reject))
        self.assertEqual(artifact["status"], "rejected")
        self.assertEqual(len(model.calls), 4)


class JudgeRetryTests(unittest.TestCase):
    def test_technical_retry_retains_usage_but_semantic_fail_is_not_retried(self):
        judge = eval_fixtures.Judge(); complete = judge.complete; calls = []
        def request(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise ModelError("Incomplete", structural=True, response_metadata={"usage": {"input_tokens": 7, "output_tokens": 8}})
            out, metadata = complete(**kwargs)
            out[ev.DIMENSIONS[0]].update(status="FAIL", could_change_decision=True,
                material_discrepancy="Missing requirement", failure_kind="missed_material_requirement")
            return out, metadata
        judge.complete = request; result = {"usage": {}}; checkpoint = Mock()
        with patch("eval_shortlist.time.sleep"):
            out = ev.call_judge(judge, {}, result, checkpoint)
        self.assertEqual(len(calls), 2); self.assertEqual(checkpoint.call_count, 2)
        self.assertEqual(out[ev.DIMENSIONS[0]]["status"], "FAIL")
        self.assertEqual(ev.usage([result])["judge"]["input_tokens"], 47)

    def test_terminal_400_retains_exact_sanitized_api_error_without_retry(self):
        judge = eval_fixtures.Judge()
        diagnostic = {"http_status": 400, "error": {"code": "invalid_json_schema", "type": "invalid_request_error", "message": "Synthetic invalid schema"}}
        judge.complete = Mock(side_effect=ModelError("HTTP 400", diagnostics=diagnostic))
        result = {"usage": {}}
        with self.assertRaises(ModelError): ev.call_judge(judge, {}, result, lambda: None)
        self.assertEqual(judge.complete.call_count, 1)
        self.assertEqual(result["judge_attempts"][0]["api_diagnostics"], diagnostic)

    def test_repeated_technical_failure_stops_after_two_attempts(self):
        judge = eval_fixtures.Judge(); judge.complete = Mock(side_effect=ModelError("timeout", transient=True))
        result = {"usage": {}}
        with patch("eval_shortlist.time.sleep"), self.assertRaises(ModelError):
            ev.call_judge(judge, {}, result, lambda: None)
        self.assertEqual(judge.complete.call_count, 2)
        self.assertEqual([a["retry"] for a in result["judge_attempts"]], [True, False])


if __name__ == "__main__": unittest.main()
