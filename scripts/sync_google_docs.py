"""Disabled placeholder for the future Google Docs synchronization layer.

Intended workflow (not implemented):
1. Validate sources/source_registry.yaml and its unique, safe logical names;
   skip and report unconfigured entries with missing Drive IDs.
2. Authenticate using credentials and OAuth tokens stored outside Git.
3. Fetch each registered Google Doc by Drive file ID with read-only access.
4. Export readable Markdown or plain text as UTF-8 with LF line endings.
   Never commit credentials, tokens, cookies, sessions, API keys, passwords,
   secrets, or .env contents; block affected exports if secrets are encountered.
5. Calculate SHA-256 over the exact snapshot bytes and compare with the
   corresponding source's previous successful hash.
6. Atomically replace sources/current/<logical_name>.md only if content changed.
7. Record the file ID, UTC success timestamp, and hash in
   data/source_sync_state.json after successful sync, including unchanged content.
8. Report new, changed, unchanged, and failed sources without logging content
   or authentication material. Preserve prior snapshots/state on fetch failure.
9. Commit only if at least one source actually changed; stage only changed
   snapshots and sync state. Use "Sync latest career source documents".
   Timestamp-only state updates remain local until a content-changing sync.

Google Docs remain the authoring source of truth. Never edit snapshots as a
substitute for editing the original Docs. Git tracks complete latest snapshots
and maintains revision history without manual versioned copies.
No sync, Git commits, candidate evidence mutations, job discovery, or
authentication are implemented here.
"""


def main():
    """Stop explicitly without network access, credential reads, or file writes."""
    print("Google Docs sync is not implemented. No authentication or sync performed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
