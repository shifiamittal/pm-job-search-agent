"""Finish a successful future discovery run from a classified JSONL input.

Usage: python scripts/finalize_discovery.py --input path/to/classified_jobs.jsonl
The input contains canonical schema jobs, not search snippets. This is the
single write path: merge -> validate -> persist -> skill synthesis -> Sheet sync.
It performs no discovery, application, outreach or recurring scheduling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from job_framework import ROOT, load_canonical_jobs, persist_discovery_run, validate_jobs


def merge_jobs(existing, updates):
    by_id = {job["job_id"]: dict(job) for job in existing}
    new_count = 0
    for incoming in updates:
        job_id = incoming["job_id"]
        if job_id not in by_id:
            new_count += 1
            by_id[job_id] = dict(incoming)
            continue
        old = by_id[job_id]
        merged = dict(old)
        merged.update(incoming)
        for field in ("discovered_at", "initial_verified_at", "application_status",
                      "outreach_status", "user_review", "user_notes", "calibration_origin"):
            if not incoming.get(field) and old.get(field):
                merged[field] = old[field]
        by_id[job_id] = merged
    return list(by_id.values()), new_count


def finalize(updates, root=ROOT, sync=True):
    existing = load_canonical_jobs(root)
    jobs, new_count = merge_jobs(existing, updates)
    validate_jobs(jobs, root)
    return persist_discovery_run(jobs, root=root, sync=sync, latest_new_count=new_count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Fully classified canonical JSONL from a successful discovery run")
    args = parser.parse_args()
    updates = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not updates:
        parser.error("Input contains no classified jobs")
    result = finalize(updates)
    print(f"Canonical local data saved: {result['jobs']} jobs; {result['skills']} skill themes")
    if result["dashboard_error"]:
        print("Dashboard sync failed; local data remains saved. Rerun: python scripts/sync_job_dashboard.py")
        print(result["dashboard_error"])
    else:
        print("Persistent Google Sheet updated")


if __name__ == "__main__":
    main()
