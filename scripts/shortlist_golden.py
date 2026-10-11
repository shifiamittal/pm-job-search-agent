"""Read-only versioned Golden Set validation. References are not shortlist runtime states."""
import csv
import hashlib
import json
import re
from pathlib import Path

from shortlist_contract import load_schema
from run_shortlist_job import normalize_input

DIMENSIONS = ("role_understanding_completeness", "career_mapping_correctness",
              "capability_domain_correctness", "gap_preservation", "decision_alignment")
EXCEPTION = "cisco_2023232_2026-10-11"
DEFAULT_DATA = Path(__file__).resolve().parents[1] / "evals/shortlist/golden/v1_2"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def fingerprint(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(Path(root).rglob("*")) if p.is_file()}


def source_text(root, case):
    embedded = [v for v in (case.get("full_job_description_raw"),
                case.get("job", {}).get("full_job_description_raw")) if isinstance(v, str) and v.strip()]
    if len(set(embedded)) > 1:
        raise ValueError("Conflicting embedded JDs")
    if embedded:
        return embedded[0]
    source = case.get("source_job", {})
    name = source.get("exact_jd_file")
    if not isinstance(name, str) or not name:
        raise ValueError("Missing frozen JD: no embedded text or source reference")
    # v1.1 used basenames; v1.2 uses sources/<basename>. Accept only these shapes.
    relative = name.removeprefix("sources/")
    if Path(relative).name != relative or "/" in relative or "\\" in relative or relative in (".", ".."):
        raise ValueError("Source reference must be a local basename or sources/<basename>")
    path = Path(root) / "sources" / relative
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("Source reference escapes frozen package")
    if not path.is_file():
        raise ValueError("Missing frozen source file: " + name)
    raw = path.read_bytes()
    if digest(raw) != source.get("sha256"):
        raise ValueError("Frozen source SHA-256 mismatch: " + name)
    text = raw.decode("utf-8-sig")
    if not text.strip():
        raise ValueError("Frozen JD is empty")
    return text


def input_job(root, case):
    metadata = case.get("job", {})
    return normalize_input({"company": case["company"], "job_id": case.get("job_id"),
        "title": case["title"], "location": metadata.get("location"),
        "work_model": metadata.get("work_model"), "travel": metadata.get("travel"),
        "canonical_job_url": metadata.get("canonical_url"), "source": "frozen Golden Set",
        "row_identity": case["case_id"], "full_job_description_raw": source_text(root, case)})


def validate_dataset(root=DEFAULT_DATA, *, expected_count=12):
    root = Path(root)
    candidates = list(root.glob("shortlist_golden_v*.json"))
    if len(candidates) != 1:
        raise ValueError("Expected exactly one versioned golden dataset JSON")
    dataset = read_json(candidates[0])
    errors, warnings, reports = [], [], []
    schema = load_schema()
    mapping = schema["$defs"]["criterion_mapping"]["properties"]
    decisions = schema["$defs"]["shortlist_decision"]["properties"]["decision"]["enum"]
    cases = dataset.get("cases", [])
    if dataset.get("version") not in ("1.1.0", "1.2.0") or not isinstance(cases, list) or len(cases) != expected_count:
        errors.append(f"Expected supported version 1.1.0/1.2.0 and {expected_count} cases")
    if dataset.get("judge_dimensions") != list(DIMENSIONS):
        errors.append("Exactly the five agreed judge dimensions are required")
    seen_ids, seen_jobs = set(), set()
    for case in cases:
        cid = case.get("case_id", "")
        issues = []
        if not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in seen_ids:
            errors.append("Invalid or duplicate case_id: " + str(cid))
        seen_ids.add(cid)
        for field in ("company", "title"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                errors.append(f"{cid}: missing {field}")
        pair = (str(case.get("company", "")).strip().casefold(), case.get("job_id"))
        if pair[1]:
            if pair in seen_jobs and not case.get("intentional_duplicate_reason"):
                errors.append(f"{cid}: duplicate company/job ID")
            seen_jobs.add(pair)
        if case.get("golden_status") != "frozen":
            errors.append(f"{cid}: golden_status must be frozen")
        ref = case.get("reference", {})
        for key in ("actual_job_to_be_done", "scope_assessment"):
            if not isinstance(ref.get(key), str) or not ref[key].strip():
                errors.append(f"{cid}: missing reference {key}")
        for key in ("material_requirements",):
            if not isinstance(ref.get(key), list) or not all(isinstance(v, str) and v.strip() for v in ref[key]):
                errors.append(f"{cid}: invalid reference {key}")
        gaps = ref.get("meaningful_gaps")
        if not isinstance(gaps, list) or not all(
            isinstance(v, str) and bool(v.strip()) or isinstance(v, dict)
            and isinstance(v.get("gap"), str) and bool(v["gap"].strip())
            and isinstance(v.get("severity"), str) and bool(v["severity"].strip())
            and isinstance(v.get("fundamental_to_role"), bool) for v in gaps):
            errors.append(f"{cid}: invalid reference meaningful_gaps")
        if not ref.get("material_requirements"):
            errors.append(f"{cid}: material requirements must not be empty")
        if ref.get("shortlist_decision") not in decisions:
            errors.append(f"{cid}: invalid reference decision")
        expectations = ref.get("capability_domain_expectations")
        if not isinstance(expectations, list) or not expectations:
            errors.append(f"{cid}: missing capability/domain expectations")
        for row in expectations or []:
            if not (row.get("capability") or row.get("criterion")):
                errors.append(f"{cid}: missing capability name")
            for optional in ("overall_fit_assessment", "limitation_or_difference"):
                if optional in row and (not isinstance(row[optional], str) or not row[optional].strip()):
                    errors.append(f"{cid}: invalid {optional}")
            for key in ("capability_fit", "domain_context_fit"):
                if row.get(key) not in mapping[key]["enum"]:
                    errors.append(f"{cid}: invalid {key}")
        review = case.get("human_review")
        if review and (review.get("human_approved") is not True or review.get("approved_decision") != ref.get("shortlist_decision")):
            errors.append(f"{cid}: human approval conflicts with reference")
        if not review:
            warnings.append(f"{cid}: approval provenance is the supplied frozen dataset; no separate per-case review metadata")
        partial = case.get("strict_jd_fidelity", True) is False
        if partial and (cid != EXCEPTION or pair != ("cisco", "2023232")):
            errors.append(f"{cid}: unapproved strict-JD exception")
        if cid == EXCEPTION:
            policy = dataset.get("evaluation_policy", {}).get("strict_jd_fidelity_exception", {})
            if not partial or policy.get("case_id") != cid or policy.get("provisional") != [DIMENSIONS[0]]:
                errors.append("Cisco 2023232 provisional exception must be preserved")
        try:
            job = input_job(root, case)
            size = len(job["full_job_description_raw"])
        except (ValueError, OSError, UnicodeError) as exc:
            issues.append(str(exc)); size = 0
        reports.append({"case_id": cid, "runnable": not issues, "blockers": issues,
            "jd_characters": size, "strict_jd_fidelity": not partial,
            "role_understanding_status": "PROVISIONAL" if partial else "NOT_EVALUATED"})
    with (root / "index.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(cases) or {r["case_id"] for r in rows} != seen_ids:
        errors.append("index.csv case coverage differs from JSON")
    for case in cases:
        row = next((r for r in rows if r["case_id"] == case.get("case_id")), {})
        expected = {"company": case.get("company"), "title": case.get("title"),
            "job_id": case.get("job_id") or "", "decision": case.get("reference", {}).get("shortlist_decision"),
            "golden_status": case.get("golden_status"), "strict_jd_fidelity": str(case.get("strict_jd_fidelity", True))}
        if any(row.get(k) != v for k, v in expected.items()):
            errors.append(f"{case.get('case_id')}: index differs from frozen JSON")
    hashes = fingerprint(root)
    manifest = read_json(root / "integrity.json")
    if dataset.get("version") == "1.2.0":
        sources = manifest.get("sources", {})
        mapped = []
        for case in cases:
            source = case.get("source_job", {})
            name = source.get("exact_jd_file", "")
            mapped.append(name)
            entry = sources.get(name.removeprefix("sources/"), {})
            raw_path = root / name
            if not name.startswith("sources/") or name.count("/") != 1 or "\\" in name:
                errors.append(f"{case.get('case_id')}: invalid v1.2 source mapping")
                continue
            if (not raw_path.is_file() or not raw_path.resolve().is_relative_to(root.resolve())
                    or entry.get("sha256") != source.get("sha256")
                    or entry.get("sha256") != hashes.get(name)
                    or entry.get("bytes") != raw_path.stat().st_size
                    or entry.get("status") != source.get("source_status")
                    or entry.get("origin") != source.get("origin")):
                errors.append(f"{case.get('case_id')}: source manifest mapping/hash/bytes/provenance mismatch")
            if source.get("source_status") == "official_same_job_id_recovered":
                warnings.append(f"{case.get('case_id')}: supplied official same-job-ID recovery, not a historical byte-for-byte snapshot")
        if len(set(mapped)) != len(cases) or set(mapped) != {"sources/" + n for n in sources}:
            errors.append("Source manifest must map one unique source to every case")
        package = read_json(root / "package_integrity.json")
        if package.get("files") != {k: v for k, v in hashes.items() if k != "package_integrity.json"}:
            errors.append("Frozen package changed from integrity manifest")
    elif manifest.get("files") != {k: v for k, v in hashes.items() if k != "integrity.json"}:
        errors.append("Frozen package changed from integrity manifest")
    return dataset, {"references_valid": not errors, "all_runnable": not errors and all(r["runnable"] for r in reports),
        "case_count": len(cases), "runnable_count": sum(r["runnable"] for r in reports),
        "errors": errors, "warnings": warnings, "cases": reports, "fingerprint": hashes}
