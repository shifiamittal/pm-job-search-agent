# Discovery evaluation design (v1)

## Boundary
Discovery answers: **what PM jobs exist in the sources we committed to crawl?**
Fit, AI/domain categorization, application posture, resume strategy and outreach are
not part of this evaluation.

## Observable artifacts
1. `data/discovery/crawl_runs.jsonl` — raw crawl telemetry: what the software did.
2. `data/discovery/raw_all_jobs.jsonl` — every job returned by the source adapter.
3. `data/discovery/raw_pm_candidates.jsonl` — broad PM candidate filter output.
4. `data/evals/discovery_reference.jsonl` — independently curated expected positives.
5. `data/evals/latest/*` — eval comparison outputs.

## Failure taxonomy
Assign a failure category only after tracing a missed reference job through the
observable artifacts.

- `SOURCE_COVERAGE`: the company/source was outside the configured crawl universe.
- `RETRIEVAL`: source was configured but fetching failed or returned an incomplete response.
- `PAGINATION`: retrieval worked but not every result page/cursor was traversed.
- `EXTRACTION`: source content was retrieved but a job record could not be parsed.
- `VALIDATION`: a parsed job was rejected because the raw schema/validation was wrong or incomplete.
- `FILTER`: the raw job exists but the PM-candidate filter excluded it.
- `DEDUPE`: the raw job existed but was incorrectly collapsed into another job.
- `STATE`: stale/seen state prevented a live job from being emitted or refreshed.
- `PERMISSION`: authentication, robots/site policy, or account permissions prevented access.
- `EVAL_MATCHING / REFERENCE`: a candidate is present but the reference comparison reports it missing.
- `UNKNOWN`: evidence is insufficient; investigate before changing architecture or prompts.

## Primary metrics
- Known-positive recall = reference PM jobs found / reference PM jobs.
- Source task success = configured source successfully enumerated and persisted without unresolved critical errors.
- Raw extraction completeness = valid raw records / source jobs seen.
- PM filter yield = PM candidates / valid raw records (diagnostic, not a quality target by itself).
- Freshness (later) = discovery timestamp - first authoritative posting timestamp when available.

Precision should only be treated as a valid metric when the reference set is exhaustive
for the same source and snapshot. Otherwise "extra" jobs may simply be legitimate jobs
missing from the reference set.

## Dashboard decision
V1 writes CSV + JSON outputs instead of adding a Google Sheets tab. Reasons:
- metric definitions and failure categories are still evolving;
- a spreadsheet UI adds no diagnostic information that the CSV lacks;
- existing Google Sheets sync is downstream/application-oriented and should not couple
  raw retrieval to presentation.

Once the harness has been used across at least 3 source types and the columns stabilize,
add two lightweight tabs to the existing workbook: `Discovery Eval` and `Discovery Failures`.
