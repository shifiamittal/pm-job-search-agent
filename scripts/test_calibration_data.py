"""Integrity checks for the first curated job-classification calibration."""

import csv
import json
import unittest
from collections import Counter
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"


def csv_rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class CalibrationDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = csv_rows("jobs_master.csv")
        cls.queue = csv_rows("review_queue.csv")
        cls.raw = [json.loads(line) for line in (DATA / "jobs_raw.jsonl").read_text(encoding="utf-8").splitlines()]

    def test_sample_is_diverse_and_deduplicated(self):
        self.assertGreaterEqual(len(self.jobs), 25)
        self.assertLessEqual(len(self.jobs), 40)
        self.assertEqual(len(self.jobs), len(self.raw))
        self.assertEqual(len({j["job_id"] for j in self.jobs}), len(self.jobs))
        self.assertEqual([j["canonical_url"] for j in self.jobs],
                         [j["canonical_url"] for j in self.raw])
        sectors = Counter(j["sector"] for j in self.jobs)
        self.assertGreaterEqual(len(sectors), 8)
        self.assertIn("AI-heavy", {j["ai_classification"] for j in self.jobs})
        self.assertIn("Non-AI", {j["ai_classification"] for j in self.jobs})

    def test_scores_and_unknown_pay(self):
        weights = [(.25, "experience_fit_score"), (.20, "interview_probability_score"),
                   (.15, "level_fit_score"), (.15, "compensation_fit_score"),
                   (.15, "career_capital_score"), (.10, "location_fit_score")]
        for job in self.jobs:
            with self.subTest(job=job["job_id"]):
                scores = [int(job[name]) for _, name in weights]
                self.assertTrue(all(1 <= score <= 5 for score in scores))
                expected = round(20 * sum(weight * int(job[name]) for weight, name in weights), 1)
                self.assertAlmostEqual(float(job["priority_score"]), expected)
                if not job["comp_min"]:
                    self.assertEqual((job["comp_max"], job["currency"], job["compensation_confidence"]), ("", "", "LOW"))
                    self.assertEqual(job["compensation_fit_score"], "3")
                self.assertEqual(job["hard_experience_gap"], str(job["primary_gap"] == "X"))
                self.assertEqual(job["status"], "live_verified")
                self.assertTrue(job["canonical_url"].startswith("https://"))

    def test_review_queue_membership_and_order(self):
        ids = {job["Canonical URL"] for job in self.queue}
        expected = {job["canonical_url"] for job in self.jobs if job["application_lane"] != "SKIP"}
        self.assertEqual(ids, expected)
        self.assertEqual(sum(job["Lane"] == "BUILD TOWARD" for job in self.queue), 5)
        order = {"APPLY NOW": 0, "APPLY + BRIDGE": 1, "BUILD TOWARD": 2}
        self.assertEqual([order[job["Lane"]] for job in self.queue],
                         sorted(order[job["Lane"]] for job in self.queue))
        keys = [(order[job["Lane"]], -int(job["Posted date"].replace("-", "") or 0),
                 -float(job["Priority score"]), job["Company"]) for job in self.queue]
        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()
