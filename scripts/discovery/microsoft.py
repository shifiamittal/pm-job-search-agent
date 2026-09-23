"""Microsoft's public Product Management facet; no benchmark dependencies."""

from __future__ import annotations

import time
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit

import requests

from .errors import CrawlError
from .models import canonicalize_url, stable_job_id, utc_now_iso, validate_raw_jobs

BASE = "https://apply.careers.microsoft.com"
SEARCH_API = BASE + "/api/pcsx/search"
DETAIL_API = BASE + "/api/pcsx/position_details"
COUNTRIES = {"united states", "india"}


def in_target_geography(job: dict) -> bool:
    """Microsoft supplies country-first locations; never infer country from city."""
    return any(location.split(",", 1)[0].strip().casefold() in COUNTRIES
               for location in job["location"].split(" | "))


def is_internship(title: str, employment_type: str = "") -> bool:
    return bool(re.search(r"\b(intern|internship|student|students)\b", title + " " + employment_type, re.I))


def detail_availability(job: dict, body: dict, http_status: int, expected_requisition: str) -> tuple[str, str, str]:
    """Source evidence only: absence is stale, uncertain responses stay unknown."""
    if http_status in {404, 410} or body.get("status") in {404, 410}:
        return "stale_unavailable", "Detail endpoint reports missing/removed posting", ""
    if http_status != 200 or body.get("status") != 200:
        return "unknown", "Detail endpoint did not return a successful job response", ""
    if (body.get("metadata") or {}).get("isFallback") is True:
        return "stale_unavailable", "Source returned a fallback instead of the requested posting", ""
    data = body.get("data") or {}
    if not isinstance(data, dict) or str(data.get("id")) != job["external_job_id"]:
        return "unknown", "Detail position identity missing or mismatched", ""
    if str(data.get("displayJobId") or data.get("atsJobId") or "") != expected_requisition:
        return "unknown", "Detail requisition identity mismatched", ""
    employment = data.get("efcustomTextEmploymentType") or []
    employment = "; ".join(employment) if isinstance(employment, list) else str(employment)
    action = ((data.get("positionUserActions") or {}).get("applyAction") or {}).get("status")
    if action in {"closed", "unavailable", "expired"}:
        return "stale_unavailable", "Source application action reports " + action, employment
    if action not in {"log_in", "apply"} or not data.get("jobDescription"):
        return "unknown", "No positive description/application availability evidence", employment
    return "available", "Matching detail identity, job description and application action: " + action, employment


def _retry_delay(response, attempt: int) -> float:
    delay = 60 * (attempt + 1)
    value = response.headers.get("Retry-After") if response is not None else None
    if value:
        try:
            delay = max(delay, float(value))
        except ValueError:
            try:
                stamp = parsedate_to_datetime(value)
                delay = max(delay, (stamp - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError):
                pass
    return delay


def fetch_microsoft_jobs(source_key: str, source: dict, session=None, timeout: int = 45,
                         *, sleep=time.sleep, monotonic=time.monotonic,
                         request_interval: float = 5, max_passes: int = 3,
                         max_pages: int = 100, verify_availability: bool = True) -> tuple[list[dict], dict]:
    """Enumerate one source-defined facet, reconciling drift with bounded passes.

    Return every verified facet job, including non-target countries. Geography
    belongs after raw retrieval so exclusions remain inspectable in raw_all_jobs.
    """
    owned_session = session is None
    session = session or requests.Session()
    telemetry = dict(source_key=source_key, company=source["company"],
                     source_type="microsoft", adapter="microsoft",
                     source_url=source.get("careers_url", BASE + "/careers"),
                     started_at=utc_now_iso(), completed_at="", request_count=0,
                     http_status="", jobs_seen=0, jobs_extracted=0, pm_candidates=0,
                     errors=[], status="started", requests=[], passes=[],
                     facet={"filter_profession": "product management"})
    last_request = None

    def request_json(url, params, phase, allow_missing=False):
        nonlocal last_request
        for attempt in range(3):
            if last_request is not None:
                sleep(max(0, request_interval - (monotonic() - last_request)))
            last_request = monotonic()
            event = dict(phase=phase, parameters=params,
                         attempt=attempt + 1, at=utc_now_iso(), http_status=None)
            telemetry["request_count"] += 1
            telemetry["requests"].append(event)
            response = None
            try:
                response = session.get(url, params=params, timeout=timeout)
                event["http_status"] = response.status_code
                telemetry["http_status"] = response.status_code
                if allow_missing and response.status_code in {404, 410}:
                    return {}, response.status_code
                response.raise_for_status()
                return response.json(), response.status_code
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
                event["error"] = f"{type(exc).__name__}: {exc}"
                telemetry["errors"].append(dict(event))
                retryable = response is None or response.status_code in {408, 429, 500, 502, 503, 504}
                if not retryable or attempt == 2:
                    raise
                event["retry_delay_seconds"] = _retry_delay(response, attempt)
                sleep(event["retry_delay_seconds"])


    def fetch_page(offset, pass_number, phase):
        params = dict(domain="microsoft.com", query="", location="", start=offset,
                      filter_profession="product management")
        body, _ = request_json(SEARCH_API, params, phase)
        if body.get("status") != 200:
            raise ValueError("Microsoft API body did not report success")
        data = body.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("positions"), list):
            raise ValueError("Microsoft response missing positions list")
        if type(data.get("count")) is not int or data["count"] < 0:
            raise ValueError("Microsoft response missing valid total count")
        if data.get("appliedFilters", {}).get("profession") != ["product management"]:
            raise ValueError("Microsoft did not acknowledge the PM profession filter")
        for item in data["positions"]:
            if not isinstance(item, dict) or not str(item.get("id") or "").isdigit():
                raise ValueError("Microsoft posting missing numeric position ID")
        return data

    try:
        previous_ids = set()
        final_records = None
        for pass_number in range(1, max_passes + 1):
            audit = dict(pass_number=pass_number, pages=[], checks=[], duplicates=[],
                         complete=False)
            telemetry["passes"].append(audit)
            found = {}
            offset = 0
            for _ in range(max_pages):
                data = fetch_page(offset, pass_number, "enumeration")
                items = data["positions"]
                ids = [str(item["id"]) for item in items]
                audit["pages"].append(dict(start=offset, count=data["count"],
                                            returned=len(items), ids=ids,
                                            captured_at=utc_now_iso()))
                for item in items:
                    ident = str(item["id"])
                    if ident in found:
                        audit["duplicates"].append(ident)
                    found[ident] = item
                telemetry["jobs_seen"] = len(found)
                if not items:
                    break
                offset += len(items)
            else:
                raise ValueError("Microsoft facet exceeded the pagination safety limit")
            last_offset = audit["pages"][-2]["start"] if len(audit["pages"]) > 1 else 0
            for check_offset in dict.fromkeys([0, last_offset]):
                data = fetch_page(check_offset, pass_number, "boundary_check")
                audit["checks"].append(dict(start=check_offset, count=data["count"],
                                             ids=[str(item["id"]) for item in data["positions"]],
                                             captured_at=utc_now_iso()))
            counts = {page["count"] for page in audit["pages"] + audit["checks"]}
            checked_counts = {page["count"] for page in audit["checks"]}
            audit["reported_counts"] = sorted(counts)
            audit["unique_count"] = len(found)
            audit["count_drift"] = len(counts) > 1
            audit["added_since_previous_pass"] = sorted(set(found) - previous_ids) if pass_number > 1 else []
            audit["removed_since_previous_pass"] = sorted(previous_ids - set(found)) if pass_number > 1 else []
            boundaries_match = all(check["ids"] == next(page["ids"] for page in audit["pages"]
                                                        if page["start"] == check["start"])
                                   for check in audit["checks"])
            # Earlier counts may drift; the final boundaries and unique count
            # must agree. Never retain a stale union across reconciliation passes.
            audit["complete"] = (checked_counts == {len(found)} and boundaries_match
                                  and not audit["duplicates"]
                                  and audit["pages"][-1]["count"] == len(found))
            if audit["complete"]:
                final_records = list(found.values())
                break
            previous_ids = set(found)
        if final_records is None:
            raise ValueError("Microsoft facet did not reconcile within the bounded passes")
        telemetry["source_reported_total"] = len(final_records)
        # Keep original source IDs, requisitions, all locations and metadata in
        # telemetry without widening the shared raw-job schema for other adapters.
        telemetry["source_records"] = final_records
        jobs = []
        for item in final_records:
            ident = str(item["id"])
            url = canonicalize_url(urljoin(BASE, item.get("positionUrl") or ""))
            if urlsplit(url).netloc != urlsplit(BASE).netloc or urlsplit(url).path != "/careers/job/" + ident:
                raise ValueError("Microsoft posting URL does not match its position ID")
            locations = item.get("locations")
            if not isinstance(locations, list) or any(not isinstance(location, str) for location in locations):
                raise ValueError("Microsoft posting missing source location list")
            timestamp = item.get("postedTs")
            job = dict(job_id=stable_job_id(source["company"], ident, url),
                       external_job_id=ident, company=source["company"], title=item.get("name") or "",
                       location=" | ".join(locations), canonical_url=url,
                       description="", source_key=source_key, source_type="microsoft",
                       source_url=telemetry["source_url"], department=item.get("department") or "",
                       source_updated_at="", posting_date=datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
                       if timestamp is not None else "", retrieved_at=utc_now_iso())
            validate_raw_jobs([job])
            jobs.append(job)
            telemetry["jobs_extracted"] = len(jobs)
        telemetry["availability_checks"] = []
        from .filters import pm_candidate_decision
        for job, item in zip(jobs, final_records):
            job.update(availability_status="not_checked", availability_checked_at="",
                       availability_reason="Outside verification scope", employment_type="")
            if not in_target_geography(job) or not pm_candidate_decision(job["title"])[0]:
                continue
            if is_internship(job["title"]):
                job["availability_reason"] = "Internship/student title excluded from live candidate scope"
                continue
            if not verify_availability:
                continue
            body, http_status = request_json(DETAIL_API, dict(domain="microsoft.com", position_id=job["external_job_id"], hl="en"), "availability", allow_missing=True)
            status, reason, employment = detail_availability(job, body, http_status, str(item.get("displayJobId") or item.get("atsJobId") or ""))
            job.update(availability_status=status, availability_checked_at=utc_now_iso(),
                       availability_reason=reason, employment_type=employment)
            data = body.get("data") or {}
            telemetry["availability_checks"].append(dict(
                external_job_id=job["external_job_id"], requisition_id=item.get("displayJobId"),
                status=status, reason=reason, http_status=http_status,
                checked_at=job["availability_checked_at"], metadata=body.get("metadata"),
                returned_id=data.get("id") if isinstance(data, dict) else None,
                returned_requisition=data.get("displayJobId") if isinstance(data, dict) else None,
                application_action=data.get("positionUserActions") if isinstance(data, dict) else None))
        validate_raw_jobs(jobs)
        telemetry["geography_retained"] = sum(in_target_geography(job) for job in jobs)
        telemetry["geography_excluded_ids"] = [job["external_job_id"] for job in jobs if not in_target_geography(job)]
        telemetry["status"] = "success"
        return jobs, telemetry
    except Exception as exc:
        telemetry["errors"].append(f"{type(exc).__name__}: {exc}")
        telemetry["status"] = "failed"
        raise CrawlError(telemetry) from exc
    finally:
        telemetry["completed_at"] = utc_now_iso()
        if owned_session:
            session.close()
