# Microsoft Careers discovery

## Scope and official source
The adapter enumerates Microsoft's public Product Management profession facet:
`GET https://apply.careers.microsoft.com/api/pcsx/search`
with `domain=microsoft.com`, `query=`, `location=`, `start=<offset>`, and
`filter_profession=product management`. It requires the returned appliedFilters
acknowledgment, preventing accidental full-board crawling. Public client/facet
inspection during the independent benchmark construction confirmed this parameter.
At that snapshot the profession and career_discipline facets had identical IDs;
production uses the profession facet alone to reduce request volume. The current
source count is read dynamically; no benchmark count or ID is used in retrieval.

## Pagination, drift and errors
The next offset advances by actual returned rows (the observed page size is 10).
Each pass reaches an empty page and rechecks its first and last populated pages.
A pass is accepted only when unique IDs equal the terminal and rechecked counts,
no duplicate IDs occurred, and the boundary ID lists remain unchanged. Earlier
page counts may drift if the final checks reconcile. Otherwise up to three full
facet passes reconcile additions/removals by source position ID. The final verified
pass replaces the selected source, rather than unioning stale jobs from earlier
passes. Unresolved drift fails visibly and preserves previous successful exports.
A 100-page safety bound prevents an unexpectedly unbounded facet crawl.

Requests are paced at least five seconds apart. Connection errors, timeouts and
HTTP 408/429/500/502/503/504 get at most three attempts. Backoff is 60 then 120
seconds, respecting a longer Retry-After value (seconds or HTTP date). Other HTTP
errors are not retried. Telemetry records each request/attempt, page count/IDs,
duplicate IDs, boundary checks, pass additions/removals, and recoverable errors.
The source is live, not a transactionally locked snapshot; these checks provide
count and boundary consistency, not a claim that the employer never changed a
middle-page job during capture.

## Raw records and geography
All jobs from the final verified PM facet are retained in raw_all_jobs, including
non-US/India locations. Canonical external_job_id is the numeric Microsoft source
position ID, which matches the individual careers URL. Display/requisition IDs,
all locations and the original listing fields are preserved in telemetry's
source_records. Raw location joins all source labels with ` | `, and posting_date
uses source postedTs in UTC. Raw description remains blank; detail descriptions
are used only as availability evidence in this discovery phase.

Only after raw retrieval does the orchestrator apply the existing PM title filter
and the Microsoft-only country rule: retain if any listed country is exactly
United States or India. Cities alone are not used to infer country. No city,
seniority, product-area or fit personalization is applied. Internship/student
titles and source employment types are excluded from Microsoft live candidates.
Extra candidates are reported for review and never added to the benchmark.
Greenhouse/Ashby adapter code and the shared title filter are unchanged.

## Detail availability gate
Every otherwise eligible non-intern role is checked with
`GET https://apply.careers.microsoft.com/api/pcsx/position_details`, parameters
`domain=microsoft.com`, `position_id=<source ID>`, `hl=en`. The same pacing and
retry policy applies. Available requires HTTP/body success, matching position and
requisition IDs, a job description, and an `apply` or `log_in` application action.
HTTP/body 404/410, explicit fallback, or a closed/unavailable/expired application
action marks a record `stale_unavailable`. Missing positive evidence or mismatched
identity is `unknown`, not a fabricated closure. Both are excluded from live output.
Exhausted transport failures fail the crawl and preserve the previous snapshot.

All facet records remain in raw output. Optional string fields
`availability_status`, `availability_checked_at`, `availability_reason`, and
`employment_type` persist verification so later single-source runs cannot
reintroduce an unavailable Microsoft listing. Telemetry includes per-job identity,
status, reason, application action and timestamp. HTTP 200 alone is insufficient;
generic page template text containing "no longer" is not a job-specific closure.
These public signals establish source availability, not a completed application.

## Benchmark boundary
The human-reviewed CSV is authoritative. Its conversion to evaluation JSONL is
independent of the adapter, which never reads benchmark files. An explicitly
authorized correction to the duplicated Hyderabad position ID/URL must be backed
by the official source and documented in the live report. The existing Anthropic
and OpenAI reference records remain unchanged. Microsoft recall is measured on
approved requisitions through their verified source position IDs.

## Commands
```powershell
.\.venv\Scripts\python.exe scripts/discover_jobs.py --source microsoft
.\.venv\Scripts\python.exe scripts/eval_discovery.py
```

Latest raw exports preserve other sources; run snapshots remain source-only.
Existing serialized-write / non-transactional multi-file limitations remain. No
classified-job finalization, Google Sheets dashboard, application action, or
candidate-profile modification is part of raw Microsoft discovery.
