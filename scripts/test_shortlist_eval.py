"""Offline evaluation contract tests; model transport is prohibited in this suite."""
import csv
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import eval_shortlist as ev
import shortlist_golden as golden
from run_shortlist_job import CANDIDATE_FILES
from shortlist_model import ModelError
from test_shortlist_runner import FakeModel, CAPABILITY, DEGREE_EVIDENCE, CONFIRMED_CAPABILITY
from test_shortlist_contract import example_record


def response():
    return {d: {"status": "PASS", "reason": "Same substantive judgment", "material_discrepancy": None,
        "could_change_decision": False, "failure_kind": None} for d in golden.DIMENSIONS}


class Judge:
    model = "offline-judge"
    def __init__(self):
        self.calls = []
    def complete(self, **request):
        self.calls.append(deepcopy(request))
        return response(), {"model": self.model, "usage": {"input_tokens": 40, "output_tokens": 20}}


class EvalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.data = self.root / "golden"; self.data.mkdir()
        self.net = patch("requests.post", side_effect=AssertionError("Network prohibited"))
        self.net.start(); self.addCleanup(self.net.stop)
        self.case = {"case_id": "synthetic_one", "company": "One Company", "job_id": "one",
            "title": "Principal Product Manager", "golden_status": "frozen",
            "full_job_description_raw": "Synthetic full JD: own developer deployment APIs, rollout safeguards and scientist adoption. Required: platform PM ownership. Preferred: orchestration. One Company",
            "job": {"location": "Remote US"},
            "reference": {"actual_job_to_be_done": "Own deployment capability", "material_requirements": ["Deployment APIs"],
                "capability_domain_expectations": [{"capability": "Platform", "capability_fit": "direct", "domain_context_fit": "transferable"}],
                "meaningful_gaps": ["Fleet scale"], "scope_assessment": "Principal",
                "shortlist_decision": example_record()["shortlist_decision"]["decision"]}}
        self.write([self.case])
        texts = [DEGREE_EVIDENCE, "# Platform evidence\n" + CAPABILITY,
                 "Ownership boundary unresolved: deployment APIs do not establish fleet-scale ownership.",
                 "Historic location scores are superseded; relocation willingness unknown.",
                 "Candidate-confirmed evidence, not documentary validation.\n" + CONFIRMED_CAPABILITY]
        for name, text in zip(CANDIDATE_FILES, texts):
            p = self.root / name; p.parent.mkdir(exist_ok=True); p.write_text(text, encoding="utf-8")

    def write(self, cases):
        dataset = {"version": "1.1.0", "judge_dimensions": list(golden.DIMENSIONS), "cases": cases,
            "evaluation_policy": {"strict_jd_fidelity_exception": {"case_id": golden.EXCEPTION, "provisional": [golden.DIMENSIONS[0]]}}}
        (self.data / "shortlist_golden_v1_1.json").write_text(json.dumps(dataset), encoding="utf-8")
        with (self.data / "index.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["case_id", "company", "job_id", "title", "decision", "golden_status", "strict_jd_fidelity"]); w.writeheader()
            for c in cases:
                w.writerow({**{k: c.get(k) or "" for k in ["case_id", "company", "job_id", "title", "golden_status"]},
                    "decision": c["reference"]["shortlist_decision"], "strict_jd_fidelity": c.get("strict_jd_fidelity", True)})
        (self.data / "README.md").write_text("Synthetic fixture", encoding="utf-8")
        self.freeze()

    def freeze(self):
        hashes = golden.fingerprint(self.data); hashes.pop("integrity.json", None)
        (self.data / "integrity.json").write_text(json.dumps({"files": hashes}), encoding="utf-8")

    def run_eval(self, **kwargs):
        with redirect_stdout(io.StringIO()):
            return ev.evaluate(self.data, model=kwargs.pop("model", FakeModel()), judge=kwargs.pop("judge", Judge()),
                candidate_root=self.root, output_root=self.root / "runs", allow_model_calls=True, expected_count=1, **kwargs)

    def test_loader_and_complete_inputs(self):
        _, report = golden.validate_dataset(self.data, expected_count=1)
        self.assertTrue(report["all_runnable"])
        self.assertEqual(golden.input_job(self.data, self.case)["full_job_description_raw"], self.case["full_job_description_raw"])

    def test_duplicates(self):
        self.write([self.case, self.case]); _, r = golden.validate_dataset(self.data, expected_count=2)
        self.assertTrue(any("duplicate case_id" in s for s in r["errors"]))
        second = deepcopy(self.case); second["case_id"] = "another"
        self.write([self.case, second]); _, r = golden.validate_dataset(self.data, expected_count=2)
        self.assertTrue(any("duplicate company/job" in s for s in r["errors"]))

    def test_invalid_reference_and_enums(self):
        for key in ("capability_fit", "domain_context_fit"):
            c = deepcopy(self.case); c["reference"]["capability_domain_expectations"][0][key] = "old_evidence_type"
            self.write([c]); self.assertFalse(golden.validate_dataset(self.data, expected_count=1)[1]["references_valid"])
        c = deepcopy(self.case); c["golden_status"] = "draft"; c["reference"].pop("meaningful_gaps")
        self.write([c]); self.assertFalse(golden.validate_dataset(self.data, expected_count=1)[1]["references_valid"])

    def test_missing_jd_and_frozen_mutation(self):
        c = deepcopy(self.case); c.pop("full_job_description_raw"); self.write([c])
        _, r = golden.validate_dataset(self.data, expected_count=1)
        self.assertTrue(r["references_valid"]); self.assertFalse(r["all_runnable"])
        (self.data / "README.md").write_text("Changed", encoding="utf-8")
        self.assertIn("Frozen package changed from integrity manifest", golden.validate_dataset(self.data, expected_count=1)[1]["errors"])

    def test_external_source_hash_and_traversal(self):
        c = deepcopy(self.case); text = c.pop("full_job_description_raw"); (self.data / "sources").mkdir()
        raw = text.encode(); (self.data / "sources/source.txt").write_bytes(raw)
        c["source_job"] = {"exact_jd_file": "source.txt", "sha256": golden.digest(raw)}; self.write([c])
        self.assertTrue(golden.validate_dataset(self.data, expected_count=1)[1]["all_runnable"])
        (self.data / "sources/source.txt").write_text("Different JD"); self.freeze()
        self.assertFalse(golden.validate_dataset(self.data, expected_count=1)[1]["all_runnable"])
        c["source_job"]["exact_jd_file"] = "../source.txt"
        with self.assertRaisesRegex(ValueError, "basename"): golden.source_text(self.data, c)

    def test_judge_schema_and_aggregation(self):
        check = {"passed": True, "exact_decision_alignment": True}
        self.assertEqual(ev.aggregate(check, ev.validate_judge(response(), self.case)), "PASS")
        r = response(); r[golden.DIMENSIONS[1]]["status"] = "WARN"
        self.assertEqual(ev.aggregate(check, ev.validate_judge(r, self.case)), "WARN")
        r[golden.DIMENSIONS[1]].update(status="FAIL", could_change_decision=True, material_discrepancy="Invented ownership", failure_kind="unsupported_career_claim")
        self.assertEqual(ev.aggregate(check, ev.validate_judge(r, self.case)), "FAIL")
        self.assertEqual(ev.aggregate({"passed": False, "exact_decision_alignment": False}, response()), "FAIL")
        r.pop("gap_preservation")
        with self.assertRaises(Exception): ev.validate_judge(r, self.case)

    def test_pending_case_prevents_premature_release_pass(self):
        completed = ev.pending_result(self.case)
        completed.update(status="completed", overall="PASS", dimensions=response(), deterministic={"exact_decision_alignment": True})
        pending = ev.pending_result({**self.case, "case_id": "pending"})
        self.assertEqual(ev.summary([completed, pending])["release_gate"], "INCOMPLETE")
        self.assertIsNone(ev.summary([completed, pending])["exact_decision_accuracy"])

    def test_structured_gaps_and_criterion_reference_are_preserved(self):
        c = deepcopy(self.case); row=c["reference"]["capability_domain_expectations"][0]
        row["criterion"]=row.pop("capability")
        c["reference"]["meaningful_gaps"]=[{"gap":"Specialist context", "severity":"Material", "fundamental_to_role":True}]
        self.write([c]); data, report=golden.validate_dataset(self.data,expected_count=1)
        self.assertTrue(report["references_valid"]); self.assertEqual(data["cases"][0],c)

    def test_provisional_exception_only_one_dimension(self):
        c = deepcopy(self.case); c.update(case_id=golden.EXCEPTION, company="Cisco", job_id="2023232", strict_jd_fidelity=False)
        self.write([c]); self.assertTrue(golden.validate_dataset(self.data, expected_count=1)[1]["all_runnable"])
        r = response(); r[golden.DIMENSIONS[0]].update(status="FAIL", could_change_decision=True, material_discrepancy="Missing footer", failure_kind="missed_material_requirement")
        dims = ev.validate_judge(r, c)
        self.assertEqual(dims[golden.DIMENSIONS[0]]["status"], "PROVISIONAL")
        self.assertEqual(ev.aggregate({"passed": True, "exact_decision_alignment": True}, dims), "PASS")
        r["gap_preservation"].update(status="FAIL", could_change_decision=True, material_discrepancy="Lost gap", failure_kind="lost_material_gap")
        self.assertEqual(ev.aggregate({"passed": True, "exact_decision_alignment": True}, ev.validate_judge(r, c)), "FAIL")

    def test_fresh_runner_judge_packet_resume_and_usage(self):
        agent, judge = FakeModel(), Judge(); before = golden.fingerprint(self.data)
        run = self.run_eval(model=agent, judge=judge)
        self.assertEqual(len(agent.calls), 4); self.assertEqual(len(judge.calls), 1)
        for call in agent.calls: self.assertNotIn("reference", call["context"])
        self.assertNotIn("candidate_context", judge.calls[0]["context"])
        self.assertNotIn("contract_hashes", judge.calls[0]["context"])
        self.assertEqual(golden.fingerprint(self.data), before)
        self.assertEqual(golden.read_json(run / "summary.json")["release_gate"], "PASS")
        self.assertEqual(golden.read_json(run / "usage.json")["total_known_tokens"], 560)
        self.run_eval(model=agent, judge=judge, resume=run)
        self.assertEqual(len(agent.calls), 4); self.assertEqual(len(judge.calls), 1)

    def test_exact_mismatch_still_judged_but_cannot_be_overridden(self):
        self.case["reference"]["shortlist_decision"] = "DO NOT APPLY"; self.write([self.case]); judge = Judge()
        run = self.run_eval(judge=judge); summary = golden.read_json(run / "summary.json")
        self.assertEqual(summary["counts"]["FAIL"], 1); self.assertEqual(summary["release_gate"], "FAIL")
        self.assertEqual(len(judge.calls), 1)
        result = golden.read_json(run / "per_case" / (self.case["case_id"] + ".json"))
        self.assertTrue(result["production_usable"])  # Golden mismatch does not change production acceptance.
        self.assertFalse(result["deterministic"]["exact_decision_alignment"])
        self.assertTrue(all(d["status"] == "PASS" for d in result["dimensions"].values()))

    def test_controller_rejected_result_judged_without_production_promotion(self):
        def reject(stage, output):
            if stage == "controller_validation":
                output["validation"] = {k: False for k in output["validation"]}
                output["issues"] = [{"stage": "career_requirements_mapping", "description": "Unsupported mentorship", "required_action": "Review evidence"}]
        judge = Judge(); run = self.run_eval(model=FakeModel(reject), judge=judge)
        result = golden.read_json(run / "per_case" / (self.case["case_id"] + ".json"))
        self.assertEqual(len(judge.calls), 1)
        self.assertFalse(result["controller"]["accepted"])
        self.assertTrue(result["controller"]["issues"])
        self.assertFalse(result["production_usable"])
        self.assertEqual(result["overall"], "FAIL")
        self.assertTrue(all(d["status"] == "PASS" for d in result["dimensions"].values()))
        self.assertEqual(golden.read_json(run / "summary.json")["release_gate"], "FAIL")
        manifest = golden.read_json(run / "manifest.json")
        artifact = golden.read_json(run / "shortlist_runs" / manifest["cases"][self.case["case_id"]]["run_id"] / "job_state.json")
        self.assertEqual(artifact["status"], "rejected")
        self.assertFalse(artifact["shortlist_state"]["validation"]["shortlist_decision_accepted"])
        self.assertNotIn("handoff", artifact["shortlist_state"])

    def test_controller_transport_failure_still_allows_completed_analysis_judging(self):
        def fail(stage, output):
            if stage == "controller_validation": raise ModelError("Synthetic controller outage")
        judge = Judge(); run = self.run_eval(model=FakeModel(fail), judge=judge)
        result = golden.read_json(run / "per_case" / (self.case["case_id"] + ".json"))
        self.assertEqual(len(judge.calls), 1)
        self.assertFalse(result["controller"]["available"])
        self.assertFalse(result["production_usable"])
        self.assertEqual(result["controller"]["execution_error"]["stage"], "controller_validation")

    def test_incomplete_mapping_does_not_invoke_judge(self):
        def fail(stage, output):
            if stage == "career_requirements_mapping": raise ModelError("Synthetic missing mapping")
        judge = Judge(); run = self.run_eval(model=FakeModel(fail), judge=judge)
        result = golden.read_json(run / "per_case" / (self.case["case_id"] + ".json"))
        self.assertEqual(judge.calls, [])
        self.assertFalse(result["judge_readiness"]["ready"])
        self.assertEqual(result["status"], "incomplete")
        self.assertFalse(result["production_usable"])

    def test_controller_and_mapping_structural_checks(self):
        run = self.run_eval(); manifest = golden.read_json(run / "manifest.json")
        path = run / "shortlist_runs" / manifest["cases"][self.case["case_id"]]["run_id"] / "job_state.json"
        artifact = golden.read_json(path); artifact["completed_stages"].pop()
        self.assertFalse(ev.deterministic(self.case, artifact, golden.input_job(self.data, self.case))["passed"])
        artifact = golden.read_json(path); artifact["shortlist_state"]["career_requirements_mapping"]["criteria"][0]["domain_context_fit"] = "invalid"
        self.assertFalse(ev.deterministic(self.case, artifact, golden.input_job(self.data, self.case))["passed"])
        self.assertFalse(ev.judge_readiness(artifact, golden.input_job(self.data, self.case))["ready"])
        artifact = golden.read_json(path)
        artifact["stage_outputs"]["shortlist_decision"]["decision_rationale"] = "Inconsistent saved stage"
        self.assertFalse(ev.judge_readiness(artifact, golden.input_job(self.data, self.case))["ready"])

    def test_runner_failure_resumes_remaining_stages(self):
        def fail(stage, output):
            if stage == "career_requirements_mapping": raise ModelError("Synthetic interruption")
        run = self.run_eval(model=FakeModel(mutate=fail))
        self.assertEqual(golden.read_json(run / "summary.json")["release_gate"], "INCOMPLETE")
        self.assertEqual(golden.read_json(run / "per_case" / (self.case["case_id"] + ".json"))["status"], "incomplete")
        agent = FakeModel(); self.run_eval(model=agent, resume=run)
        self.assertEqual(len(agent.calls), 3)
        self.assertEqual(golden.read_json(run / "summary.json")["release_gate"], "PASS")

    def test_uncertain_judge_is_not_retried(self):
        judge = Judge()
        with patch.object(judge, "complete", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): self.run_eval(judge=judge)
        run = next((self.root / "runs").iterdir())
        self.run_eval(judge=judge, resume=run)
        self.assertEqual(judge.calls, [])
        self.assertEqual(golden.read_json(run / "summary.json")["release_gate"], "INCOMPLETE")

    def test_resume_rejects_evidence_change(self):
        run = self.run_eval(); (self.root / CANDIDATE_FILES[0]).write_text("Changed")
        with self.assertRaisesRegex(ValueError, "Cannot resume"): self.run_eval(resume=run)

    def test_cli_dry_run_never_constructs_model(self):
        with patch.object(ev, "ResponsesModel", side_effect=AssertionError("No client in dry-run")), redirect_stdout(io.StringIO()):
            self.assertEqual(ev.main(["--dataset", str(self.data), "--dry-run"]), 2)  # one-case fixture, expected twelve

    def test_v12_source_manifest_and_package_integrity(self):
        copied = self.root / "v12"
        shutil.copytree(golden.DEFAULT_DATA, copied)
        manifest_path = copied / "integrity.json"
        manifest = golden.read_json(manifest_path)
        name = next(iter(manifest["sources"]))
        manifest["sources"][name]["bytes"] += 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        package = golden.fingerprint(copied); package.pop("package_integrity.json")
        (copied / "package_integrity.json").write_text(json.dumps({"files": package}), encoding="utf-8")
        report = golden.validate_dataset(copied)[1]
        self.assertFalse(report["all_runnable"])
        self.assertTrue(any("mapping/hash/bytes/provenance mismatch" in e for e in report["errors"]))
        (copied / "README.md").write_text("drift", encoding="utf-8")
        self.assertIn("Frozen package changed from integrity manifest", golden.validate_dataset(copied)[1]["errors"])

    def test_v12_prefixed_source_and_reference_preservation(self):
        data, report = golden.validate_dataset()
        for case in data["cases"]:
            self.assertTrue(golden.source_text(golden.DEFAULT_DATA, case).strip())
        self.assertEqual(sum(c["role_understanding_status"] == "PROVISIONAL" for c in report["cases"]), 1)
        with patch.object(ev, "ResponsesModel", side_effect=AssertionError("No paid client")), redirect_stdout(io.StringIO()):
            self.assertEqual(ev.main(["--dry-run"]), 0)
            self.assertEqual(ev.main(["--validate"]), 0)

    def test_pilot_allowlist_and_production_models(self):
        data, _ = golden.validate_dataset()
        ids = ["microsoft_200051931", "microsoft_200015839", "flexport_8110066"]
        self.assertEqual([c["case_id"] for c in ev.select_cases(data, ids)], ids)
        for invalid in ([], [ids[0], ids[0]], ["unknown"]):
            with self.assertRaises(ValueError): ev.select_cases(data, invalid)
        from run_shortlist_batch import DEFAULT_STAGE_MODELS
        agent = FakeModel()
        run = self.run_eval(model=agent, case_ids=[self.case["case_id"]], stage_models=DEFAULT_STAGE_MODELS)
        self.assertEqual([c["model"] for c in agent.calls], list(DEFAULT_STAGE_MODELS.values()))
        manifest = golden.read_json(run / "manifest.json")
        self.assertEqual(list(manifest["cases"]), [self.case["case_id"]])
        self.assertEqual(manifest["config"]["stage_models"], DEFAULT_STAGE_MODELS)
        with patch.object(ev, "ResponsesModel", side_effect=AssertionError("No client")), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(ev.main(["--dry-run", *sum((["--case-id", cid] for cid in ids), [])]), 0)
        self.assertEqual(json.loads(out.getvalue())["call_plan"]["shortlist_calls_no_retries"], 12)

    def test_supplied_dataset_and_exception(self):
        data, r = golden.validate_dataset()
        self.assertTrue(r["references_valid"]); self.assertEqual(r["case_count"], 12)
        self.assertEqual(r["runnable_count"], 12); self.assertTrue(r["all_runnable"])
        self.assertEqual(next(c for c in r["cases"] if c["case_id"] == golden.EXCEPTION)["role_understanding_status"], "PROVISIONAL")
        self.assertEqual(ev.call_plan(r)["shortlist_calls_no_retries"], 48)


if __name__ == "__main__":
    unittest.main()
