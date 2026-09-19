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
- `sources/current/`: ignored local directory for latest plain-text snapshots only.
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
Google Drive is the source of truth for detailed project documents. Keep editing
the original Google Docs; manual uploads and versioned document copies are not
part of this architecture. Local snapshots are disposable caches, and downstream
career evidence is derived material. No sources or candidate facts are populated.

The registry maps each logical source name to its Google Doc title, Google Drive
file ID, related career project, and downstream evidence files. A commented entry
template documents the fields without inventing real source details. Registry
metadata is tracked, so keep titles and project labels suitable for Git.

Intended future sync workflow (not implemented or enabled):
1. Validate registered sources and unique filename-safe logical names. Identify
   documents by Drive file ID, since titles can change.
2. Authenticate with read-only access using credentials and OAuth tokens stored
   outside the repository. Never commit credentials, tokens, cookies, browser
   state, secrets, or `.env` files; ignore rules provide additional protection.
3. Fetch the latest version of every registered Google Doc and export it as
   consistently normalized UTF-8 plain text.
4. Compute SHA-256 over the snapshot bytes and compare it with that source's
   previous successful hash. A first successful fetch is new; subsequent hashes
   identify changed versus unchanged content.
5. Atomically overwrite `sources/current/<logical_name>.txt`. Keep only the latest
   snapshot per source, with no timestamped copies or raw document Git history.
6. After each successful snapshot write, update that source's state with its
   logical name (map key), `google_drive_file_id`, `last_successful_sync_at`
   (UTC ISO 8601), and `latest_content_hash` (`sha256:<hex>`). This state records
   the latest success timestamp and hash; it must never contain document bodies,
   credentials, tokens, or secrets.
7. Report new, changed, unchanged, and failed sources using metadata only. On
   failure, preserve that source's previous snapshot and successful state; do not
   mark a failed attempt as a successful sync.

`sources/current/` is entirely ignored and is created locally in this scaffold.
Git does not preserve empty ignored directories, so a future sync implementation
must create it on fresh clones. Do not force-add snapshots to Git.

The Python placeholder exits with status 1 and an explicit not-implemented
message. It does not read credentials, authenticate, access the network, create
snapshots, or mutate state. No dependencies or scheduled synchronization are set
up. Downstream paths document intended dependencies only; career-evidence updates
are a separate future phase and are not implemented.

## Future operation
TODO: Define and authorize each workflow. No jobs will be searched, applications submitted, or people contacted by this scaffold.
