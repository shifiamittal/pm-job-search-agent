# Product Management Job-Search Agent

## Status
Single-source Google Docs sync is implemented. No scheduled sync, job discovery,
career-evidence generation, applications, or outreach are enabled by this script.

## Repository layout
- `AGENTS.md`: job-search operating contract.
- `config/`: search preferences, role taxonomy, and classification rubric placeholders.
- `profile/`: candidate profile, career evidence, and application answer placeholders.
- `prompts/`: discovery, classification, application, and outreach prompt placeholders.
- `data/`: empty job-search files and metadata-only source sync state.
- `sources/source_registry.yaml`: Google Doc identities and downstream dependencies.
- `sources/current/`: tracked latest project snapshots in readable `.md` files.
- `resumes/`: reserved for resume assets.
- `portfolio/`: reserved for portfolio assets.
- `scripts/sync_google_docs.py`: explicitly selected, read-only Google Doc sync.

Empty asset and script directories contain `.gitkeep` files so Git preserves them.

## Configuration
TODO: Supply user-approved search preferences, role definitions, and classification criteria.

## Candidate information
TODO: Supply verified candidate facts and supporting evidence. Do not infer missing facts.

## Data and privacy
Job-search data files are intentionally empty, with no headers or records. TODO: Define job schemas before use.
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
user-supplied sources and evidence rules. Only `data_platform` is authorized for
the initial test. Sheets are not supported by this command. Placeholder snapshots
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
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p test_sync_google_docs.py -v
```

Downstream paths document dependencies only. Career-evidence updates are not
implemented. Do not edit snapshots as a substitute for editing Google Docs.

## Future operation
TODO: Define and authorize each workflow. No jobs will be searched, applications submitted, or people contacted by this scaffold.
