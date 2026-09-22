# Discovery evaluation

`discovery_reference.jsonl` is a separately curated reference set. The discovery
system must never read it while crawling; `scripts/eval_discovery.py` reads it only
after a run.

Each row should contain at least:

```json
{"company":"Anthropic","external_job_id":"<Greenhouse id if known>","title":"Product Manager, ...","location":"...","canonical_url":"https://..."}
```

Use official career/ATS listings plus manual review to establish the reference for
a fixed source and time window. An empty `external_job_id` is permitted; the harness
then matches on normalized company + title + location.

Outputs in `data/evals/latest/`:
- `summary.json`: overall metrics and unmatched records.
- `company_metrics.csv`: reference/found/missed counts by company.
- `missed_jobs.csv`: misses pre-filled with `UNDIAGNOSED`; after inspection, assign
  a failure taxonomy label such as `SOURCE_COVERAGE`, `RETRIEVAL`, `PAGINATION`,
  `EXTRACTION`, `VALIDATION`, `FILTER`, `DEDUPE`, `STATE`, or `PERMISSION`.

The CSVs are intentionally Google-Sheets-friendly. V1 does not add another dashboard
tab until the metric definitions and workflow stabilize.
