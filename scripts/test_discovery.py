import json
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from discovery.filters import pm_candidate_decision
from discovery.greenhouse import CrawlError, fetch_greenhouse_jobs
from discovery.models import canonicalize_url, stable_job_id, validate_raw_jobs
from discover_jobs import run
from eval_discovery import load_jsonl, write_reports
from eval_discovery import evaluate


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "jobs": [
                {
                    "id": 101,
                    "title": "Product Manager, Claude",
                    "location": {"name": "San Francisco, CA"},
                    "absolute_url": "https://job-boards.greenhouse.io/anthropic/jobs/101?gh_jid=101",
                    "content": "<p>Build product.</p>",
                    "updated_at": "2026-09-21T01:02:03-07:00",
                    "departments": [{"name": "Product Management"}],
                },
                {
                    "id": 102,
                    "title": "Product Marketing Manager, Claude",
                    "location": {"name": "New York City, NY"},
                    "absolute_url": "https://job-boards.greenhouse.io/anthropic/jobs/102",
                    "content": "<p>Market product.</p>",
                    "updated_at": "2026-09-21T01:02:03-07:00",
                    "departments": [{"name": "Marketing"}],
                },
            ]
        }


class FakeSession:
    def get(self, url, params=None, timeout=None):
        self.url = url
        self.params = params
        return FakeResponse()


class DiscoveryTests(unittest.TestCase):
    def test_greenhouse_adapter_extracts_raw_facts(self):
        source = {"company": "Anthropic", "board_token": "anthropic", "careers_url": "https://job-boards.greenhouse.io/anthropic"}
        jobs, telemetry = fetch_greenhouse_jobs("anthropic", source, session=FakeSession())
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["job_id"], "anthropic:101")
        self.assertEqual(jobs[0]["title"], "Product Manager, Claude")
        self.assertEqual(jobs[0]["description"], "Build product.")
        self.assertEqual(jobs[0]["posting_date"], "")
        self.assertEqual(telemetry["jobs_seen"], 2)
        self.assertEqual(telemetry["status"], "success")
        validate_raw_jobs(jobs)

    def test_high_recall_pm_filter_keeps_pm_but_not_product_marketing(self):
        self.assertTrue(pm_candidate_decision("Product Manager, Claude")[0])
        self.assertTrue(pm_candidate_decision("Product Management, Research")[0])
        self.assertTrue(pm_candidate_decision("Product Lead, AI Platform")[0])
        self.assertFalse(pm_candidate_decision("Product Marketing Manager, Claude")[0])
        self.assertFalse(pm_candidate_decision("Product Operations Manager")[0])

    def test_eval_harness_reports_misses(self):
        reference = [
            {"company": "Anthropic", "external_job_id": "101", "title": "A", "location": "SF"},
            {"company": "Anthropic", "external_job_id": "103", "title": "B", "location": "SF"},
        ]
        discovered = [
            {"company": "Anthropic", "external_job_id": "101", "title": "A", "location": "SF"},
        ]
        result = evaluate(reference, discovered)
        self.assertEqual(result["found_count"], 1)
        self.assertEqual(result["missed_count"], 1)
        self.assertEqual(result["known_positive_recall"], 0.5)


class DiscoveryRobustnessTests(unittest.TestCase):
    source = {"company": "Anthropic", "board_token": "anthropic"}

    def test_all_reviewed_title_families(self):
        for title in ["Product Manager", "Product Management", "Principal PM", "Principal PM-T",
                      "Staff PM", "Group Product Manager", "Product Lead", "Product Owner", "Research Product Manager"]:
            with self.subTest(title=title):
                self.assertTrue(pm_candidate_decision(title)[0])
        for title in ["Product Operations Manager, Embedded", "Product Marketing", "Product Support",
                      "Product Design", "Product Designer", "Product Counsel", "Software Engineer"]:
            with self.subTest(title=title):
                self.assertFalse(pm_candidate_decision(title)[0])

    def test_http_error_keeps_telemetry(self):
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests.HTTPError("unavailable")
        with self.assertRaises(CrawlError) as caught:
            fetch_greenhouse_jobs("anthropic", self.source, Mock(get=Mock(return_value=response)))
        telemetry = caught.exception.telemetry
        self.assertEqual(telemetry["http_status"], 503)
        self.assertEqual(telemetry["request_count"], 1)
        self.assertTrue(telemetry["started_at"])
        self.assertTrue(telemetry["completed_at"])
        self.assertEqual(telemetry["status"], "failed")

    def test_timeout_keeps_attempt_count(self):
        with self.assertRaises(CrawlError) as caught:
            fetch_greenhouse_jobs("anthropic", self.source, Mock(get=Mock(side_effect=requests.Timeout("timeout"))))
        self.assertEqual(caught.exception.telemetry["request_count"], 1)

    def test_malformed_payload_fails_observably(self):
        response = Mock(status_code=200)
        response.json.return_value = {"jobs": {}}
        with self.assertRaises(CrawlError) as caught:
            fetch_greenhouse_jobs("anthropic", self.source, Mock(get=Mock(return_value=response)))
        self.assertIn("jobs list", caught.exception.telemetry["errors"][0])

    def test_duplicate_and_invalid_raw_records_rejected(self):
        jobs, _ = fetch_greenhouse_jobs("anthropic", self.source, FakeSession())
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_raw_jobs([jobs[0], jobs[0]])
        for changes in [{"canonical_url": "https://"}, {"title": None}, {"fit_score": "1"}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_raw_jobs([dict(jobs[0], **changes)])

    def test_null_external_id_uses_url_identity(self):
        response = Mock(status_code=200)
        payload = FakeResponse().json()
        payload["jobs"][0]["id"] = None
        response.json.return_value = payload
        jobs, _ = fetch_greenhouse_jobs("anthropic", self.source, Mock(get=Mock(return_value=response)))
        self.assertEqual(jobs[0]["external_job_id"], "")
        self.assertIn(":url-", jobs[0]["job_id"])

    def test_url_normalization_preserves_functional_query(self):
        self.assertEqual(canonicalize_url("https://EXAMPLE.com/job/?id=42&utm_source=x#apply"), "https://example.com/job?id=42")
        self.assertNotEqual(stable_job_id("A", "", "https://example.com/1"), stable_job_id("A", "", "https://example.com/2"))

    def test_matching_fallback_on_either_missing_id(self):
        row = dict(company="Anthropic", external_job_id="101", title="Product Manager", location="New York")
        for reference, discovered in [(row, dict(row, external_job_id="")), (dict(row, external_job_id=""), row)]:
            self.assertEqual(evaluate([reference], [discovered])["found_count"], 1)
        self.assertEqual(evaluate([row], [dict(row, external_job_id="102")])["found_count"], 0)
        self.assertEqual(evaluate([row], [dict(row, company="Other")])["found_count"], 0)

    def test_id_match_ignores_title_location_drift(self):
        row = dict(company="Anthropic", external_job_id="101", title="Old", location="SF")
        self.assertEqual(evaluate([row], [dict(row, title="New", location="NY")])["found_count"], 1)

    def test_ambiguous_fallback_and_duplicate_reference(self):
        row = dict(company="Anthropic", title="PM", location="SF")
        self.assertEqual(evaluate([row], [dict(row, external_job_id="1"), dict(row, external_job_id="2")])["found_count"], 0)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            evaluate([row, row], [])

    def test_approved_reference_exactly_nineteen(self):
        rows = [row for row in load_jsonl(ROOT / "data/evals/discovery_reference.jsonl") if row["company"] == "Anthropic"]
        self.assertEqual(len(rows), 19)
        self.assertEqual(len({row["external_job_id"] for row in rows}), 19)
        self.assertNotIn("5179891008", {row["external_job_id"] for row in rows})
        for row in rows:
            self.assertTrue(row["canonical_url"].endswith("/jobs/" + row["external_job_id"]))
            self.assertTrue(row["reference_source"])
            self.assertTrue(row["reference_captured_at"])

    def test_run_preserves_raw_exclusions_and_failed_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config/job_sources.yaml").write_text("sources:\n  anthropic:\n    company: Anthropic\n    adapter: greenhouse\n    board_token: anthropic\n")
            jobs, telemetry = fetch_greenhouse_jobs("anthropic", self.source, FakeSession())
            with patch("discover_jobs.fetch_greenhouse_jobs", return_value=(jobs, telemetry)):
                result = run(["anthropic"], root)
            self.assertEqual(result["raw_jobs"], 2)
            self.assertEqual(result["pm_candidates"], 1)
            output = root / "data/discovery"
            self.assertEqual(len(load_jsonl(output / "raw_all_jobs.jsonl")), 2)
            before = (output / "raw_all_jobs.jsonl").read_bytes()
            failed = dict(telemetry, status="failed", errors=["HTTP 503"], http_status=503)
            with patch("discover_jobs.fetch_greenhouse_jobs", side_effect=CrawlError(failed)):
                result = run(["anthropic"], root)
            self.assertTrue(result["failures"])
            self.assertEqual((output / "raw_all_jobs.jsonl").read_bytes(), before)
            self.assertEqual(load_jsonl(output / "crawl_runs.jsonl")[-1]["http_status"], 503)
            self.assertEqual(len(list((output / "runs").glob("*/raw_all_jobs.jsonl"))), 1)

    def test_reports_include_company_candidates_and_missed_ids(self):
        row = dict(company="Anthropic", external_job_id="123", title="PM", location="SF")
        with tempfile.TemporaryDirectory() as temp:
            write_reports(evaluate([row], []), Path(temp))
            self.assertIn("123", (Path(temp) / "missed_jobs.csv").read_text(encoding="utf-8-sig"))
            self.assertIn("discovered", (Path(temp) / "company_metrics.csv").read_text(encoding="utf-8-sig"))

    def test_missing_eval_input_is_not_empty_success(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(FileNotFoundError):
            load_jsonl(Path(temp) / "absent.jsonl")


if __name__ == "__main__":
    unittest.main()
