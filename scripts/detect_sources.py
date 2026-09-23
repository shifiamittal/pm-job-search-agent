#!/usr/bin/env python3
"""Evaluate source detection without using expected labels as detection inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from discovery.source_detection import detect_source

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["company", "careers_url", "expected_source_type", "expected_source_identifier",
          "benchmark_confidence", "detected_source_type", "detected_source_identifier",
          "detector_confidence", "detection_method", "evidence", "adapter_available",
          "match_status", "review_needed", "identifier_comparison", "identifier_note", "source_ready"]
TYPE_ALIASES = {"microsoft custom careers api": "microsoft_custom",
                "company-native/custom": "company_native_custom", "rippling ats": "rippling"}


def normalize_type(value):
    value = value.strip().lower()
    value = TYPE_ALIASES.get(value, value)
    if value not in {"greenhouse", "ashby", "workday", "lever", "rippling", "microsoft_custom", "company_native_custom", "unknown"}:
        raise ValueError(f"Unrecognized benchmark source type: {value}")
    return value


def compare_identifier(expected, detected, family):
    if not expected.strip() or not detected.strip():
        return "NOT_COMPARABLE"
    a, b = expected.strip().casefold(), detected.strip().casefold()
    if family == "microsoft_custom":
        a = a.removesuffix(" / pcsx")
    if a == b:
        return "EXACT"
    # Benchmark v1 Workday identifiers may specify only a tenant OR site.
    if family == "workday" and "/" not in a and a in b.split("/"):
        return "PARTIAL_COMPONENT_MATCH"
    return "MISMATCH"


def evaluate_row(reference, detected):
    expected = normalize_type(reference["source_type"])
    actual = detected["detected_source_type"]
    comparison = compare_identifier(reference["source_identifier"], detected["detected_source_identifier"], expected)
    if expected != actual and comparison != "NOT_COMPARABLE":
        comparison = "MISMATCH"
    high = reference["confidence"].strip().lower() == "high"
    if actual == "unknown":
        status = "UNKNOWN"
    elif expected != actual:
        status = "TYPE_MISMATCH" if high else "BENCHMARK_REVIEW"
    elif comparison == "MISMATCH":
        status = "IDENTIFIER_MISMATCH" if high else "BENCHMARK_REVIEW"
    else:
        status = "MATCH"
    return dict(company=reference["company"], careers_url=reference["careers_url"],
                expected_source_type=expected, expected_source_identifier=reference["source_identifier"],
                benchmark_confidence=reference["confidence"], detected_source_type=actual,
                detected_source_identifier=detected["detected_source_identifier"],
                detector_confidence=detected["confidence"], detection_method=detected["detection_method"],
                evidence=json.dumps(detected["evidence"], ensure_ascii=False),
                adapter_available=detected["adapter_available"], match_status=status,
                source_ready=detected["source_ready"],
                review_needed=(status != "MATCH" or not high or comparison == "NOT_COMPARABLE"),
                identifier_comparison=comparison, identifier_note=detected["identifier_note"])


def summarize(rows):
    high = [r for r in rows if r["benchmark_confidence"].lower() == "high"]
    comparable = [r for r in rows if r["identifier_comparison"] != "NOT_COMPARABLE"]
    unsupported = defaultdict(list)
    for r in rows:
        if not r["adapter_available"]:
            unsupported[r["detected_source_type"]].append(r["company"])
    metric = lambda count, total: dict(numerator=count, denominator=total, rate=count / total if total else None)
    agreement = lambda r: r["expected_source_type"] == r["detected_source_type"]
    return dict(total_companies=len(rows),
                high_confidence_source_type_accuracy=metric(sum(map(agreement, high)), len(high)),
                overall_source_type_agreement=metric(sum(map(agreement, rows)), len(rows)),
                identifier_accuracy=metric(sum(r["identifier_comparison"] in {"EXACT", "PARTIAL_COMPONENT_MATCH"} for r in comparable), len(comparable)),
                identifier_exact_accuracy=metric(sum(r["identifier_comparison"] == "EXACT" for r in comparable), len(comparable)),
                identifier_not_comparable=[r["company"] for r in rows if r["identifier_comparison"] == "NOT_COMPARABLE"],
                unknown_rate=metric(sum(r["detected_source_type"] == "unknown" for r in rows), len(rows)),
                adapter_coverage=metric(sum(r["adapter_available"] for r in rows), len(rows)),
                identifier_ready_coverage=metric(sum(r["source_ready"] for r in rows), len(rows)),
                supported_family_missing_identifier=[r["company"] for r in rows if r["adapter_available"] and not r["source_ready"]],
                unsupported_by_type=dict(sorted(unsupported.items())),
                detected_distribution=dict(Counter(r["detected_source_type"] for r in rows)),
                proposed_benchmark_corrections=[r for r in rows if r["match_status"] == "BENCHMARK_REVIEW" and r["detector_confidence"] == "high"],
                metric_notes=["Types normalized by explicit spelling aliases only.",
                              "Workday partial tenant/site component matches count as compatible; exact accuracy also reported.",
                              "Blank detector identifiers are NOT_COMPARABLE, never identifier successes.",
                              "MATCH means type agreement and no comparable identifier conflict; review_needed captures unverified identifiers.",
                              "Adapter coverage measures implemented families; identifier-ready coverage additionally requires a verified identifier. Neither is a live job-discovery success rate.",
                              "Custom/native is a verified front end with unresolved underlying ATS, not proof no third-party ATS exists."])


def run(benchmark: Path, output: Path, detector=detect_source):
    started_at = datetime.now(timezone.utc).isoformat()
    raw = benchmark.read_bytes()
    with benchmark.open(encoding="utf-8-sig", newline="") as stream:
        refs = list(csv.DictReader(stream))
    required = {"company", "careers_url", "source_type", "source_identifier", "confidence"}
    if not refs or not required.issubset(refs[0]):
        raise ValueError("Benchmark is empty or missing required columns")
    if len({r["company"] for r in refs}) != len(refs):
        raise ValueError("Duplicate benchmark companies")
    for ref in refs:
        normalize_type(ref["source_type"])
        if ref["confidence"].lower() not in {"high", "medium", "low"}:
            raise ValueError("Invalid benchmark confidence")
    detections, rows = [], []
    for ref in refs:
        detected = detector(ref["company"], ref["careers_url"])
        detections.append(detected)
        row = evaluate_row(ref, detected)
        rows.append(row)
        print(f"{ref['company']}: {row['detected_source_type']} [{row['detected_source_identifier']}] {row['match_status']}", flush=True)
    summary = summarize(rows)
    summary["benchmark_sha256"] = hashlib.sha256(raw).hexdigest()
    summary["benchmark_path"] = str(benchmark)
    summary["request_count"] = sum(len(d["requests"]) for d in detections)
    summary["http_attempt_count"] = sum(len(a.get("attempts", [None])) for d in detections for a in d["requests"])
    summary["request_errors"] = [dict(company=d["company"], **a) for d in detections for a in d["requests"] if a.get("error") or a.get("status") != 200]
    summary["capture_started_at"] = started_at
    summary["capture_completed_at"] = detections[-1]["captured_at"]
    output.mkdir(parents=True, exist_ok=True)
    for name, subset in [("results.csv", rows), ("mismatches.csv", [r for r in rows if r["match_status"] != "MATCH"])]:
        with (output / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(subset)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "evidence.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in detections), encoding="utf-8")
    if benchmark.read_bytes() != raw:
        raise RuntimeError("Benchmark changed during evaluation")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "data/evals/source_detection/latest")
    args = parser.parse_args()
    summary = run(args.benchmark, args.output)
    print(json.dumps({k: v for k, v in summary.items() if k in {"total_companies", "high_confidence_source_type_accuracy", "overall_source_type_agreement", "identifier_accuracy", "unknown_rate", "adapter_coverage"}}, indent=2))


if __name__ == "__main__":
    main()
