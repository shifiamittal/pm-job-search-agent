# OpenAI / Ashby integration

## Source contract
- Board identifier: `openai`, from https://jobs.ashbyhq.com/openai.
- Structured endpoint: `GET https://api.ashbyhq.com/posting-api/job-board/openai`.
- [Ashby public API documentation](https://developers.ashbyhq.com/docs/public-job-posting-api)
  describes a full list of currently published postings. There are no documented
  pagination parameters or cursors. The adapter uses one request with no title query.
- Completeness means every posting exposed by this public board response, not
  unpublished/internal vacancies or an independent audit of every employer page.
- Every returned job is extracted before the unchanged local PM filter, including
  direct-link/unlisted records if the API supplies them.

## Field mapping
The public API exposes ATS identity in `jobUrl`; the adapter validates the expected
Ashby host, board path and UUID, then retains that UUID as external_job_id. Raw
canonical URLs are individual Ashby job URLs with tracking removed. Reference URLs
remain the supplied OpenAI careers URLs, and existing ID-first evaluation matches
them without requiring URL equality.

Primary and secondary location labels are whitespace-normalized, deduplicated in
source order and joined with ` | `. No state/country is inferred. descriptionPlain
is preserved as text. publishedAt denotes last publication, so it is retained in
source_updated_at; posting_date remains blank rather than asserting an original
posting date. No raw schema or classification changes were needed.

## Shared compatibility changes
CrawlError moved to discovery/errors.py and is still importable from greenhouse.py.
Greenhouse retrieval/conversion is otherwise unchanged. The orchestrator dispatches
the selected adapter and still permits only one source per invocation. With both
sources enabled, specify --source explicitly. Latest JSONL/CSV files merge the
selected board snapshot with unchanged records from other sources; run snapshots
remain source-only. Historical snapshots are preserved even if a job disappears.

The evaluator now checks the latest telemetry for each source, so another source's
success cannot hide an earlier source's latest failed attempt. Matching logic is
unchanged. Default reports cover all reference records against combined snapshots.

Existing limitations remain: execute serially; concurrent writers are unsupported;
latest exports are not an atomic multi-file transaction. A write failure is logged
and blocks default evaluation. No scheduler, dashboard or downstream classification
is invoked, and neither adapter reads reference data.
