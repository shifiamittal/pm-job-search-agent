"""Synthetic v1 records only; no real candidate claims or persisted job changes."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from shortlist_contract import ROOT, load_schema, shortlist_outcomes, validate_shortlist_record


def example_record(outcome="APPLY"):
    identity = {"company": "Synthetic Company", "title": "Senior Product Manager",
                "job_id": None, "location": None, "work_model": None, "travel": None}
    return {
        "schema_version": "1.2.0", "job": {**identity, "jd_source": "synthetic posting"},
        "role_understanding": {
            "role_identity": dict(identity),
            "actual_job_to_be_done": {"summary": "Own shared reporting definitions."},
            "major_responsibility_clusters": [{"name": "Reporting", "description": "Own reporting definitions."}],
            "hiring_criteria": [{"criterion_id": "reporting", "criterion": "Reporting ownership",
                                 "description": "Own shared definitions.", "importance": "Critical"}],
            "specialist_requirements": [{"requirement": "Shared semantics", "importance": "High", "notes": "Explicit in synthetic JD."}],
            "baseline_qualifications": [{"qualification_id": "degree-experience", "requirement": "Bachelor's degree and 8+ years, or equivalent experience.",
                                          "requirement_type": "education", "required_or_preferred": "required",
                                          "notes": "Explicit basic qualification."},
                                         {"qualification_id": "background-check", "requirement": "Pass required background screening.",
                                          "requirement_type": "screening", "required_or_preferred": "required",
                                          "notes": "Future screening requirement."}],
            "actual_scope": {"scope_signals": ["Foundational shared platform"], "scope_summary": "Broad shared charter."},
            "likely_hiring_manager_questions": ["Have you owned shared reporting definitions?"],
        },
        "career_requirements_mapping": {
            "criteria": [{"criterion_id": "reporting", "criterion": "Reporting ownership",
                          "role_requirement": "Own shared definitions.",
                          "strongest_evidence": {"project_or_role": "Synthetic project",
                                                 "evidence_summary": "Synthetic artifact section 1: owned reporting definitions.",
                                                 "measurable_outcomes": []},
                          "capability_fit": "direct", "domain_context_fit": "direct",
                          "overall_fit_assessment": "Strong fit", "limitation_or_difference": None}],
            "specialist_requirement_mapping": [{"requirement": "Shared semantics", "evidence": "Synthetic artifact section 1.",
                                                "assessment": "Direct evidence.", "gap_if_any": None}],
            "baseline_qualification_mapping": [{"qualification_id": "degree-experience",
                                                  "requirement": "Bachelor's degree and 8+ years, or equivalent experience.",
                                                  "requirement_type": "education", "required_or_preferred": "required",
                                                  "evidence": "Approved degree and experience headline.", "assessment": "met",
                                                  "limitation_or_unknown": "Timeline ambiguity remains preserved."},
                                                 {"qualification_id": "background-check",
                                                  "requirement": "Pass required background screening.",
                                                  "requirement_type": "screening", "required_or_preferred": "required",
                                                  "evidence": None, "assessment": "unknown",
                                                  "limitation_or_unknown": "A future screening outcome cannot be established from career evidence."}],
            "strongest_role_stories": [{"story": "Synthetic shared definitions", "criteria_supported": ["reporting"], "why_relevant": "Same work."}],
            "meaningful_gaps": [], "overall_evidence_summary": "Synthetic direct evidence for the criterion.",
        },
        "shortlist_decision": {
            "decision": outcome,
            "actual_work_alignment": {"classification": "Directly aligned", "rationale": "Same synthetic work."},
            "scope_assessment": {"classification": "High-value Senior", "rationale": "Foundational charter."},
            "evidence_strength": {"classification": "Strong direct evidence", "rationale": "Same synthetic work."},
            "career_value": {"classification": "High", "rationale": "Deepens platform ownership."},
            "primary_reasons_to_pursue": ["Shared platform ownership"],
            "key_gap_or_risk": {"description": None, "severity": None},
            "location_work_model": {"location": None, "work_model": None, "travel": None},
            "eligibility_relocation_flag": {"status": "Unknown", "details": "Synthetic posting is silent."},
            "decision_rationale": "Synthetic proposed decision; semantic review has not occurred.",
            "next_action": "Controller review required.",
        },
        "validation": {"role_understanding_complete": True, "career_mapping_complete": True,
                       "shortlist_decision_complete": True, "factual_grounding_passed": False,
                       "capability_domain_fit_check_passed": False, "gaps_preserved": True,
                       "semantic_validation_passed": False, "selection_policy_check_passed": False,
                       "shortlist_decision_accepted": False},
    }


def with_handoff():
    record = example_record()
    record["validation"] = {key: True for key in record["validation"]}
    role = copy.deepcopy(record["role_understanding"])
    identity = role.pop("role_identity")
    role.update({key: identity[key] for key in ("location", "work_model")})
    mapping = copy.deepcopy(record["career_requirements_mapping"])
    mapping["criteria_mapping"] = mapping.pop("criteria")
    mapping["capability_domain_classification"] = [
        {key: criterion[key] for key in ("criterion_id", "capability_fit", "domain_context_fit",
                                         "overall_fit_assessment", "limitation_or_difference")}
        for criterion in mapping["criteria_mapping"]]
    record["handoff"] = {"role_state": role, "career_mapping_state": mapping,
                         "shortlist_decision": copy.deepcopy(record["shortlist_decision"]),
                         "validation": dict(record["validation"])}
    return record


class ContractTests(unittest.TestCase):
    def test_schema_is_valid_and_outcomes_exact(self):
        load_schema()
        self.assertEqual(shortlist_outcomes(), ("APPLY — PRIORITY", "APPLY", "HOLD / INVESTIGATE", "DO NOT APPLY"))

    def test_all_new_outcomes_supported_without_auto_acceptance(self):
        for outcome in shortlist_outcomes():
            with self.subTest(outcome=outcome):
                record = example_record(outcome)
                before = copy.deepcopy(record)
                validate_shortlist_record(record)
                self.assertEqual(record, before)
                self.assertFalse(record["validation"]["shortlist_decision_accepted"])

    def test_one_criterion_and_unknown_job_id_allowed(self):
        validate_shortlist_record(example_record())

    def test_legacy_values_rejected_not_mapped(self):
        for old in ("Apply Now", "Apply Now + Bridge", "Build Toward", "Skip", "APPLY - PRIORITY"):
            with self.subTest(old=old), self.assertRaises(ValueError):
                validate_shortlist_record(example_record(old))

    def test_legacy_fields_scores_and_gap_labels_rejected(self):
        for field in ("application_lane", "primary_gap", "priority_score", "location_fit_score"):
            record = example_record()
            record[field] = "legacy"
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_shortlist_record(record)
        record = example_record()
        record["career_requirements_mapping"]["meaningful_gaps"] = [{
            "requirement": "Specialty", "severity": "Experience Gap", "description": "Unestablished",
            "closest_transferable_evidence": None, "fundamental_to_role": False}]
        with self.assertRaises(ValueError):
            validate_shortlist_record(record)

    def test_missing_stages_rejected(self):
        for stage in ("role_understanding", "career_requirements_mapping", "shortlist_decision", "validation"):
            record = example_record()
            del record[stage]
            with self.subTest(stage=stage), self.assertRaises(ValueError):
                validate_shortlist_record(record)

    def test_every_completion_flag_required_before_acceptance(self):
        for flag in example_record()["validation"]:
            if flag == "shortlist_decision_accepted":
                continue
            record = example_record()
            record["validation"] = {key: True for key in record["validation"]}
            record["validation"][flag] = False
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                validate_shortlist_record(record)

    def test_cross_stage_identity_and_location_match(self):
        record = example_record()
        record["job"]["title"] = "Different title"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            validate_shortlist_record(record)
        record = example_record()
        record["shortlist_decision"]["location_work_model"]["location"] = "Invented location"
        with self.assertRaisesRegex(ValueError, "location/work-model mismatch"):
            validate_shortlist_record(record)

    def test_location_normalization_allows_same_city_and_state_enrichment(self):
        for role_location, decision_location in (
                ("Redmond", "Redmond, Washington"),
                ("Seattle", "Seattle, WA"),
                ("Seattle, WA", "Seattle, Washington")):
            record = example_record()
            record["job"]["location"] = role_location
            record["role_understanding"]["role_identity"]["location"] = role_location
            record["shortlist_decision"]["location_work_model"]["location"] = decision_location
            with self.subTest(role=role_location, decision=decision_location):
                validate_shortlist_record(record)

    def test_location_normalization_rejects_different_city_or_state(self):
        for role_location, decision_location in (
                ("Redmond", "Seattle"),
                ("New York", "Redmond"),
                ("Portland, OR", "Portland, ME"),
                ("Paris, France", "Paris, Texas"),
                ("London, Ontario", "London, England")):
            record = example_record()
            record["job"]["location"] = role_location
            record["role_understanding"]["role_identity"]["location"] = role_location
            record["shortlist_decision"]["location_work_model"]["location"] = decision_location
            with self.subTest(role=role_location, decision=decision_location), \
                 self.assertRaisesRegex(ValueError, "location/work-model mismatch: location"):
                validate_shortlist_record(record)

    def test_unknown_locations_and_work_model_exactness_are_preserved(self):
        validate_shortlist_record(example_record())  # null equals null
        for role_location, decision_location in ((None, "Seattle"), ("Seattle", None)):
            record = example_record()
            record["job"]["location"] = role_location
            record["role_understanding"]["role_identity"]["location"] = role_location
            record["shortlist_decision"]["location_work_model"]["location"] = decision_location
            with self.subTest(role=role_location, decision=decision_location), \
                 self.assertRaisesRegex(ValueError, "location/work-model mismatch: location"):
                validate_shortlist_record(record)
        record = example_record()
        record["job"]["work_model"] = "Remote"
        record["role_understanding"]["role_identity"]["work_model"] = "Remote"
        record["shortlist_decision"]["location_work_model"]["work_model"] = "remote"
        with self.assertRaisesRegex(ValueError, "location/work-model mismatch: work_model"):
            validate_shortlist_record(record)

    def test_criteria_cannot_disappear_duplicate_or_change_names(self):
        for operation in ("missing", "duplicate", "rename"):
            record = example_record()
            criteria = record["career_requirements_mapping"]["criteria"]
            if operation == "missing":
                criteria[0]["criterion_id"] = "unknown"
            elif operation == "duplicate":
                criteria.append(copy.deepcopy(criteria[0]))
            else:
                criteria[0]["criterion"] = "Different work"
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                validate_shortlist_record(record)

    def test_specialists_and_story_references_preserved(self):
        record = example_record()
        record["career_requirements_mapping"]["specialist_requirement_mapping"] = []
        with self.assertRaisesRegex(ValueError, "Specialist requirements"):
            validate_shortlist_record(record)
        record = example_record()
        record["career_requirements_mapping"]["strongest_role_stories"][0]["criteria_supported"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "unknown criterion"):
            validate_shortlist_record(record)

    def test_baseline_qualifications_are_exactly_preserved(self):
        for operation in ("missing", "duplicate", "changed_requirement", "changed_preference"):
            record = example_record()
            mapped = record["career_requirements_mapping"]["baseline_qualification_mapping"]
            if operation == "missing":
                mapped.pop()
            elif operation == "duplicate":
                mapped.append(copy.deepcopy(mapped[0]))
            elif operation == "changed_requirement":
                mapped[0]["requirement"] = "Different requirement"
            else:
                mapped[0]["required_or_preferred"] = "preferred"
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                validate_shortlist_record(record)

    def test_preferred_baseline_remains_preferred_and_specialist_is_separate(self):
        record = example_record()
        role_item = record["role_understanding"]["baseline_qualifications"][0]
        mapped_item = record["career_requirements_mapping"]["baseline_qualification_mapping"][0]
        role_item["required_or_preferred"] = mapped_item["required_or_preferred"] = "preferred"
        validate_shortlist_record(record)
        self.assertNotIn(role_item["requirement"],
                         [row["requirement"] for row in record["role_understanding"]["specialist_requirements"]])

    def test_unknown_screening_is_not_a_capability_gap(self):
        record = example_record()
        screening = record["career_requirements_mapping"]["baseline_qualification_mapping"][1]
        self.assertEqual(screening["assessment"], "unknown")
        self.assertFalse(any("screen" in gap["requirement"].casefold()
                             for gap in record["career_requirements_mapping"]["meaningful_gaps"]))
        validate_shortlist_record(record)

    def test_transfer_requires_limitations_and_gap_can_disclose_missing_evidence(self):
        for fit_field, fit_value in (("capability_fit", "adjacent"), ("capability_fit", "transferable"),
                                     ("domain_context_fit", "adjacent"), ("domain_context_fit", "transferable"),
                                     ("domain_context_fit", "gap")):
            record = example_record()
            criterion = record["career_requirements_mapping"]["criteria"][0]
            criterion[fit_field] = fit_value
            with self.assertRaises(ValueError):
                validate_shortlist_record(record)
            criterion["limitation_or_difference"] = "Different scale and domain."
            validate_shortlist_record(record)
        record = example_record()
        criterion = record["career_requirements_mapping"]["criteria"][0]
        criterion.update(capability_fit="gap", domain_context_fit="gap", overall_fit_assessment="Material gap",
                         limitation_or_difference="No established evidence.",
                         strongest_evidence={"project_or_role": None, "evidence_summary": None, "measurable_outcomes": []})
        record["career_requirements_mapping"]["meaningful_gaps"] = [{
            "requirement": "Reporting ownership", "severity": "Material gap", "description": "No established evidence.",
            "closest_transferable_evidence": None, "fundamental_to_role": True}]
        validate_shortlist_record(record)

    def test_capability_and_domain_fit_combinations_are_independent(self):
        combinations = (("direct", "transferable"), ("direct", "direct"),
                        ("transferable", "direct"), ("gap", "direct"))
        for capability, domain in combinations:
            record = example_record()
            criterion = record["career_requirements_mapping"]["criteria"][0]
            criterion.update(capability_fit=capability, domain_context_fit=domain,
                             limitation_or_difference=(None if capability == domain == "direct"
                                                       else "Capability and domain assessed separately."))
            if capability == "gap":
                criterion["overall_fit_assessment"] = "Material gap"
                criterion["strongest_evidence"] = {"project_or_role": None, "evidence_summary": None,
                                                     "measurable_outcomes": []}
                record["career_requirements_mapping"]["meaningful_gaps"] = [{
                    "requirement": "Reporting ownership", "severity": "Material gap",
                    "description": "Capability is not established.", "closest_transferable_evidence": None,
                    "fundamental_to_role": True}]
            with self.subTest(capability=capability, domain=domain):
                validate_shortlist_record(record)

    def test_domain_gap_does_not_require_capability_gap(self):
        record = example_record()
        criterion = record["career_requirements_mapping"]["criteria"][0]
        criterion.update(capability_fit="direct", domain_context_fit="gap",
                         overall_fit_assessment="Strong transferable fit",
                         limitation_or_difference="Accounting domain is not established.")
        validate_shortlist_record(record)
        self.assertEqual(criterion["capability_fit"], "direct")

    def test_historical_v1_record_validates_without_rewrite(self):
        record = example_record()
        record["role_understanding"].pop("baseline_qualifications")
        record["career_requirements_mapping"].pop("baseline_qualification_mapping")
        record["schema_version"] = "1.0.0"
        criterion = record["career_requirements_mapping"]["criteria"][0]
        criterion["evidence_type"] = criterion.pop("capability_fit")
        criterion["fit_assessment"] = criterion.pop("overall_fit_assessment")
        criterion.pop("domain_context_fit")
        record["validation"]["direct_vs_transferable_check_passed"] = record["validation"].pop("capability_domain_fit_check_passed")
        before = copy.deepcopy(record)
        validate_shortlist_record(record)
        self.assertEqual(record, before)

    def test_historical_v11_record_validates_without_rewrite(self):
        record = example_record()
        record["schema_version"] = "1.1.0"
        record["role_understanding"].pop("baseline_qualifications")
        record["career_requirements_mapping"].pop("baseline_qualification_mapping")
        before = copy.deepcopy(record)
        validate_shortlist_record(record)
        self.assertEqual(record, before)

    def test_historical_v11_handoff_validates_without_rewrite(self):
        record = with_handoff()
        record["schema_version"] = "1.1.0"
        record["role_understanding"].pop("baseline_qualifications")
        record["career_requirements_mapping"].pop("baseline_qualification_mapping")
        record["handoff"]["role_state"].pop("baseline_qualifications")
        record["handoff"]["career_mapping_state"].pop("baseline_qualification_mapping")
        before = copy.deepcopy(record)
        validate_shortlist_record(record)
        self.assertEqual(record, before)

    def test_new_records_reject_legacy_evidence_field(self):
        record = example_record()
        criterion = record["career_requirements_mapping"]["criteria"][0]
        criterion["evidence_type"] = criterion.pop("capability_fit")
        with self.assertRaises(ValueError):
            validate_shortlist_record(record)

    def test_historical_v1_handoff_validates_without_rewrite(self):
        record = with_handoff()
        record["role_understanding"].pop("baseline_qualifications")
        record["career_requirements_mapping"].pop("baseline_qualification_mapping")
        record["handoff"]["role_state"].pop("baseline_qualifications")
        record["handoff"]["career_mapping_state"].pop("baseline_qualification_mapping")
        record["schema_version"] = "1.0.0"
        for criterion in (record["career_requirements_mapping"]["criteria"] +
                          record["handoff"]["career_mapping_state"]["criteria_mapping"]):
            criterion["evidence_type"] = criterion.pop("capability_fit")
            criterion["fit_assessment"] = criterion.pop("overall_fit_assessment")
            criterion.pop("domain_context_fit")
        for validation in (record["validation"], record["handoff"]["validation"]):
            validation["direct_vs_transferable_check_passed"] = validation.pop("capability_domain_fit_check_passed")
        state = record["handoff"]["career_mapping_state"]
        old_projection = []
        for row in state.pop("capability_domain_classification"):
            old_projection.append({"criterion_id": row["criterion_id"],
                                   "evidence_type": row["capability_fit"],
                                   "limitation_or_difference": row["limitation_or_difference"]})
        state["direct_vs_transferable_classification"] = old_projection
        before = copy.deepcopy(record)
        validate_shortlist_record(record)
        self.assertEqual(record, before)

    def test_handoff_exact_and_only_for_accepted_apply_outcomes(self):
        record = with_handoff()
        validate_shortlist_record(record)
        record["handoff"]["career_mapping_state"]["overall_evidence_summary"] = "Different story"
        with self.assertRaisesRegex(ValueError, "exactly preserve"):
            validate_shortlist_record(record)
        for outcome in ("HOLD / INVESTIGATE", "DO NOT APPLY"):
            record = with_handoff()
            record["shortlist_decision"]["decision"] = outcome
            record["handoff"]["shortlist_decision"]["decision"] = outcome
            with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                validate_shortlist_record(record)

    def test_cli_reads_only_and_does_not_claim_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"
            path.write_text(json.dumps(example_record()), encoding="utf-8")
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/shortlist_contract.py"),
                                     "--input", str(path)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("controller review remains required", result.stdout)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(temp).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
