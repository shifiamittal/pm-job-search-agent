# Workday discovery

`scripts/discovery/workday.py` implements one public CXS adapter for configurable
Workday tenants and sites. It has no benchmark imports, company branches, PM title
rules, or reference IDs. The normal discovery runner invokes it through the existing
adapter dispatch and then uses the unchanged `retain_candidate` / PM title filter.

## Configuration

```yaml
company: Example
adapter: workday
tenant: example
site: External
careers_url: https://www.example.com/careers
workday_url: https://example.wd5.myworkdayjobs.com/External
# Optional. Omit both to retrieve the whole public board.
search_text: ""
applied_facets: {}
# Optional operational bounds:
page_size: 20
detail_workers: 6
max_pages: 1000
```

Use facet IDs published by the configured site. `workday_url` is required when
`careers_url` is a corporate portal rather than the Workday site. The checked-in
Adobe, NVIDIA, and CrowdStrike configurations retrieve **all US/India jobs**, with
no search keyword or PM-family facet. Their different geography facet names are
configuration data, not different retrieval implementations.

## Retrieval and completeness

The adapter POSTs to `/wday/cxs/{tenant}/{site}/jobs`, passing `limit`, `offset`,
`searchText`, and `appliedFacets`. It advances by the actual returned row count,
retains unique `externalPath` values, and detects repeated pages. A first-page total
is authoritative for that pass; zero totals on continuation pages are not treated
as empty universes. At the count boundary it probes the next offset. An empty page
or a reset to already-seen jobs is accepted; new records or count drift fail.

Two full passes must agree on listing identities, malformed-record membership,
and source count. Unknown-count
queries require actual empty-page exhaustion on both passes. Early repeats,
count shortfalls, disagreeing passes, and max-page exhaustion raise `CrawlError`.
No partial result replaces a successful discovery snapshot. Unstable sources may
require a later rerun; incomplete passes are not patched using benchmark IDs.

An individual malformed listing is an explicit exception to withholding output:
missing/blank titles, unusable detail paths, and non-object rows are recorded in
`malformed_records` with `failure_reason=malformed_source_record`, the original raw
record, specific reasons, and pass/offset observations. Valid neighboring records
continue through detail retrieval. Missing required detail title or requisition ID
is also recorded and skipped, without inventing source facts. Transport failures,
identity conflicts, and other detail validation failures still fail the crawl.

Pagination counts include both valid and malformed source records. A usable path
remains the listing identity; otherwise exact raw JSON is used only as an opaque
pagination/audit fingerprint, never as a job ID. Duplicate ambiguous malformed
rows cannot artificially satisfy a source count. Diagnostics are deduplicated
across passes and terminal probes. `malformed_records_skipped` records unique
skips; `valid_listings` records detail-eligible listings. `pagination_complete`
describes enumeration; `extraction_complete=false` explicitly indicates that
malformed records prevented full extraction even when valid output succeeds.

Every listing is fetched through its official CXS detail path. Normal operation
uses bounded workers with one HTTP session per thread; injected test sessions use
one worker. Timeouts, connection errors, HTTP 429, and selected 5xx responses get
up to three attempts. Exhausted failures and malformed details are recorded, all
other detail attempts finish, and the crawl fails rather than publishing partial
results. Canonical URLs must remain on the configured public Workday origin/site.
When detail exposes a posting slug, it must agree with the requested listing slug.

Detail requisition IDs determine stable company-prefixed IDs. Identical postings
sharing a requisition ID are collapsed and counted; conflicting records with the
same requisition ID fail visibly. No source posting is filtered by title, fit,
availability, seniority, or resume evidence in the adapter.

## Existing raw schema mapping

| Source fact | Raw field |
| --- | --- |
| `jobReqId` | `external_job_id`; stable `job_id` |
| `title` | `title` |
| `location` and `additionalLocations` | `location`, joined with ` | ` |
| Exact location structure | `primary_location`, `all_locations` as a JSON string |
| `externalUrl` | `canonical_url`, tracking parameters removed |
| `startDate` | `posting_date`; blank if absent |
| `jobDescription` | `full_job_description_raw`, exact HTML |
| HTML text extraction | `description`, full normalized text |
| ATS and crawl provenance | `source_type=workday`, source key/URL, `retrieved_at` |

The new location and raw-description fields are optional string-valued source
facts in the shared validator; other adapter output formats are unchanged. No
responsibilities, qualifications, compensation, status, or fit fields are required.
The exact raw description is preserved even though the convenience plain-text
representation normalizes whitespace.

## Independent evaluation

`scripts/eval_workday.py` invokes the adapter with source configuration only,
applies the existing PM candidate filter, saves evaluation-run outputs, and **then**
opens the independent reference file. It accepts JSONL, a named reviewed XLSX
sheet, or a combined CSV with `company`, `job_id` (requisition ID), `title`,
`locations`, and `canonical_job_url`. CSV company selection and field mapping occur
only in the evaluator. Duplicate reference identities are rejected.
An expected count guards against accidentally evaluating the earlier broad
candidate snapshots as the reviewed reference set. Reference hashes are recorded
and checked after reading; references are never rewritten.

Example:

```powershell
.\.venv\Scripts\python.exe scripts/eval_workday.py --source adobe --reference data/evals/workday/adobe_product_management_snapshot.jsonl --expected-count 38 --output-dir data/evals/workday/adapter/adobe
```

For the reviewed workbooks, use `--reference <path> --sheet 'Likely PM'` and the
appropriate independently supplied expected count. Reports include raw and
candidate benchmark matches, recall, missing IDs with raw-versus-filter reasons,
extras for human review, duplicates, completeness, and source/detail failures.
Extras are not assumed false positives. This harness does not update production
discovery or classification outputs or Google Sheets.

To evaluate a frozen reference against saved discovery without network requests,
add `--saved-crawl-dir data/evals/workday/adapter/adobe` and select a separate
`--output-dir`. Saved raw records must validate and agree with successful, complete
crawl telemetry. The existing PM filter is applied before opening the reference.
Reports preserve original crawl timestamps and record the new evaluation time.
See [frozen v1 results](discovery_workday_frozen_v1_report.md).

## Limitations

- Public `*.wdN.myworkdayjobs.com` CXS sites only; authenticated, custom-proxy, or
  non-CXS career portals are not supported. A Phenom-only facet is not a CXS facet.
- CXS may cap broad results at 2,000. Queries reporting 2,000 or more fail
  conservatively; configure narrower independent source facets. Automatic
  partitioning of capped boards is not implemented, because overlapping or
  unassigned facet membership requires a separate coverage proof.
- A repeated page without a source count is ambiguous and fails. Two equal
  passes cannot make a changing live source an atomic snapshot.
- Missing full descriptions still fail. Missing required titles or requisition
  IDs are diagnosed and skipped; no truncated/unstable raw record is returned.
  No browser bypass or benchmark fallback is used.
- Source-side PM family semantics and the repository's broad title filter may
  disagree. Evaluation reports those misses; it does not tune the filter to the
  reference set.
