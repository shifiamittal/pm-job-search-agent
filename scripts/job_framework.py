"""Canonical narrative job schema, review queue and recurring skill synthesis.

No numeric fit/priority score is accepted. A successful discovery writer calls
``persist_discovery_run``; dashboard failure never rolls back canonical data.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MASTER_FIELDS = [
    "job_id", "company", "company_brief", "role_title", "exact_level",
    "posting_date", "posting_date_source", "posting_date_confidence",
    "location", "country", "work_arrangement", "compensation", "currency",
    "sector", "role_domain", "domain_fit", "domain_requirement_strength",
    "domain_transfer_rationale", "technology_orientation", "role_cluster",
    "role_mandate", "key_functional_requirements", "hard_prerequisites",
    "candidate_relevant_evidence", "primary_gap", "gap_gating", "gap_rationale",
    "bridge_action", "bridge_timing", "strategic_skill_overlap",
    "skill_build_priority", "application_posture", "application_lane",
    "decision_rationale", "recommended_resume_variant",
    "recommended_portfolio_artifact", "canonical_url", "source", "status",
    "discovered_at", "last_verified_at", "application_status", "outreach_status",
    "user_review", "user_notes",
]
LEGACY_SCORE_FIELDS = {
    "experience_fit_score", "interview_probability_score", "level_fit_score",
    "compensation_fit_score", "career_capital_score", "location_fit_score",
    "priority_score", "normalized_level", "ai_classification", "hard_experience_gap",
}
REVIEW_FIELDS = [
    "job_id", "company", "role_title", "exact_level", "posting_date", "location",
    "work_arrangement", "compensation", "sector", "role_domain", "domain_fit",
    "technology_orientation", "application_posture", "application_lane", "primary_gap",
    "gap_gating", "bridge_action", "bridge_timing", "skill_build_priority",
    "decision_rationale", "recommended_resume_variant",
    "recommended_portfolio_artifact", "canonical_url", "last_verified_at",
    "user_review", "user_notes",
]
SKILL_FIELDS = [
    "skill", "role_count", "example_companies", "example_roles",
    "candidate_current_strength", "strategic_leverage", "recommended_action",
    "rationale",
]
SKILL_CATALOG = {
    "AI Evaluation Systems": ("Moderate", "High", "Build Now", "Deepen golden datasets, graders, judge calibration, regression gates and measurable reliability across agent products."),
    "Agent Orchestration and Reliability": ("Moderate", "High", "Build Now", "Extend existing Forecasting Agent designs into repeatable production-grade tool use, observability, safety and failure recovery stories."),
    "Developer-Facing AI APIs": ("Emerging", "High", "Build Now", "Build hands-on API/primitives fluency to widen access to senior agent-platform roles."),
    "AI Platform Fundamentals": ("Moderate", "High", "Build Now", "Extend enterprise and ML platform evidence into model serving, agent runtimes, evaluation integration and platform economics."),
    "AI Reliability / Observability / Quality": ("Moderate", "High", "Build Now", "Practice tracing, failure analysis, safety controls and quality monitoring for production-oriented AI products."),
    "RAG and Retrieval Quality": ("Moderate", "High", "Build Now", "Package Patent AI and agent retrieval work; deepen recall/ranking tradeoffs and reproducible evaluation."),
    "Hands-On AI Prototyping": ("Moderate", "High", "Build Now", "Show concrete Python/LLM API prototypes without claiming unverified production implementation."),
    "Enterprise Data Platform Architecture": ("Strong", "High", "Maintain / Package Better", "Keystone Data Platform already supports reusable data contracts, quality, lineage and enterprise integrations."),
    "Classical ML Productization": ("Strong", "Medium", "Maintain / Package Better", "Amazon ML Platform and supply-chain optimization provide current platform and model-lifecycle evidence."),
    "Financial Risk Decisioning": ("Strong", "Medium", "Maintain / Package Better", "Amazon Financial Services provides credit and decisioning evidence; translate it clearly into banking risk products."),
    "Supply-Chain Forecasting and Optimization": ("Strong", "Medium", "Maintain / Package Better", "Amazon Supply Chain and Keystone Forecasting Agent demonstrate planning and optimization context."),
    "Role-Specific Regulated Workflows": ("Emerging", "Low", "Interview Triggered", "Claims, treasury, receivables and healthcare details are learnable for an interview but not a general AI-PM study track."),
    "Specialist Database Internals": ("Limited", "Low", "Interview Triggered", "Study streaming concepts only for a progressing interview; do not substitute for required hands-on database engineering."),
    "PM People Management": ("Limited", "Low", "Do Not Build", "Formal PM management is not established in the evidence; do not divert an IC-focused search merely for isolated Group/Director roles."),
}


def taxonomy(root=ROOT):
    return yaml.safe_load((root / "config/role_taxonomy.yaml").read_text(encoding="utf-8-sig"))


def validate_job(job, values=None):
    values = values or taxonomy()
    missing = [key for key in MASTER_FIELDS if key not in job]
    if missing:
        raise ValueError(f"Missing canonical job fields: {', '.join(missing)}")
    if LEGACY_SCORE_FIELDS.intersection(job):
        raise ValueError("Legacy scores/normalized level/AI labels are not canonical fields")
    for key, allowed_key in [
        ("sector", "sectors"), ("role_cluster", "role_clusters"),
        ("technology_orientation", "technology_orientation"),
        ("domain_fit", "domain_fit"),
        ("domain_requirement_strength", "domain_requirement_strength"),
        ("primary_gap", "primary_gap"), ("gap_gating", "gap_gating"),
        ("bridge_timing", "bridge_timing"),
        ("strategic_skill_overlap", "strategic_skill_overlap"),
        ("skill_build_priority", "skill_build_priority"),
        ("application_posture", "application_posture"),
        ("application_lane", "application_lanes"),
        ("recommended_resume_variant", "resume_variants"),
        ("recommended_portfolio_artifact", "portfolio_artifacts"),
    ]:
        if job[key] not in values[allowed_key]:
            raise ValueError(f"Invalid {key} for {job['job_id']}: {job[key]}")
    if job["posting_date"] == "Not exposed":
        if job["posting_date_source"] != "Not exposed" or job["posting_date_confidence"] != "Unavailable":
            raise ValueError("Unknown posting date needs unavailable provenance")
    if job["compensation"] == "Not published" and job["currency"]:
        raise ValueError("Unpublished compensation must not imply currency")
    if job["status"] not in {"Live", "Closed", "Unverified"}:
        raise ValueError("Invalid live status")
    if job["status"] == "Closed" and job["application_lane"] != "Skip":
        raise ValueError("Closed jobs cannot be in an application lane")
    if job["application_lane"] == "Build Toward" and not (
        job["skill_build_priority"] == "Build Now" and job["strategic_skill_overlap"] == "High"
    ):
        raise ValueError("Build Toward requires a reusable high-leverage skill")
    if job["application_lane"] == "Apply Now + Bridge" and job["bridge_timing"] == "Before Application":
        raise ValueError("Apply Now + Bridge must not delay application")
    if len([part for part in job["key_functional_requirements"].split("; ") if part]) < 4:
        raise ValueError("Record at least four concrete JD functional requirements")
    if not str(job["canonical_url"]).startswith("https://") or not job["job_id"]:
        raise ValueError("Canonical HTTPS URL and stable job_id required")


def validate_jobs(jobs, root=ROOT):
    values = taxonomy(root)
    ids = set()
    for job in jobs:
        validate_job(job, values)
        if job["job_id"] in ids:
            raise ValueError(f"Duplicate job_id: {job['job_id']}")
        ids.add(job["job_id"])


def review_queue(jobs):
    order = {"Apply Now": 0, "Apply Now + Bridge": 1, "Build Toward": 2}
    candidates = [job for job in jobs if job["status"] == "Live" and job["application_lane"] in order]
    candidates.sort(key=lambda job: (order[job["application_lane"]],
                                     -int(job["posting_date"].replace("-", "") if job["posting_date"] != "Not exposed" else 0),
                                     job["company"].casefold(), job["job_id"]))
    return [{key: job[key] for key in REVIEW_FIELDS} for job in candidates]


def synthesize_skills(jobs):
    groups = defaultdict(list)
    for job in jobs:
        if job["status"] != "Live" or job["application_lane"] == "Skip":
            continue
        for tag in dict.fromkeys(job.get("skill_tags", [])):
            if tag not in SKILL_CATALOG:
                raise ValueError(f"Unknown normalized skill tag: {tag}")
            groups[tag].append(job)
    rows = []
    for skill, matches in groups.items():
        strength, leverage, action, rationale = SKILL_CATALOG[skill]
        rows.append({
            "skill": skill, "role_count": len(matches),
            "example_companies": "; ".join(dict.fromkeys(job["company"] for job in matches))[:250],
            "example_roles": "; ".join(job["role_title"] for job in matches[:3]),
            "candidate_current_strength": strength, "strategic_leverage": leverage,
            "recommended_action": action, "rationale": rationale,
        })
    rows.sort(key=lambda row: ({"High": 0, "Medium": 1, "Low": 2}[row["strategic_leverage"]],
                               -row["role_count"], row["skill"]))
    return rows


def _atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, suffix=".tmp", delete=False) as stream:
            temp = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def _csv_text(fields, rows):
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def persist_discovery_run(jobs, root=ROOT, sync=True, latest_new_count=0):
    """Finalization hook for a successful discovery/classification run.

    Local records are validated and written before dashboard sync. A dashboard
    failure is returned distinctly and leaves the canonical files intact.
    """
    validate_jobs(jobs, root)
    data = root / "data"
    skills = synthesize_skills(jobs)
    _atomic_text(data / "jobs_raw.jsonl", "".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs))
    _atomic_text(data / "jobs_master.csv", _csv_text(MASTER_FIELDS, jobs))
    _atomic_text(data / "review_queue.csv", _csv_text(REVIEW_FIELDS, review_queue(jobs)))
    _atomic_text(data / "skills_synthesis.csv", _csv_text(SKILL_FIELDS, skills))
    log = data / "discovery_log.csv"
    existing = list(csv.DictReader(log.open(encoding="utf-8", newline=""))) if log.exists() else []
    existing.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "event": "calibrated_discovery_finalized", "count": str(len(jobs)),
                     "notes": f"Local canonical data written; {latest_new_count} new jobs. Dashboard sync follows separately."})
    _atomic_text(log, _csv_text(["timestamp_utc", "event", "count", "notes"], existing))
    result = {"local_saved": True, "dashboard_synced": False, "dashboard_error": None,
              "jobs": len(jobs), "skills": len(skills)}
    if sync:
        try:
            from sync_job_dashboard import sync_dashboard
            sync_dashboard(root=root, latest_new_count=latest_new_count)
            result["dashboard_synced"] = True
        except Exception as exc:
            result["dashboard_error"] = f"{type(exc).__name__}: {exc}"
    return result


def load_canonical_jobs(root=ROOT):
    path = root / "data/jobs_raw.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
