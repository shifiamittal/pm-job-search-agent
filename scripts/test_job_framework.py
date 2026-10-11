"""Offline migration tests: history preservation and retired consumer barriers."""
import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

import finalize_discovery
import job_framework
import reprocess_calibration_jobs
import sync_job_dashboard
from shortlist_contract import ROOT, ShortlistIntegrationPending, shortlist_outcomes


class MigrationTests(unittest.TestCase):
    def test_instructions_defer_to_one_contract(self):
        for name in ("AGENTS.md", "prompts/classification.md", "config/classification_rubric.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                for stage in ("role_understanding.md", "career_requirements_mapping.md",
                              "shortlist_decision.md", "controller_validation.md", "schema.yaml"):
                    self.assertIn("shortlist/" + stage, text)
                self.assertIn("1.2.0", text)
                for old in ("Apply Now", "Build Toward", "Non-gating", "1–5", "four to seven", "$500K"):
                    self.assertNotIn(old, text)
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for outcome in shortlist_outcomes():
            self.assertIn(f"`{outcome}`", agents)
        self.assertIn("superseded", agents)

    def test_live_configs_do_not_supply_legacy_decisions(self):
        taxonomy = yaml.safe_load((ROOT / "config/role_taxonomy.yaml").read_text(encoding="utf-8"))
        self.assertEqual(set(taxonomy), {"sectors", "role_clusters", "technology_orientation", "resume_variants", "portfolio_artifacts"})
        config = yaml.safe_load((ROOT / "config/search_config.yaml").read_text(encoding="utf-8"))
        self.assertEqual(config["shortlist_contract"], "shortlist/schema.yaml")
        self.assertEqual(config["shortlist_version"], "1.2.0")
        self.assertEqual(config["geography"]["scope"], ["United States", "India"])
        self.assertIn("shortlist_integration_pending", config["post_success_workflow"])

    def test_historical_jsonl_and_deprecated_read_alias(self):
        path = ROOT / "data/jobs_raw.jsonl"
        before = path.read_bytes()
        expected = [json.loads(line) for line in before.decode("utf-8-sig").splitlines() if line.strip()]
        actual = job_framework.load_legacy_jobs()
        self.assertEqual(actual, expected)
        self.assertGreaterEqual(len(actual), 30)
        self.assertTrue(all("application_lane" in job for job in actual))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(job_framework.load_canonical_jobs(), expected)
        self.assertEqual(path.read_bytes(), before)

    def test_reader_preserves_every_legacy_lane_without_translation(self):
        rows = [{"job_id": str(i), "application_lane": lane, "my_notes": "Keep me"}
                for i, lane in enumerate(("Apply Now", "Apply Now + Bridge", "Build Toward", "Skip"))]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "data").mkdir()
            path = root / "data/jobs_raw.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            self.assertEqual(job_framework.load_legacy_jobs(root), rows)

    def test_historical_csv_and_annotations_are_readable_unchanged(self):
        for name in ("jobs_master.csv", "review_queue.csv", "skills_synthesis.csv", "calibration_lane_changes.csv"):
            path = ROOT / "data" / name
            before = path.read_bytes()
            with path.open(encoding="utf-8-sig", newline="") as stream:
                expected = list(csv.DictReader(stream))
            self.assertEqual(job_framework.load_legacy_csv(path), expected)
            self.assertEqual(path.read_bytes(), before)
        path = ROOT / "data/calibration_annotations.yaml"
        self.assertEqual(reprocess_calibration_jobs.annotations(), yaml.safe_load(path.read_text(encoding="utf-8")))

    def test_legacy_feedback_preserves_labels_unknown_ids_and_conflicts(self):
        original = {"Build Toward": [["Job ID", "System Recommendation", "My Notes"],
                    ["unknown-id", "Build Toward", "Exact user words"], ["unknown-id", "Skip", "Conflicting row"]]}
        saved = copy.deepcopy(original)
        result = sync_job_dashboard.read_legacy_feedback(original)
        self.assertEqual(result, saved)
        result["Build Toward"][1][2] = "Changed copy"
        self.assertEqual(original, saved)

    def test_retired_apis_fail_before_io(self):
        calls = [(job_framework.taxonomy, ()), (job_framework.validate_job, ({},)),
                 (job_framework.validate_jobs, ([],)), (job_framework.review_queue, ([],)),
                 (job_framework.synthesize_skills, ([],)), (job_framework.persist_discovery_run, ([],)),
                 (reprocess_calibration_jobs.migrate_job, ({}, {}, "now")),
                 (reprocess_calibration_jobs.reprocess, ()), (finalize_discovery.merge_jobs, ([], [])),
                 (finalize_discovery.finalize, ([],))]
        with mock.patch("pathlib.Path.open", side_effect=AssertionError("Unexpected file IO")):
            for call, args in calls:
                with self.subTest(call=call.__name__), self.assertRaisesRegex(ShortlistIntegrationPending, "blocked pending shortlist-runner integration"):
                    call(*args)

    def test_dashboard_blocked_even_with_enabled_config(self):
        session = mock.Mock()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            path = root / "config/google_sheets.yaml"
            path.write_text("sync_enabled: true\nspreadsheet_id: retain-me\n", encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaisesRegex(sync_job_dashboard.DashboardError, "blocked pending"):
                sync_job_dashboard.sync_dashboard(root=root, session=session)
            session.request.assert_not_called()
            self.assertEqual(before, path.read_bytes())
            self.assertFalse((root / "data").exists())
        real = yaml.safe_load((ROOT / "config/google_sheets.yaml").read_text(encoding="utf-8"))
        self.assertFalse(real["sync_enabled"])
        self.assertTrue(real["spreadsheet_id"])
        self.assertTrue(real["spreadsheet_url"])

    def test_retired_clis_fail_before_reading_inputs(self):
        for script, args in [("finalize_discovery.py", ["--input", "does-not-exist.jsonl"]),
                             ("reprocess_calibration_jobs.py", ["--no-sheet"]),
                             ("sync_job_dashboard.py", ["--token", "does-not-exist.json"])]:
            with self.subTest(script=script):
                result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 2)
                self.assertIn("blocked pending shortlist-runner integration", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
