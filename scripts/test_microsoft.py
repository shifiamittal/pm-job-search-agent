import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from discovery.errors import CrawlError
from discovery.microsoft import fetch_microsoft_jobs, in_target_geography
from discover_jobs import retain_candidate, run
from eval_discovery import load_jsonl

SOURCE = {"company": "Microsoft", "adapter": "microsoft"}


def item(ident, locations=None, title="Principal Product Manager"):
    return dict(id=ident, displayJobId=str(ident + 1000), atsJobId=str(ident + 1000),
                name=title, locations=locations if locations is not None else ["India, Telangana, Hyderabad"],
                positionUrl=f"/careers/job/{ident}", department="Product Management", postedTs=1790070490)


def page(ids, count):
    return dict(status=200, data=dict(positions=[item(ident) for ident in ids], count=count,
                                    appliedFilters={"profession": ["product management"]}))


def response(payload, status=200, headers=None):
    r = Mock(status_code=status, headers=headers or {})
    r.json.return_value = payload
    if status >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}")
    return r


def fetch(pages, **kwargs):
    session = Mock()
    session.get.side_effect = [value if isinstance(value, (Exception, Mock)) else response(value) for value in pages]
    sleeper = Mock()
    kwargs.setdefault("verify_availability", False)
    result = fetch_microsoft_jobs("microsoft", SOURCE, session, sleep=sleeper,
                                  monotonic=lambda: 0, **kwargs)
    return result, session, sleeper


class MicrosoftTests(unittest.TestCase):
    def test_listing_detail_availability_mismatch_preserves_raw_and_excludes_live(self):
        active = dict(status=200, data=dict(id=1, displayJobId="1001", jobDescription="Current job",
                      positionUserActions={"applyAction": {"status": "log_in"}}))
        fallback = dict(status=200, data={}, metadata={"isFallback": True})
        data = page([1, 2, 3], 3)
        (jobs, telemetry), _, _ = fetch([data, page([], 3), data, active,
                                         response({}, 404), fallback], verify_availability=True)
        self.assertEqual(len(jobs), 3)
        self.assertEqual([job["external_job_id"] for job in jobs if retain_candidate(job)], ["1"])
        self.assertEqual([job["availability_status"] for job in jobs],
                         ["available", "stale_unavailable", "stale_unavailable"])
        self.assertEqual(len(telemetry["source_records"]), 3)
        self.assertEqual(telemetry["availability_checks"][1]["http_status"], 404)
        self.assertTrue(jobs[1]["availability_checked_at"])

    def test_unknown_detail_not_falsely_classified_stale_or_live(self):
        data = page([1], 1)
        mismatch = dict(status=200, data=dict(id=999, displayJobId="1001"))
        (jobs, _), _, _ = fetch([data, page([], 1), data, mismatch], verify_availability=True)
        self.assertEqual(jobs[0]["availability_status"], "unknown")
        self.assertFalse(retain_candidate(jobs[0]))

    def test_internships_excluded_by_title_or_source_employment_type(self):
        data = page([1, 2], 2)
        data["data"]["positions"][0]["name"] = "Product Management Intern - CTJ - TS"
        intern = dict(status=200, data=dict(id=2, displayJobId="1002", jobDescription="Intern job",
                      efcustomTextEmploymentType=["Internship"],
                      positionUserActions={"applyAction": {"status": "log_in"}}))
        (jobs, telemetry), _, _ = fetch([data, page([], 2), data, intern], verify_availability=True)
        self.assertFalse(any(retain_candidate(job) for job in jobs))
        self.assertEqual(len(jobs), 2)
        self.assertEqual(len(telemetry["availability_checks"]), 1)

    def test_reviewed_benchmark_has_63_unique_positions_and_requisitions(self):
        root = Path(__file__).resolve().parents[1]
        rows = load_jsonl(root / "data/evals/microsoft_pm_reference_final_reviewed.jsonl")
        self.assertEqual(len(rows), 63)
        self.assertEqual(len({row["external_job_id"] for row in rows}), 63)
        self.assertEqual(len({row["requisition_id"] for row in rows}), 63)
        by_req = {row["requisition_id"]: row for row in rows}
        self.assertEqual(by_req["200045393"]["external_job_id"], "1970393556944421")
        self.assertEqual(by_req["200055927"]["external_job_id"], "1970393556999250")
        self.assertTrue(all(in_target_geography(row) for row in rows))
        combined = load_jsonl(root / "data/evals/discovery_reference.jsonl")
        self.assertEqual([row for row in combined if row["company"] == "Microsoft"], rows)

    def test_full_facet_pagination_source_identity_and_metadata(self):
        (jobs, telemetry), session, _ = fetch([page([1, 2], 3), page([3], 3), page([], 3),
                                               page([1, 2], 3), page([3], 3)])
        self.assertEqual([job["external_job_id"] for job in jobs], ["1", "2", "3"])
        self.assertEqual(jobs[0]["job_id"], "microsoft:1")
        self.assertEqual(jobs[0]["canonical_url"], "https://apply.careers.microsoft.com/careers/job/1")
        self.assertEqual(jobs[0]["description"], "")
        self.assertTrue(jobs[0]["posting_date"].endswith("+00:00"))
        self.assertEqual(telemetry["source_records"][0]["displayJobId"], "1001")
        self.assertEqual(telemetry["request_count"], 5)
        self.assertEqual(telemetry["source_reported_total"], 3)
        self.assertTrue(telemetry["passes"][0]["complete"])
        self.assertEqual([c.kwargs["params"]["start"] for c in session.get.call_args_list], [0, 2, 3, 0, 2])
        for call in session.get.call_args_list:
            self.assertEqual(call.kwargs["params"]["filter_profession"], "product management")
            self.assertEqual(call.kwargs["params"]["query"], "")
            self.assertEqual(call.kwargs["params"]["location"], "")

    def test_small_count_drift_can_reconcile_in_current_pass(self):
        (jobs, telemetry), _, _ = fetch([page([1, 2], 3), page([3, 4], 4), page([], 4),
                                         page([1, 2], 4), page([3, 4], 4)])
        self.assertEqual(len(jobs), 4)
        self.assertTrue(telemetry["passes"][0]["count_drift"])
        self.assertTrue(telemetry["passes"][0]["complete"])

    def test_duplicate_pass_reconciles_additions_and_removals_without_stale_union(self):
        (jobs, telemetry), _, _ = fetch([
            page([1, 2], 3), page([2, 3], 3), page([], 3), page([1, 2], 3), page([2, 3], 3),
            page([3, 4], 2), page([], 2), page([3, 4], 2)])
        self.assertEqual([job["external_job_id"] for job in jobs], ["3", "4"])
        self.assertEqual(telemetry["passes"][0]["duplicates"], ["2"])
        self.assertEqual(telemetry["passes"][1]["removed_since_previous_pass"], ["1", "2"])
        self.assertEqual(telemetry["passes"][1]["added_since_previous_pass"], ["4"])

    def test_boundary_id_drift_even_with_unchanged_count_requires_new_pass(self):
        (jobs, telemetry), _, _ = fetch([page([1], 1), page([], 1), page([2], 1),
                                         page([2], 1), page([], 1), page([2], 1)])
        self.assertEqual(jobs[0]["external_job_id"], "2")
        self.assertFalse(telemetry["passes"][0]["complete"])
        self.assertEqual(len(telemetry["passes"]), 2)

    def test_unresolved_drift_fails_with_original_audit(self):
        with self.assertRaises(CrawlError) as caught:
            fetch([page([1], 2), page([], 2), page([1], 2)], max_passes=1)
        telemetry = caught.exception.telemetry
        self.assertEqual(telemetry["status"], "failed")
        self.assertEqual(telemetry["passes"][0]["unique_count"], 1)
        self.assertEqual(telemetry["passes"][0]["reported_counts"], [2])

    def test_429_retry_after_and_transient_connection_attempts(self):
        (jobs, telemetry), _, sleeper = fetch([
            response({}, 429, {"Retry-After": "125"}), requests.ConnectionError("closed"),
            page([1], 1), page([], 1), page([1], 1)])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(telemetry["request_count"], 5)
        self.assertEqual(len(telemetry["errors"]), 2)
        sleeper.assert_any_call(125.0)
        sleeper.assert_any_call(120)

    def test_retries_are_bounded_and_403_is_not_retried(self):
        for responses, expected in [([response({}, 429)] * 3, 3), ([response({}, 403)], 1)]:
            with self.subTest(expected=expected), self.assertRaises(CrawlError) as caught:
                fetch(responses)
            self.assertEqual(caught.exception.telemetry["request_count"], expected)

    def test_503_recovers(self):
        (_, telemetry), _, _ = fetch([response({}, 503), page([], 0), page([], 0)])
        self.assertEqual(telemetry["status"], "success")
        self.assertEqual(telemetry["request_count"], 3)

    def test_filter_acknowledgment_required_prevents_full_board_crawl(self):
        data = page([1], 2300)
        data["data"]["appliedFilters"] = {}
        with self.assertRaises(CrawlError) as caught:
            fetch([data])
        self.assertEqual(caught.exception.telemetry["request_count"], 1)

    def test_malformed_count_payload_and_missing_id_fail(self):
        missing_id = page([1], 1)
        del missing_id["data"]["positions"][0]["id"]
        bad_count = page([], 0)
        bad_count["data"]["count"] = "0"
        for data in [{}, bad_count, missing_id]:
            with self.subTest(data=data), self.assertRaises(CrawlError):
                fetch([data])

    def test_empty_facet_is_verified(self):
        (jobs, telemetry), _, _ = fetch([page([], 0), page([], 0)])
        self.assertEqual(jobs, [])
        self.assertEqual(telemetry["source_reported_total"], 0)

    def test_pagination_safety_limit(self):
        with self.assertRaises(CrawlError) as caught:
            fetch([page([1], 2)], max_pages=1)
        self.assertIn("pagination safety limit", str(caught.exception))

    def test_geography_uses_any_source_location_not_city_guessing(self):
        for location, expected in [("United Kingdom, London | India, Telangana, Hyderabad", True),
                                   ("United States, Washington, Redmond", True),
                                   ("India, Multiple Locations", True),
                                   ("Canada, Ontario, Toronto", False),
                                   ("Hyderabad", False), ("", False)]:
            with self.subTest(location=location):
                self.assertEqual(in_target_geography({"location": location}), expected)

    def test_non_target_geography_retained_raw_but_excluded_from_candidates(self):
        data = page([1, 2], 2)
        data["data"]["positions"][1]["locations"] = ["Canada, Ontario, Toronto"]
        (jobs, telemetry), _, _ = fetch([data, page([], 2), data])
        self.assertEqual(len(jobs), 2)
        self.assertEqual(telemetry["geography_retained"], 1)
        self.assertEqual(telemetry["geography_excluded_ids"], ["2"])
        self.assertFalse(retain_candidate(jobs[0]))
        self.assertTrue(retain_candidate(dict(jobs[0], availability_status="available")))
        self.assertFalse(retain_candidate(jobs[1]))
        self.assertTrue(retain_candidate(dict(jobs[1], source_type="ashby")))

    def test_invalid_url_and_location_shape_fail(self):
        for key, value in [("positionUrl", "https://example.com/careers/job/1"),
                           ("positionUrl", "/careers/job/2"), ("locations", "India")]:
            data = page([1], 1)
            data["data"]["positions"][0][key] = value
            with self.subTest(key=key), self.assertRaises(CrawlError):
                fetch([data, page([], 1), data])

    def test_orchestrator_preserves_other_source_and_previous_outputs_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config/job_sources.yaml").write_text(
                "sources:\n  microsoft:\n    company: Microsoft\n    adapter: microsoft\n", encoding="utf-8")
            (jobs, telemetry), _, _ = fetch([page([1], 1), page([], 1), page([1], 1)])
            output = root / "data/discovery"
            output.mkdir(parents=True)
            other = dict(jobs[0], job_id="anthropic:1", company="Anthropic", source_type="greenhouse", source_key="anthropic")
            (output / "raw_all_jobs.jsonl").write_text(json.dumps(other) + "\n", encoding="utf-8")
            with patch("discover_jobs.fetch_microsoft_jobs", return_value=(jobs, telemetry)):
                self.assertFalse(run(["microsoft"], root)["failures"])
            saved = load_jsonl(output / "raw_all_jobs.jsonl")
            self.assertEqual(saved, [other] + jobs)
            before = (output / "raw_pm_candidates.jsonl").read_bytes()
            failure = copy.deepcopy(telemetry)
            failure.update(status="failed", errors=["unresolved count drift"])
            with patch("discover_jobs.fetch_microsoft_jobs", side_effect=CrawlError(failure)):
                self.assertTrue(run(["microsoft"], root)["failures"])
            self.assertEqual((output / "raw_pm_candidates.jsonl").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
