"""Offline tests for the sequential shortlist batch orchestrator."""
from contextlib import redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from uuid import uuid4

import run_shortlist_batch as batch
import run_shortlist_job as single


class Model:
    model = "offline"
    timeout = 180
    max_output_tokens = 12000


def job(company, index):
    return single.normalize_input({
        "company": company, "title": "Principal Product Manager",
        "job_id": f"job-{index}", "location": "Seattle, WA",
        "canonical_job_url": None, "source": "offline test",
        "full_job_description_raw": f"Full JD {company} {index}",
    }, row_identity=f"offline#row={index}")


def records(names):
    return [{"input_index": index, "job": job(name, index),
             "input_sha256": batch._sha_json(job(name, index)), "raw_sha256": str(index)}
            for index, name in enumerate(names, 1)]


def state(company, decision="APPLY", accepted=True):
    return {
        "shortlist_decision": {
            "decision": decision,
            "actual_work_alignment": {"classification": "Directly aligned"},
            "scope_assessment": {"classification": "Principal / Staff equivalent"},
            "evidence_strength": {"classification": "Strong direct evidence"},
            "career_value": {"classification": "High"},
            "key_gap_or_risk": {"description": None, "severity": None},
            "decision_rationale": f"Decision for {company}",
        },
        "validation": {"shortlist_decision_accepted": accepted},
    }


def write_artifact(run_dir, company, *, status="accepted", failed_stage=None,
                   cached=40, run_id=None):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "run_id": run_id or run_dir.name, "status": status,
        "shortlist_state": state(company, accepted=status == "accepted") if status != "failed" else None,
        "model_calls": [{"stage": "career_requirements_mapping", "telemetry": {
            "input_tokens": 100, "cached_input_tokens": cached,
            "cache_write_input_tokens": 60, "output_tokens": 20,
            "reasoning_tokens": 5, "elapsed_seconds": 1.5,
        }}],
        "error": ({"stage": failed_stage or "career_requirements_mapping",
                   "type": "SyntheticError", "message": f"failure for {company}"}
                  if status == "failed" else None),
    }
    (run_dir / "job_state.json").write_text(json.dumps(artifact), encoding="utf-8")
    return artifact


class FakeExecution:
    def __init__(self, fail=(), reject=()):
        self.fail = set(fail)
        self.reject = set(reject)
        self.calls = []
        self.resumes = []

    def run(self, value, model, *, output_root, run_id=None, **kwargs):
        company = value["company"]
        self.calls.append(company)
        run_dir = Path(output_root) / (run_id or uuid4().hex)
        if company in self.fail:
            write_artifact(run_dir, company, status="failed")
            raise single.RunError(run_dir)
        status = "rejected" if company in self.reject else "accepted"
        write_artifact(run_dir, company, status=status)
        return run_dir

    def resume(self, run_dir, model, **kwargs):
        self.resumes.append(Path(run_dir).name)
        old = json.loads((Path(run_dir) / "job_state.json").read_text(encoding="utf-8"))
        company = old["error"]["message"].removeprefix("failure for ")
        write_artifact(run_dir, company, status="accepted", run_id=old["run_id"])
        return Path(run_dir)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.batch_dir = self.root / "batch"
        self.batch_dir.mkdir()
        self.models = dict(batch.DEFAULT_STAGE_MODELS)
        self.settings = {"timeout": 180, "max_output_tokens": 12000}
        self.fingerprints = {"contract_hashes": {"contract": "hash"},
                             "candidate_context_hashes": {"candidate": "hash"},
                             "schema_sha256": "schema"}

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self, names, max_jobs=None):
        return batch.create_manifest(records(names), self.root / "input.csv", "input-hash",
                                     self.models, self.settings, self.fingerprints,
                                     max_jobs=max_jobs, batch_id="a" * 32)

    def execute(self, manifest, fake):
        with mock.patch.object(batch.single, "run_job", side_effect=fake.run), \
             mock.patch.object(batch.single, "resume_job", side_effect=fake.resume):
            return batch.execute_batch(manifest, self.batch_dir, Model())

    def test_multiple_jobs_run_sequentially_and_models_persist(self):
        manifest = self.manifest(["One", "Two", "Three"])
        fake = FakeExecution()
        self.execute(manifest, fake)
        self.assertEqual(fake.calls, ["One", "Two", "Three"])
        self.assertEqual(manifest["stage_models"], self.models)
        self.assertEqual(manifest["accepted_jobs"], 3)

    def test_one_failure_does_not_stop_batch_and_failure_csv_is_separate(self):
        manifest = self.manifest(["One", "Fails", "Three"])
        fake = FakeExecution(fail={"Fails"})
        self.execute(manifest, fake)
        self.assertEqual(fake.calls, ["One", "Fails", "Three"])
        self.assertEqual([entry["status"] for entry in manifest["jobs"]],
                         ["accepted", "failed", "accepted"])
        with (self.batch_dir / "failures.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["company"], "Fails")
        self.assertEqual(rows[0]["failed_stage"], "career_requirements_mapping")

    def test_completed_jobs_skip_and_incomplete_job_resumes(self):
        manifest = self.manifest(["Done", "Incomplete"])
        done_dir = self.batch_dir / "runs" / ("1" * 32)
        failed_dir = self.batch_dir / "runs" / ("2" * 32)
        write_artifact(done_dir, "Done", status="accepted")
        write_artifact(failed_dir, "Incomplete", status="failed")
        batch._apply_artifact(manifest["jobs"][0], batch._read_artifact(done_dir),
                              self.batch_dir, done_dir, action="completed")
        batch._apply_artifact(manifest["jobs"][1], batch._read_artifact(failed_dir),
                              self.batch_dir, failed_dir, action="failed")
        fake = FakeExecution()
        self.execute(manifest, fake)
        self.assertEqual(fake.calls, [])
        self.assertEqual(fake.resumes, ["2" * 32])
        self.assertTrue(manifest["jobs"][0]["reused"])
        self.assertEqual(manifest["jobs"][1]["status"], "accepted")

    def test_changed_input_hash_or_row_blocks_reuse(self):
        manifest = self.manifest(["One"])
        with self.assertRaisesRegex(ValueError, "input file hash"):
            batch._validate_resume(manifest, self.root / "input.csv", "changed",
                                   self.fingerprints, self.models, self.settings)
        changed = records(["One"])[0]
        changed["job"]["title"] = "Changed title"
        self.assertNotEqual(changed["input_sha256"], batch._sha_json(changed["job"]))

    def test_summary_has_required_columns_and_rejection_is_not_failure(self):
        manifest = self.manifest(["Rejected"])
        self.execute(manifest, FakeExecution(reject={"Rejected"}))
        with (self.batch_dir / "shortlist_summary.csv").open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(tuple(reader.fieldnames), batch.SUMMARY_FIELDS)
            row = next(reader)
        self.assertEqual(row["run_status"], "rejected")
        self.assertEqual(row["controller_accepted"], "False")
        with (self.batch_dir / "failures.csv").open(encoding="utf-8", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [])

    def test_manifest_is_written_incrementally(self):
        manifest = self.manifest(["One", "Two"])
        real = batch.persist_batch
        with mock.patch.object(batch, "persist_batch", wraps=real) as persist:
            self.execute(manifest, FakeExecution())
        self.assertGreaterEqual(persist.call_count, 5)  # initial, running/result per job, final
        saved = json.loads((self.batch_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["completed_jobs"], 2)

    def test_cached_token_telemetry_aggregates_actual_unique_calls(self):
        manifest = self.manifest(["One", "Two"])
        self.execute(manifest, FakeExecution())
        mapping = manifest["usage"]["mapping"]
        self.assertEqual(mapping["input_tokens"], 200)
        self.assertEqual(mapping["cached_input_tokens"], 80)
        self.assertEqual(mapping["cache_write_input_tokens"], 120)
        self.assertEqual(mapping["calls_with_cache_hits"], 2)
        self.assertEqual(mapping["cache_hit_rate_by_tokens"], 0.4)

    def test_max_jobs_limits_selected_records(self):
        manifest = self.manifest(["One", "Two", "Three"], max_jobs=2)
        self.assertEqual(manifest["total_input_jobs"], 3)
        self.assertEqual(manifest["selected_jobs"], 2)
        self.execute(manifest, FakeExecution())
        self.assertEqual(manifest["accepted_jobs"], 2)

    def test_exact_duplicate_is_processed_once_and_reused_deterministically(self):
        source = records(["One", "Other"])
        duplicate = dict(source[0])
        duplicate["input_index"] = 2
        duplicate["job"] = dict(source[0]["job"], row_identity="offline#row=2",
                                internal_record_key="different-row-key")
        manifest = batch.create_manifest([source[0], duplicate], self.root / "input.csv",
                                         "hash", self.models, self.settings,
                                         self.fingerprints, batch_id="b" * 32)
        fake = FakeExecution()
        self.execute(manifest, fake)
        self.assertEqual(fake.calls, ["One"])
        self.assertEqual(manifest["jobs"][1]["duplicate_of"], 1)
        self.assertEqual(manifest["jobs"][1]["run_id"], manifest["jobs"][0]["run_id"])
        self.assertTrue(manifest["jobs"][1]["reused"])
        self.assertEqual(manifest["usage"]["mapping"]["calls"], 1)

    def test_dry_run_creates_no_model_and_makes_no_batch_directory(self):
        path = self.root / "jobs.jsonl"
        path.write_text(json.dumps({"company": "One", "title": "PM",
                                    "full_job_description_raw": "Full JD"}) + "\n",
                        encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(batch, "ResponsesModel") as transport, redirect_stdout(output):
            result = batch.main(["--input", str(path), "--dry-run",
                                 "--batch-root", str(self.root / "batches")])
        self.assertEqual(result, 0)
        transport.assert_not_called()
        self.assertFalse((self.root / "batches").exists())
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["model_calls"], 0)
        self.assertEqual(plan["stage_models"], batch.DEFAULT_STAGE_MODELS)

    def test_csv_uses_shared_normalization_and_keeps_optional_fields_optional(self):
        path = self.root / "jobs.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=(
                "company", "title", "full_job_description_raw", "location", "canonical_url"))
            writer.writeheader()
            writer.writerow({"company": "One", "title": "PM", "full_job_description_raw": "Full JD",
                             "location": "", "canonical_url": ""})
        loaded = batch.load_batch_records(path)
        self.assertEqual(len(loaded), 1)
        self.assertIsNone(loaded[0]["job"]["location"])
        self.assertIsNone(loaded[0]["job"]["canonical_job_url"])
        self.assertTrue(loaded[0]["job"]["source"].startswith("User-supplied CSV:"))

    def test_planned_run_id_is_durable_before_single_job_call(self):
        manifest = self.manifest(["One"])
        observed = {}

        def inspect(value, model, *, output_root, run_id, **kwargs):
            saved = json.loads((self.batch_dir / "manifest.json").read_text(encoding="utf-8"))
            observed.update(saved["jobs"][0])
            run_dir = Path(output_root) / run_id
            write_artifact(run_dir, value["company"], status="accepted", run_id=run_id)
            return run_dir

        with mock.patch.object(batch.single, "run_job", side_effect=inspect):
            batch.execute_batch(manifest, self.batch_dir, Model())
        self.assertEqual(observed["status"], "running")
        self.assertRegex(observed["run_id"], r"^[0-9a-f]{32}$")
        self.assertEqual(observed["run_path"], "runs/" + observed["run_id"])

    def test_row_level_input_failure_isolated(self):
        path = self.root / "jobs.jsonl"
        path.write_text("{bad json}\n" + json.dumps({"company": "Good", "title": "PM",
                            "full_job_description_raw": "Full JD"}) + "\n", encoding="utf-8")
        loaded = batch.load_batch_records(path)
        self.assertIsNone(loaded[0]["job"])
        self.assertIsNotNone(loaded[1]["job"])
        manifest = batch.create_manifest(loaded, path, "hash", self.models, self.settings,
                                         self.fingerprints, batch_id="c" * 32)
        fake = FakeExecution()
        self.execute(manifest, fake)
        self.assertEqual(fake.calls, ["Good"])
        self.assertEqual(manifest["failed_jobs"], 1)


if __name__ == "__main__":
    unittest.main()
