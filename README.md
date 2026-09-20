# Product Management Job-Search Agent

## Status
The first 30-role calibration is stored locally with narrative classification and a persistent Google Sheets dashboard. No recurring discovery, applications, outreach, or automatic candidate-evidence editing is enabled. Google Docs and the Patent AI Sheet remain the authoring sources for career evidence and use a separate read-only source-sync token.

## Repository layout
- `AGENTS.md`: job-search operating contract.
- `config/`: search scope, calibrated taxonomy/rubric, and persistent dashboard ID.
- `profile/`: approved candidate evidence and preferences.
- `prompts/`: future workflow prompts; applications and outreach are disabled.
- `data/`: canonical calibration jobs, review queue, skills synthesis, annotations, discovery log, and source sync state.
- `sources/source_registry.yaml`: Google Doc identities and downstream dependencies.
- `sources/current/`: tracked latest project snapshots in readable `.md` files.
- `resumes/`: reserved for resume assets.
- `portfolio/`: reserved for portfolio assets.
- `scripts/sync_google_docs.py`: explicitly selected, read-only Google Doc/Sheet sync.
- `scripts/sync_google_sheets.py`: workbook-to-Markdown conversion for Sheets.
- `scripts/reprocess_calibration_jobs.py`: reprocesses only the registered calibration job IDs.
- `scripts/finalize_discovery.py`: future successful discovery finalization and automatic dashboard sync.
- `scripts/sync_job_dashboard.py`: create once/update the persistent human-review spreadsheet.

Empty asset directories contain `.gitkeep` files so Git preserves them.

## Classification and local data
The current rules are [classification rubric](config/classification_rubric.md), [taxonomy](config/role_taxonomy.yaml), [search scope](config/search_config.yaml), and confirmed [job preferences](profile/job_preferences.md). Exact JD facts, business domain, technology orientation, role cluster, candidate evidence, gap gating, bridge timing, strategic learning, posture, and action are separate fields. No numeric fit or priority score drives a lane. `Apply Now + Bridge` means apply immediately and prepare while awaiting an interview; the repository does not submit applications.

`data/jobs_raw.jsonl` is the canonical structured record. `data/jobs_master.csv` is a flat export; `data/review_queue.csv` excludes Skip/closed roles; `data/skills_synthesis.csv` counts normalized capabilities in live non-Skip roles. The Git files remain authoritative for the agent. `data/calibration_annotations.yaml` records the first 30 JD interpretations and candidate evidence mapping. Reprocessing preserves job IDs and original discovery timestamps. `data/calibration_lane_changes.csv` records the one-time change from the original calibration.

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

## Persistent job dashboard

The spreadsheet named **Shifia PM Job Search Dashboard** is created once. Its ID and URL are stored in `config/google_sheets.yaml`. Each later sync updates that same spreadsheet and its Dashboard, Jobs Master, Apply Now, Apply Now + Bridge, Build Toward, Skills Synthesis, and Calibration Feedback tabs. The Sheet is a review projection, not the machine-readable source of truth. User Review/Override/Notes on the feedback tab are retained by job ID on subsequent sheet syncs; overrides do not automatically retrain classification or modify the local canonical record.

The dashboard writer requests only `spreadsheets` edit and `drive.file` OAuth scopes. It reuses the Desktop OAuth **client credentials**, but stores its own `%LOCALAPPDATA%\pm-job-search-agent\dashboard_token.json`, outside Git. It never changes or broadens the existing `%LOCALAPPDATA%\pm-job-search-agent\token.json` with `drive.readonly` scope. Enable Google Sheets API and Google Drive API for the existing OAuth client project, authorize the separate dashboard token in the local browser, and use an account that can create the spreadsheet. Never commit either token, credentials, cookies, browser state or secrets.

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-sync.txt
.\.venv\Scripts\python.exe scripts/sync_job_dashboard.py
```

The manual command above is safe to rerun: a populated spreadsheet ID is updated, never recreated. A future successful discovery/classification job should pass canonical JSONL through the single finalizer:

```powershell
.\.venv\Scripts\python.exe scripts/finalize_discovery.py --input path\to\classified_jobs.jsonl
```

This entrypoint merges by stable job ID, validates the narrative schema, writes local jobs/review/skills files, then calls the Sheet sync. If the Sheet request fails, local data remains saved and the failure is reported; rerun `scripts/sync_job_dashboard.py`. The finalizer performs no web search itself. No recurring discovery is scheduled.

Offline verification:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```
