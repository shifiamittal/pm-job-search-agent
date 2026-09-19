# Product Management Job-Search Agent

## Status
Scaffold only. No candidate facts, job records, automation, or search integration have been configured.

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
- `scripts/sync_google_docs.py`: disabled source synchronization placeholder.

Empty asset and script directories contain `.gitkeep` files so Git preserves them.

## Configuration
TODO: Supply user-approved search preferences, role definitions, and classification criteria.

## Candidate information
TODO: Supply verified candidate facts and supporting evidence. Do not infer missing facts.

## Data and privacy
Job-search data files are intentionally empty, with no headers or records. TODO: Define job schemas before use.
`data/source_sync_state.json` contains only an empty source map and schema version.
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
file ID, related career project, and downstream evidence files. Seven logical
sources have placeholder snapshots: `deep_enterprise`, `data_platform`,
`forecasting_agent`, `patent_ai`, `amazon_fintech`, `amazon_ml_platform`, and
`amazon_supply_chain`. Exact Google Doc titles, Drive IDs, and project mappings
remain null until supplied. Placeholders are not evidence or successful exports.

Intended future sync workflow (not implemented or enabled):
1. Validate registered sources and unique filename-safe logical names. Identify
   documents by Drive file ID, since titles can change. Skip incomplete entries
   and report them as unconfigured; never guess IDs or locate documents by title.
2. Authenticate with read-only access using credentials and OAuth tokens stored
   outside the repository. Never commit credentials, tokens, cookies, browser
   sessions, API keys, passwords, secrets, or `.env` files; ignore rules provide
   additional protection. Keep all authentication material outside Git, including
   any such material encountered inside source content; block and report an
   affected export rather than committing secrets.
3. Fetch the latest version of every registered Google Doc and export it as
   readable Markdown (or plain text in the `.md` file), consistently normalized
   to UTF-8 with LF line endings.
4. Compute SHA-256 over the snapshot bytes and compare it with that source's
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

8. Commit changed snapshots and their sync metadata only when at least one source
   actually changed, using `Sync latest career source documents`. Stage only
   intended sync outputs, never unrelated user changes or authentication files.
   Timestamp-only state updates do not trigger a commit; they may remain local
   until the next content-changing sync. This architecture commit is separate
   from the future content-based sync commit rule.

`sources/current/` is tracked. Its seven initial files contain only explicit
placeholder notices; no Google Docs have been fetched. Sync state remains empty
until a real successful sync, with no invented hashes or timestamps.

The Python placeholder exits with status 1 and an explicit not-implemented
message. It does not read credentials, authenticate, access the network, create
snapshots, or mutate state. No dependencies or scheduled synchronization are set
up. Downstream paths document intended dependencies only; career-evidence updates
are a separate future phase and are not implemented.

## Future operation
TODO: Define and authorize each workflow. No jobs will be searched, applications submitted, or people contacted by this scaffold.
