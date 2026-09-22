# Discovery V1: implementation and live review

Implemented the approved REVIEW.md design on the clean current repository, using
the patch as a draft. The user subsequently approved expanding the benchmark to 19 roles and committing
and pushing after successful evaluation and regression tests.

## Tests
35 tests run, 35 passed, 0 failed: 18 existing tests and 17 discovery tests.
No existing-test regressions. Command: `.venv/Scripts/python.exe -m unittest discover -s scripts -p 'test_*.py' -v`.

## Live Anthropic crawl
- Successful crawl: 2026-09-22, 08:13:36–08:13:37 UTC.
- Jobs seen: 619; raw jobs extracted: 619; PM candidates retained: 19.
- Status: success; HTTP 200; request count: 1; errors: none.
- Both raw JSONL outputs, candidate CSV, and append-only telemetry were written.
- Successful run snapshot: `data/discovery/runs/6e84739336d2425dbb4c413f30175a54/`.
- An earlier sandboxed attempt failed with socket permission error WinError 10013
  before receiving an HTTP response. Its telemetry is retained. The authorized
  network retry succeeded. There were two attempts total, one request each.

## Evaluation
| Company | Reference | Candidates | Found | Missed | Known-positive recall |
|---|---:|---:|---:|---:|---:|
| Anthropic | 19 | 19 | 19 | 0 | 100% |

All 19 exact reference IDs occur in both raw_all_jobs and raw_pm_candidates.
There are no missed IDs/titles and no retrieval/extraction, FILTER, or
EVAL_MATCHING / REFERENCE misses to diagnose for this snapshot.

Product Operations Manager, Embedded (5179891008) is retained in raw_all_jobs and
excluded from both the PM candidates and reference set, as requested.

The user approved adding these two candidates to the original 17-role benchmark:
- 5397737008 — c
- 5394887008 — Product Manager, Claude Science

The approved benchmark now contains exactly 19 roles. Their source facts come from
the existing live Greenhouse snapshot; the expansion records explicit user approval.
No code was changed to chase live misses.

## Implementation and architecture concerns
- Deterministic Greenhouse retrieval enumerates the full board before PM filtering.
  The crawler never imports or reads the reference set.
- Raw records contain only source facts/provenance. Existing fit, classification,
  canonical job records, candidate evidence, and Google Sheets behavior are unchanged.
- Corrected draft telemetry loss, unsafe empty-output replacement on failed crawls,
  null external IDs, URL/schema validation, and asymmetric evaluation fallback.
  ID mismatches cannot be rescued by title matches; ambiguous fallback stays unmatched.
- Successful run snapshots preserve historical raw records. Latest files describe
  the current board; missing jobs are not silently deleted from historical snapshots.
- Repository AGENTS.md describes full discovery/classification and canonical Sheet
  synchronization, while this explicitly authorized task ends at raw PM candidates.
  The new command therefore does not invoke classification/finalize_discovery or
  Sheet sync. Raw records cannot be passed directly to the classified-job finalizer.
- V1 enforces one enabled source per run. Multi-source snapshot merging is deferred.
- Latest exports are not a multi-file transaction. Persistence failures are recorded
  as failed, and default evaluation rejects a failed latest crawl. JSONL files are
  individually atomic and the successful run has a retained snapshot.
- No additional source or eval dashboard was added.

## Approval and validation
The updated evaluation uses the same successful live snapshot, with no new crawl.
All 19 approved roles were found (100% recall, zero misses or extra candidates).
The full test suite passed: 35 tests, zero failures or regressions.
The user authorized committing and pushing Discovery V1 on these conditions.

## Every added or modified file
- Modified: [README.md](../README.md)
- Added: [config/job_sources.yaml](../config/job_sources.yaml)
- Added: [data/discovery/crawl_runs.jsonl](../data/discovery/crawl_runs.jsonl)
- Added: [data/discovery/raw_all_jobs.jsonl](../data/discovery/raw_all_jobs.jsonl)
- Added: [data/discovery/raw_pm_candidates.csv](../data/discovery/raw_pm_candidates.csv)
- Added: [data/discovery/raw_pm_candidates.jsonl](../data/discovery/raw_pm_candidates.jsonl)
- Added: [data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_all_jobs.jsonl](../data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_all_jobs.jsonl)
- Added: [data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_pm_candidates.csv](../data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_pm_candidates.csv)
- Added: [data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_pm_candidates.jsonl](../data/discovery/runs/6e84739336d2425dbb4c413f30175a54/raw_pm_candidates.jsonl)
- Added: [data/evals/README.md](../data/evals/README.md)
- Added: [data/evals/discovery_reference.jsonl](../data/evals/discovery_reference.jsonl)
- Added: [data/evals/latest/company_metrics.csv](../data/evals/latest/company_metrics.csv)
- Added: [data/evals/latest/missed_jobs.csv](../data/evals/latest/missed_jobs.csv)
- Added: [data/evals/latest/summary.json](../data/evals/latest/summary.json)
- Added: [docs/discovery_build_notes.md](../docs/discovery_build_notes.md)
- Added: [docs/discovery_eval_design.md](../docs/discovery_eval_design.md)
- Added: [docs/discovery_v1_live_report.md](../docs/discovery_v1_live_report.md)
- Added: [scripts/discover_jobs.py](../scripts/discover_jobs.py)
- Added: [scripts/discovery/__init__.py](../scripts/discovery/__init__.py)
- Added: [scripts/discovery/filters.py](../scripts/discovery/filters.py)
- Added: [scripts/discovery/greenhouse.py](../scripts/discovery/greenhouse.py)
- Added: [scripts/discovery/io.py](../scripts/discovery/io.py)
- Added: [scripts/discovery/models.py](../scripts/discovery/models.py)
- Added: [scripts/eval_discovery.py](../scripts/eval_discovery.py)
- Added: [scripts/test_discovery.py](../scripts/test_discovery.py)
