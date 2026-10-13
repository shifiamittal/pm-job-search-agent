"""Single-job orchestration and HTTP contract tests; no paid model calls."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from jsonschema import Draft202012Validator
import requests

from run_shortlist_job import (CANDIDATE_FILES, STAGES, RunError, _check_provenance,
                               _check_role_completeness, _controller_consistency,
                               main, normalize_input, run_job, stage_schema, validate_input)
from shortlist_contract import load_schema, validate_shortlist_record
from shortlist_model import ModelError, ResponsesModel
from test_shortlist_contract import example_record


CAPABILITY = "Owned reusable deployment APIs, launch approvals, rollback safeguards and adoption feedback for science teams."
CONFIRMED_CAPABILITY = "Led cross-functional product development across 20+ engineers and scientists."
DEGREE_EVIDENCE = "MBA and B.E. degrees; approved 11+ years of product experience."


def input_job(company="One Company", job_id="one"):
    return {"company": company, "job_id": job_id, "title": "Principal Product Manager",
            "location": "Remote US", "posted_date": "2026-09-30",
            "canonical_job_url": "https://example.com/jobs/" + job_id, "source": "Synthetic official fixture",
            "full_job_description_raw": "Synthetic full JD: own developer deployment APIs, rollout safeguards and scientist adoption. Required: platform PM ownership. Preferred: orchestration. " + company,
            "extra_metadata": {"keep": "original"}}


class FakeModel:
    model = "offline-test-double"

    def __init__(self, mutate=None):
        self.calls = []
        self.mutate = mutate

    def complete(self, **request):
        self.calls.append(deepcopy(request))
        stage, context = request["stage"], request["context"]
        identity = {key: context["input_job"].get(key) for key in ("company", "title", "job_id", "location", "work_model", "travel")}
        fixture = example_record()
        if stage == "role_understanding":
            output = fixture[stage]
            output["role_identity"] = identity
            output["actual_job_to_be_done"]["summary"] = "Own deployment capability at " + identity["company"]
        elif stage == "career_requirements_mapping":
            mapping = fixture[stage]
            mapping["criteria"][0]["role_requirement"] = "Own reusable developer deployment capabilities."
            mapping["criteria"][0]["strongest_evidence"] = {
                "project_or_role": "Synthetic ML Platform",
                "evidence_summary": "profile/career_evidence.md, Platform evidence: " + CAPABILITY +
                    " These reusable APIs and rollout decisions demonstrate the required platform ownership.",
                "measurable_outcomes": [],
            }
            mapping["criteria"][0]["limitation_or_difference"] = "No established fleet-scale ownership; profile/evidence_conflicts.md retains the unresolved boundary."
            mapping["baseline_qualification_mapping"][0]["evidence"] = DEGREE_EVIDENCE
            output = {"career_requirements_mapping": mapping, "evidence_provenance": [
                {"criterion_id": "reporting", "sources": [{"source_path": "profile/career_evidence.md", "quote": CAPABILITY,
                    "provenance_type": "source_validated"}]}],
                "baseline_qualification_provenance": [
                    {"qualification_id": "degree-experience", "sources": [{"source_path": "profile/candidate_profile.md",
                        "quote": DEGREE_EVIDENCE, "provenance_type": "source_validated"}]},
                    {"qualification_id": "background-check", "sources": []}]}
        elif stage == "shortlist_decision":
            output = fixture[stage]
            output["location_work_model"] = {key: identity[key] for key in ("location", "work_model", "travel")}
        else:
            output = {
                "validation": {key: True for key in fixture["validation"]},
                "check_rationales": {key: "Synthetic source and capability check completed." for key in fixture["validation"]},
                "evidence_checks": [{"criterion_id": "reporting", "checks": {key: True for key in load_schema()["$defs"]["evidence_check"]["properties"]},
                                     "rationale": "Specific deployment capability supported by the supplied excerpt."}],
                "specialist_requirement_checks": [{"requirement": "Shared semantics", "checks": {
                    "requirement_preserved": True, "evidence_grounded": True,
                    "assessment_supported": True, "limitations_preserved": True},
                    "rationale": "Specialist requirement was independently audited."}],
                "baseline_qualification_checks": [
                    {"qualification_id": "degree-experience", "checks": {
                        "qualification_preserved": True, "required_preferred_preserved": True,
                        "evidence_grounded": True, "assessment_supported": True,
                        "uncertainty_preserved": True}, "rationale": "Degree and duration evidence audited."},
                    {"qualification_id": "background-check", "checks": {
                        "qualification_preserved": True, "required_preferred_preserved": True,
                        "evidence_grounded": True, "assessment_supported": True,
                        "uncertainty_preserved": True}, "rationale": "Future screening remains unknown."}],
                "issues": [],
            }
        if self.mutate:
            self.mutate(stage, output)
        selected_model = request.get("model") or self.model
        return output, {"model": selected_model, "response_id": "synthetic", "usage": {
            "input_tokens": 100, "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 25, "output_tokens_details": {"reasoning_tokens": 5},
            "total_tokens": 125}}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "profile").mkdir()
        self.contents = {
            "profile/candidate_profile.md": "Candidate fixture, complete beginning.\r\n" + DEGREE_EVIDENCE + "\r\nComplete ending.\r\n",
            "profile/career_evidence.md": "# Platform evidence\n" + CAPABILITY + "\nEvidence tail MUST remain.\n",
            "profile/evidence_conflicts.md": "Ownership boundary unresolved: deployment APIs do not establish fleet-scale ownership.\nCONFLICTS TAIL\n",
            "profile/job_preferences.md": "Historic location scores are superseded; relocation willingness unknown.\nPREFERENCES TAIL\n",
            "profile/candidate_confirmed_facts.md": "Candidate-confirmed evidence, not documentary validation.\n" + CONFIRMED_CAPABILITY + "\nNot direct reports; preserve conflicts.\n",
        }
        for name, content in self.contents.items():
            (self.root / name).write_bytes(content.encode("utf-8"))

    def execute(self, model=None, job=None):
        model = model or FakeModel()
        directory = run_job(job or input_job(), model, output_root=self.root / "runs", candidate_root=self.root)
        return directory, json.loads((directory / "job_state.json").read_text(encoding="utf-8")), model

    def test_single_job_executes_four_stages_and_outputs_validate(self):
        directory, artifact, model = self.execute()
        self.assertEqual(artifact["completed_stages"], list(STAGES))
        self.assertEqual([call["stage"] for call in model.calls], list(STAGES))
        self.assertEqual(artifact["status"], "accepted")
        self.assertEqual(artifact["input_job"], input_job())
        validate_shortlist_record(artifact["shortlist_state"])
        Draft202012Validator(load_schema()).validate(artifact["shortlist_state"])
        self.assertEqual(json.loads((directory / "shortlist_state.json").read_text(encoding="utf-8")), artifact["shortlist_state"])
        review = (directory / "review.md").read_text(encoding="utf-8")
        for expected in ("One Company", "Principal Product Manager", CAPABILITY, "direct", "Meaningful gaps", "Scope:", "Controller accepted: **True**"):
            self.assertIn(expected, review)

    def test_progress_is_flushed_persisted_and_excludes_payloads(self):
        with patch("builtins.print") as console:
            directory, _, _ = self.execute()
        log = (directory / "progress.log").read_text(encoding="utf-8")
        self.assertIn("Models: Role Understanding=offline-test-double", log)
        self.assertIn("Job: One Company / Principal Product Manager", log)
        self.assertIn("Internal key: shortlist:", log)
        self.assertIn(str(directory), log)
        for number in range(1, 5):
            self.assertEqual(log.count(f"[{number}/4]"), 2)
        self.assertEqual(log.count("sending request..."), 4)
        self.assertEqual(log.count("(success)"), 4)
        self.assertNotIn(input_job()["full_job_description_raw"], log)
        self.assertNotIn(CAPABILITY, log)
        self.assertTrue(all(call.kwargs.get("flush") for call in console.call_args_list))

    def test_failure_and_interrupt_retain_partial_state_without_logging_secrets(self):
        for failure in (ModelError("SECRET PAYLOAD", error_type="ReadTimeout"),
                        ValueError("SECRET PAYLOAD"), KeyboardInterrupt("SECRET PAYLOAD")):
            with self.subTest(error=type(failure).__name__):
                def fail_mapping(stage, output):
                    if stage == "career_requirements_mapping":
                        raise failure
                expected = KeyboardInterrupt if isinstance(failure, KeyboardInterrupt) else RunError
                before = set((self.root / "runs").glob("*"))
                with redirect_stdout(io.StringIO()) as console, self.assertRaises(expected):
                    self.execute(FakeModel(fail_mapping))
                directory, = set((self.root / "runs").glob("*")) - before
                artifact = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
                self.assertEqual(artifact["completed_stages"], ["role_understanding"])
                self.assertIn("role_understanding", artifact["stage_outputs"])
                self.assertEqual(artifact["status"], "interrupted" if expected is KeyboardInterrupt else "failed")
                self.assertTrue((directory / "review.md").exists())
                self.assertFalse((directory / "shortlist_state.json").exists())
                log = (directory / "progress.log").read_text(encoding="utf-8")
                self.assertIn("[2/4] Career / Requirements Mapping", log)
                self.assertIn("ReadTimeout" if isinstance(failure, ModelError) else type(failure).__name__, log)
                self.assertNotIn("SECRET PAYLOAD", log + console.getvalue())

    def test_full_context_conflicts_and_specific_provenance_are_retained(self):
        _, artifact, model = self.execute()
        self.assertNotIn("candidate_context", model.calls[0]["context"])
        for call in model.calls[1:]:
            self.assertEqual(set(call["context"]["candidate_context"]), set(CANDIDATE_FILES))
            for name, text in self.contents.items():
                supplied = call["context"]["candidate_context"][name]
                self.assertEqual(supplied["content"], text)
                self.assertEqual(supplied["sha256"], hashlib.sha256(text.encode()).hexdigest())
        mapping = artifact["shortlist_state"]["career_requirements_mapping"]
        self.assertIn(CAPABILITY, mapping["criteria"][0]["strongest_evidence"]["evidence_summary"])
        self.assertEqual(mapping["criteria"][0]["strongest_evidence"]["project_or_role"], "Synthetic ML Platform")
        provenance = artifact["stage_outputs"]["career_requirements_mapping"]["evidence_provenance"]
        self.assertEqual(provenance[0]["sources"][0]["quote"], CAPABILITY)
        self.assertIn("profile/evidence_conflicts.md", mapping["criteria"][0]["limitation_or_difference"])
        for name, text in self.contents.items():
            self.assertEqual((self.root / name).read_bytes(), text.encode("utf-8"))

    def test_full_workflow_without_posting_url_or_source(self):
        for value in (None, "", "   ", "omitted"):
            job = input_job()
            if value == "omitted":
                job.pop("canonical_job_url")
                job.pop("source")
            else:
                job["canonical_job_url"] = value
                job["source"] = value
            with self.subTest(value=value):
                _, artifact, model = self.execute(job=job)
                self.assertEqual(artifact["status"], "accepted")
                self.assertEqual(artifact["input_job"], job)
                self.assertEqual(len(model.calls), 4)
                self.assertEqual(artifact["shortlist_state"]["job"]["jd_source"],
                                 "User-supplied full job description; posting URL not provided")
                validate_shortlist_record(artifact["shortlist_state"])

    def test_source_provenance_is_used_when_url_missing(self):
        job = input_job()
        job.pop("canonical_job_url")
        _, artifact, _ = self.execute(job=job)
        self.assertEqual(artifact["shortlist_state"]["job"]["jd_source"], job["source"])

    def test_only_three_required_fields_execute_with_stable_internal_key(self):
        job = {key: input_job()[key] for key in ("company", "title", "full_job_description_raw")}
        validate_input(job)
        first_dir, first, _ = self.execute(job=job)
        second_dir, second, _ = self.execute(job=job)
        self.assertNotEqual(first_dir, second_dir)
        self.assertEqual(first["internal_record_key"], second["internal_record_key"])
        self.assertEqual(first["input_job"], job)
        self.assertIsNone(first["normalized_job"]["canonical_job_url"])
        self.assertIsNone(first["shortlist_state"]["job"]["job_id"])
        self.assertIsNone(first["shortlist_state"]["job"]["location"])
        self.assertEqual(first["completed_stages"], list(STAGES))
        validate_shortlist_record(first["shortlist_state"])

    def test_internal_keys_are_stable_separate_from_external_ids(self):
        job = {"company": " Example Co ", "title": " HEAD of Product ", "full_job_description_raw": "Full JD", "row_identity": "source:row:1"}
        one = normalize_input(job)
        self.assertEqual(one, normalize_input(one))
        normalized_names = normalize_input({**job, "company": "example co", "title": "head OF product"})
        self.assertEqual(one["internal_record_key"], normalized_names["internal_record_key"])
        self.assertNotEqual(one["internal_record_key"], normalize_input({**job, "row_identity": "source:row:2"})["internal_record_key"])
        self.assertIsNone(one["job_id"])
        with_requisition = normalize_input({**job, "requisition_id": "REQ-1"})
        self.assertEqual(with_requisition["job_id"], "REQ-1")
        self.assertEqual(with_requisition["requisition_id"], "REQ-1")
        self.assertNotEqual(with_requisition["internal_record_key"], "REQ-1")
        self.assertEqual(normalize_input({**job, "job_id": "A", "requisition_id": "B"})["job_id"], "A")

    def test_separate_jobs_and_repeat_runs_have_isolated_state(self):
        model = FakeModel()
        first_dir, first, _ = self.execute(model, input_job("UNIQUE_FIRST", "1"))
        snapshot = (first_dir / "job_state.json").read_bytes()
        second_dir, second, _ = self.execute(model, input_job("UNIQUE_SECOND", "2"))
        repeat_dir, _, _ = self.execute(model, input_job("UNIQUE_SECOND", "2"))
        self.assertEqual(len({first_dir, second_dir, repeat_dir}), 3)
        self.assertEqual(snapshot, (first_dir / "job_state.json").read_bytes())
        self.assertNotIn("UNIQUE_FIRST", json.dumps(model.calls[4:]))
        self.assertNotIn("UNIQUE_FIRST", json.dumps(second))
        self.assertEqual(model.calls[4]["context"]["upstream"], {})
        self.assertNotEqual(first["run_id"], second["run_id"])

    def test_controller_rejection_preserves_decision_and_diagnostics(self):
        def reject(stage, output):
            if stage == "controller_validation":
                output["validation"]["semantic_validation_passed"] = False
                output["validation"]["shortlist_decision_accepted"] = False
                output["issues"] = [{"stage": "career_requirements_mapping", "description": "Ownership conflict not resolved in wording.",
                                     "required_action": "Preserve the ownership limitation and rerun."}]
        directory, artifact, _ = self.execute(FakeModel(reject))
        self.assertEqual(artifact["status"], "rejected")
        self.assertEqual(artifact["shortlist_state"]["shortlist_decision"]["decision"], "APPLY")
        validate_shortlist_record(artifact["shortlist_state"])
        self.assertIn("Correction needed", (directory / "review.md").read_text(encoding="utf-8"))

    def test_fabricated_quotes_and_missing_sources_stop_before_decision(self):
        for mode in ("fake", "missing"):
            def break_mapping(stage, output):
                if stage == "career_requirements_mapping":
                    if mode == "fake":
                        output["evidence_provenance"][0]["sources"][0]["quote"] = "Invented metric or capability"
                    elif mode == "missing":
                        output["evidence_provenance"][0]["sources"] = []
            model = FakeModel(break_mapping)
            with self.subTest(mode=mode), self.assertRaises(RunError) as caught:
                self.execute(model)
            directory = caught.exception.run_dir
            artifact = json.loads((directory / "job_state.json").read_text(encoding="utf-8"))
            self.assertEqual(artifact["status"], "failed")
            self.assertEqual(len(model.calls), 2)
            self.assertFalse((directory / "shortlist_state.json").exists())

    def test_structured_provenance_without_prose_paths_passes(self):
        def omit_paths(stage, output):
            if stage == "career_requirements_mapping":
                output["career_requirements_mapping"]["criteria"][0]["strongest_evidence"]["evidence_summary"] = CAPABILITY
                output["evidence_provenance"][0]["sources"][0]["quote"] = CAPABILITY.replace(" ", "\r\n  ")
        _, artifact, _ = self.execute(FakeModel(omit_paths))
        self.assertEqual(artifact["status"], "accepted")

    def test_candidate_confirmed_and_documentary_evidence_can_support_same_criterion(self):
        def add_confirmation(stage, output):
            if stage == "career_requirements_mapping":
                output["career_requirements_mapping"]["criteria"][0]["strongest_evidence"]["evidence_summary"] += (
                    " Candidate-confirmed evidence: " + CONFIRMED_CAPABILITY + " This is cross-functional leadership, not direct reports.")
                output["evidence_provenance"][0]["sources"].append({
                    "source_path": "profile/candidate_confirmed_facts.md", "quote": CONFIRMED_CAPABILITY,
                    "provenance_type": "candidate_confirmed"})
        _, artifact, model = self.execute(FakeModel(add_confirmation))
        self.assertEqual(artifact["status"], "accepted")
        for call in model.calls[1:]:
            self.assertEqual(call["context"]["candidate_context"]["profile/candidate_confirmed_facts.md"]["content"],
                             self.contents["profile/candidate_confirmed_facts.md"])
            self.assertEqual(call["context"]["candidate_context"]["profile/evidence_conflicts.md"]["content"],
                             self.contents["profile/evidence_conflicts.md"])
        sources = artifact["stage_outputs"]["career_requirements_mapping"]["evidence_provenance"][0]["sources"]
        self.assertEqual([source["provenance_type"] for source in sources], ["source_validated", "candidate_confirmed"])
        for call in model.calls[2:]:
            self.assertEqual(call["context"]["upstream"]["career_requirements_mapping"]["evidence_provenance"][0]["sources"], sources)

    def test_candidate_confirmed_evidence_alone_is_valid_without_documentary_confirmation(self):
        def use_confirmation(stage, output):
            if stage == "career_requirements_mapping":
                output["career_requirements_mapping"]["criteria"][0]["strongest_evidence"]["evidence_summary"] = CONFIRMED_CAPABILITY
                output["evidence_provenance"][0]["sources"] = [{
                    "source_path": "profile/candidate_confirmed_facts.md", "quote": CONFIRMED_CAPABILITY,
                    "provenance_type": "candidate_confirmed"}]
        _, artifact, _ = self.execute(FakeModel(use_confirmation))
        self.assertEqual(artifact["status"], "accepted")

    def test_candidate_confirmed_provenance_rejects_false_type_and_invented_quote(self):
        for mode in ("false_type", "missing_type", "invented_quote"):
            def bad_confirmation(stage, output):
                if stage == "career_requirements_mapping":
                    source = {"source_path": "profile/candidate_confirmed_facts.md",
                              "quote": CONFIRMED_CAPABILITY, "provenance_type": "candidate_confirmed"}
                    if mode == "false_type":
                        source["provenance_type"] = "source_validated"
                    elif mode == "missing_type":
                        source.pop("provenance_type")
                    else:
                        source["quote"] = "Managed 20 direct reports."
                    output["evidence_provenance"][0]["sources"] = [source]
            with self.subTest(mode=mode), self.assertRaises(RunError) as caught:
                self.execute(FakeModel(bad_confirmation))
            artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
            self.assertEqual(artifact["completed_stages"], ["role_understanding"])

    def test_candidate_confirmed_synthesis_excerpt_cannot_be_promoted(self):
        content = ("Documentary evidence.\n\nCandidate-confirmed evidence: " + CONFIRMED_CAPABILITY +
                   " Not direct reports.\n\nMore documentary evidence.")
        candidate = {"profile/career_evidence.md": {"content": content}}
        mapping = {"criteria": [{"criterion_id": "leadership", "capability_fit": "direct",
                                 "domain_context_fit": "not_applicable",
                                 "strongest_evidence": {"evidence_summary": CONFIRMED_CAPABILITY}}]}
        for quote in (CONFIRMED_CAPABILITY, CONFIRMED_CAPABILITY.replace(" ", "\r\n "),
                      "Not direct reports.\n\nMore documentary evidence."):
            provenance = [{"criterion_id": "leadership", "sources": [{
                "source_path": "profile/career_evidence.md", "quote": quote,
                "provenance_type": "candidate_confirmed"}]}]
            with self.subTest(quote=quote):
                _check_provenance(mapping, provenance, candidate)
                provenance[0]["sources"][0]["provenance_type"] = "source_validated"
                with self.assertRaisesRegex(ValueError, "must be candidate_confirmed"):
                    _check_provenance(mapping, provenance, candidate)

    def test_confirmations_do_not_bypass_controller_conflict_checks(self):
        def inflate_confirmation(stage, output):
            if stage == "career_requirements_mapping":
                output["career_requirements_mapping"]["criteria"][0]["strongest_evidence"]["evidence_summary"] = "Managed 20 direct reports."
                output["evidence_provenance"][0]["sources"] = [{
                    "source_path": "profile/candidate_confirmed_facts.md", "quote": CONFIRMED_CAPABILITY,
                    "provenance_type": "candidate_confirmed"}]
            elif stage == "controller_validation":
                output["validation"]["semantic_validation_passed"] = False
                output["validation"]["shortlist_decision_accepted"] = False
                output["issues"] = [{"stage": "career_requirements_mapping",
                    "description": "Cross-functional leadership does not establish direct reports.",
                    "required_action": "Retain the candidate-confirmed ownership limit and conflicts."}]
        _, artifact, _ = self.execute(FakeModel(inflate_confirmation))
        self.assertEqual(artifact["status"], "rejected")

    def test_structural_provenance_rejects_missing_invalid_and_misassigned_sources(self):
        mapping = {"criteria": [{"criterion_id": "capability", "capability_fit": "direct",
                                "domain_context_fit": "not_applicable",
                                "strongest_evidence": {"evidence_summary": CAPABILITY}}]}
        provenance = [{"criterion_id": "capability", "sources": [
            {"source_path": "profile/career_evidence.md", "quote": CAPABILITY, "provenance_type": "source_validated"}]}]
        candidate = {name: {"content": content} for name, content in self.contents.items()}
        for mode in ("missing", "empty_sources", "invalid_path", "unsupplied_path", "invented_quote",
                     "blank_quote", "wrong_criterion", "duplicate_criterion"):
            rows = deepcopy(provenance)
            supplied = deepcopy(candidate)
            if mode == "missing":
                rows = []
            elif mode == "empty_sources":
                rows[0]["sources"] = []
            elif mode == "invalid_path":
                rows[0]["sources"][0]["source_path"] = "other.md"
                supplied["other.md"] = {"content": CAPABILITY}
            elif mode == "unsupplied_path":
                supplied.pop("profile/career_evidence.md")
            elif mode == "invented_quote":
                rows[0]["sources"][0]["quote"] = "Invented ownership"
            elif mode == "blank_quote":
                rows[0]["sources"][0]["quote"] = " \n "
            elif mode == "wrong_criterion":
                rows[0]["criterion_id"] = "unrelated"
            else:
                rows.append(deepcopy(rows[0]))
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                _check_provenance(mapping, rows, supplied)

    def test_controller_rejects_unsupported_direct_capability_claim(self):
        def reject_wrong_claim(stage, output):
            if stage == "career_requirements_mapping":
                # A real quote and matching ID do not establish semantic support.
                output["career_requirements_mapping"]["criteria"][0]["strongest_evidence"]["evidence_summary"] = "Owned unrelated clinical trials."
            elif stage == "controller_validation":
                output["validation"]["semantic_validation_passed"] = False
                output["validation"]["shortlist_decision_accepted"] = False
                output["issues"] = [{"stage": "career_requirements_mapping",
                    "description": "Deployment API quote does not support the clinical-trial claim.",
                    "required_action": "Correct the evidence mapping."}]
        _, artifact, model = self.execute(FakeModel(reject_wrong_claim))
        self.assertEqual(len(model.calls), 4)
        self.assertEqual(artifact["status"], "rejected")
        criterion = artifact["stage_outputs"]["career_requirements_mapping"]["career_requirements_mapping"]["criteria"][0]
        self.assertEqual((criterion["capability_fit"], criterion["domain_context_fit"]), ("direct", "direct"))

    def test_controller_rejects_capability_downgrade_based_only_on_domain_gap(self):
        def reject_conflation(stage, output):
            if stage == "career_requirements_mapping":
                criterion = output["career_requirements_mapping"]["criteria"][0]
                criterion.update(capability_fit="transferable", domain_context_fit="gap",
                                 overall_fit_assessment="Strong transferable fit",
                                 limitation_or_difference="Only the target industry differs; the capability is directly demonstrated.")
            elif stage == "controller_validation":
                output["validation"]["capability_domain_fit_check_passed"] = False
                output["validation"]["shortlist_decision_accepted"] = False
                output["issues"] = [{"stage": "career_requirements_mapping",
                    "description": "Capability was downgraded solely because the target domain differs.",
                    "required_action": "Classify capability and domain/context independently."}]
        _, artifact, _ = self.execute(FakeModel(reject_conflation))
        self.assertEqual(artifact["status"], "rejected")
        self.assertFalse(artifact["controller_review"]["validation"]["capability_domain_fit_check_passed"])

    def test_controller_cannot_accept_failed_evidence_checks(self):
        def bad_controller(stage, output):
            if stage == "controller_validation":
                output["evidence_checks"][0]["checks"]["evidence_source_exists"] = False
        with self.assertRaises(RunError) as caught:
            self.execute(FakeModel(bad_controller))
        artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
        self.assertFalse(artifact["shortlist_state"]["validation"]["shortlist_decision_accepted"])

    def test_controller_audits_each_category_exactly_once(self):
        collections = {
            "evidence_checks": {"criterion_id": "extra"},
            "specialist_requirement_checks": {"requirement": "Extra specialty"},
            "baseline_qualification_checks": {"qualification_id": "extra"},
        }
        for collection, replacement in collections.items():
            for mode in ("missing", "duplicate", "extra"):
                def mutate(stage, output, collection=collection, replacement=replacement, mode=mode):
                    if stage != "controller_validation":
                        return
                    if mode == "missing":
                        output[collection].pop()
                    elif mode == "duplicate":
                        output[collection].append(deepcopy(output[collection][0]))
                    else:
                        extra = deepcopy(output[collection][0])
                        extra.update(replacement)
                        output[collection].append(extra)
                with self.subTest(collection=collection, mode=mode), self.assertRaises(RunError):
                    self.execute(FakeModel(mutate))

    def test_baseline_provenance_is_required_for_supported_claims(self):
        def remove_baseline_source(stage, output):
            if stage == "career_requirements_mapping":
                output["baseline_qualification_provenance"][0]["sources"] = []
        with self.assertRaises(RunError):
            self.execute(FakeModel(remove_baseline_source))

    def test_prompts_separate_baseline_qualifications_and_forbid_date_inference(self):
        _, _, model = self.execute(FakeModel())
        role_prompt = next(call["instructions"] for call in model.calls if call["stage"] == "role_understanding")
        mapping_prompt = next(call["instructions"] for call in model.calls if call["stage"] == "career_requirements_mapping")
        self.assertIn("minimum experience duration", role_prompt)
        self.assertIn("mandatory screening/background check", role_prompt)
        self.assertIn("Preserve preferred qualifications as preferred", role_prompt)
        self.assertIn("Do not infer credentials or missing employment periods", mapping_prompt)

    def test_required_degree_years_and_equivalent_experience_cannot_be_omitted(self):
        job = input_job()
        job["full_job_description_raw"] = (
            "Qualifications\nBachelor's Degree AND 8+ years experience in product/service/program "
            "management or software development\nOR equivalent experience.\nPreferred Qualifications\n"
            "Bachelor's Degree and 12+ years preferred."
        )
        _check_role_completeness(example_record()["role_understanding"], job)

        for mode in ("missing", "drops_equivalent"):
            def mutate(stage, output, mode=mode):
                if stage == "role_understanding":
                    if mode == "missing":
                        output["baseline_qualifications"] = output["baseline_qualifications"][1:]
                    else:
                        output["baseline_qualifications"][0]["requirement"] = "Bachelor's degree and 8+ years."
            with self.subTest(mode=mode), self.assertRaises(RunError) as caught:
                self.execute(FakeModel(mutate), job)
            artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
            self.assertEqual(artifact["completed_stages"], [])
            self.assertIn("equivalent-experience qualification", artifact["error"]["message"])

    def test_required_and_preferred_baselines_remain_distinct(self):
        role = deepcopy(example_record()["role_understanding"])
        role["baseline_qualifications"].append({
            "qualification_id": "preferred-advanced-degree",
            "requirement": "Advanced degree preferred.",
            "requirement_type": "education",
            "required_or_preferred": "preferred",
            "notes": "Explicit preferred qualification.",
        })
        self.assertEqual(role["baseline_qualifications"][0]["required_or_preferred"], "required")
        self.assertEqual(role["baseline_qualifications"][-1]["required_or_preferred"], "preferred")
        Draft202012Validator(stage_schema(load_schema(), "role_understanding")).validate(role)

    def test_specialists_never_appear_as_extra_evidence_criterion_ids(self):
        def add_specialist_as_criterion(stage, output):
            if stage == "controller_validation":
                extra = deepcopy(output["evidence_checks"][0])
                extra["criterion_id"] = "Shared semantics"
                output["evidence_checks"].append(extra)
        with self.assertRaises(RunError) as caught:
            self.execute(FakeModel(add_specialist_as_criterion))
        artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
        self.assertIn("hiring criterion exactly once", artifact["error"]["message"])

    def test_controller_can_report_specialist_omission_without_structural_failure(self):
        fixture = example_record()
        report = FakeModel().complete(stage="controller_validation", context={"input_job": input_job()},
                                      instructions="", output_schema={})[0]
        report["validation"]["career_mapping_complete"] = False
        report["validation"]["shortlist_decision_accepted"] = False
        report["specialist_requirement_checks"][0]["checks"]["evidence_grounded"] = False
        report["issues"] = [{"stage": "career_requirements_mapping",
                             "description": "Specialist requirement is unmapped.",
                             "required_action": "Map the missing specialist requirement."}]
        _check_shape = Draft202012Validator(stage_schema(load_schema(), "controller_validation")).validate
        _check_shape(report)
        _controller_consistency(report, fixture["role_understanding"], fixture["career_requirements_mapping"])

    def test_controller_can_reject_missing_mandatory_qualification_without_schema_failure(self):
        fixture = example_record()
        fixture["role_understanding"]["baseline_qualifications"] = []
        fixture["career_requirements_mapping"]["baseline_qualification_mapping"] = []
        report = FakeModel().complete(stage="controller_validation", context={"input_job": input_job()},
                                      instructions="", output_schema={})[0]
        report["validation"]["role_understanding_complete"] = False
        report["validation"]["career_mapping_complete"] = False
        report["validation"]["shortlist_decision_accepted"] = False
        report["baseline_qualification_checks"] = []
        report["issues"] = [{"stage": "role_understanding",
                             "description": "Explicit mandatory degree and experience qualification was omitted.",
                             "required_action": "Rerun Role Understanding and downstream stages."}]
        Draft202012Validator(stage_schema(load_schema(), "controller_validation")).validate(report)
        _controller_consistency(report, fixture["role_understanding"], fixture["career_requirements_mapping"])

    def test_malformed_stage_and_missing_mapping_fail_without_fabricating_decision(self):
        for stage_name in ("role_understanding", "career_requirements_mapping"):
            def bad(stage, output):
                if stage == stage_name:
                    if stage == "role_understanding":
                        output.pop("actual_scope")
                    else:
                        output["career_requirements_mapping"]["criteria"][0]["criterion_id"] = "unmatched"
                        output["evidence_provenance"][0]["criterion_id"] = "unmatched"
            with self.subTest(stage=stage_name), self.assertRaises(RunError) as caught:
                self.execute(FakeModel(bad))
            artifact = json.loads((caught.exception.run_dir / "job_state.json").read_text(encoding="utf-8"))
            self.assertEqual(artifact["status"], "failed")
            self.assertFalse((caught.exception.run_dir / "shortlist_state.json").exists())

    def test_batch_missing_jd_or_missing_source_rejected_before_model_call(self):
        model = FakeModel()
        for job in ([input_job()], {**input_job(), "full_job_description_raw": ""}):
            with self.assertRaises(ValueError):
                run_job(job, model, output_root=self.root / "runs", candidate_root=self.root)
        (self.root / CANDIDATE_FILES[-1]).unlink()
        with self.assertRaises(OSError):
            run_job(input_job(), model, output_root=self.root / "runs", candidate_root=self.root)
        self.assertEqual(model.calls, [])
        self.assertFalse((self.root / "runs").exists())

    def test_cli_single_job_invocation_without_real_api(self):
        path = self.root / "input.json"
        path.write_text(json.dumps(input_job()), encoding="utf-8")
        # CLI uses the real orchestrator, with candidate test root injected only here.
        def local_run(job, model, **kwargs):
            return run_job(job, model, candidate_root=self.root, **kwargs)
        with patch("sys.argv", ["run_shortlist_job.py", "--input", str(path), "--model", "test-model", "--output-root", str(self.root / "runs")]), \
             patch("run_shortlist_job.ResponsesModel", return_value=FakeModel()), \
             patch("run_shortlist_job.run_job", side_effect=local_run):
            main()
        self.assertEqual(len(list((self.root / "runs").glob("*/shortlist_state.json"))), 1)


class TransportTests(unittest.TestCase):
    def invoke(self, body=None, status=200):
        response = Mock(status_code=status)
        response.json.return_value = body or {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"ok": true}'}]}]}
        with patch("shortlist_model.requests.post", return_value=response) as post:
            result = ResponsesModel("selected-model", api_key="TEST-SECRET").complete(
                stage="role_understanding", instructions="Return JSON", context={"job": "one"},
                output_schema={"type": "object", "properties": {"ok": {"type": "boolean"}},
                               "required": ["ok"], "additionalProperties": False})
        return result, post.call_args

    def test_stateless_request_has_no_tools_history_or_auto_truncation(self):
        result, call = self.invoke()
        payload = call.kwargs["json"]
        self.assertEqual(result[0], {"ok": True})
        self.assertEqual(payload["model"], "selected-model")
        self.assertFalse(payload["store"])
        self.assertEqual(payload["truncation"], "disabled")
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])
        for forbidden in ("previous_response_id", "conversation", "tools"):
            self.assertNotIn(forbidden, payload)
        self.assertFalse(call.kwargs["allow_redirects"])

    def test_refusal_incomplete_malformed_and_http_fail_closed(self):
        for body in ({"status": "incomplete"},
                     {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]},
                     {"status": "completed", "output": []}):
            with self.subTest(body=body), self.assertRaises(ModelError):
                self.invoke(body)
        with self.assertRaises(ModelError) as caught:
            self.invoke(status=401)
        self.assertNotIn("TEST-SECRET", str(caught.exception))
        self.assertEqual(caught.exception.error_type, "HTTP 401")

    def test_explicit_model_and_key_required(self):
        with self.assertRaises(ValueError):
            ResponsesModel(None, api_key="test")
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
            ResponsesModel("selected-model")
        with patch("shortlist_model.requests.post", side_effect=requests.Timeout("SECRET BODY")), self.assertRaises(ModelError) as caught:
            ResponsesModel("selected-model", api_key="key").complete(stage="role", instructions="JSON", context={}, output_schema={})
        self.assertNotIn("SECRET BODY", str(caught.exception))
        self.assertEqual(caught.exception.error_type, "Timeout")


if __name__ == "__main__":
    unittest.main()
