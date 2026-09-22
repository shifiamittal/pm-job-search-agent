# Discovery v1 build notes

Implemented September 22, 2026.

## Added
- `config/job_sources.yaml`: executable job-source responsibility registry.
- `scripts/discovery/models.py`: raw source-fact schema and validation.
- `scripts/discovery/greenhouse.py`: deterministic Greenhouse public-board adapter.
- `scripts/discovery/filters.py`: conservative/high-recall PM-family title filter.
- `scripts/discovery/io.py`: atomic JSONL/CSV and telemetry helpers.
- `scripts/discover_jobs.py`: source orchestration CLI.
- `scripts/eval_discovery.py`: reference-vs-discovered eval harness.
- `data/evals/discovery_reference.jsonl`: first Anthropic PM reference snapshot.
- `docs/discovery_eval_design.md`: observability, metrics and failure taxonomy.
- `scripts/test_discovery.py`: adapter/filter/eval unit tests.

## Outputs created by a live crawl
- `data/discovery/raw_all_jobs.jsonl`: all source records before PM filtering.
- `data/discovery/raw_pm_candidates.jsonl`: broad PM-family candidates.
- `data/discovery/raw_pm_candidates.csv`: review-friendly export.
- `data/discovery/crawl_runs.jsonl`: append-only crawl telemetry.

## Outputs created by eval
- `data/evals/latest/summary.json`
- `data/evals/latest/company_metrics.csv`
- `data/evals/latest/missed_jobs.csv`

## Run locally
```bash
python -m pip install -r scripts/requirements-sync.txt
python scripts/discover_jobs.py --source anthropic
python scripts/eval_discovery.py
```

## Persistence and failure behavior
Successful runs also retain immutable snapshots in `data/discovery/runs/<run_id>/`.
The top-level files are the latest successful snapshot, not a historical job ledger.
Failed retrievals preserve that snapshot and append original error telemetry. The
default evaluator rejects a failed latest crawl instead of silently using old data.
Each JSONL write is atomic; the three latest export files are not a transactional
bundle. A persistence failure is recorded as failed and must be resolved before eval.
V1 accepts one enabled source per run; multi-source state merging is deferred.

Raw records contain only the reviewed fields. PM title decisions are reproducible
from the filter, with every excluded title retained in raw_all_jobs. Existing
classification/finalization and its Google Sheet synchronization remain separate.
No canonical classified records are written by this raw discovery command.

## Dashboard decision
Do not add Google Sheets eval tabs yet. Use the generated CSVs for the first 2-3
source types. If the columns and taxonomy remain stable, add:
1. `Discovery Eval`: one row per source/run with task success, jobs seen, candidates,
   known-positive recall, errors and run timestamp.
2. `Discovery Failures`: one row per missed reference job with diagnosed taxonomy,
   notes and resolution status.
