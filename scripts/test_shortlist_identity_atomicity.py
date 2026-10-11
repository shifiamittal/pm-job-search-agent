"""Offline regressions for the three-case pilot; no paid model calls."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
import unittest
from unittest.mock import patch

import run_shortlist_job as runner
from shortlist_contract import validate_shortlist_record
import test_shortlist_runner as fixtures
from test_shortlist_runner import FakeModel, input_job


class IdentityAtomicityTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    execute = fixtures.RunnerTests.execute

    def checked_run(self, model, job):
        with patch("requests.post", side_effect=AssertionError("Network forbidden")), redirect_stdout(io.StringIO()):
            return self.execute(model, job)

    def test_null_identity_cannot_be_enriched_from_jd_or_decision(self):
        job = input_job()
        job.update(location=None, work_model=None, travel=None)
        job["full_job_description_raw"] += " Bellevue, Washington. Hybrid. Travel 25%."
        def rewrite(stage, output):
            if stage == "role_understanding":
                output["role_identity"].update(company="Invented", job_id="other", title="Changed",
                    location="Bellevue, Washington", work_model="Hybrid", travel="25%")
            if stage == "shortlist_decision":
                output["location_work_model"] = {"location": "Not specified; designated US hub",
                                                "work_model": "Hybrid", "travel": "25%"}
        _, artifact, model = self.checked_run(FakeModel(rewrite), job)
        canonical = runner.canonical_identity(runner.normalize_input(job))
        self.assertEqual(artifact["status"], "accepted")
        self.assertEqual(artifact["stage_outputs"]["role_understanding"]["role_identity"], canonical)
        self.assertEqual(artifact["stage_outputs"]["shortlist_decision"]["location_work_model"],
                         dict(location=None, work_model=None, travel=None))
        for call in model.calls:
            self.assertEqual(call["context"]["canonical_identity"], canonical)
            if call["stage"] != "role_understanding":
                self.assertEqual(call["context"]["upstream"]["role_understanding"]["role_identity"], canonical)
        self.assertEqual(model.calls[-1]["context"]["proposed_state"]["job"]["location"], None)
        self.assertEqual(artifact["raw_stage_outputs"]["role_understanding"]["role_identity"]["location"], "Bellevue, Washington")
        self.assertNotEqual(artifact["model_calls"][0]["raw_output_sha256"], artifact["model_calls"][0]["output_sha256"])

    def test_nonnull_identity_remains_exact_even_if_model_omits_copies(self):
        job = input_job()
        job.update(location="Redmond, WA — USA", work_model="4 days / week", travel="Less than 25%")
        def omit(stage, output):
            if stage == "role_understanding": output.pop("role_identity")
            if stage == "shortlist_decision": output.pop("location_work_model")
        _, artifact, _ = self.checked_run(FakeModel(omit), job)
        state = artifact["shortlist_state"]
        for key in runner.IDENTITY_FIELDS:
            self.assertEqual(state["job"][key], job.get(key))
            self.assertEqual(state["role_understanding"]["role_identity"][key], job.get(key))
        for key in ("location", "work_model", "travel"):
            self.assertEqual(state["shortlist_decision"]["location_work_model"][key], job[key])
        invalid = deepcopy(state)
        invalid["shortlist_decision"]["location_work_model"]["location"] = "London"
        with self.assertRaises(ValueError): validate_shortlist_record(invalid)

    def test_non_identity_invalid_output_still_rejected(self):
        def invalid(stage, output):
            if stage == "shortlist_decision": output["decision"] = "INVALID"
        with self.assertRaises(runner.RunError): self.checked_run(FakeModel(invalid), input_job())

    def test_hc9_atomic_mappings_preserve_separate_supported_and_missing_capabilities(self):
        # Microsoft 200015839 HC9 incorrectly grouped these four material concepts.
        names = ["Improving product metrics", "Disrupting a market",
                 "Leading consumer-product teams", "Taking products to market"]
        ids = ["reporting", "market-disruption", "consumer-team-leadership", "product-launch"]
        def atomic(stage, output):
            if stage == "role_understanding":
                output["hiring_criteria"] = [dict(criterion_id=cid, criterion=name,
                    description="Preferred capability: " + name, importance="Helpful") for cid, name in zip(ids, names)]
            elif stage == "career_requirements_mapping":
                mapping = output[stage]
                template = mapping["criteria"][0]
                provenance = output["evidence_provenance"][0]
                mapping["criteria"] = []
                output["evidence_provenance"] = []
                for i, (cid, name) in enumerate(zip(ids, names)):
                    row = deepcopy(template)
                    row.update(criterion_id=cid, criterion=name, role_requirement=name)
                    source = deepcopy(provenance); source["criterion_id"] = cid
                    if i in (1, 2):
                        row.update(capability_fit="gap", domain_context_fit="not_applicable",
                            overall_fit_assessment="Material gap", limitation_or_difference="Capability not established")
                        row["strongest_evidence"] = dict(project_or_role=None, evidence_summary=None, measurable_outcomes=[])
                        source["sources"] = []
                    mapping["criteria"].append(row); output["evidence_provenance"].append(source)
            elif stage == "controller_validation":
                check = output["evidence_checks"][0]
                output["evidence_checks"] = [{**deepcopy(check), "criterion_id": cid} for cid in ids]
        job = input_job()
        job["full_job_description_raw"] += " Preferred experience: " + "; ".join(names)
        _, artifact, model = self.checked_run(FakeModel(atomic), job)
        state = artifact["shortlist_state"]
        self.assertEqual([c["capability_fit"] for c in state["career_requirements_mapping"]["criteria"]],
                         ["direct", "gap", "gap", "direct"])
        self.assertEqual([c["criterion"] for c in state["role_understanding"]["hiring_criteria"]], names)
        # Existing baseline compound degree/years/alternative survives independently.
        self.assertIn("or equivalent experience", state["role_understanding"]["baseline_qualifications"][0]["requirement"])
        self.assertIn("atomic", model.calls[0]["instructions"])
        self.assertIn("direct requires support for the whole", model.calls[1]["instructions"])
        missing = deepcopy(state); missing["career_requirements_mapping"]["criteria"].pop()
        with self.assertRaises(ValueError): validate_shortlist_record(missing)
        # Controller still cannot accept an unsupported positive capability claim.
        report = deepcopy(artifact["controller_review"])
        report["evidence_checks"][0]["checks"]["capability_fit_classified"] = False
        with self.assertRaisesRegex(ValueError, "unsupported positive fit"):
            runner._controller_consistency(report, state["role_understanding"], state["career_requirements_mapping"])


if __name__ == "__main__":
    unittest.main()
