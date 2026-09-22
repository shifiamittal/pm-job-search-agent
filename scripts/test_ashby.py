import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from discovery.ashby import fetch_ashby_jobs
from discovery.errors import CrawlError
from discovery.filters import pm_candidate_decision
from discovery.greenhouse import fetch_greenhouse_jobs
from discover_jobs import run
from eval_discovery import evaluate, load_jsonl, validate_latest_crawls
from test_discovery import FakeSession

ROOT = Path(__file__).resolve().parents[1]
IDENT = "fc38c6bf-5330-435c-99b6-1bcf1f5829a8"
SOURCE = dict(company="OpenAI", adapter="ashby", board_token="openai", careers_url="https://jobs.ashbyhq.com/openai")


def payload():
    return {"apiVersion": "1", "jobs": [
        {"title": "Product Manager, API Agents", "location": "San Francisco, CA",
         "secondaryLocations": [{"location": "New York, NY"}, {"location": "San Francisco, CA"}],
         "jobUrl": f"https://jobs.ashbyhq.com/openai/{IDENT}?utm_source=test#apply",
         "descriptionPlain": "Build tools < 10 ms.", "department": "Product",
         "publishedAt": "2026-09-20T10:00:00Z", "isListed": True},
        {"title": "Product Operations Manager", "location": "London",
         "jobUrl": "https://jobs.ashbyhq.com/openai/7ffa2a14-fa9c-46cb-a30a-1f7a35ae904a",
         "isListed": False},
    ]}


def fetch(data=None):
    response = Mock(status_code=200)
    response.json.return_value = payload() if data is None else data
    session = Mock(get=Mock(return_value=response))
    result = fetch_ashby_jobs("openai", SOURCE, session)
    return result, session


class AshbyTests(unittest.TestCase):
    def test_response_identity_and_source_facts(self):
        (jobs, telemetry), session = fetch()
        session.get.assert_called_once_with("https://api.ashbyhq.com/posting-api/job-board/openai", timeout=45)
        self.assertEqual(jobs[0]["external_job_id"], IDENT)
        self.assertEqual(jobs[0]["job_id"], "openai:" + IDENT)
        self.assertEqual(jobs[0]["canonical_url"], "https://jobs.ashbyhq.com/openai/" + IDENT)
        self.assertEqual(jobs[0]["description"], "Build tools < 10 ms.")
        self.assertEqual(jobs[0]["department"], "Product")
        self.assertEqual(jobs[0]["source_updated_at"], "2026-09-20T10:00:00Z")
        self.assertEqual(jobs[0]["posting_date"], "")
        self.assertEqual(telemetry["jobs_seen"], 2)
        self.assertEqual(telemetry["jobs_extracted"], 2)
        self.assertEqual(telemetry["request_count"], 1)
        self.assertEqual(telemetry["status"], "success")

    def test_locations_preserve_secondary_and_deduplicate(self):
        (jobs, _), _ = fetch()
        self.assertEqual(jobs[0]["location"], "San Francisco, CA | New York, NY")
        self.assertEqual(jobs[1]["location"], "London")
        data = payload()
        data["jobs"][0]["location"] = None
        data["jobs"][0]["secondaryLocations"] = []
        (jobs, _), _ = fetch(data)
        self.assertEqual(jobs[0]["location"], "")

    def test_filter_only_after_full_extraction(self):
        (jobs, _), _ = fetch()
        self.assertEqual(len(jobs), 2)
        self.assertEqual([job["external_job_id"] for job in jobs if pm_candidate_decision(job["title"])[0]], [IDENT])

    def test_wrong_board_or_non_individual_url_fails(self):
        for url in ["http://jobs.ashbyhq.com/openai/" + IDENT,
                    "https://jobs.ashbyhq.com/other/" + IDENT,
                    "https://jobs.ashbyhq.com/openai", "https://example.com/openai/" + IDENT,
                    "https://jobs.ashbyhq.com/openai/not-a-job-id"]:
            data = payload()
            data["jobs"][0]["jobUrl"] = url
            with self.subTest(url=url), self.assertRaises(CrawlError):
                fetch(data)

    def test_http_error_keeps_status_and_timestamps(self):
        response = Mock(status_code=429)
        response.raise_for_status.side_effect = requests.HTTPError("rate limited")
        with self.assertRaises(CrawlError) as caught:
            fetch_ashby_jobs("openai", SOURCE, Mock(get=Mock(return_value=response)))
        telemetry = caught.exception.telemetry
        self.assertEqual(telemetry["http_status"], 429)
        self.assertEqual(telemetry["request_count"], 1)
        self.assertEqual(telemetry["status"], "failed")
        self.assertTrue(telemetry["started_at"] and telemetry["completed_at"])

    def test_timeout_and_invalid_json_are_observable(self):
        with self.assertRaises(CrawlError) as caught:
            fetch_ashby_jobs("openai", SOURCE, Mock(get=Mock(side_effect=requests.Timeout("timeout"))))
        self.assertIn("Timeout", caught.exception.telemetry["errors"][0])
        response = Mock(status_code=200)
        response.json.side_effect = ValueError("invalid JSON")
        with self.assertRaises(CrawlError) as caught:
            fetch_ashby_jobs("openai", SOURCE, Mock(get=Mock(return_value=response)))
        self.assertEqual(caught.exception.telemetry["http_status"], 200)

    def test_malformed_payload_and_duplicates_rejected(self):
        duplicate = payload()
        duplicate["jobs"].append(copy.deepcopy(duplicate["jobs"][0]))
        for data in [{}, {"jobs": {}}, duplicate]:
            with self.subTest(data=data), self.assertRaises(CrawlError):
                fetch(data)

    def test_partial_extraction_error_retains_counts(self):
        data = payload()
        data["jobs"][1]["title"] = ""
        with self.assertRaises(CrawlError) as caught:
            fetch(data)
        self.assertEqual(caught.exception.telemetry["jobs_seen"], 2)
        self.assertEqual(caught.exception.telemetry["jobs_extracted"], 1)

    def test_empty_board_is_valid(self):
        (jobs, telemetry), _ = fetch({"jobs": []})
        self.assertEqual(jobs, [])
        self.assertEqual(telemetry["status"], "success")

    def test_reference_keeps_official_urls_and_id_matching(self):
        rows = load_jsonl(ROOT / "data/evals/discovery_reference.jsonl")
        refs = [row for row in rows if row["company"] == "OpenAI"]
        self.assertEqual(len(refs), 10)
        self.assertEqual(len({row["external_job_id"] for row in refs}), 10)
        self.assertTrue(all(row["canonical_url"].startswith("https://openai.com/careers/") for row in refs))
        (jobs, _), _ = fetch()
        result = evaluate([refs[0]], jobs[:1])
        self.assertEqual(result["found_count"], 1)
        self.assertNotEqual(refs[0]["canonical_url"], jobs[0]["canonical_url"])

    def test_one_source_run_preserves_other_source_and_replaces_selected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config/job_sources.yaml").write_text(
                "sources:\n  anthropic:\n    company: Anthropic\n    adapter: greenhouse\n    board_token: anthropic\n"
                "  openai:\n    company: OpenAI\n    adapter: ashby\n    board_token: openai\n", encoding="utf-8")
            greenhouse = fetch_greenhouse_jobs("anthropic", {"company": "Anthropic", "board_token": "anthropic"}, FakeSession())
            ashby, _ = fetch()
            with patch("discover_jobs.fetch_greenhouse_jobs", return_value=greenhouse):
                run(["anthropic"], root)
            with patch("discover_jobs.fetch_ashby_jobs", return_value=ashby):
                self.assertFalse(run(["openai"], root)["failures"])
            output = root / "data/discovery"
            combined = load_jsonl(output / "raw_all_jobs.jsonl")
            self.assertEqual(len(combined), 4)
            self.assertEqual([row for row in combined if row["source_key"] == "anthropic"], greenhouse[0])
            self.assertEqual(len(load_jsonl(output / "raw_pm_candidates.jsonl")), 2)
            # A refreshed empty OpenAI board removes only OpenAI from latest;
            # the previous source run snapshot remains available for history.
            empty, _ = fetch({"jobs": []})
            with patch("discover_jobs.fetch_ashby_jobs", return_value=empty):
                run(["openai"], root)
            self.assertEqual(load_jsonl(output / "raw_all_jobs.jsonl"), greenhouse[0])
            self.assertEqual(len(list((output / "runs").glob("*/raw_all_jobs.jsonl"))), 3)
            before = (output / "raw_all_jobs.jsonl").read_bytes()
            error = dict(ashby[1], status="failed", errors=["timeout"])
            with patch("discover_jobs.fetch_ashby_jobs", side_effect=CrawlError(error)):
                self.assertTrue(run(["openai"], root)["failures"])
            self.assertEqual((output / "raw_all_jobs.jsonl").read_bytes(), before)

    def test_eval_checks_latest_status_per_source(self):
        runs = [dict(source_key="openai", status="failed", outputs_written=False),
                dict(source_key="anthropic", status="success", outputs_written=True)]
        with self.assertRaises(ValueError):
            validate_latest_crawls(runs)
        runs.append(dict(source_key="openai", status="success", outputs_written=True))
        validate_latest_crawls(runs)


if __name__ == "__main__":
    unittest.main()
