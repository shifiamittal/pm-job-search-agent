"""Offline tests for per-stage models, caching layout, telemetry, and resume."""
from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

import run_shortlist_job as runner
from shortlist_contract import load_schema
from shortlist_model import ModelError, ResponsesModel
import test_shortlist_runner as fixtures


MIX = {
    "role_understanding": "gpt-6-luna",
    "career_requirements_mapping": "gpt-6-sol",
    "shortlist_decision": "gpt-6-astra",
    "controller_validation": "gpt-5.6-terra",
}


class StageModelTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp

    def run_mixed(self, model=None):
        model = model or fixtures.FakeModel()
        directory = runner.run_job(
            fixtures.input_job(), model, output_root=self.root / "runs",
            candidate_root=self.root, stage_models=MIX)
        artifact = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        return directory, artifact, model

    def test_four_stage_models_are_used_saved_and_audited(self):
        _, artifact, model = self.run_mixed()
        self.assertEqual([call["model"] for call in model.calls], [MIX[stage] for stage in runner.STAGES])
        self.assertEqual(artifact["stage_models"], MIX)
        self.assertEqual([call["requested_model"] for call in artifact["model_calls"]],
                         [MIX[stage] for stage in runner.STAGES])
        completed = [event for event in artifact["history"] if event["event"] == "stage_completed"]
        self.assertEqual([event["requested_model"] for event in completed],
                         [MIX[stage] for stage in runner.STAGES])
        Draft202012Validator(load_schema()).validate(artifact["shortlist_state"])

    def test_single_model_is_backward_compatible_fallback(self):
        expected = {stage: "one-model" for stage in runner.STAGES}
        self.assertEqual(runner.resolve_stage_models("one-model"), expected)
        model = fixtures.FakeModel()
        model.model = "one-model"
        directory = runner.run_job(fixtures.input_job(), model, output_root=self.root / "runs",
                                   candidate_root=self.root)
        artifact = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["stage_models"], expected)
        self.assertEqual([call["model"] for call in model.calls], ["one-model"] * 4)

    def test_downstream_model_change_does_not_invalidate_completed_stages(self):
        def fail_decision(stage, output):
            if stage == "shortlist_decision":
                raise ModelError("synthetic terminal failure", error_type="Synthetic", transient=False)
        first = fixtures.FakeModel(fail_decision)
        with self.assertRaises(runner.RunError) as caught:
            runner.run_job(fixtures.input_job(), first, output_root=self.root / "runs",
                           candidate_root=self.root, stage_models=MIX)
        changed = dict(MIX, shortlist_decision="gpt-6-sol", controller_validation="gpt-6-sol")
        resumed = fixtures.FakeModel()
        runner.resume_job(caught.exception.run_dir, resumed, candidate_root=self.root, stage_models=changed)
        self.assertEqual([call["stage"] for call in resumed.calls], list(runner.STAGES[2:]))
        self.assertEqual([call["model"] for call in resumed.calls], ["gpt-6-sol", "gpt-6-sol"])
        artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["stage_models"], changed)
        self.assertEqual([call["requested_model"] for call in artifact["model_calls"][:2]],
                         [MIX[stage] for stage in runner.STAGES[:2]])

    def test_changed_model_for_completed_stage_blocks_resume(self):
        def fail_decision(stage, output):
            if stage == "shortlist_decision":
                raise ModelError("synthetic terminal failure", transient=False)
        with self.assertRaises(runner.RunError) as caught:
            runner.run_job(fixtures.input_job(), fixtures.FakeModel(fail_decision),
                           output_root=self.root / "runs", candidate_root=self.root, stage_models=MIX)
        changed = dict(MIX, role_understanding="gpt-6-sol")
        with self.assertRaisesRegex(ValueError, "model identity changed"):
            runner.resume_job(caught.exception.run_dir, fixtures.FakeModel(),
                              candidate_root=self.root, stage_models=changed)

    def test_cache_token_telemetry_is_saved_and_totaled(self):
        class CachedModel(fixtures.FakeModel):
            def complete(self, **request):
                output, metadata = super().complete(**request)
                metadata["usage"]["input_tokens_details"]["cached_tokens"] = 80
                metadata["usage"]["input_tokens_details"]["cache_write_tokens"] = 10
                return output, metadata

        _, artifact, _ = self.run_mixed(CachedModel())
        mapping = artifact["usage_summary"]["stages"]["career_requirements_mapping"]
        self.assertEqual(mapping["cached_input_tokens"], 80)
        self.assertEqual(mapping["cache_write_input_tokens"], 10)
        self.assertEqual(artifact["usage_summary"]["totals"]["cached_input_tokens"], 320)
        self.assertEqual(artifact["usage_summary"]["totals"]["reasoning_tokens"], 20)


class MappingCacheLayoutTests(unittest.TestCase):
    def test_stable_prefix_is_deterministic_and_job_content_follows_it(self):
        candidate = {name: {"content": f"Exact unchanged content for {name}\r\n", "sha256": "same"}
                     for name in runner.CANDIDATE_FILES}
        schema = {"type": "object", "properties": {"answer": {"type": "string"}},
                  "required": ["answer"], "additionalProperties": False}
        first_context = {"input_job": {"company": "One"}, "upstream": {"role": "one"},
                         "candidate_context": deepcopy(candidate)}
        second_context = {"input_job": {"company": "Two"}, "upstream": {"role": "two"},
                          "candidate_context": deepcopy(candidate)}
        transport = ResponsesModel("gpt-6-sol", api_key="test")
        first, first_meta = transport.build_payload(
            stage="career_requirements_mapping", instructions="UNCHANGED INSTRUCTIONS",
            context=first_context, output_schema=schema, model="gpt-6-sol")
        second, second_meta = transport.build_payload(
            stage="career_requirements_mapping", instructions="UNCHANGED INSTRUCTIONS",
            context=second_context, output_schema=schema, model="gpt-6-sol")

        first_blocks = first["input"][0]["content"]
        second_blocks = second["input"][0]["content"]
        self.assertEqual(first_blocks[0], second_blocks[0])
        self.assertNotEqual(first_blocks[1], second_blocks[1])
        self.assertEqual(first["prompt_cache_key"], second["prompt_cache_key"])
        self.assertEqual(first_meta, second_meta)
        self.assertEqual(first["prompt_cache_options"], {"mode": "explicit"})
        rendered = json.loads("".join(block["text"] for block in first_blocks))
        self.assertEqual(rendered["context"], {
            "candidate_context": candidate,
            "input_job": first_context["input_job"],
            "upstream": first_context["upstream"],
        })
        self.assertEqual(rendered["required_output_schema"], schema)
        self.assertEqual(first_blocks[0]["prompt_cache_breakpoint"], {"mode": "explicit"})


class StructuredOutputTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()
        self.transport = ResponsesModel("gpt-6-luna", api_key="test")

    def payload(self, stage):
        payload, _ = self.transport.build_payload(
            stage=stage, instructions="UNCHANGED INSTRUCTIONS", context={},
            output_schema=runner.stage_schema(self.schema, stage), model="gpt-6-luna")
        return payload

    def test_all_four_stages_use_strict_json_schema(self):
        unsupported = {"allOf", "not", "dependentRequired", "dependentSchemas",
                       "if", "then", "else"}
        for stage in runner.STAGES:
            with self.subTest(stage=stage):
                response_format = self.payload(stage)["text"]["format"]
                self.assertEqual(response_format["type"], "json_schema")
                self.assertTrue(response_format["strict"])
                self.assertEqual(response_format["name"], "shortlist_" + stage)
                encoded = json.dumps(response_format["schema"])
                for keyword in unsupported:
                    self.assertNotIn(f'"{keyword}"', encoded)

    def test_controller_api_schema_requires_check_rationales(self):
        api_schema = self.payload("controller_validation")["text"]["format"]["schema"]
        self.assertIn("check_rationales", api_schema["required"])
        invalid = {
            "validation": {key: True for key in self.schema["$defs"]["validation"]["properties"]},
            "evidence_checks": [], "issues": [],
        }
        errors = list(Draft202012Validator(api_schema).iter_errors(invalid))
        self.assertTrue(any(error.validator == "required" and
                            "check_rationales" in error.message for error in errors))

    def test_decision_api_schema_enforces_authoritative_enum(self):
        api_schema = self.payload("shortlist_decision")["text"]["format"]["schema"]
        decision_enum = api_schema["properties"]["decision"]["enum"]
        self.assertEqual(decision_enum, ["APPLY — PRIORITY", "APPLY", "HOLD / INVESTIGATE", "DO NOT APPLY"])
        fixture = deepcopy(fixtures.example_record()["shortlist_decision"])
        fixture["decision"] = "MAYBE"
        self.assertTrue(any(error.validator == "enum"
                            for error in Draft202012Validator(api_schema).iter_errors(fixture)))

    def test_authoritative_schema_and_local_conditional_validation_remain(self):
        authoritative = runner.stage_schema(self.schema, "controller_validation")
        self.assertIn("allOf", authoritative["$defs"]["validation"])
        api_schema = self.payload("controller_validation")["text"]["format"]["schema"]
        self.assertNotIn("allOf", api_schema["$defs"]["validation"])


class StructuredOutputResumeTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp

    def test_json_object_checkpoint_resumes_at_controller_with_strict_output(self):
        def fail_controller(stage, output):
            if stage == "controller_validation":
                output.pop("check_rationales")
        with self.assertRaises(runner.RunError) as caught:
            runner.run_job(fixtures.input_job(), fixtures.FakeModel(fail_controller),
                           output_root=self.root / "runs", candidate_root=self.root,
                           stage_models=MIX)
        path = caught.exception.run_dir / "job_state.json"
        artifact = json.loads(path.read_text(encoding="utf-8"))
        for stage in artifact["completed_stages"]:
            artifact["stage_model_settings"][stage]["text_format"] = "json_object"
        artifact["model_settings"]["text_format"] = "json_object"
        path.write_text(runner._json(artifact), encoding="utf-8")

        resumed = fixtures.FakeModel()
        runner.resume_job(caught.exception.run_dir, resumed, candidate_root=self.root,
                          stage_models=MIX)
        self.assertEqual([call["stage"] for call in resumed.calls], ["controller_validation"])
        final = json.loads(path.read_text(encoding="utf-8"))
        for stage in runner.STAGES[:3]:
            self.assertEqual(final["stage_model_settings"][stage]["text_format"], "json_object")
        self.assertEqual(final["stage_model_settings"]["controller_validation"]["text_format"],
                         "json_schema_strict")


if __name__ == "__main__":
    unittest.main()
