"""Offline regression tests for calibrated jobs and persistent dashboard sync."""

import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from finalize_discovery import merge_jobs
from job_framework import (LEGACY_SCORE_FIELDS, ROOT, load_canonical_jobs,
                           persist_discovery_run, review_queue, synthesize_skills,
                           taxonomy, validate_job, validate_jobs)
from reprocess_calibration_jobs import annotations, migrate_job
from sync_job_dashboard import (FEEDBACK_HEADERS, JOB_COLUMNS, TABS, DashboardError,
                                collect_live_feedback, normalize_legacy_review,
                                parse_feedback, serialize_feedback_rows,
                                serialize_job_rows, sync_dashboard, tab_rows)


class FakeResponse:
    status_code = 200
    content = b"{}"

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.creates = 0
        self.updates = []

    def request(self, method, url, **kwargs):
        if method == "POST" and url.endswith("/spreadsheets"):
            self.creates += 1
            return FakeResponse({"spreadsheetId": "persistent-test-id", "spreadsheetUrl":
                                 "https://docs.google.com/spreadsheets/d/persistent-test-id/edit"})
        if method == "GET" and url.endswith("/persistent-test-id"):
            return FakeResponse({"spreadsheetId": "persistent-test-id", "sheets": [
                {"properties": {"title": title, "sheetId": index + 1,
                                "gridProperties": {"rowCount": 100, "columnCount": 45}},
                 "conditionalFormats": [{"rule": "already exists"}] if title == "Jobs Master" and self.updates else []}
                for index, title in enumerate(TABS)]})
        if method == "GET" and "values:batchGet" in url:
            return FakeResponse({"valueRanges": [{"values": []} for _ in range(5)]})
        if method == "POST" and url.endswith(":batchUpdate"):
            self.updates.append(kwargs["json"])
            return FakeResponse({})
        raise AssertionError(f"Unexpected API request: {method} {url}")


class FrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_canonical_jobs()

    def test_taxonomy_and_no_old_scoring_schema(self):
        values = taxonomy()
        self.assertGreaterEqual(len(self.jobs), 30)
        self.assertEqual(values["application_lanes"], ["Apply Now", "Apply Now + Bridge", "Build Toward", "Skip"])
        self.assertNotIn("K", values["primary_gap"])
        self.assertNotIn("AI-heavy", values["technology_orientation"])
        self.assertTrue(all(not LEGACY_SCORE_FIELDS.intersection(job) for job in self.jobs))
        self.assertTrue(all("P/S" not in job["exact_level"] for job in self.jobs))
        validate_jobs(self.jobs)

    def test_enums_and_narrative_gating(self):
        job = copy.deepcopy(self.jobs[0])
        for field, invalid in [("domain_fit", "SOMEWHAT"), ("technology_orientation", "AI-heavy"),
                               ("application_lane", "APPLY NOW"), ("skill_build_priority", "Soon")]:
            broken = dict(job, **{field: invalid})
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_job(broken)
        with self.assertRaises(ValueError):
            validate_job(dict(job, priority_score=90))
        with self.assertRaises(ValueError):
            validate_job(dict(job, application_lane="Build Toward", skill_build_priority="Do Not Build"))

    def test_unknown_date_pay_and_closed_history(self):
        unknown = next(job for job in self.jobs if job["posting_date"] == "Not exposed")
        self.assertEqual(unknown["posting_date_confidence"], "Unavailable")
        unpaid = next(job for job in self.jobs if job["compensation"] == "Not published")
        self.assertFalse(unpaid["currency"])
        closed = migrate_job(dict(self.jobs[0], status="Closed"), annotations()[self.jobs[0]["job_id"]], "2026-09-20T00:00:00+00:00")
        self.assertEqual((closed["status"], closed["application_lane"]), ("Closed", "Skip"))
        self.assertEqual(closed["job_id"], self.jobs[0]["job_id"])
        validate_job(closed)

    def test_skill_synthesis_normalizes_and_excludes_skip(self):
        rows = synthesize_skills(self.jobs)
        by_name = {row["skill"]: row for row in rows}
        self.assertGreaterEqual(by_name["AI Evaluation Systems"]["role_count"], 2)
        self.assertEqual(by_name["AI Evaluation Systems"]["recommended_action"], "Build Now")
        self.assertNotIn("PM People Management", by_name)
        self.assertTrue(any("PM People Management" in job.get("skill_tags", [])
                            for job in self.jobs if job["application_lane"] == "Skip"))
        self.assertTrue(all(row["role_count"] >= 1 for row in rows))

    def test_row_serialization_and_feedback_preservation(self):
        feedback = {self.jobs[0]["job_id"]: {"my_decision": "Apply", "my_notes": "Keep this note",
                                                "stage": "Discovered", "user_override": "Apply Now"}}
        rows = serialize_job_rows(self.jobs, feedback)
        self.assertEqual(len(rows[0]), 16)
        self.assertEqual([name for name, _ in JOB_COLUMNS], rows[0])
        self.assertEqual(rows[0][0], "Company")
        self.assertNotIn("Priority Score", rows[0])
        self.assertNotIn("Level", rows[0])
        self.assertNotIn("Application Posture", rows[0])
        self.assertEqual(rows[1][rows[0].index("Role Title")], self.jobs[0]["role_title"])
        self.assertEqual(rows[1][rows[0].index("My Notes")], "Keep this note")
        self.assertEqual(rows[1][rows[0].index("My Decision")], "Apply")
        self.assertEqual(rows[1][rows[0].index("Job URL")], self.jobs[0]["canonical_url"])
        feedback_rows = serialize_feedback_rows(self.jobs, feedback)
        self.assertEqual(parse_feedback(feedback_rows)[self.jobs[0]["job_id"]]["User Override"], "Apply Now")
        tabs = tab_rows(self.jobs, synthesize_skills(self.jobs), feedback, 0)
        self.assertEqual(len(tabs), 7)
        self.assertEqual(len(tabs["Dashboard"]), 11)
        for title in ("Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward"):
            self.assertEqual(tabs[title][0], rows[0])

    def test_legacy_feedback_from_lane_tab_survives(self):
        job = self.jobs[0]
        legacy = "Do not apply. The direct requirement is too niche."
        self.assertEqual(normalize_legacy_review(legacy),
                         ("Do Not Apply", "The direct requirement is too niche."))
        values = {"Jobs Master": [["Job ID", "User Review"], [job["job_id"], ""]],
                  "Apply Now": [["Job ID", "User Review"], [job["job_id"], legacy]]}
        feedback = collect_live_feedback(values, [job])
        self.assertEqual(feedback[job["job_id"]]["my_decision"], "Do Not Apply")
        self.assertEqual(feedback[job["job_id"]]["my_notes"], "The direct requirement is too niche.")
        self.assertEqual(feedback[job["job_id"]]["legacy_review"], legacy)

    def test_merge_preserves_job_id_and_discovery_state(self):
        existing = [copy.deepcopy(self.jobs[0])]
        update = dict(existing[0], role_mandate="Updated mandate", discovered_at="", user_notes="")
        merged, count = merge_jobs(existing, [update])
        self.assertEqual(count, 0)
        self.assertEqual(merged[0]["job_id"], existing[0]["job_id"])
        self.assertEqual(merged[0]["discovered_at"], existing[0]["discovered_at"])

    def test_local_data_survives_dashboard_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config/role_taxonomy.yaml").write_text((ROOT / "config/role_taxonomy.yaml").read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch("sync_job_dashboard.sync_dashboard", side_effect=DashboardError("simulated failure")):
                result = persist_discovery_run(self.jobs, root=root, sync=True)
            self.assertTrue(result["local_saved"])
            self.assertFalse(result["dashboard_synced"])
            self.assertIn("simulated failure", result["dashboard_error"])
            with (root / "data/jobs_master.csv").open(encoding="utf-8") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), len(self.jobs))

    def test_create_once_and_update_same_spreadsheet(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "data").mkdir()
            (root / "config/role_taxonomy.yaml").write_text((ROOT / "config/role_taxonomy.yaml").read_text(encoding="utf-8"), encoding="utf-8")
            (root / "config/google_sheets.yaml").write_text("spreadsheet_id: ''\nspreadsheet_url: ''\nspreadsheet_title: Shifia PM Job Search Dashboard\nsync_enabled: true\n", encoding="utf-8")
            (root / "data/jobs_raw.jsonl").write_text("".join(json.dumps(job) + "\n" for job in self.jobs), encoding="utf-8")
            api = FakeSession()
            first = sync_dashboard(root=root, session=api)
            second = sync_dashboard(root=root, session=api)
            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            self.assertEqual(first["spreadsheet_id"], second["spreadsheet_id"])
            self.assertEqual(api.creates, 1)
            self.assertEqual(len(api.updates), 2)
            self.assertEqual(yaml.safe_load((root / "config/google_sheets.yaml").read_text(encoding="utf-8"))["spreadsheet_id"], "persistent-test-id")
            second_jobs = next(request["updateCells"] for request in api.updates[1]["requests"]
                               if "updateCells" in request and request["updateCells"]["range"]["sheetId"] == 2)
            header = [cell["userEnteredValue"]["stringValue"] for cell in second_jobs["rows"][0]["values"]]
            note = second_jobs["rows"][1]["values"][header.index("My Notes")]["userEnteredValue"]["stringValue"]
            self.assertEqual(note, self.jobs[0]["my_notes"])
            self.assertEqual(len(header), 16)
            dropdowns = [item["setDataValidation"] for item in api.updates[1]["requests"]
                         if "setDataValidation" in item and item["setDataValidation"].get("rule")]
            self.assertTrue(any([v["userEnteredValue"] for v in item["rule"]["condition"]["values"]] ==
                                ["Apply", "Maybe", "Do Not Apply", "Needs Review"] for item in dropdowns))
            self.assertTrue(all("updateCells" not in item or item["updateCells"]["range"]["sheetId"] <= 7
                                for item in api.updates[1]["requests"]))


if __name__ == "__main__":
    unittest.main()
