"""Sync one registered Google Doc using read-only OAuth; never commit or push.

Usage: python scripts/sync_google_docs.py --source data_platform
Install dependencies: python -m pip install -r scripts/requirements-sync.txt
Credentials and token default to %LOCALAPPDATA%/pm-job-search-agent/ on Windows.
Google Docs are authoritative; edit the original, not the generated snapshot.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DOC_MIME = "application/vnd.google-apps.document"


class SyncError(Exception):
    """A safe, user-facing error that contains no authentication material."""


def normalize(content):
    # Preserve indentation, Markdown hard breaks, lists, tables and code blocks.
    return content.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, suffix=".tmp", delete=False) as f:
            temp_path = Path(f.name)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def load_source(root, name):
    registry = yaml.safe_load((root / "sources/source_registry.yaml").read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        raise SyncError("Invalid source registry.")
    matches = [s for s in registry["sources"] if isinstance(s, dict) and s.get("logical_name") == name]
    if len(matches) != 1:
        raise SyncError("Select exactly one uniquely registered source with --source.")
    source = matches[0]
    for key in ("logical_name", "drive_id", "title", "type", "output"):
        if not isinstance(source.get(key), str) or not source[key].strip():
            raise SyncError(f"Source is missing required registry field: {key}.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise SyncError("Invalid logical source name.")
    if source["type"] != "google_doc":
        raise SyncError("Only google_doc sources are supported by this sync command.")
    output = (root / source["output"]).resolve()
    if not output.is_relative_to((root / "sources/current").resolve()) or output.suffix != ".md":
        raise SyncError("Snapshot output must be a Markdown file under sources/current/.")
    return source, output


def load_state(path):
    if not path.exists():
        return {"schema_version": 1, "sources": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("schema_version") != 1 or not isinstance(state.get("sources"), dict):
        raise SyncError("Invalid sync state; existing state was not overwritten.")
    if any(not isinstance(v, dict) for v in state["sources"].values()):
        raise SyncError("Invalid source state entry.")
    return state


def authenticate(credentials_path, token_path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    for path in (credentials_path, token_path):
        if path.resolve().is_relative_to(ROOT):
            raise SyncError("OAuth credentials and tokens must be outside this repository.")
    if credentials_path.resolve() == token_path.resolve():
        raise SyncError("Credentials and token must use different files.")
    creds = None
    result = "cached token"
    try:
        if token_path.exists():
            token_data = json.loads(token_path.read_text(encoding="utf-8"))
            if set(token_data.get("scopes", [])) != set(SCOPES):
                raise SyncError("Existing token does not have exactly Drive read-only scope. Use a separate token path.")
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        if creds and not creds.valid and creds.refresh_token:
            creds.refresh(Request())
            result = "refreshed token"
        if not creds or not creds.valid:
            if not credentials_path.is_file():
                raise SyncError(f"OAuth desktop credentials are missing: {credentials_path}")
            config = json.loads(credentials_path.read_text(encoding="utf-8"))
            if "installed" not in config:
                raise SyncError("Credentials must be a Google OAuth Desktop app client.")
            flow = InstalledAppFlow.from_client_config(config, SCOPES, autogenerate_code_verifier=True)
            print("Browser authorization required: sign in to the account with access to this document and allow read-only Drive access.", flush=True)
            creds = flow.run_local_server(
                host="localhost", port=0, open_browser=True, timeout_seconds=300,
                authorization_prompt_message="Authorization opened in your default browser. Waiting for consent...",
                success_message="Authorization complete. You may close this tab and return to Codex.",
                access_type="offline", prompt="consent",
            )
            result = "browser authorization"
        if set(creds.granted_scopes or creds.scopes or []) != set(SCOPES):
            raise SyncError("Authorization did not grant exactly the requested read-only scope.")
        atomic_write(token_path, creds.to_json() + "\n")
    except SyncError:
        raise
    except Exception:
        # OAuth exceptions can contain tokens or client secrets. Never echo them.
        raise SyncError("OAuth failed or timed out. Check the Desktop client, consent-screen test user, and browser authorization, then retry.") from None
    return creds, result


def fetch_markdown(session, source):
    base = "https://www.googleapis.com/drive/v3/files/" + quote(source["drive_id"], safe="")
    metadata = session.get(base, params={"fields": "id,name,mimeType,trashed,webViewLink", "supportsAllDrives": "true"}, timeout=60)
    check_response(metadata, "metadata fetch")
    details = metadata.json()
    if details.get("mimeType") != DOC_MIME or details.get("trashed"):
        raise SyncError("Registered source is not a live Google Doc.")
    exported = session.get(base + "/export", params={"mimeType": "text/markdown"}, timeout=60)
    check_response(exported, "Markdown export")
    return normalize(exported.content.decode("utf-8-sig"))


def check_response(response, operation):
    if response.status_code != 200:
        hints = {
            401: "Reauthorize the OAuth token.",
            403: "Check Drive API enablement, account access, export permissions, and the 10 MB export limit.",
            404: "Check the registered Drive ID and signed-in account's access.",
            429: "Google rate limit reached; retry later.",
        }
        raise SyncError(f"Drive {operation} failed (HTTP {response.status_code}). " + hints.get(response.status_code, "Retry later or check Google Drive API settings."))


def save_snapshot(source, output, state_path, state, content, timestamp):
    content = normalize(content)
    content_hash = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
    previous = state["sources"].get(source["logical_name"], {})
    changed = (previous.get("latest_content_hash") != content_hash
               or previous.get("google_drive_file_id") != source["drive_id"]
               or not output.exists())
    if changed:
        header = {
            "logical_name": source["logical_name"],
            "google_drive_file_id": source["drive_id"],
            "source_title": source["title"],
            "sync_timestamp": timestamp,
            "source_type": source["type"],
        }
        snapshot = "---\n" + yaml.safe_dump(header, sort_keys=False, allow_unicode=True) + "---\n\n" + content
        atomic_write(output, snapshot)
    state["sources"][source["logical_name"]] = {
        "logical_name": source["logical_name"],
        "google_drive_file_id": source["drive_id"],
        "last_successful_sync_at": timestamp,
        "latest_content_hash": content_hash,
    }
    atomic_write(state_path, json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    return content_hash, "changed" if changed else "unchanged"


def main():
    default_auth = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share")) / "pm-job-search-agent"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="One registry logical name; no bulk sync option")
    parser.add_argument("--credentials", type=Path, default=default_auth / "credentials.json")
    parser.add_argument("--token", type=Path, default=default_auth / "token.json")
    args = parser.parse_args()
    try:
        source, output = load_source(ROOT, args.source)
        state_path = ROOT / "data/source_sync_state.json"
        state = load_state(state_path)
        creds, auth_result = authenticate(args.credentials, args.token)
        print(f"Authentication: successful ({auth_result}; read-only Google Drive)", flush=True)
        from google.auth.transport.requests import AuthorizedSession
        with AuthorizedSession(creds) as session:
            content = fetch_markdown(session, source)
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        content_hash, status = save_snapshot(source, output, state_path, state, content, timestamp)
        print(json.dumps({"source": args.source, "title": source["title"], "output": str(output),
                          "content_hash": content_hash, "status": status}, indent=2))
        return 0
    except SyncError as exc:
        print(f"Sync stopped: {exc}", file=sys.stderr)
    except Exception as exc:
        # Do not expose request objects, response bodies, or OAuth data in tracebacks.
        print(f"Sync stopped ({type(exc).__name__}); check local file permissions, registry/state format, or network connectivity. No successful sync recorded.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
