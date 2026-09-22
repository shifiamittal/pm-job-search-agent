#!/usr/bin/env python3
"""Run raw job discovery for configured sources.

V1 intentionally supports Greenhouse only. Other adapters should be added after
this vertical slice is measured rather than hidden behind a generic LLM crawler.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from discovery.filters import pm_candidate_decision
from discovery.greenhouse import CrawlError, fetch_greenhouse_jobs
from discovery.models import utc_now_iso
from discovery.io import append_jsonl, atomic_jsonl, load_job_sources, write_csv


def run(source_keys: list[str] | None = None, root: Path = ROOT) -> dict:
    sources = load_job_sources(root / "config/job_sources.yaml")
    selected = list(dict.fromkeys(source_keys or [key for key, value in sources.items() if value.get("enabled", True)]))
    # V1 publishes one complete board snapshot. Do not silently overwrite other boards.
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
    jobs, candidates, failures = [], [], []
    try:
        if source.get("adapter") != "greenhouse":
            raise ValueError(f"Unsupported adapter: {source.get('adapter')}")
        jobs, telemetry = fetch_greenhouse_jobs(key, source)
        candidates = [job for job in jobs if pm_candidate_decision(job["title"])[0]]
        telemetry["pm_candidates"] = len(candidates)
        # Preserve successful snapshots even when the next board removes a job.
        # A failed retrieval never replaces the previous successful snapshot.
        fields = ["job_id", "external_job_id", "company", "title", "location", "canonical_url", "department", "source_key", "retrieved_at"]
        for destination in (output / "runs" / run_id, output):
            atomic_jsonl(destination / "raw_all_jobs.jsonl", jobs)
            atomic_jsonl(destination / "raw_pm_candidates.jsonl", candidates)
            write_csv(destination / "raw_pm_candidates.csv", candidates, fields)
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
    return {"raw_jobs": len(jobs), "pm_candidates": len(candidates), "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", dest="sources", help="Source key from config/job_sources.yaml; repeatable")
    args = parser.parse_args()
    result = run(args.sources)
    print(f"Raw jobs: {result['raw_jobs']}")
    print(f"PM candidates: {result['pm_candidates']}")
    if result["failures"]:
        for failure in result["failures"]:
            print(f"FAILED {failure['source_key']}: {failure['error']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
