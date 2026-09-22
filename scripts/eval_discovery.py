#!/usr/bin/env python3
"""Evaluate job discovery against a human/authoritative reference set.

The harness does not invent ground truth. It compares discovery output with a
separately curated reference JSONL. Prefer external_job_id; otherwise use a
normalized company/title/location key.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def match_key(row: dict) -> tuple:
    external = str(row.get("external_job_id") or "").strip()
    company = norm(row.get("company", ""))
    if external:
        return ("id", company, external)
    return ("text", company, norm(row.get("title", "")), norm(row.get("location", "")))


def text_key(row: dict) -> tuple:
    return tuple(norm(row.get(field, "")) for field in ("company", "title", "location"))


def evaluate(reference: list[dict], discovered: list[dict]) -> dict:
    for label, rows in (("reference", reference), ("discovered", discovered)):
        keys = [match_key(row) for row in rows]
        if len(keys) != len(set(keys)):
            raise ValueError(f"Duplicate identities in {label}")
    remaining = set(range(len(discovered)))
    matches = {}
    # Reserve exact ID matches before considering any text fallback.
    for i, row in enumerate(reference):
        if match_key(row)[0] == "id":
            for j in sorted(remaining):
                if match_key(row) == match_key(discovered[j]):
                    matches[i] = j
                    remaining.remove(j)
                    break
    for i, row in enumerate(reference):
        if i in matches:
            continue
        possible = [j for j in sorted(remaining)
                    if text_key(row) == text_key(discovered[j])
                    and (match_key(row)[0] == "text" or match_key(discovered[j])[0] == "text")]
        # Ambiguous fallback is not evidence of a match.
        if len(possible) == 1:
            matches[i] = possible[0]
            remaining.remove(possible[0])
    per_company = defaultdict(lambda: {"reference": 0, "discovered": 0, "found": 0, "missed": 0})
    company_names = {norm(row.get("company")): row.get("company", "") for row in reference}
    for row in discovered:
        company = company_names.get(norm(row.get("company")), row.get("company", ""))
        per_company[company]["discovered"] += 1
    for i, row in enumerate(reference):
        metrics = per_company[row.get("company", "")]
        metrics["reference"] += 1
        metrics["found" if i in matches else "missed"] += 1
    return {
        "reference_count": len(reference),
        "discovered_count": len(discovered),
        "found_count": len(matches),
        "missed_count": len(reference) - len(matches),
        "extra_count": len(remaining),
        "known_positive_recall": len(matches) / len(reference) if reference else None,
        "missed": [row for i, row in enumerate(reference) if i not in matches],
        "extras": [discovered[j] for j in sorted(remaining)],
        "per_company": dict(per_company),
    }


def write_reports(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output_dir / "missed_jobs.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        fields = ["company", "external_job_id", "title", "location", "canonical_url", "failure_category", "failure_notes"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in result["missed"]:
            writer.writerow(dict(row, failure_category="UNDIAGNOSED", failure_notes=""))
    with (output_dir / "company_metrics.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["company", "reference", "discovered", "found", "missed", "recall"])
        writer.writeheader()
        for company, metrics in sorted(result["per_company"].items()):
            reference = metrics["reference"]
            writer.writerow({"company": company, **metrics, "recall": metrics["found"] / reference if reference else ""})


def validate_latest_crawls(telemetry: list[dict]) -> None:
    """A later success on one board must not hide a failed crawl of another."""
    latest = {row["source_key"]: row for row in telemetry}
    failed = [key for key, row in latest.items() if row["status"] != "success" or not row.get("outputs_written")]
    if not latest or failed:
        raise ValueError(f"Latest crawl did not succeed for {', '.join(failed) or 'any source'}; retained outputs are not a current benchmark")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default=str(ROOT / "data/evals/discovery_reference.jsonl"))
    parser.add_argument("--discovered", default=str(ROOT / "data/discovery/raw_pm_candidates.jsonl"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/evals/latest"))
    args = parser.parse_args()
    try:
        reference = load_jsonl(Path(args.reference))
        discovered = load_jsonl(Path(args.discovered))
        # Do not silently evaluate a retained snapshot after a failed latest crawl.
        if Path(args.discovered).resolve() == (ROOT / "data/discovery/raw_pm_candidates.jsonl").resolve():
            telemetry = load_jsonl(ROOT / "data/discovery/crawl_runs.jsonl")
            validate_latest_crawls(telemetry)
    except (OSError, ValueError) as exc:
        print(f"Evaluation input error: {exc}")
        return 2
    if not reference:
        print("Reference set is empty. Curate data/evals/discovery_reference.jsonl before interpreting recall.")
        return 2
    result = evaluate(reference, discovered)
    write_reports(result, Path(args.output_dir))
    recall = result["known_positive_recall"]
    print(f"Reference jobs: {result['reference_count']}")
    print(f"Discovered candidates: {result['discovered_count']}")
    print(f"Found reference jobs: {result['found_count']}")
    print(f"Missed reference jobs: {result['missed_count']}")
    print(f"Known-positive recall: {recall:.1%}" if recall is not None else "Known-positive recall: n/a")
    print("Recall measures known positives only; extra candidates are not assumed false positives.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
