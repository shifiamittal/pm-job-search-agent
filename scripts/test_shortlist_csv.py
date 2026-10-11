"""Input-boundary tests only; no model calls or discovery changes."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from run_shortlist_job import load_csv_job, main


class CsvInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "jobs.csv"
        self.row = {
            "company": "Example", "job_id": "example:001", "title": "Principal Product Manager",
            "location": "Remote US", "canonical_url": "https://example.com/jobs/001",
            "source_key": "example_workday", "source_type": "workday", "posting_date": "2026-10-01",
            "description": "Short description must not replace the full JD",
            "full_job_description_raw": 'Full JD, with "quotes".\r\n<html>Unabridged text.</html>\nTail.',
        }

    def write_rows(self, rows):
        with self.path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_successful_exact_lookup_preserves_full_jd_and_provenance(self):
        self.write_rows([{**self.row, "job_id": "other"}, self.row])
        job = load_csv_job(self.path, "example:001")
        self.assertEqual(job["job_id"], "example:001")
        self.assertEqual(job["canonical_job_url"], self.row["canonical_url"])
        self.assertEqual(job["source"], self.row["source_key"])
        self.assertEqual(job["posted_date"], self.row["posting_date"])
        for key, value in self.row.items():
            self.assertEqual(job[key], value)

    def test_missing_job_id(self):
        self.write_rows([self.row])
        with self.assertRaisesRegex(ValueError, "not found"):
            load_csv_job(self.path, "001")

    def test_windows_1252_export_preserves_full_jd(self):
        self.row["full_job_description_raw"] = 'Microsoft’s platform — full JD\r\n“Quoted text” and £100.'
        self.write_rows([self.row])
        text = self.path.read_bytes().decode("utf-8-sig")
        self.path.write_bytes(text.encode("cp1252"))
        self.assertEqual(load_csv_job(self.path, self.row["job_id"])["full_job_description_raw"],
                         self.row["full_job_description_raw"])

    def test_utf8_stays_utf8_instead_of_windows_fallback(self):
        self.row["full_job_description_raw"] = 'Full JD: Bengaluru — भारत 🔍'
        self.write_rows([self.row])
        self.assertEqual(load_csv_job(self.path, self.row["job_id"])["full_job_description_raw"],
                         self.row["full_job_description_raw"])

    def test_duplicate_job_id(self):
        self.write_rows([self.row, self.row])
        with self.assertRaisesRegex(ValueError, "Multiple CSV rows"):
            load_csv_job(self.path, self.row["job_id"])

    def test_missing_or_blank_required_fields(self):
        for key in ("company", "job_id", "title", "full_job_description_raw"):
            row = dict(self.row)
            del row[key]
            self.write_rows([row])
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "(required field|requires nonempty)"):
                load_csv_job(self.path, self.row["job_id"])
        self.write_rows([{**self.row, "full_job_description_raw": "   "}])
        with self.assertRaisesRegex(ValueError, "full_job_description_raw"):
            load_csv_job(self.path, self.row["job_id"])

    def test_csv_without_url_or_source_is_valid(self):
        for remove_columns in (False, True):
            row = dict(self.row)
            for key in ("canonical_url", "source_key", "source_type"):
                if remove_columns:
                    row.pop(key)
                else:
                    row[key] = ""
            self.write_rows([row])
            job = load_csv_job(self.path, row["job_id"])
            self.assertIsNone(job["canonical_job_url"])
            self.assertEqual(job["source"], "User-supplied CSV: jobs.csv")
            self.assertEqual(job["full_job_description_raw"], row["full_job_description_raw"])

    def test_row_selection_without_any_optional_metadata(self):
        row = {key: self.row[key] for key in ("company", "title", "full_job_description_raw")}
        self.write_rows([row, row])
        first = load_csv_job(self.path, row_number=1)
        second = load_csv_job(self.path, row_number=2)
        self.assertIsNone(first["job_id"])
        self.assertIsNone(first["location"])
        self.assertIsNone(first["canonical_job_url"])
        self.assertNotEqual(first["internal_record_key"], second["internal_record_key"])
        self.assertEqual(first, load_csv_job(self.path, row_number=1))
        for number in (0, 3):
            with self.assertRaises(ValueError):
                load_csv_job(self.path, row_number=number)

    def test_csv_row_cli_needs_no_external_id(self):
        self.write_rows([{key: self.row[key] for key in ("company", "title", "full_job_description_raw")}])
        job = self.invoke_cli(["--csv", str(self.path), "--row", "1"])
        self.assertIsNone(job["job_id"])
        self.assertTrue(job["internal_record_key"].startswith("shortlist:"))

    def test_long_jd_and_optional_unknown_fields(self):
        self.row.update(full_job_description_raw="Large full JD " * 20000, location="", posting_date="")
        self.write_rows([self.row])
        limit = csv.field_size_limit()
        job = load_csv_job(self.path, self.row["job_id"])
        self.assertEqual(job["full_job_description_raw"], self.row["full_job_description_raw"])
        self.assertIsNone(job["location"])
        self.assertIsNone(job["posted_date"])
        self.assertEqual(csv.field_size_limit(), limit)

    def test_normalized_csv_columns_also_work(self):
        self.row.update(canonical_job_url="https://example.com/canonical", source="Explicit source", posted_date="2026-09-30")
        self.write_rows([self.row])
        job = load_csv_job(self.path, self.row["job_id"])
        for key in ("canonical_job_url", "source", "posted_date"):
            self.assertEqual(job[key], self.row[key])

    def invoke_cli(self, arguments):
        result = self.root / "result"
        result.mkdir(exist_ok=True)
        (result / "job_state.json").write_text('{"status": "accepted"}', encoding="utf-8")
        with patch("sys.argv", ["run_shortlist_job.py", *arguments, "--model", "test-model"]), \
             patch("run_shortlist_job.ResponsesModel") as model, \
             patch("run_shortlist_job.run_job", return_value=result) as runner, \
             patch("sys.stdout", new_callable=io.StringIO):
            main()
        model.assert_called_once()
        runner.assert_called_once()
        return runner.call_args.args[0]

    def test_csv_cli_passes_normalized_job_to_unchanged_runner(self):
        self.write_rows([self.row])
        job = self.invoke_cli(["--csv", str(self.path), "--job-id", self.row["job_id"]])
        self.assertEqual(job, load_csv_job(self.path, self.row["job_id"]))

    def test_existing_json_mode_preserves_exact_object(self):
        job = {**self.row, "canonical_job_url": self.row["canonical_url"], "source": "Original source",
               "extra_metadata": {"unchanged": True}}
        path = self.root / "job.json"
        path.write_text(json.dumps(job), encoding="utf-8-sig")
        self.assertEqual(self.invoke_cli(["--input", str(path)]), job)

    def test_invalid_cli_combinations_fail_before_model_creation(self):
        for args in (["--csv", str(self.path)], ["--input", "job.json", "--job-id", "one"],
                     ["--input", "job.json", "--csv", str(self.path), "--job-id", "one"]):
            with self.subTest(args=args), patch("sys.argv", ["run_shortlist_job.py", *args]), \
                 patch("sys.stderr", new_callable=io.StringIO), patch("run_shortlist_job.ResponsesModel") as model, \
                 self.assertRaises(SystemExit) as caught:
                main()
            self.assertEqual(caught.exception.code, 2)
            model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
