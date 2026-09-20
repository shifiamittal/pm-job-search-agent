"""Create once, then update the persistent PM job-search Google Spreadsheet.

Usage: python scripts/sync_job_dashboard.py
The dashboard writer uses separate OAuth scopes and a separate token outside Git.
It never changes the existing read-only career-source token or Google Docs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from pathlib import Path

import yaml

from job_framework import ROOT, load_canonical_jobs, review_queue, synthesize_skills, validate_jobs

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
API = "https://sheets.googleapis.com/v4/spreadsheets"
TABS = ["Dashboard", "Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward",
        "Skills Synthesis", "Calibration Feedback"]
JOB_COLUMNS = [
    ("Company", "company"), ("Role Title", "role_title"),
    ("Posting Date", "posting_date"), ("Location", "location"),
    ("Compensation", "compensation"), ("Industry / Sector", "sector"),
    ("Technology / Product Focus", "technology_product_focus"),
    ("Functional Requirements", "key_functional_requirements"),
    ("My Relevant Experience", "candidate_relevant_evidence"),
    ("Key Gaps / Risks", "key_gaps_risks"),
    ("System Recommendation", "application_lane"),
    ("My Decision", "my_decision"), ("My Notes", "my_notes"),
    ("Stage", "stage"), ("Job URL", "canonical_url"),
    ("Last Verified", "last_verified_at"),
]
SKILL_COLUMNS = [
    ("Skill / Capability", "skill"), ("# Roles Requiring It", "role_count"),
    ("Example Companies", "example_companies"), ("Example Roles", "example_roles"),
    ("Candidate Current Strength", "candidate_current_strength"),
    ("Strategic Leverage", "strategic_leverage"),
    ("Recommended Action", "recommended_action"), ("Rationale", "rationale"),
]
FEEDBACK_HEADERS = ["Company", "Role", "System Recommendation", "My Decision", "My Notes",
                    "Stage", "User Override", "Job URL", "Job ID"]
DECISIONS = ["Apply", "Maybe", "Do Not Apply", "Needs Review"]
STAGES = ["Discovered", "Resume Prep", "Ready to Apply", "Applied", "Interviewing", "Closed"]


class DashboardError(Exception):
    """User-facing failure without OAuth or HTTP response body material."""


def config_path(root):
    return root / "config/google_sheets.yaml"


def read_config(root=ROOT):
    config = yaml.safe_load(config_path(root).read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict) or config.get("spreadsheet_title") != "Shifia PM Job Search Dashboard":
        raise DashboardError("Invalid dashboard configuration")
    return config


def write_config(root, config):
    from job_framework import _atomic_text
    _atomic_text(config_path(root), yaml.safe_dump(config, sort_keys=False, allow_unicode=True))


def default_auth_dir():
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share")) / "pm-job-search-agent"


def authenticate(root=ROOT, credentials_path=None, token_path=None):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    auth_dir = default_auth_dir()
    credentials_path = Path(credentials_path or auth_dir / "credentials.json")
    token_path = Path(token_path or auth_dir / "dashboard_token.json")
    source_token = (auth_dir / "token.json").resolve()
    if any(p.resolve().is_relative_to(root.resolve()) for p in (credentials_path, token_path)):
        raise DashboardError("OAuth credentials and dashboard token must remain outside Git")
    if token_path.resolve() in {credentials_path.resolve(), source_token}:
        raise DashboardError("Dashboard token must be separate from credentials and source-read token")
    if not credentials_path.is_file():
        raise DashboardError(f"Desktop OAuth credentials missing at {credentials_path}")
    try:
        creds = None
        result = "cached dashboard token"
        if token_path.exists():
            info = json.loads(token_path.read_text(encoding="utf-8"))
            if set(info.get("scopes", [])) != set(SCOPES):
                raise DashboardError("Dashboard token scopes differ; use only the separate writer token")
            creds = Credentials.from_authorized_user_info(info, SCOPES)
        if creds and not creds.valid and creds.refresh_token:
            creds.refresh(Request())
            result = "refreshed dashboard token"
        if not creds or not creds.valid:
            config = json.loads(credentials_path.read_text(encoding="utf-8"))
            if "installed" not in config:
                raise DashboardError("Credentials must be a Google OAuth Desktop app client")
            flow = InstalledAppFlow.from_client_config(config, SCOPES, autogenerate_code_verifier=True)
            print("Authorize the separate dashboard writer in your browser (Sheets edit and Drive file access only).", flush=True)
            creds = flow.run_local_server(
                host="localhost", port=0, open_browser=False, timeout_seconds=300,
                authorization_prompt_message="If the browser did not open, use this dashboard authorization URL: {url}\nWaiting for consent...",
                success_message="Dashboard authorization complete. Return to Codex.",
                access_type="offline", prompt="consent",
            )
            result = "browser authorization"
        if set(creds.granted_scopes or creds.scopes or []) != set(SCOPES):
            raise DashboardError("Authorization did not grant only the requested dashboard scopes")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        from job_framework import _atomic_text
        _atomic_text(token_path, creds.to_json() + "\n")
        return creds, result
    except DashboardError:
        raise
    except Exception:
        raise DashboardError("Dashboard OAuth failed or timed out; check Sheets/Drive APIs, consent-screen test user and browser authorization") from None


def api_json(session, method, url, operation, **kwargs):
    try:
        response = session.request(method, url, timeout=90, **kwargs)
    except Exception:
        raise DashboardError(f"Google Sheets {operation} failed due to network/authorization connectivity") from None
    if response.status_code < 200 or response.status_code >= 300:
        hints = {401: "Reauthorize dashboard_token.json", 403: "Enable Google Sheets and Drive APIs and check account access/scopes",
                 404: "Check persistent spreadsheet ID and account access", 429: "Wait for API quota"}
        # Report only Google's structured error codes, never its full response
        # body, which could contain account or request details.
        try:
            error = response.json().get("error", {})
            reasons = [item.get("reason") for item in error.get("errors", [])]
            reasons.extend(item.get("reason") for item in error.get("details", []) if isinstance(item, dict))
            reasons = [reason for reason in reasons if isinstance(reason, str) and reason.isidentifier()]
            code = error.get("status") if isinstance(error.get("status"), str) else ""
            detail = "; ".join(dict.fromkeys(([code] if code.isidentifier() else []) + reasons))
        except (ValueError, TypeError, AttributeError):
            detail = ""
        suffix = f" ({detail})" if detail else ""
        raise DashboardError(f"Google Sheets {operation} HTTP {response.status_code}{suffix}. " + hints.get(response.status_code, "Retry after checking Google API configuration"))
    return response.json() if response.content else {}


def serialize_job_rows(jobs, feedback=None):
    feedback = feedback or {}
    header = [name for name, _ in JOB_COLUMNS]
    rows = [header]
    for job in jobs:
        remembered = feedback.get(job["job_id"], {})
        rows.append([str(remembered.get(key, job.get(key, "")))
                     if key not in {"application_lane", "my_decision", "my_notes", "stage"} else
                     str("Skip" if key == "application_lane" and job[key] == "Build Toward" else
                         remembered.get(key, job.get(key, "")))
                     for _, key in JOB_COLUMNS])
    return rows


def serialize_feedback_rows(jobs, previous=None):
    previous = previous or {}
    rows = [FEEDBACK_HEADERS]
    for job in jobs:
        retained = previous.get(job["job_id"], {})
        rows.append([job["company"], job["role_title"],
                     "Skip" if job["application_lane"] == "Build Toward" else job["application_lane"],
                     retained.get("my_decision", job.get("my_decision", "")),
                     retained.get("my_notes", job.get("my_notes", "")),
                     retained.get("stage", job.get("stage", "Discovered")),
                     retained.get("user_override", job.get("user_override", "")),
                     job["canonical_url"], job["job_id"]])
    return rows


def parse_feedback(values):
    """Parse the current feedback tab; legacy cells are handled during migration."""
    if not values or values[0] != FEEDBACK_HEADERS:
        return {}
    return {row[8]: dict(zip(FEEDBACK_HEADERS, row)) for row in values[1:] if len(row) >= 9 and row[8]}


def normalize_legacy_review(value):
    """Retain a user's wording while separating an explicit decision from notes."""
    raw = value.strip()
    if not raw:
        return "", ""
    for pattern, decision in ((r"^do not apply\b[. :,-]*", "Do Not Apply"),
                              (r"^apply\b[. :,-]*", "Apply"),
                              (r"^maybe\b[. :,-]*", "Maybe"),
                              (r"^not sure\b[. :,-]*", "Needs Review")):
        match = re.match(pattern, raw, re.I)
        if match:
            return decision, raw[match.end():].strip()
    return "Needs Review", raw


def collect_live_feedback(values_by_tab, jobs):
    """Read decisions/notes from every review surface before rewriting tabs."""
    by_url = {job["canonical_url"].rstrip("/"): job["job_id"] for job in jobs}
    by_id = {job["job_id"]: job for job in jobs}
    feedback = {}
    for tab in ("Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward", "Calibration Feedback"):
        values = values_by_tab.get(tab, [])
        if not values:
            continue
        header = values[0]
        if "Job ID" not in header and "Job URL" not in header:
            raise DashboardError(f"Cannot preserve feedback on {tab}: no stable Job ID or URL column")
        for row in values[1:]:
            cells = dict(zip(header, row))
            job_id = cells.get("Job ID") or by_url.get(cells.get("Job URL", "").rstrip("/"))
            if not job_id or job_id not in by_id:
                continue
            target = feedback.setdefault(job_id, {})
            decision = cells.get("My Decision", "").strip()
            note = cells.get("My Notes", "").strip()
            if not decision and cells.get("User Review", ""):
                decision, legacy_note = normalize_legacy_review(cells["User Review"])
                note = "\n".join(part for part in (note, legacy_note) if part)
                target.setdefault("legacy_review", cells["User Review"])
            if not note and cells.get("User Notes", ""):
                note = cells["User Notes"].strip()
            if decision:
                if decision not in DECISIONS:
                    raise DashboardError(f"Invalid My Decision for {job_id} on {tab}: {decision}")
                if target.get("my_decision") and target["my_decision"] != decision:
                    raise DashboardError(f"Conflicting My Decision values for {job_id}; resolve them in the Sheet")
                target["my_decision"] = decision
            if note and note not in target.get("my_notes", "").split("\n\n"):
                target["my_notes"] = "\n\n".join(part for part in (target.get("my_notes", ""), note) if part)
            stage = cells.get("Stage", "").strip()
            if stage:
                if stage not in STAGES:
                    raise DashboardError(f"Invalid Stage for {job_id} on {tab}: {stage}")
                if target.get("stage") and target["stage"] != stage:
                    raise DashboardError(f"Conflicting Stage values for {job_id}; resolve them in the Sheet")
                target["stage"] = stage
            override = cells.get("User Override", "").strip()
            if override:
                target["user_override"] = override
    return feedback


def apply_feedback_to_jobs(jobs, feedback, root=ROOT):
    """Persist user authority locally before any full-sheet rewrite."""
    changed = False
    for job in jobs:
        values = feedback.get(job["job_id"], {})
        for key in ("my_decision", "stage", "user_override"):
            if values.get(key) and values[key] != job.get(key, ""):
                job[key] = values[key]
                changed = True
        note = values.get("my_notes", "")
        if note and note not in job.get("my_notes", ""):
            job["my_notes"] = "\n\n".join(part for part in (job.get("my_notes", ""), note) if part)
            changed = True
        if values.get("legacy_review") and not job.get("user_review"):
            job["user_review"] = values["legacy_review"]
            changed = True
    if changed:
        from job_framework import MASTER_FIELDS, REVIEW_FIELDS, _atomic_text, _csv_text
        validate_jobs(jobs, root)
        data = root / "data"
        _atomic_text(data / "jobs_raw.jsonl", "".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs))
        _atomic_text(data / "jobs_master.csv", _csv_text(MASTER_FIELDS, jobs))
        _atomic_text(data / "review_queue.csv", _csv_text(REVIEW_FIELDS, review_queue(jobs)))
    return changed


def dashboard_rows(jobs, skills, latest_new_count):
    live = [job for job in jobs if job["status"] == "Live"]
    counts = Counter(job["application_lane"] for job in live)
    technology = Counter(job["technology_orientation"] for job in live)
    domains = Counter(job["domain_fit"] for job in live)
    metrics = [
        ("Total live jobs", len(live)), ("New jobs from latest run", latest_new_count),
        ("Apply Now", counts["Apply Now"]), ("Apply Now + Bridge", counts["Apply Now + Bridge"]),
        ("Build Toward", counts["Build Toward"]), ("Skip", counts["Skip"]),
        ("Seattle / Bellevue / Redmond", sum(any(place in job["location"] for place in ["Seattle", "Bellevue", "Redmond"]) for job in live)),
        ("Remote US", sum(job["country"] == "US" and "Remote" in job["work_arrangement"] for job in live)),
        ("Bengaluru", sum("Bengaluru" in job["location"] for job in live)),
        ("Hyderabad", sum("Hyderabad" in job["location"] for job in live)),
    ]
    orientations = [(name, technology[name]) for name in
                    ("GenAI / Agentic AI", "Classical ML / Data Science", "Data / Infrastructure", "Non-AI", "Mixed")]
    fits = [(name, domains[name]) for name in ("Direct", "Adjacent", "Bridgeable", "Niche / Far")]
    build_skills = [(skill["skill"], skill["role_count"]) for skill in skills
                    if skill["recommended_action"] == "Build Now"][:10]
    rows = [["Metric", "Count", "", "Technology orientation", "Count", "Domain fit", "Count", "Build-Now skill theme", "Roles"]]
    for index, (label, number) in enumerate(metrics):
        orientation = orientations[index] if index < len(orientations) else ("", "")
        fit = fits[index] if index < len(fits) else ("", "")
        skill = build_skills[index] if index < len(build_skills) else ("", "")
        rows.append([label, number, "", *orientation, *fit, *skill])
    return rows


def tab_rows(jobs, skills, feedback, latest_new_count):
    by_lane = {lane: [job for job in jobs if job["application_lane"] == lane and job["status"] == "Live"]
               for lane in ("Apply Now", "Apply Now + Bridge", "Build Toward")}
    return {
        "Dashboard": dashboard_rows(jobs, skills, latest_new_count),
        "Jobs Master": serialize_job_rows(jobs, feedback),
        "Apply Now": serialize_job_rows(by_lane["Apply Now"], feedback),
        "Apply Now + Bridge": serialize_job_rows(by_lane["Apply Now + Bridge"], feedback),
        "Build Toward": serialize_job_rows(by_lane["Build Toward"], feedback),
        "Skills Synthesis": [[name for name, _ in SKILL_COLUMNS]] + [[str(item.get(key, "")) for _, key in SKILL_COLUMNS] for item in skills],
        "Calibration Feedback": serialize_feedback_rows(jobs, feedback),
    }


def _cell(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"userEnteredValue": {"numberValue": value}}
    # Explicit stringValue prevents spreadsheet formula interpretation of JD text.
    return {"userEnteredValue": {"stringValue": str(value)}}


def _format_requests(sheet_id, title, row_count, col_count, first_creation=False):
    extent = {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": row_count,
              "startColumnIndex": 0, "endColumnIndex": col_count}
    requests = [
        {"repeatCell": {"range": extent, "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
                        "fields": "userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment"}},
        {"repeatCell": {"range": {**extent, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True},
                                                       "backgroundColor": {"red": 0.88, "green": 0.93, "blue": 0.97}}},
                        "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"}},
    ]
    if title != "Dashboard":
        requests.append({"setBasicFilter": {"filter": {"range": {**extent, "endRowIndex": max(2, row_count)}}}})
    for index in range(col_count):
        width = ([190, 330, 125, 250, 205, 160, 350, 520, 420, 460, 195, 150,
                  420, 150, 330, 190][index] if title in ("Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward")
                 else 190)
        if title == "Dashboard":
            width = [270, 100, 32, 270, 100, 190, 100, 320, 100][index]
        requests.append({"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": index, "endIndex": index + 1},
            "properties": {"pixelSize": width}, "fields": "pixelSize"}})
    if title in ("Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward", "Calibration Feedback"):
        requests.append({"setDataValidation": {"range": {"sheetId": sheet_id, "startRowIndex": 1,
                                                     "endRowIndex": row_count, "startColumnIndex": 0,
                                                     "endColumnIndex": col_count}}})
        positions = ((11, DECISIONS), (13, STAGES)) if title != "Calibration Feedback" else ((3, DECISIONS), (5, STAGES))
        for index, options in positions:
            requests.append({"setDataValidation": {"range": {"sheetId": sheet_id, "startRowIndex": 1,
                                                              "endRowIndex": row_count, "startColumnIndex": index,
                                                              "endColumnIndex": index + 1},
                                                    "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                                                        {"userEnteredValue": option} for option in options]},
                                                             "strict": True, "showCustomUi": True}}})
    if title == "Jobs Master" and first_creation:
        lane_index = [name for name, _ in JOB_COLUMNS].index("System Recommendation")
        for lane, color in [
            ("Apply Now", (0.83, 0.94, 0.83)),
            ("Apply Now + Bridge", (0.97, 0.93, 0.77)),
            ("Skip", (0.93, 0.93, 0.93)),
        ]:
            requests.append({"addConditionalFormatRule": {"index": 0, "rule": {
                "ranges": [{"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": row_count,
                            "startColumnIndex": lane_index, "endColumnIndex": lane_index + 1}],
                "booleanRule": {"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": lane}]},
                                "format": {"backgroundColor": {"red": color[0], "green": color[1], "blue": color[2]}}}}}})
    return requests


def build_update_requests(existing_sheets, rows_by_tab):
    requests = []
    for title in TABS:
        rows = rows_by_tab[title]
        current = existing_sheets.get(title)
        if current is None:
            raise DashboardError(f"Missing dashboard tab: {title}")
        sheet_id = current["sheetId"]
        current_grid = current.get("gridProperties", {})
        row_count = max(current_grid.get("rowCount", 0), len(rows) + 10, 50)
        col_count = len(rows[0])
        if current.get("basicFilter"):
            requests.append({"clearBasicFilter": {"sheetId": sheet_id}})
        lane_rules = []
        if title == "Jobs Master":
            lanes = {"Apply Now", "Apply Now + Bridge", "Build Toward", "Skip"}
            for index, rule in enumerate(current.get("conditionalFormats", [])):
                condition = rule.get("booleanRule", {}).get("condition", {})
                values = condition.get("values", [])
                if condition.get("type") == "TEXT_EQ" and values and values[0].get("userEnteredValue") in lanes:
                    lane_rules.append(index)
            for index in reversed(lane_rules):
                requests.append({"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": index}})
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet_id,
                           "gridProperties": {"rowCount": row_count, "columnCount": col_count, "frozenRowCount": 1}},
                           "fields": "gridProperties.rowCount,gridProperties.columnCount,gridProperties.frozenRowCount"}})
        requests.append({"updateCells": {"range": {"sheetId": sheet_id, "startRowIndex": 0,
                         "endRowIndex": row_count, "startColumnIndex": 0, "endColumnIndex": col_count},
                         "rows": [{"values": [_cell(value) for value in row]} for row in rows],
                         "fields": "userEnteredValue"}})
        requests.extend(_format_requests(sheet_id, title, row_count, len(rows[0]),
                                         first_creation=title == "Jobs Master" and (bool(lane_rules) or not current.get("conditionalFormats"))))
    return requests


def sync_dashboard(root=ROOT, session=None, credentials_path=None, token_path=None, latest_new_count=0):
    config = read_config(root)
    if not config.get("sync_enabled"):
        raise DashboardError("Dashboard sync is disabled in config/google_sheets.yaml")
    jobs = load_canonical_jobs(root)
    validate_jobs(jobs, root)
    skills = synthesize_skills(jobs)
    auth_result = "injected test session"
    if session is None:
        from google.auth.transport.requests import AuthorizedSession
        creds, auth_result = authenticate(root, credentials_path, token_path)
        session = AuthorizedSession(creds)
    spreadsheet_id = config.get("spreadsheet_id") or ""
    created = False
    if not spreadsheet_id:
        result = api_json(session, "POST", API, "create", json={
            "properties": {"title": config["spreadsheet_title"]},
            "sheets": [{"properties": {"title": title, "gridProperties": {
                "rowCount": 100, "columnCount": 45, "frozenRowCount": 1}}} for title in TABS],
        })
        spreadsheet_id = result.get("spreadsheetId")
        if not spreadsheet_id:
            raise DashboardError("Google Sheets creation returned no spreadsheet ID")
        config["spreadsheet_id"] = spreadsheet_id
        config["spreadsheet_url"] = result.get("spreadsheetUrl") or f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        write_config(root, config)  # Persist identity before any content update; reruns cannot create a duplicate.
        created = True
    metadata = api_json(session, "GET", f"{API}/{spreadsheet_id}", "metadata",
                        params={"fields": "spreadsheetId,spreadsheetUrl,properties.title,sheets.properties,sheets.conditionalFormats,sheets.basicFilter"})
    if metadata.get("spreadsheetId") != spreadsheet_id:
        raise DashboardError("Configured spreadsheet ID did not match Google response")
    existing = {sheet["properties"]["title"]: {**sheet["properties"],
                "conditionalFormats": sheet.get("conditionalFormats", []),
                "basicFilter": sheet.get("basicFilter")} for sheet in metadata.get("sheets", [])}
    missing = [title for title in TABS if title not in existing]
    if missing:
        raise DashboardError("Existing dashboard is missing tabs: " + ", ".join(missing))
    feedback = {}
    if not created:
        feedback_tabs = ("Jobs Master", "Apply Now", "Apply Now + Bridge", "Build Toward", "Calibration Feedback")
        ranges = [f"'{title}'!A1:AM{min(existing[title].get('gridProperties', {}).get('rowCount', 200), 500)}"
                  for title in feedback_tabs]
        read = api_json(session, "GET", f"{API}/{spreadsheet_id}/values:batchGet",
                        "read all user feedback", params={"ranges": ranges, "valueRenderOption": "FORMATTED_VALUE"})
        feedback = collect_live_feedback({title: block.get("values", []) for title, block in
                                          zip(feedback_tabs, read.get("valueRanges", []))}, jobs)
        apply_feedback_to_jobs(jobs, feedback, root)
    rows = tab_rows(jobs, skills, feedback, latest_new_count)
    requests = build_update_requests(existing, rows)
    # One Sheets batchUpdate validates and applies the complete dashboard update atomically.
    api_json(session, "POST", f"{API}/{spreadsheet_id}:batchUpdate", "atomic update",
             json={"requests": requests, "includeSpreadsheetInResponse": False})
    return {"spreadsheet_id": spreadsheet_id, "spreadsheet_url": config["spreadsheet_url"],
            "created": created, "auth": auth_result, "jobs": len(jobs), "skills": len(skills),
            "tabs": TABS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials", type=Path, default=None)
    parser.add_argument("--token", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = sync_dashboard(credentials_path=args.credentials, token_path=args.token)
    except DashboardError as exc:
        parser.exit(1, f"Dashboard sync failed: {exc}\n")
    print(f"Authentication: {result['auth']}; {'created' if result['created'] else 'updated'} existing dashboard")
    print(f"Dashboard: {result['spreadsheet_url']}")
    print(f"Rows: {result['jobs']} jobs; {result['skills']} skill themes; {len(result['tabs'])} tabs")


if __name__ == "__main__":
    main()
