# Workday malformed-listing robustness: NVIDIA validation

Generic handling only: malformed listing titles/paths and missing required detail title/requisition ID are diagnosed as `malformed_source_record` and skipped. Original raw source metadata and pass/offset observations are retained. No values are invented. Listing-count accounting includes malformed records; two-pass consistency, terminal probes, and existing request/detail failure handling remain in force. No company-specific conditions or benchmark IDs were added to production code.

| Metric | Result |
|---|---:|
| Raw valid jobs | 1622 |
| Malformed records skipped | 1 |
| PM candidates | 36 |
| Frozen benchmark matches | 35 / 35 |
| Recall | 100.00% |
| Extras | 1 |
| Duplicate job IDs | 0 |
| Duplicate listing paths | 0 |
| Source failures | 0 |
| Detail failures | 0 |
| Retries | 82 |
| Source count | 1623 |
| Pagination complete | True |
| Extraction complete | False |

Capture: 2026-09-30T16:22:22.184951+00:00 to 2026-09-30T16:29:16.762061+00:00.
Missing benchmark IDs: [].

## Malformed source diagnostics

```json
[
  {
    "failure_reason": "malformed_source_record",
    "reasons": [
      "Listing missing title",
      "Listing missing or unusable externalPath"
    ],
    "raw_record": {
      "bulletFields": [
        "JR2025784"
      ]
    },
    "observations": [
      {
        "phase": "listing",
        "pass_number": 1,
        "offset": 240,
        "index": 9
      },
      {
        "phase": "listing",
        "pass_number": 2,
        "offset": 240,
        "index": 9
      }
    ]
  }
]
```

## Extra PM candidates

- JR2010985: Senior Silicon and System Product Lead — US, CA, Santa Clara

Extras are unreviewed benchmark differences, not filter defects. The NVIDIA reference remains unchanged at 35. Product Lead and Product Owner remain positive signals.

## Validation and scope

All 115 tests passed (`python -B -m unittest discover -s scripts -p "test_*.py"`). Four focused test methods cover missing listing title/path (including both missing, blank title and non-object rows), valid neighbors, diagnostic metadata and reasons, missing required detail identity/title, and count-shortfall/pass-drift protection. An existing test was updated to reflect the newly required missing-ID skip behavior; missing descriptions/offsite URLs still fail.

Changed code: `scripts/discovery/workday.py` and `scripts/test_workday.py`. Updated documentation: `docs/discovery_workday.md` and this report. New evaluation artifacts: `data/evals/workday/malformed_listing_fix/nvidia/`. PM filtering, benchmarks, other adapters, and source mappings were not changed. No commits or pushes.
