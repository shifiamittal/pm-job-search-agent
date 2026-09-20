"""Apply the calibrated narrative framework to the 30 existing job IDs only.

The official postings and annotations were reviewed in the browser. This script
never discovers a new job or fetches a candidate source. Re-running it after
the migration preserves discovery metadata, job IDs, and review fields.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

import yaml

from job_framework import ROOT, load_canonical_jobs, persist_discovery_run

OFFICIAL_DATES = {
    "R-575564": "2026-09-17", "R-553892": "2026-09-14",
    "R-575654": "2026-09-15", "23749240": "2026-08-24",
    "JB0074880": "2026-08-26",
}
ANNOTATION_FIELDS = {
    "brief", "title", "level", "domain", "fit", "strength", "transfer", "technology",
    "mandate", "functions", "hard", "evidence", "gap", "gating", "gap_detail",
    "bridge", "timing", "overlap", "build", "posture", "lane", "decision", "skills",
}
OLD_LANES = {
    "APPLY NOW": "Apply Now", "APPLY + BRIDGE": "Apply Now + Bridge",
    "BUILD TOWARD": "Build Toward", "SKIP": "Skip",
}


def annotations(root=ROOT):
    result = yaml.safe_load((root / "data/calibration_annotations.yaml").read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("Calibration annotations must be a map by existing job ID")
    for job_id, record in result.items():
        if not isinstance(record, dict) or ANNOTATION_FIELDS - record.keys():
            raise ValueError(f"Incomplete annotation for {job_id}: {ANNOTATION_FIELDS - record.keys()}")
        if len(record["functions"]) < 4 or not record["skills"]:
            raise ValueError(f"Functional requirements or normalized skill tags missing for {job_id}")
    return result


def migrate_job(old, annotation, now):
    job_id = old["job_id"]
    if job_id in OFFICIAL_DATES:
        posted, posted_source, date_confidence = OFFICIAL_DATES[job_id], "Official employer JD", "High"
    elif old.get("posting_date") and old.get("posting_date") != "Not exposed":
        posted = old["posting_date"]
        posted_source = old.get("posting_date_source", "Official employer JD")
        date_confidence = old.get("posting_date_confidence", "High")
    else:
        posted, posted_source, date_confidence = "Not exposed", "Not exposed", "Unavailable"
    if old.get("compensation"):
        compensation, currency = old["compensation"], old.get("currency", "")
    elif old.get("comp_min") and old.get("comp_max"):
        currency = old.get("currency", "")
        compensation = f'{currency} {int(old["comp_min"]):,}–{int(old["comp_max"]):,} (published range)'
    else:
        compensation, currency = "Not published", ""
    old_status = old.get("status", "live_verified")
    status = "Closed" if old_status in {"closed", "Closed"} else "Live"
    lane = "Skip" if status == "Closed" else annotation["lane"]
    decision = ("Closed posting retained for calibration history." if status == "Closed"
                else annotation["decision"])
    return {
        "job_id": job_id, "company": old["company"], "company_brief": annotation["brief"],
        "role_title": annotation["title"], "exact_level": annotation["level"],
        "posting_date": posted, "posting_date_source": posted_source,
        "posting_date_confidence": date_confidence,
        "location": old["location"], "country": old["country"],
        "work_arrangement": old.get("work_arrangement", old.get("remote_or_hybrid", "Not exposed")),
        "compensation": compensation, "currency": currency,
        "sector": old["sector"], "role_domain": annotation["domain"],
        "domain_fit": annotation["fit"], "domain_requirement_strength": annotation["strength"],
        "domain_transfer_rationale": annotation["fit"] + ": " + annotation["transfer"],
        "technology_orientation": annotation["technology"], "role_cluster": old["role_cluster"],
        "role_mandate": annotation["mandate"],
        "key_functional_requirements": "; ".join(annotation["functions"]),
        "hard_prerequisites": annotation["hard"],
        "candidate_relevant_evidence": annotation["evidence"],
        "primary_gap": annotation["gap"], "gap_gating": annotation["gating"],
        "gap_rationale": annotation["gap_detail"], "bridge_action": annotation["bridge"],
        "bridge_timing": annotation["timing"], "strategic_skill_overlap": annotation["overlap"],
        "skill_build_priority": annotation["build"],
        "application_posture": "Skip" if status == "Closed" else annotation["posture"],
        "application_lane": lane, "decision_rationale": decision,
        "recommended_resume_variant": old["recommended_resume_variant"],
        "recommended_portfolio_artifact": old["recommended_portfolio_artifact"],
        "canonical_url": old["canonical_url"], "source": old["source"], "status": status,
        "discovered_at": old["discovered_at"], "last_verified_at": now,
        "application_status": old.get("application_status", "Not started"),
        "outreach_status": old.get("outreach_status", "Not started"),
        "user_review": old.get("user_review", ""), "user_notes": old.get("user_notes", ""),
        "skill_tags": annotation["skills"],
        "initial_verified_at": old.get("initial_verified_at", old.get("last_verified_at", "")),
        "verification_method": old.get("verification_method", "Official page checked in browser"),
        "calibration_origin": old.get("calibration_origin", "2026-09-19 initial discovery"),
    }


def reprocess(root=ROOT, now=None, sync=True):
    old_jobs = load_canonical_jobs(root)
    by_id = annotations(root)
    if {job["job_id"] for job in old_jobs} != set(by_id):
        raise ValueError("Annotations must match exactly the existing calibration job IDs")
    now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_jobs = [migrate_job(old, by_id[old["job_id"]], now) for old in old_jobs]
    # Preserve the first calibration-to-new-framework comparison on later runs.
    changes = root / "data/calibration_lane_changes.csv"
    if not changes.exists():
        with changes.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["job_id", "company", "role_title", "previous_lane", "calibrated_lane"])
            writer.writeheader()
            for old, new in zip(old_jobs, new_jobs):
                old_lane = OLD_LANES.get(old.get("application_lane", ""), old.get("application_lane", ""))
                if old_lane != new["application_lane"]:
                    writer.writerow({"job_id": new["job_id"], "company": new["company"],
                                     "role_title": new["role_title"], "previous_lane": old_lane,
                                     "calibrated_lane": new["application_lane"]})
    return persist_discovery_run(new_jobs, root=root, sync=sync, latest_new_count=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-sheet", action="store_true", help="Write and test local data before first dashboard authorization")
    args = parser.parse_args()
    result = reprocess(sync=not args.no_sheet)
    print(f"Local calibration: {result['jobs']} jobs; {result['skills']} skill themes")
    if result["dashboard_error"]:
        print("Dashboard sync failed; local canonical data preserved: " + result["dashboard_error"])
    elif result["dashboard_synced"]:
        print("Persistent dashboard synced")


if __name__ == "__main__":
    main()
