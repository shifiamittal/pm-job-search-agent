# Product Management Job-Search Agent

## Status

`shortlist/` **v1.2.0 is the sole authoritative role-evaluation and shortlist contract for new runs**.
Workflow: Role Understanding → Career / Requirements Mapping → Shortlist Decision
→ Validation. [Migration status and dependency map](docs/shortlist_v1_migration.md).
Raw discovery applies the deterministic US/India Phase-1 geography gate before producing
PM candidates; candidate-source sync remains independent. The historical
30-role calibration is preserved; it has not been reclassified under v1.

## Repository layout

- `AGENTS.md`: repository instructions and shortlist authority.
- `shortlist/`: versioned stage contracts and structured state schema.
- `resume_agent/`: canonical downstream resume-generation workflow, evidence rules, manifest/template discipline, and QA gates.
- `prompts/classification.md`: thin entrypoint to the versioned stages.
- `config/`: search metadata and retained dashboard identity; no legacy decision rubric.
- `profile/`, `sources/`, `resumes/`, `portfolio/`: existing candidate sources/assets.
- `data/`: historical calibration and independent raw discovery/evaluation artifacts.
- `scripts/shortlist_contract.py`: read-only schema/structural consistency validation.
- `scripts/run_shortlist_job.py`: four-stage, single-job execution with full candidate context.
- `scripts/run_shortlist_batch.py`: sequential, resumable orchestration over CSV/JSONL inputs.
- `scripts/shortlist_model.py`: stateless OpenAI Responses transport.
- `scripts/discovery/geography.py`: deterministic US/India discovery gate.
- `scripts/filter_discovery_geography.py`: offline CSV/JSONL geography-filter command.
- `scripts/job_framework.py`: historical-data reads and explicit retired-API guards.
- `scripts/reprocess_calibration_jobs.py`, `scripts/finalize_discovery.py`,
  `scripts/sync_job_dashboard.py`: blocked legacy entrypoints pending v1 integration.
- `scripts/sync_google_docs.py`, `scripts/sync_google_sheets.py`: unchanged, independent
  read-only candidate-source export tools.

## Shortlisting and historical data

Use [Role Understanding](shortlist/role_understanding.md),
[Career / Requirements Mapping](shortlist/career_requirements_mapping.md),
[Shortlist Decision](shortlist/shortlist_decision.md), and
[Controller / Validation](shortlist/controller_validation.md), with
[schema.yaml](shortlist/schema.yaml). There is no alternate classification rubric.

`data/jobs_raw.jsonl`, `jobs_master.csv`, `review_queue.csv`, `skills_synthesis.csv`,
`calibration_annotations.yaml`, `calibration_lane_changes.csv`, and historical log
entries are retained read-only. Old classifications are historical, not current
recommendations, and are never automatically mapped to v1 outcomes. The existing
review queue is not a v1 queue. `load_legacy_jobs()` reads original records unchanged.

The protected `profile/job_preferences.md` retains historical policy wording. Its
location scoring, old lanes, title/economics gates and automatic AI preference are
superseded by v1; confirmed facts/preferences and unresolved questions are preserved.

Install local validation dependencies and validate an already completed record:

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-shortlist.txt
.\.venv\Scripts\python.exe scripts/shortlist_contract.py --input path\to\completed_shortlist.json
```

This checks schema and cross-stage structure only. It does not verify source facts,
produce decisions, set validation flags, persist jobs, enqueue resumes, or replace
semantic controller review. No selective evidence retrieval is implemented.

## Single-job shortlist baseline

The [single-job runner](docs/single_job_shortlist.md) executes the four authoritative
stages using the full JD and all five candidate files, without selective retrieval.
Set `OPENAI_API_KEY` and explicitly select an API model via `SHORTLIST_MODEL` or
`--model`, then run one normalized job JSON object:

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-shortlist.txt
.\.venv\Scripts\python.exe scripts/run_shortlist_job.py --input path\to\job.json --model $env:SHORTLIST_MODEL
```

Each invocation creates a new ignored `local_private/shortlist/<run_id>/` directory
with `job_state.json`, `shortlist_state.json` (on completed controller review), and
`review.md`. The envelope retains original metadata; `shortlist_state.json` conforms
to the unchanged v1 schema. Model review is not independent human verification.
The [batch runner](docs/batch_shortlist.md) calls this same execution path sequentially
with isolated per-job state, incremental summaries, failure isolation, and safe resume.
No cross-job conversation, selective evidence retrieval, legacy writes, dashboard sync,
programmatic resume generation, applications or outreach is enabled. Accepted roles may
continue through the documented `resume_agent/` workflow manually/agentically, but a full
resume runtime is not yet implemented in this repository.

## Resume-generation workflow

For roles accepted by shortlist v1.2, use [resume_agent/README.md](resume_agent/README.md).
The resume workflow is recovered from the Resume Agent Starter Kit and integrated so that
`shortlist/` v1.2 remains authoritative upstream. The original starter-kit snapshot is preserved
under `docs/source_snapshots/resume_agent_starter_kit_v1/` for provenance.

Important: the starter kit's original `02_JOB_SEARCH_SHORTLIST_MODE.md` predates the v1.2
capability/domain split. New shortlist runs must use `shortlist/`; `resume_agent/02_...` is only
an integration bridge.

The downstream sequence is Evidence Retrieval → Hiring Criteria Evidence Mapping → Resume
Strategy / Architecture → Resume Writing → Content Freeze / Manifest → Document Generation →
Exact Content Validation → Render / Page-Space Audit → compression only if needed → revalidate → Final QA.

The workflow specification exists; a complete programmatic resume runner does not yet.

## Candidate information
Use the verified candidate profile, career evidence, conflicts, job preferences, and approved master resume. Do not infer missing facts or change those files during discovery.

## Data and privacy
`data/source_sync_state.json` stores source IDs, successful sync timestamps, and content hashes only.
Store local private material under ignored `private/`, `local_private/`, or `*.local.*` paths.
Tracked profile and asset paths are not private storage; review their contents before committing.

## Living Google Docs sources
Google Docs remain the authoring source of truth for detailed project documents.
Edit the original Google Doc, never its snapshot as a substitute. Complete latest
exports will be committed to this private repository so Codex can read the full
project context. Git maintains revision history automatically; no manual uploads,
versioned filenames, or timestamped document copies are required.

```text
Google Docs
↓
automated sync
↓
sources/current/*.md
↓
career_evidence.md (profile/career_evidence.md)
↓
job classification / resume / application system
```

This is the intended pipeline, not an active automation. Career-evidence updates
and downstream actions are outside this architecture change.

The registry maps each logical source name to its Google Doc title, Google Drive
file ID, related career project, and downstream evidence files. It contains six
user-supplied sources and evidence rules. Each run selects exactly one source.
Google Docs and Sheets are supported. Placeholder snapshots
are not evidence or successful exports; Amazon sources remain unregistered.

Single-source sync workflow:
1. Validate registered sources and unique filename-safe logical names. Identify
   documents by Drive file ID, since titles can change. Reject an incomplete or
   unsupported selected entry; never guess IDs or locate documents by title.
2. Authenticate with read-only access using credentials and OAuth tokens stored
   outside the repository. Never commit credentials, tokens, cookies, browser
   sessions, API keys, passwords, secrets, or `.env` files; ignore rules provide
   additional protection. Keep all authentication material outside Git, including
   any such material encountered inside source content; block and report an
   affected export rather than committing secrets.
3. Fetch only the explicitly selected Google Doc and use Drive's native export as
   readable Markdown (or plain text in the `.md` file), consistently normalized
   to UTF-8 with LF line endings.
4. Compute SHA-256 over normalized document content, excluding the generated
   metadata header, and compare it with that source's
   previous successful hash. A first successful fetch is new; subsequent hashes
   identify changed versus unchanged content.
5. Atomically overwrite `sources/current/<logical_name>.md` only when content
   changed. Leave unchanged snapshots untouched. Keep only the latest snapshot
   at each path; Git holds prior revisions.
6. After each successful source sync, including unchanged content, update its
   state with its
   logical name (map key), `google_drive_file_id`, `last_successful_sync_at`
   (UTC ISO 8601), and `latest_content_hash` (`sha256:<hex>`). This state records
   the latest success timestamp and hash; it must never contain document bodies,
   credentials, tokens, or secrets.
7. Report new, changed, unchanged, and failed sources using metadata only. On
   failure, preserve that source's previous snapshot and successful state; do not
   mark a failed attempt as a successful sync.

8. Stop for human inspection. The script never stages, commits, or pushes.
   Future auto-commit remains disabled; if later enabled, it should commit only
   when a source changed, using `Sync latest career source documents`.

`sources/current/` is tracked. Each successful initial export replaces its
placeholder. Unchanged content leaves the snapshot and its header timestamp
untouched, while sync state records the latest successful check. Native Markdown
export retains supported headings, lists, and tables; complex layouts and images
may not translate completely. Drive limits API exports to 10 MB; export failures
are reported, never silently truncated or replaced with browser scraping.

## Run the authorized Data Platform test

Use Python 3.10+ and an ignored local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-sync.txt
.\.venv\Scripts\python.exe scripts/sync_google_docs.py --source data_platform
```

Place Desktop OAuth client credentials at
`%LOCALAPPDATA%\pm-job-search-agent\credentials.json`. The browser consent flow
requests `https://www.googleapis.com/auth/drive.readonly` and stores `token.json`
in the same directory. Both paths must remain outside this repository. Optional
`--credentials` and `--token` arguments accept other external paths. The script
does not print token contents or client secrets. Authorization waits up to five
minutes; rerun if it times out. Use an account with access to the selected Doc.

Exit code 0 means a successful changed or unchanged sync; 1 means failure.
Run offline regression tests without authenticating or syncing:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_sync_google*.py' -v
```

Downstream paths document dependencies only. Career-evidence updates are not
implemented. Do not edit snapshots as a substitute for editing Google Docs.

## Google Sheets synchronization

Run `scripts/sync_google_docs.py --source patent_ai` with the same virtual-environment
Python and OAuth token. No separate credentials or additional OAuth scopes are
needed. Drive exports the spreadsheet as XLSX in memory; openpyxl reads all visible
worksheets and cached formula values. The intermediate workbook is never saved.

Each tab gets its own heading and used cell range. Empty outer regions are omitted;
original row numbers, column letters, header rows, zero values, dates, versions,
notes, and percentage units are retained. Narrow tabs become Markdown tables.
Wide, long-text, or sparse tabs become cell-addressed rows without dropping populated
columns. Hidden tabs are excluded; hidden rows/columns within visible tabs are retained.

Merged ranges are described, not visually merged. Styling, charts, images, threaded
discussions, and custom display formatting are not reproduced. Numeric values are
kept rather than rounded to display precision; dates use ISO format. If a formula
lacks a cached value, its formula is retained with a warning rather than silently
exporting a blank. Cell notes are retained when present in the Drive workbook export.
Normalized Markdown content feeds the existing SHA-256/state/change-detection logic.
The script does not commit or push; those remain explicit repository actions.

## Persistent job dashboard — integration blocked

The existing **Shifia PM Job Search Dashboard** identity remains in
`config/google_sheets.yaml`. Synchronization is disabled in configuration and code.
Existing remote tabs and user feedback are untouched historical views, not v1
recommendations. This migration does not authenticate, write to, or replace the Sheet.

The old dashboard writer, calibration reprocessor and finalizer exit with an explicit
integration error before any file writes or network/authentication. Even changing
`sync_enabled` cannot reactivate the legacy writer. Future integration needs v1
records, durable identity, feedback preservation, accepted-record routing, and a
reviewed projection to the same Sheet. It must not convert old labels to new outcomes.
The original OAuth credentials and tokens remain outside Git; candidate-source sync
is unaffected. See the migration note for the complete pending work.

Run the full offline suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

## Raw job discovery (v1)
Discovery is now separated from downstream fit/classification. `config/job_sources.yaml`
defines job sources (distinct from `sources/source_registry.yaml`, which is candidate
evidence). `scripts/discover_jobs.py` implements deterministic Greenhouse, Ashby, Microsoft, and Workday
retrieval and writes all raw jobs plus a high-recall PM-candidate subset under
`data/discovery/`. Each source crawl appends telemetry to
`data/discovery/crawl_runs.jsonl`.

Run one selected source per invocation:

```bash
python scripts/discover_jobs.py --source anthropic
python scripts/discover_jobs.py --source openai
python scripts/discover_jobs.py --source microsoft
```

Curate a separate reference set in `data/evals/discovery_reference.jsonl`, then run:

```bash
python scripts/eval_discovery.py
```

The eval emits Google-Sheets-friendly CSV reports in `data/evals/latest/`. We are
intentionally not adding an eval dashboard tab until the metrics/failure workflow
stabilize; the existing dashboard can be extended later without coupling discovery
to presentation logic.

Each crawl refreshes only the selected source in the latest combined exports;
other source records retain their original retrieval timestamps. Run-specific
snapshots remain source-only. Evaluation checks each source's latest crawl status
and reports each company separately. See [Ashby integration](docs/discovery_ashby.md)
and the [OpenAI live report](docs/discovery_openai_live_report.md).

Microsoft enumerates its official Product Management facet and retains US/India
candidates after detail availability verification and internship exclusion.
Unavailable and uncertain jobs remain in raw diagnostics. See [Microsoft discovery](docs/discovery_microsoft.md)
for pagination, drift reconciliation, retry behavior and benchmark separation.

Workday uses one configurable CXS adapter with two-pass enumeration and complete
detail retrieval. The Adobe, NVIDIA, and CrowdStrike configurations fetch every
US/India job before applying the unchanged broad PM title filter. See
[Workday discovery](docs/discovery_workday.md) and the
[Workday live evaluation](docs/discovery_workday_live_report.md).

## Source detection benchmark

Inspect careers URLs without crawling job boards or adding source adapters:

```bash
python scripts/detect_sources.py --benchmark data/evals/source_detection/target_company_source_map_v1.csv
```

The detector uses public URL, redirect, page, job-link, metadata and linked-script
evidence. Expected labels are evaluation-only. Results, mismatches, metrics and
request audits are written under `data/evals/source_detection/latest/`.
Blocked or inconclusive sources remain unresolved; a custom/native front end does
not prove the absence of a third-party ATS. See the
[source detection review](docs/source_detection_v1.md) for results and limitations.
