"""Offline prompt-contract and propagation tests, not simulated semantic model scores."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import unittest
from unittest.mock import patch

import run_shortlist_job as runner
import shortlist_golden as golden
import test_shortlist_runner as fixtures


class QualityRegressionTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    execute = fixtures.RunnerTests.execute

    def run_offline(self, mutate, job=None):
        with patch("requests.post", side_effect=AssertionError("Network forbidden")), redirect_stdout(io.StringIO()):
            return self.execute(fixtures.FakeModel(mutate), job)

    def golden_job(self, job_id):
        dataset = golden.read_json(golden.DEFAULT_DATA / "shortlist_golden_v1_2.json")
        case = next(c for c in dataset["cases"] if c["job_id"] == job_id)
        return golden.input_job(golden.DEFAULT_DATA, case)

    def test_baseline_duration_taxonomy_and_source_wording(self):
        # Scripted outputs verify guidance delivery and preservation, not LLM semantics.
        cases = [("5+ years of product experience", "experience_duration"),
                 ("Experience with reporting, analytics, business intelligence, data products, or data platforms.", "other"),
                 ("Bachelor's degree AND 8 years of product experience OR equivalent experience", "experience_duration")]
        for requirement, kind in cases:
            with self.subTest(requirement=requirement):
                def response(stage, out):
                    if stage == "role_understanding":
                        out["baseline_qualifications"][0].update(requirement=requirement, requirement_type=kind)
                    elif stage == "career_requirements_mapping":
                        out[stage]["baseline_qualification_mapping"][0].update(requirement=requirement, requirement_type=kind)
                _, artifact, model = self.run_offline(response)
                row = artifact["shortlist_state"]["role_understanding"]["baseline_qualifications"][0]
                self.assertEqual((row["requirement"], row["requirement_type"]), (requirement, kind))
                prompt = model.calls[0]["instructions"]
                for text in ("only for an explicit measurable tenure threshold", "is other, not experience_duration", "never infer years", "preserve its complete"):
                    self.assertIn(text, prompt)

    def test_atomic_partner_components_have_independent_mappings(self):
        job = self.golden_job("200015839")
        for word in ("catalog", "credentials", "integrations"):
            self.assertIn(word, job["full_job_description_raw"].lower())
        criteria = [("catalog", "Content/catalog ecosystem", "transferable"),
                    ("credentials", "Credential partnerships", "gap"),
                    ("integrations", "Enterprise integrations", "adjacent")]
        def response(stage, out):
            for cid, label, fit in criteria:
                if stage == "role_understanding":
                    out["hiring_criteria"].append(dict(criterion_id=cid, criterion=label, description=label, importance="High"))
                elif stage == "career_requirements_mapping":
                    row = deepcopy(out[stage]["criteria"][0])
                    row.update(criterion_id=cid, criterion=label, role_requirement=label, capability_fit=fit,
                               domain_context_fit="gap", limitation_or_difference="Separate synthetic evidence boundary for " + label)
                    out[stage]["criteria"].append(row)
                    provenance = deepcopy(out["evidence_provenance"][0]); provenance["criterion_id"] = cid
                    out["evidence_provenance"].append(provenance)
                elif stage == "controller_validation":
                    row = deepcopy(out["evidence_checks"][0]); row["criterion_id"] = cid
                    out["evidence_checks"].append(row)
        _, artifact, model = self.run_offline(response, job)
        rows = artifact["shortlist_state"]["career_requirements_mapping"]["criteria"][-3:]
        self.assertEqual([(r["criterion_id"], r["capability_fit"]) for r in rows], [(c, f) for c, _, f in criteria])
        self.assertIn("independent evidence could support one but not the others", model.calls[0]["instructions"])

    def test_prioritization_and_measurement_keep_direct_capability(self):
        for capability in ("Portfolio prioritization and trade-offs", "Product quality and outcome measurement"):
            for domain in ("transferable", "adjacent"):
                with self.subTest(capability=capability, domain=domain):
                    def response(stage, out):
                        if stage == "role_understanding":
                            out["hiring_criteria"][0].update(criterion=capability, description=capability)
                        elif stage == "career_requirements_mapping":
                            out[stage]["criteria"][0].update(criterion=capability, role_requirement=capability,
                                capability_fit="direct", domain_context_fit=domain,
                                limitation_or_difference="Learning/skilling context differs; underlying capability demonstrated.")
                    _, artifact, model = self.run_offline(response)
                    row = artifact["shortlist_state"]["career_requirements_mapping"]["criteria"][0]
                    self.assertEqual((row["capability_fit"], row["domain_context_fit"]), ("direct", domain))
                    self.assertIn("Different learning/skilling", model.calls[1]["instructions"])
                    self.assertIn("quality/outcome measurement", model.calls[1]["instructions"])

    def test_pm_mentorship_requires_specific_evidence(self):
        for evidence, fit in [(fixtures.CAPABILITY, "gap"), ("Coached product managers in discovery and improved PM decision reviews.", "direct")]:
            with self.subTest(fit=fit):
                (self.root / "profile/career_evidence.md").write_text(evidence, encoding="utf-8")
                def response(stage, out):
                    if stage == "role_understanding":
                        out["hiring_criteria"][0].update(criterion="PM mentorship", description="Coach PMs and improve PM craft")
                    elif stage == "career_requirements_mapping":
                        row = out[stage]["criteria"][0]
                        row.update(criterion="PM mentorship", role_requirement="Coach PMs and improve PM craft", capability_fit=fit,
                            limitation_or_difference="No PM-specific mentoring evidence; general leadership is context only." if fit == "gap" else "PM coaching demonstrated; no formal management or direct reports implied.")
                        row["strongest_evidence"]["evidence_summary"] = evidence
                        out["evidence_provenance"][0]["sources"][0]["quote"] = evidence
                _, artifact, model = self.run_offline(response)
                self.assertEqual(artifact["shortlist_state"]["career_requirements_mapping"]["criteria"][0]["capability_fit"], fit)
                for text in ("do not establish even adjacent PM mentorship", "classify the mentorship capability as gap", "supported PM coaching", "not imply formal management"):
                    self.assertIn(text, model.calls[1]["instructions"])

    def test_posting_constraints_survive_null_identity_through_controller(self):
        job = self.golden_job("200051931")
        self.assertIn("50-mile commute", job["full_job_description_raw"])
        constraints = ["Posting constraint: AI Experiences employees within a 50-mile commute of a designated Microsoft Hub in the U.S. are expected in office at least four days per week, subject to local law and jurisdiction.",
                       "Posting constraint: Travel less than 25%."]
        def response(stage, out):
            if stage == "role_understanding":
                out["actual_scope"]["scope_signals"].extend(constraints)
                out["role_identity"]["location"] = "Inferred hub"
                out["baseline_qualifications"][0]["requirement"] = "Bachelor's degree and 5+ years, or equivalent experience."
            elif stage == "career_requirements_mapping":
                out[stage]["baseline_qualification_mapping"][0]["requirement"] = "Bachelor's degree and 5+ years, or equivalent experience."
        _, artifact, model = self.run_offline(response, job)
        self.assertIsNone(artifact["shortlist_state"]["job"]["location"])
        for request in model.calls[1:]:
            role = request["context"]["upstream"]["role_understanding"]
            self.assertIsNone(role["role_identity"]["location"])
            self.assertTrue(set(constraints).issubset(role["actual_scope"]["scope_signals"]))
        self.assertIn("Posting constraint:", model.calls[0]["instructions"])
        self.assertIn("feasibility facts, not seniority signals", model.calls[0]["instructions"])

    def test_partner_integration_requirement_gets_its_own_mapping_and_audit(self):
        job = self.golden_job("200015839")
        self.assertIn("partner", job["full_job_description_raw"].lower())
        def response(stage, out):
            if stage == "role_understanding":
                out["hiring_criteria"].append(dict(criterion_id="partner-integration",
                    criterion="Partner ecosystem integrations", description="Integrate partner content and credentials with enterprise workflows.", importance="High"))
            elif stage == "career_requirements_mapping":
                row = deepcopy(out[stage]["criteria"][0])
                row.update(criterion_id="partner-integration", criterion="Partner ecosystem integrations",
                    role_requirement="Integrate partner content and credentials with enterprise workflows.",
                    capability_fit="gap", domain_context_fit="gap", overall_fit_assessment="Material gap",
                    limitation_or_difference="This synthetic fixture does not establish partner ecosystem integration ownership.")
                row["strongest_evidence"] = dict(project_or_role=None, evidence_summary=None, measurable_outcomes=[])
                out[stage]["criteria"].append(row)
                out["evidence_provenance"].append(dict(criterion_id="partner-integration", sources=[]))
            elif stage == "controller_validation":
                row = deepcopy(out["evidence_checks"][0]); row["criterion_id"] = "partner-integration"
                out["evidence_checks"].append(row)
        _, artifact, model = self.run_offline(response, job)
        state = artifact["shortlist_state"]
        self.assertEqual(state["career_requirements_mapping"]["criteria"][-1]["capability_fit"], "gap")
        report = deepcopy(artifact["controller_review"]); report["evidence_checks"].pop()
        with self.assertRaisesRegex(ValueError, "every hiring criterion"):
            runner._controller_consistency(report, state["role_understanding"], state["career_requirements_mapping"])
        self.assertIn("not only a responsibility cluster", model.calls[0]["instructions"])
        self.assertIn("atomic", model.calls[0]["instructions"])

    def test_direct_capability_survives_transferable_domain_without_reclassification(self):
        def response(stage, out):
            if stage == "career_requirements_mapping":
                out[stage]["criteria"][0].update(domain_context_fit="transferable",
                    limitation_or_difference="Direct deployment capability; different industry context.")
        _, artifact, model = self.run_offline(response)
        for request in model.calls[2:]:
            row = request["context"]["upstream"]["career_requirements_mapping"]["career_requirements_mapping"]["criteria"][0]
            self.assertEqual((row["capability_fit"], row["domain_context_fit"]), ("direct", "transferable"))
        self.assertIn("non-direct capability rating needs a", model.calls[1]["instructions"])
        self.assertEqual(artifact["status"], "accepted")

    def test_uncertainty_and_candidate_confirmed_provenance_survive(self):
        uncertainty = "Candidate-confirmed pilot launch; production maturity unverified. Authorization/sponsorship conflict remains unresolved."
        def response(stage, out):
            if stage == "career_requirements_mapping":
                row = out[stage]["criteria"][0]
                row["limitation_or_difference"] = uncertainty
                row["strongest_evidence"]["evidence_summary"] = fixtures.CONFIRMED_CAPABILITY + " " + uncertainty
                out[stage]["overall_evidence_summary"] = uncertainty
                out["evidence_provenance"][0]["sources"] = [dict(source_path=runner.CONFIRMED_FACTS_FILE,
                    quote=fixtures.CONFIRMED_CAPABILITY, provenance_type="candidate_confirmed")]
            elif stage == "shortlist_decision":
                out["eligibility_relocation_flag"] = dict(status="Unresolved", details=uncertainty)
        _, artifact, model = self.run_offline(response)
        self.assertEqual(artifact["shortlist_state"]["shortlist_decision"]["eligibility_relocation_flag"]["details"], uncertainty)
        self.assertIn(uncertainty, json.dumps(model.calls[-1]["context"]))
        self.assertIn("'launched' alone does not", model.calls[1]["instructions"])
        self.assertIn("cite both sides", model.calls[1]["instructions"])
        self.assertIn("Unknown is not a confirmed blocker", model.calls[2]["instructions"])
        bad = deepcopy(artifact["controller_review"])
        bad["issues"].append(dict(stage="career_requirements_mapping", description="Production claim unsupported", required_action="Preserve uncertainty"))
        state = artifact["shortlist_state"]
        with self.assertRaisesRegex(ValueError, "unresolved validation issues"):
            runner._controller_consistency(bad, state["role_understanding"], state["career_requirements_mapping"])

    def test_fundamental_and_manageable_domain_gaps_do_not_rewrite_direct_capability(self):
        # Scripted decisions exercise transport/schema, not an offline semantic oracle.
        for fundamental, decision in [(True, "DO NOT APPLY"), (False, "APPLY")]:
            with self.subTest(fundamental=fundamental):
                def response(stage, out):
                    if stage == "career_requirements_mapping":
                        out[stage]["criteria"][0].update(domain_context_fit="gap", limitation_or_difference="Specialist operating context not established.")
                        out[stage]["meaningful_gaps"] = [dict(requirement="Specialist operating knowledge", severity="Material gap",
                            description="Central unbridged shortfall." if fundamental else "Preferred context; demonstrated capability transfers.",
                            closest_transferable_evidence=fixtures.CAPABILITY, fundamental_to_role=fundamental)]
                    elif stage == "shortlist_decision":
                        out["decision"] = decision
                        out["decision_rationale"] = "Central specialist operating knowledge is unbridged." if fundamental else "Preferred domain difference is manageable with demonstrated transfer."
                _, artifact, model = self.run_offline(response)
                state = artifact["shortlist_state"]
                self.assertEqual(state["shortlist_decision"]["decision"], decision)
                self.assertEqual(state["career_requirements_mapping"]["criteria"][0]["capability_fit"], "direct")
                self.assertTrue(state["validation"]["shortlist_decision_accepted"])
                self.assertIn("product-function mismatch is not required", model.calls[2]["instructions"])
                self.assertIn("flag is an automatic veto", model.calls[2]["instructions"])

    def test_priority_is_not_capped_by_senior_title_or_awarded_by_principal_title(self):
        for title, decision in [("Senior Product Manager", "APPLY — PRIORITY"), ("Principal Product Manager", "APPLY")]:
            with self.subTest(title=title):
                job = fixtures.input_job(); job["title"] = title
                def response(stage, out):
                    if stage == "shortlist_decision":
                        out["decision"] = decision
                        out["scope_assessment"]["classification"] = "High-value Senior"
                _, artifact, model = self.run_offline(response, job)
                self.assertEqual(artifact["shortlist_state"]["shortlist_decision"]["decision"], decision)
                prompt = model.calls[2]["instructions"]
                self.assertIn("unusually strong use of application effort", prompt)
                self.assertIn("title, prestige", prompt)
                self.assertIn("do not alone cap a role at APPLY", prompt)


if __name__ == "__main__":
    unittest.main()
