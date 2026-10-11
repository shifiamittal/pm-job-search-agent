#!/usr/bin/env python3
"""Filter an existing discovery CSV or JSONL to the Phase-1 US/India universe."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from discovery.geography import enrich_geography, geography_summary
from discovery.io import atomic_jsonl, write_csv


def load_rows(path: Path) -> list[dict]:
    if path.suffix.casefold() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    if path.suffix.casefold() in {".jsonl", ".ndjson"}:
        return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    raise ValueError("Input must be CSV or JSONL")


def _csv_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    converted = []
    for row in rows:
        item = dict(row)
        for key in ("all_locations_raw", "normalized_countries"):
            item[key] = json.dumps(item[key], ensure_ascii=False)
        item["geography_in_scope"] = str(item["geography_in_scope"]).lower()
        converted.append(item)
    return converted, fields


def filter_file(input_path: Path, output_dir: Path) -> dict:
    rows = load_rows(input_path)
    enriched = [enrich_geography(row) for row in rows]
    groups = {
        "shortlist_input_us_india": [row for row in enriched if row["geography_status"] == "in_scope"],
        "geography_excluded": [row for row in enriched if row["geography_status"] == "out_of_scope"],
        "geography_unknown": [row for row in enriched if row["geography_status"] == "geography_unknown"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, group in groups.items():
        atomic_jsonl(output_dir / f"{name}.jsonl", group)
        csv_rows, fields = _csv_rows(group)
        if not fields:
            fields = list(rows[0]) + ["all_locations_raw", "normalized_countries", "geography_in_scope",
                                      "geography_status", "geography_reason"] if rows else ["geography_status"]
        write_csv(output_dir / f"{name}.csv", csv_rows, fields)
    summary = geography_summary(rows)
    summary.update(input_path=str(input_path.resolve()), output_dir=str(output_dir.resolve()))
    (output_dir / "geography_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = filter_file(args.input, args.output_dir)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
