import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from discovery.geography import classify_geography, enrich_geography, geography_summary
from filter_discovery_geography import filter_file
from discover_jobs import retain_candidate


def job(location=None, **extra):
    row = {"company": "Example", "title": "Product Manager", "location": location or ""}
    row.update(extra)
    return row


class GeographyGateTests(unittest.TestCase):
    def test_required_single_locations(self):
        cases = {
            "Seattle, WA": (True, ["US"]),
            "Redmond, Washington": (True, ["US"]),
            "Remote - US": (True, ["US"]),
            "Bengaluru": (True, ["IN"]),
            "Bangalore, India": (True, ["IN"]),
            "Hyderabad": (True, ["IN"]),
            "London, UK": (False, ["GB"]),
            "Toronto, Canada": (False, ["CA"]),
            "Singapore": (False, ["SG"]),
        }
        for location, (kept, countries) in cases.items():
            with self.subTest(location=location):
                result = classify_geography(job(location))
                self.assertEqual(result["geography_in_scope"], kept)
                self.assertEqual(result["normalized_countries"], countries)

    def test_generic_remote_and_missing_are_unknown(self):
        for location in ("Remote", "Global", "Worldwide", "Anywhere", "Remote - Americas",
                         "Remote - EMEA", "Remote - APAC", None):
            with self.subTest(location=location):
                result = classify_geography(job(location))
                self.assertEqual(result["geography_status"], "geography_unknown")
                self.assertFalse(result["geography_in_scope"])
        self.assertTrue(classify_geography(job("Remote", country="United States"))["geography_in_scope"])
        self.assertTrue(classify_geography(job("Worldwide", country_code="IND"))["geography_in_scope"])

    def test_multi_location_keeps_any_target_country(self):
        result = classify_geography(job("Seattle, WA | London, UK"))
        self.assertTrue(result["geography_in_scope"])
        self.assertEqual(result["normalized_countries"], ["GB", "US"])
        excluded = classify_geography(job("London, UK; Dublin, Ireland"))
        self.assertEqual(excluded["geography_status"], "out_of_scope")
        self.assertEqual(excluded["normalized_countries"], ["GB", "IE"])

    def test_source_location_list_is_preserved_exactly(self):
        original = ["Seattle, WA", "London, UK"]
        row = job("primary ignored", all_locations=json.dumps(original))
        enriched = enrich_geography(row)
        self.assertEqual(enriched["all_locations"], json.dumps(original))
        self.assertEqual(enriched["all_locations_raw"], original)
        self.assertEqual(row["all_locations"], json.dumps(original))

    def test_country_metadata_is_preferred_and_conflicts_fail_closed(self):
        self.assertTrue(classify_geography(job("Unrecognized campus", country_code="IND"))["geography_in_scope"])
        conflict = classify_geography(job("Seattle, WA", country="Canada"))
        self.assertEqual(conflict["geography_status"], "geography_unknown")
        malformed = classify_geography(job("Seattle, WA", country="not-a-country"))
        self.assertEqual(malformed["geography_status"], "geography_unknown")
        self.assertFalse(malformed["geography_in_scope"])

    def test_summary_counts_country_and_gate_outcomes(self):
        rows = [job("Seattle, WA"), job("Bengaluru"), job("London"), job("Remote")]
        self.assertEqual(geography_summary(rows), {
            "total_jobs_before_geography_gate": 4,
            "jobs_kept": 2,
            "jobs_excluded": 1,
            "jobs_geography_unknown": 1,
            "counts_by_country": {"GB": 1, "IN": 1, "US": 1},
        })

    def test_geography_gate_runs_before_pm_family_filter(self):
        row = job("London, UK", source_type="ashby")
        with patch("discover_jobs.pm_candidate_decision") as pm_filter:
            self.assertFalse(retain_candidate(row))
        pm_filter.assert_not_called()

    def test_offline_csv_filter_writes_isolated_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "jobs.csv"
            rows = [job("Seattle, WA", job_id="1"), job("London", job_id="2"),
                    job("Remote", job_id="3")]
            with source.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            before = source.read_bytes()
            summary = filter_file(source, root / "filtered")
            self.assertEqual((summary["jobs_kept"], summary["jobs_excluded"],
                              summary["jobs_geography_unknown"]), (1, 1, 1))
            self.assertEqual(source.read_bytes(), before)
            kept = (root / "filtered/shortlist_input_us_india.jsonl").read_text(encoding="utf-8")
            self.assertIn('"job_id": "1"', kept)
            self.assertTrue((root / "filtered/geography_excluded.csv").exists())
            self.assertTrue((root / "filtered/geography_unknown.csv").exists())


if __name__ == "__main__":
    unittest.main()
