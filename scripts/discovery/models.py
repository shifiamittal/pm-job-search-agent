"""Schemas and validation for raw discovery records.

Raw discovery intentionally contains only source facts and crawl provenance.
Candidate fit, domain classification and application decisions belong downstream.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RAW_JOB_FIELDS = [
    "job_id",
    "external_job_id",
    "company",
    "title",
    "location",
    "canonical_url",
    "description",
    "source_key",
    "source_type",
    "source_url",
    "department",
    "source_updated_at",
    "posting_date",
    "retrieved_at",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonicalize_url(url: str) -> str:
    """Normalize a URL for stable identity without inventing a different destination."""
    parts = urlsplit((url or "").strip())
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError(f"Expected canonical HTTPS URL, got: {url!r}")
    if parts.username or parts.password or not parts.hostname:
        raise ValueError("Canonical URL must have a hostname and no credentials")
    # Keep functional query parameters; remove only known tracking parameters.
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if not key.casefold().startswith("utm_")
             and key.casefold() not in {"gh_src", "gh_jid", "source", "ref", "fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def stable_job_id(company: str, external_job_id: str, canonical_url: str) -> str:
    """Prefer the source requisition ID; fall back to a stable URL hash."""
    company_key = re.sub(r"[^a-z0-9]+", "-", company.casefold()).strip("-")
    if str(external_job_id or "").strip():
        return f"{company_key}:{str(external_job_id).strip()}"
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:16]
    return f"{company_key}:url-{digest}"


def validate_raw_job(job: dict) -> None:
    missing = [field for field in RAW_JOB_FIELDS if field not in job]
    if missing:
        raise ValueError(f"Missing raw job fields: {', '.join(missing)}")
    optional = {"availability_status", "availability_checked_at", "availability_reason", "employment_type"}
    if set(job) - set(RAW_JOB_FIELDS) - optional:
        raise ValueError("Raw jobs must contain only source facts/provenance")
    if any(not isinstance(job[field], str) for field in job):
        raise ValueError("Raw job fields must be strings")
    for field in ("job_id", "company", "title", "canonical_url", "source_key", "source_type", "retrieved_at"):
        if not str(job.get(field, "")).strip():
            raise ValueError(f"Raw job field {field} must not be blank")
    if canonicalize_url(job["canonical_url"]) != job["canonical_url"]:
        raise ValueError("Raw job canonical_url must be canonical HTTPS")
    if job["job_id"] != stable_job_id(job["company"], job["external_job_id"], job["canonical_url"]):
        raise ValueError("Raw job_id does not match source identity")
    if datetime.fromisoformat(job["retrieved_at"]).tzinfo is None:
        raise ValueError("retrieved_at must include a timezone")
    if job["source_type"] not in {"greenhouse", "ashby", "microsoft", "lever", "custom", "web_search"}:
        raise ValueError(f"Unsupported source_type: {job['source_type']}")


def validate_raw_jobs(jobs: list[dict]) -> None:
    seen = set()
    for job in jobs:
        validate_raw_job(job)
        if job["job_id"] in seen:
            raise ValueError(f"Duplicate raw job_id: {job['job_id']}")
        seen.add(job["job_id"])
