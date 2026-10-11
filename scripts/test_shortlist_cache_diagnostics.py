"""Tests for the no-workflow prompt-cache diagnostic utility."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest import mock
import unittest

import run_shortlist_job as runner
import shortlist_cache_diagnostics as diagnostics
from shortlist_cache_diagnostics import compare_saved_runs
from shortlist_model import ResponsesModel


def artifact(run_id, company, completed_at):
    candidate = {
        name: {"content": f"content for {name}", "sha256": f"hash-{index}"}
        for index, name in enumerate(runner.CANDIDATE_FILES)
    }
    normalized = {"company": company, "title": "Product Lead",
                  "full_job_description_raw": f"JD for {company}"}
    role = {"role_identity": {"company": company}}
    context = {"input_job": normalized, "upstream": {"role_understanding": role},
               "candidate_context": candidate}
    _, suffix = ResponsesModel.mapping_prompt_parts(
        stage="career_requirements_mapping", context=context, output_schema={})
    del suffix
    return {
        "run_id": run_id, "normalized_job": normalized, "candidate_context": candidate,
        "stage_outputs": {"role_understanding": role},
        "model_calls": [{
            "stage": "career_requirements_mapping", "requested_model": "gpt-6-sol",
            "instructions_sha256": "instructions", "context_sha256": runner._hash(runner._json(context)),
            "response": {"model": "gpt-6-sol", "max_output_tokens": 12000,
                         "prompt_cache": {"key": "shared", "stable_prefix_sha256": "prefix",
                                          "explicit_breakpoint": True},
                         "usage": {"input_tokens": 30000,
                                   "input_tokens_details": {"cached_tokens": 0,
                                                            "cache_write_tokens": 29000}}},
        }],
        "history": [{"event": "stage_completed", "stage": "career_requirements_mapping",
                     "at": completed_at.isoformat()}],
    }


class SavedCacheComparisonTests(unittest.TestCase):
    def test_identical_prefix_and_first_suffix_difference_are_reported(self):
        now = datetime.now(timezone.utc)
        report = compare_saved_runs(artifact("a", "Count", now),
                                    artifact("b", "Microsoft", now + timedelta(hours=12)))
        self.assertTrue(report["before_explicit_breakpoint"]["identical"])
        self.assertEqual(report["first_job_specific_difference"]["semantic"]["path"],
                         "$.input_job.company")
        self.assertTrue(report["outside_guaranteed_lifetime"])
        self.assertEqual(report["completion_gap_seconds"], 12 * 60 * 60)

    def test_changed_candidate_hash_marks_prefix_nonidentical(self):
        now = datetime.now(timezone.utc)
        left = artifact("a", "Count", now)
        right = artifact("b", "Microsoft", now + timedelta(minutes=1))
        right["candidate_context"][runner.CANDIDATE_FILES[0]]["sha256"] = "changed"
        report = compare_saved_runs(left, right)
        self.assertFalse(report["before_explicit_breakpoint"]["identical"])
        self.assertFalse(report["before_explicit_breakpoint"]["checks"]["candidate_file_hashes"])

    def test_context_reconstruction_is_verified(self):
        now = datetime.now(timezone.utc)
        left = artifact("a", "Count", now)
        right = artifact("b", "Microsoft", now + timedelta(minutes=1))
        left["model_calls"][0]["context_sha256"] = "tampered"
        report = compare_saved_runs(left, right)
        saved = report["saved_request_fingerprints"]["a"]
        self.assertFalse(saved["context_reconstruction_matches"])

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @mock.patch.object(diagnostics.requests, "post")
    def test_live_probe_makes_exactly_two_calls_and_compares_the_second(self, post):
        class Response:
            status_code = 200
            headers = {}

            def __init__(self, response_id, cached, written):
                self.response_id = response_id
                self.cached = cached
                self.written = written

            def json(self):
                return {"id": self.response_id, "status": "incomplete", "model": "gpt-6-sol",
                        "service_tier": "default",
                        "usage": {"input_tokens": 100,
                                  "input_tokens_details": {"cached_tokens": self.cached,
                                                           "cache_write_tokens": self.written}}}

        post.side_effect = [Response("first", 0, 90), Response("second", 90, 0)]
        report = diagnostics.run_live_probe(max_output_tokens=32)
        self.assertEqual(post.call_count, 2)
        first_payload = post.call_args_list[0].kwargs["json"]
        second_payload = post.call_args_list[1].kwargs["json"]
        self.assertEqual(first_payload["input"][0]["content"][0],
                         second_payload["input"][0]["content"][0])
        self.assertNotEqual(first_payload["input"][0]["content"][1],
                            second_payload["input"][0]["content"][1])
        self.assertEqual(second_payload["prompt_cache_options"]["comparison_response_id"],
                         "first")
        self.assertEqual(report["request_count"], 2)
        self.assertEqual(report["second"]["usage"]["input_tokens_details"]["cached_tokens"], 90)


if __name__ == "__main__":
    unittest.main()
