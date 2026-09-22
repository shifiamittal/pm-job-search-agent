"""Deterministic public Ashby board retrieval, without upstream title filtering."""

from __future__ import annotations

from urllib.parse import urlsplit
from uuid import UUID

import requests

from .errors import CrawlError
from .models import canonicalize_url, stable_job_id, utc_now_iso, validate_raw_jobs

ASHBY_API = "https://api.ashbyhq.com/posting-api/job-board/{board_token}"


def external_id_from_url(url: str, board_token: str) -> str:
    """The public API exposes posting identity in its individual jobUrl."""
    parts = urlsplit(url)
    path = parts.path.strip("/").split("/")
    if parts.hostname != "jobs.ashbyhq.com" or len(path) != 2 or path[0] != board_token:
        raise ValueError(f"Expected individual Ashby URL for board {board_token}")
    UUID(path[1])  # Fail visibly rather than silently losing the ATS identity.
    return path[1]


def normalize_location(item: dict) -> str:
    locations = [item.get("location") or ""]
    secondary = item.get("secondaryLocations") or []
    if not isinstance(secondary, list):
        raise ValueError("Ashby secondaryLocations must be a list")
    locations.extend(row.get("location") or "" for row in secondary)
    return " | ".join(dict.fromkeys(" ".join(value.split()) for value in locations if value.strip()))


def fetch_ashby_jobs(source_key: str, source: dict, session=None, timeout: int = 45) -> tuple[list[dict], dict]:
    """Fetch all published postings. This endpoint has no pagination parameters."""
    session = session or requests.Session()
    url = ASHBY_API.format(board_token=source["board_token"])
    telemetry = dict(source_key=source_key, company=source["company"], source_type="ashby",
                     adapter="ashby", source_url=source.get("careers_url", url),
                     started_at=utc_now_iso(), completed_at="", request_count=1,
                     http_status="", jobs_seen=0, jobs_extracted=0, pm_candidates=0,
                     errors=[], status="started")
    try:
        response = session.get(url, timeout=timeout)
        telemetry["http_status"] = response.status_code
        response.raise_for_status()
        payload = response.json()
        source_jobs = payload.get("jobs")
        if not isinstance(source_jobs, list):
            raise ValueError("Ashby response did not contain a jobs list")
        telemetry["jobs_seen"] = len(source_jobs)
        jobs = []
        retrieved_at = utc_now_iso()
        for item in source_jobs:
            canonical_url = canonicalize_url(item.get("jobUrl", ""))
            external_id = external_id_from_url(canonical_url, source["board_token"])
            job = dict(
                job_id=stable_job_id(source["company"], external_id, canonical_url),
                external_job_id=external_id, company=source["company"],
                title=(item.get("title") or "").strip(), location=normalize_location(item),
                canonical_url=canonical_url, description=item.get("descriptionPlain") or "",
                source_key=source_key, source_type="ashby",
                source_url=source.get("careers_url", url), department=item.get("department") or "",
                # publishedAt is LAST publication, not a confirmed original posting date.
                source_updated_at=item.get("publishedAt") or "", posting_date="",
                retrieved_at=retrieved_at,
            )
            validate_raw_jobs([job])
            jobs.append(job)
            telemetry["jobs_extracted"] = len(jobs)
        validate_raw_jobs(jobs)
        telemetry["status"] = "success"
        return jobs, telemetry
    except Exception as exc:
        telemetry["errors"].append(f"{type(exc).__name__}: {exc}")
        telemetry["status"] = "failed"
        raise CrawlError(telemetry) from exc
    finally:
        telemetry["completed_at"] = utc_now_iso()
