#!/usr/bin/env python3
"""Run raw job discovery for configured sources.

Greenhouse, Ashby, Microsoft and Workday use deterministic retrieval. Each invocation crawls one
source and preserves the other sources in the latest combined exports.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from discovery.filters import pm_candidate_decision
from discovery.geography import classify_geography, enrich_geography, geography_summary
from discovery.greenhouse import fetch_greenhouse_jobs
from discovery.ashby import fetch_ashby_jobs
from discovery.workday import fetch_workday_jobs
from discovery.microsoft import fetch_microsoft_jobs, is_internship
from discovery.errors import CrawlError
from discovery.models import utc_now_iso, validate_raw_jobs
from discovery.io import append_jsonl, atomic_jsonl, load_job_sources, write_csv


def retain_candidate(job: dict) -> bool:
    """Apply the deterministic geography gate before the PM-family filter."""
    if not classify_geography(job)["geography_in_scope"]:
        return False
    if not pm_candidate_decision(job["title"])[0]:
        return False
    return (job["source_type"] != "microsoft" or
            (job.get("availability_status") == "available"
             and not is_internship(job["title"], job.get("employment_type", ""))))


def run(source_keys: list[str] | None = None, root: Path = ROOT) -> dict:
    sources = load_job_sources(root / "config/job_sources.yaml")
    selected = list(dict.fromkeys(source_keys or [key for key, value in sources.items() if value.get("enabled", True)]))
    # Keep explicit single-source execution; latest exports preserve other boards.
    if len(selected) != 1:
        raise ValueError("Discovery V1 requires exactly one source")
    key = selected[0]
    if key not in sources or not sources[key].get("enabled", True):
        raise ValueError(f"Unknown or disabled source: {key}")
    source = sources[key]
    started_at = utc_now_iso()
    run_id = uuid.uuid4().hex
    output = root / "data/discovery"
    telemetry = None
    geography = {"total_jobs_before_geography_gate": 0, "jobs_kept": 0,
                 "jobs_excluded": 0, "jobs_geography_unknown": 0, "counts_by_country": {}}
    jobs, candidates, failures = [], [], []
    try:
        adapters = {"greenhouse": fetch_greenhouse_jobs, "ashby": fetch_ashby_jobs,
                    "microsoft": fetch_microsoft_jobs, "workday": fetch_workday_jobs}
        if source.get("adapter") not in adapters:
            raise ValueError(f"Unsupported adapter: {source.get('adapter')}")
        jobs, telemetry = adapters[source["adapter"]](key, source)
        geography = geography_summary(jobs)
        telemetry.update(geography)
        candidates = [enrich_geography(job) for job in jobs if retain_candidate(job)]
        telemetry["pm_candidates"] = len(candidates)
        # Preserve successful snapshots even when the next board removes a job.
        # A failed retrieval never replaces the previous successful snapshot.
        fields = ["job_id", "external_job_id", "company", "title", "location", "canonical_url", "department", "source_key", "retrieved_at"]
        previous_path = output / "raw_all_jobs.jsonl"
        previous = []
        if previous_path.exists():
            previous = [json.loads(line) for line in previous_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        combined = [job for job in previous if job["source_key"] != key] + jobs
        validate_raw_jobs(combined)
        combined_candidates = [enrich_geography(job) for job in combined if retain_candidate(job)]
        for destination, raw_rows, pm_rows in (
            (output / "runs" / run_id, jobs, candidates),
            (output, combined, combined_candidates),
        ):
            atomic_jsonl(destination / "raw_all_jobs.jsonl", raw_rows)
            atomic_jsonl(destination / "raw_pm_candidates.jsonl", pm_rows)
            csv_fields = fields + ["all_locations_raw", "normalized_countries", "geography_in_scope",
                                   "geography_status", "geography_reason"]
            csv_rows = []
            for row in pm_rows:
                item = dict(row)
                item["all_locations_raw"] = json.dumps(item["all_locations_raw"], ensure_ascii=False)
                item["normalized_countries"] = json.dumps(item["normalized_countries"], ensure_ascii=False)
                csv_rows.append(item)
            write_csv(destination / "raw_pm_candidates.csv", csv_rows, csv_fields)
            categorized = [enrich_geography(job) for job in raw_rows]
            atomic_jsonl(destination / "geography_excluded.jsonl",
                         [row for row in categorized if row["geography_status"] == "out_of_scope"])
            atomic_jsonl(destination / "geography_unknown.jsonl",
                         [row for row in categorized if row["geography_status"] == "geography_unknown"])
            (destination / "geography_summary.json").write_text(
                json.dumps(geography_summary(raw_rows), indent=2), encoding="utf-8")
        telemetry["outputs_written"] = True
    except Exception as exc:
        if isinstance(exc, CrawlError):
            telemetry = exc.telemetry
        if telemetry is None:
            telemetry = dict(source_key=key, company=source.get("company", ""),
                             source_type=source.get("adapter", ""), started_at=started_at,
                             request_count=0, http_status="", jobs_seen=0,
                             jobs_extracted=0, pm_candidates=0, errors=[])
        message = f"{type(exc).__name__}: {exc}"
        if not isinstance(exc, CrawlError):
            telemetry["errors"].append(message)
        telemetry["status"] = "failed"
        telemetry["outputs_written"] = False
        failures.append({"source_key": key, "error": message})
    finally:
        telemetry["run_id"] = run_id
        telemetry["completed_at"] = utc_now_iso()
        append_jsonl(output / "crawl_runs.jsonl", telemetry)
    return {"raw_jobs": len(jobs), "pm_candidates": len(candidates),
            "geography": geography, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", dest="sources", help="Source key from config/job_sources.yaml; repeatable")
    args = parser.parse_args()
    result = run(args.sources)
    print(f"Raw jobs: {result['raw_jobs']}")
    print(f"PM candidates: {result['pm_candidates']}")
    geo = result["geography"]
    print("Geography gate: "
          f"total={geo['total_jobs_before_geography_gate']} kept={geo['jobs_kept']} "
          f"excluded={geo['jobs_excluded']} unknown={geo['jobs_geography_unknown']}")
    print("Countries: " + json.dumps(geo["counts_by_country"], sort_keys=True))
    if result["failures"]:
        for failure in result["failures"]:
            print(f"FAILED {failure['source_key']}: {failure['error']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
