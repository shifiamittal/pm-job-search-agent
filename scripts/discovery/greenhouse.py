"""Deterministic Greenhouse job-board adapter."""

from __future__ import annotations

import html
import re
from typing import Any

import requests

from .models import canonicalize_url, stable_job_id, utc_now_iso, validate_raw_jobs

from .errors import CrawlError


GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"


def _text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def fetch_greenhouse_jobs(source_key: str, source: dict, session=None, timeout: int = 45) -> tuple[list[dict], dict]:
    """Fetch every job exposed by a Greenhouse board in one deterministic call.

    Greenhouse's public board endpoint returns the complete board; therefore there
    is no browser pagination to reason about for this adapter.
    """
    session = session or requests.Session()
    board_token = source["board_token"]
    url = GREENHOUSE_API.format(board_token=board_token)
    started_at = utc_now_iso()
    telemetry = {
        "source_key": source_key,
        "company": source["company"],
        "source_type": "greenhouse",
        "adapter": "greenhouse",
        "source_url": source.get("careers_url", url),
        "started_at": started_at,
        "completed_at": "",
        "request_count": 1,
        "http_status": "",
        "jobs_seen": 0,
        "jobs_extracted": 0,
        "pm_candidates": 0,
        "errors": [],
        "status": "started",
    }
    try:
        response = session.get(url, params={"content": "true"}, timeout=timeout)
        telemetry["http_status"] = response.status_code
        response.raise_for_status()
        payload = response.json()
        source_jobs = payload.get("jobs")
        if not isinstance(source_jobs, list):
            raise ValueError("Greenhouse response did not contain a jobs list")
        telemetry["jobs_seen"] = len(source_jobs)
        retrieved_at = utc_now_iso()
        jobs = []
        for item in source_jobs:
            canonical_url = canonicalize_url(item.get("absolute_url", ""))
            external_id = str(item.get("id") or "").strip()
            departments = item.get("departments") or []
            department = "; ".join(_text(row.get("name")) for row in departments if isinstance(row, dict))
            job = {
                "job_id": stable_job_id(source["company"], external_id, canonical_url),
                "external_job_id": external_id,
                "company": source["company"],
                "title": _text(item.get("title")),
                "location": _text((item.get("location") or {}).get("name")),
                "canonical_url": canonical_url,
                "description": _text(item.get("content")),
                "source_key": source_key,
                "source_type": "greenhouse",
                "source_url": source.get("careers_url", url),
                "department": department,
                "source_updated_at": _text(item.get("updated_at")),
                # Greenhouse's public board API exposes updated_at, not a reliable
                # original posting date. Do not relabel updated_at as posting_date.
                "posting_date": "",
                "retrieved_at": retrieved_at,
            }
            validate_raw_jobs([job])
            jobs.append(job)
            telemetry["jobs_extracted"] = len(jobs)
        validate_raw_jobs(jobs)
        telemetry["jobs_extracted"] = len(jobs)
        telemetry["status"] = "success"
        return jobs, telemetry
    except Exception as exc:
        telemetry["errors"].append(f"{type(exc).__name__}: {exc}")
        telemetry["status"] = "failed"
        raise CrawlError(telemetry) from exc
    finally:
        telemetry["completed_at"] = utc_now_iso()
