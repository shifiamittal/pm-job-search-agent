# OpenAI / Ashby implementation and live evaluation

Not committed or pushed; awaiting user review.

## Architecture
Added deterministic Ashby retrieval for board `openai` using
`https://api.ashbyhq.com/posting-api/job-board/openai`. The public API returns all
published postings in one response; no pagination is documented or needed for
this endpoint. Completeness is relative to the public board, not unpublished roles.
See [Ashby documentation](https://developers.ashbyhq.com/docs/public-job-posting-api)
and [integration notes](discovery_ashby.md).

The adapter extracts all records before the unchanged PM filter. It preserves the
job UUID from the individual Ashby URL and source location labels. The ten supplied
OpenAI reference records retain their official OpenAI careers URLs unchanged.
Existing ID-first matching handles the different URL hosts and location spelling.
Neither discovery adapter reads the benchmark.

Shared changes are limited to adapter dispatch, a shared CrawlError, preserving
other sources in the latest exports, and checking latest crawl status per source.
Each invocation still runs exactly one source. Historical run snapshots remain
source-only. Combined latest files now contain 1,430 raw jobs and 29 PM candidates.
No fit/classification, dashboard, scheduler, or other source was added.

## Tests and regression check
47 tests run: 47 passed, 0 failed, no regressions. This includes all 35 existing
tests and 12 new Ashby/shared-output tests.

Anthropic's 19 reference records and all 619 raw / 19 PM candidate records were
compared with the committed versions and are unchanged. Its saved live snapshot
still evaluates at 19/19; Anthropic was not re-crawled during this task. Greenhouse
retrieval and normalization are unchanged apart from importing the shared error.

## OpenAI live crawl
- source_key: `openai`
- adapter: `ashby`
- started_at: `2026-09-22T09:53:55.373628+00:00`
- completed_at: `2026-09-22T09:53:56.876608+00:00`
- request_count: `1`
- http_status: `200`
- jobs_seen: `811`
- jobs_extracted: `811`
- pm_candidates: `10`
- status: `success`
- errors: `[]`
- run_id: `279f60f6793547f0a37a5cb831617060`
- outputs_written: `True`

Both JSONL outputs, candidate CSV and telemetry were written. The successful OpenAI
run snapshot is retained under `data/discovery/runs/279f60f6793547f0a37a5cb831617060/`.

## Formal evaluation
| Company | Reference | Candidates | Found | Missed | Recall |
|---|---:|---:|---:|---:|---:|
| OpenAI | 10 | 10 | 10 | 0 | 100% |
| Anthropic | 19 | 19 | 19 | 0 | 100% |
| Total | 29 | 29 | 29 | 0 | 100% |

## Every OpenAI PM candidate
All ten were present in the live published Ashby board response. Location is
reported verbatim as `San Francisco`; the source did not label it `San Francisco, CA`.

| External job ID | Exact title | Location | Individual source URL |
|---|---|---|---|
| fc38c6bf-5330-435c-99b6-1bcf1f5829a8 | Product Manager, API Agents | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/fc38c6bf-5330-435c-99b6-1bcf1f5829a8) |
| 7ffa2a14-fa9c-46cb-a30a-1f7a35ae904a | Product Manager, API Infrastructure | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/7ffa2a14-fa9c-46cb-a30a-1f7a35ae904a) |
| 33b8effb-b048-4934-a279-87fff192a330 | Product Manager, Core Models | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/33b8effb-b048-4934-a279-87fff192a330) |
| 83f6d415-9462-4afc-a539-ca8d996e011a | Product Manager, Enterprise Identity | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/83f6d415-9462-4afc-a539-ca8d996e011a) |
| 0f4da2b4-df8a-4560-809d-d0a6ac1ad9bc | Product Manager, Financial Engineering | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/0f4da2b4-df8a-4560-809d-d0a6ac1ad9bc) |
| 5953fed7-1466-4e90-94c9-43716a55e032 | Product Manager, Learning | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/5953fed7-1466-4e90-94c9-43716a55e032) |
| 70d5259a-f18c-4595-bf52-ec03eeeeac4c | Product Manager, Multimodal Safety | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/70d5259a-f18c-4595-bf52-ec03eeeeac4c) |
| fbc7ebaf-3a26-406d-9ff6-f166f3e246a2 | Product Manager, Safety Measurement | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/fbc7ebaf-3a26-406d-9ff6-f166f3e246a2) |
| 05a8cae8-81bd-4f7b-bc48-41ef1bd67e5d | Product Manager, Sensitive Deployments | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/05a8cae8-81bd-4f7b-bc48-41ef1bd67e5d) |
| cc0d0d86-eb9d-44a0-a6a4-42bbb6066b4b | Product Manager, Youth | San Francisco | [Ashby posting](https://jobs.ashbyhq.com/openai/cc0d0d86-eb9d-44a0-a6a4-42bbb6066b4b) |

## Extra candidates and miss diagnosis
No extra PM candidates and no misses. All ten approved IDs are present in both
raw_all_jobs and raw_pm_candidates and matched by the evaluator. There are no
retrieval/enumeration/extraction, FILTER, EVAL_MATCHING / REFERENCE, or
REFERENCE_STALENESS / SOURCE_CHANGE cases to diagnose. No filter or matching change
was made to chase the live result, and no extra benchmark records were added.

## Suggested next step
Review and approve this OpenAI integration for commit; the second ATS meets the
approved benchmark while preserving Anthropic behavior.

## Every added or modified file
- Modified: [README.md](../README.md)
- Modified: [config/job_sources.yaml](../config/job_sources.yaml)
- Modified: [data/discovery/crawl_runs.jsonl](../data/discovery/crawl_runs.jsonl)
- Modified: [data/discovery/raw_all_jobs.jsonl](../data/discovery/raw_all_jobs.jsonl)
- Modified: [data/discovery/raw_pm_candidates.csv](../data/discovery/raw_pm_candidates.csv)
- Modified: [data/discovery/raw_pm_candidates.jsonl](../data/discovery/raw_pm_candidates.jsonl)
- Added: [data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_all_jobs.jsonl](../data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_all_jobs.jsonl)
- Added: [data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_pm_candidates.csv](../data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_pm_candidates.csv)
- Added: [data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_pm_candidates.jsonl](../data/discovery/runs/279f60f6793547f0a37a5cb831617060/raw_pm_candidates.jsonl)
- Modified: [data/evals/README.md](../data/evals/README.md)
- Modified: [data/evals/discovery_reference.jsonl](../data/evals/discovery_reference.jsonl)
- Modified: [data/evals/latest/company_metrics.csv](../data/evals/latest/company_metrics.csv)
- Modified: [data/evals/latest/summary.json](../data/evals/latest/summary.json)
- Added: [docs/discovery_ashby.md](../docs/discovery_ashby.md)
- Modified: [docs/discovery_build_notes.md](../docs/discovery_build_notes.md)
- Added: [docs/discovery_openai_live_report.md](../docs/discovery_openai_live_report.md)
- Modified: [scripts/discover_jobs.py](../scripts/discover_jobs.py)
- Added: [scripts/discovery/ashby.py](../scripts/discovery/ashby.py)
- Added: [scripts/discovery/errors.py](../scripts/discovery/errors.py)
- Modified: [scripts/discovery/greenhouse.py](../scripts/discovery/greenhouse.py)
- Modified: [scripts/eval_discovery.py](../scripts/eval_discovery.py)
- Added: [scripts/test_ashby.py](../scripts/test_ashby.py)
- Modified: [scripts/test_discovery.py](../scripts/test_discovery.py)
