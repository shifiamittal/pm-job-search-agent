"""Reusable public Workday CXS retrieval. No benchmark or PM-filter dependencies."""

from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urlsplit

import requests

from .errors import CrawlError
from .models import canonicalize_url, stable_job_id, utc_now_iso, validate_raw_jobs


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


class _MalformedSourceRecord(ValueError):
    """Required per-record source facts are absent; other records remain usable."""


def _endpoints(source):
    tenant, site = source['tenant'], source['site']
    if not all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_-]+', x) for x in (tenant, site)):
        raise ValueError('Invalid Workday tenant/site')
    url = canonicalize_url(source.get('workday_url') or source['careers_url'])
    parts = urlsplit(url)
    if not re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com', parts.netloc):
        raise ValueError('Expected a public Workday myworkdayjobs origin')
    if site not in parts.path.split('/'):
        raise ValueError('Workday URL must contain the configured site')
    origin = f'https://{parts.netloc}'
    return origin, f'{origin}/wday/cxs/{tenant}/{site}'


def _path(item):
    path = item.get('externalPath')
    if (not isinstance(path, str) or not path.startswith('/job/')
            or any(x in path for x in ('..', '?', '#', '\\'))):
        raise ValueError('Invalid Workday externalPath')
    return path


def _normalize(source_key, source, origin, item, payload):
    info = payload.get('jobPostingInfo')
    if not isinstance(info, dict):
        raise ValueError('Workday detail missing jobPostingInfo')
    external_id = info.get('jobReqId')
    description = info.get('jobDescription')
    if not isinstance(external_id, str) or not external_id.strip():
        raise _MalformedSourceRecord('Workday detail missing requisition ID')
    if not isinstance(info.get('title'), str) or not info['title'].strip():
        raise _MalformedSourceRecord('Workday detail missing title')
    if not isinstance(description, str) or not description.strip():
        raise ValueError('Workday detail missing full job description')
    external_id = external_id.strip()
    # CXS supplies a posting slug independently in detail responses. Reject a
    # detail body for another posting instead of silently replacing an identity.
    posting_id = info.get('jobPostingId')
    if posting_id is not None and posting_id != _path(item).rsplit('/', 1)[-1]:
        raise ValueError('Workday listing/detail posting identity mismatch')
    url = canonicalize_url(info.get('externalUrl') or f"{origin}/{source['site']}{_path(item)}")
    parts = urlsplit(url)
    if f'https://{parts.netloc}' != origin or f"/{source['site']}/job/" not in parts.path:
        raise ValueError('Detail canonical URL points outside configured Workday site')
    primary = info.get('location') or ''
    additional = info.get('additionalLocations') or []
    if not isinstance(primary, str) or not isinstance(additional, list) or not all(isinstance(x, str) for x in additional):
        raise ValueError('Invalid Workday detail locations')
    locations = list(dict.fromkeys(x for x in [primary] + additional if x))
    text = _Text()
    text.feed(description)
    job = dict(job_id=stable_job_id(source['company'], external_id, url), external_job_id=external_id,
               company=source['company'], title=info.get('title') or '', location=' | '.join(locations),
               canonical_url=url, description=' '.join(' '.join(text.parts).split()),
               full_job_description_raw=description, primary_location=primary,
               all_locations=json.dumps(locations, ensure_ascii=False),
               source_key=source_key, source_type='workday', source_url=source.get('careers_url', origin),
               department='', source_updated_at='', posting_date=info.get('startDate') or '',
               retrieved_at=utc_now_iso())
    validate_raw_jobs([job])
    return job


def fetch_workday_jobs(source_key: str, source: dict, session=None, timeout: int = 45) -> tuple[list[dict], dict]:
    """Two listing passes, then valid details; malformed records are audited/skipped.

    Defaults to an unfiltered board. Optional search_text/applied_facets define
    the entire requested universe, not a post-retrieval PM classification.
    Injected sessions run serially; normal detail workers have isolated sessions.
    """
    telemetry = dict(source_key=source_key, company=source.get('company', ''), source_type='workday',
                     adapter='workday', source_url=source.get('careers_url', ''), started_at=utc_now_iso(),
                     completed_at='', request_count=0, http_status='', jobs_seen=0, jobs_extracted=0,
                     pm_candidates=0, errors=[], status='started', retries=0, request_errors=[],
                     source_failures=[], detail_failures=[], passes=[], source_count=None,
                     duplicate_listing_paths=0, duplicate_job_ids=0, pagination_complete=False,
                     malformed_records=[], malformed_records_skipped=0, extraction_complete=False)
    owned_sessions = []
    lock = threading.Lock()
    local = threading.local()
    malformed = {}

    def record_malformed(key, item, problems, **context):
        if key not in malformed:
            entry = dict(failure_reason='malformed_source_record', reasons=problems,
                         raw_record=item, observations=[])
            malformed[key] = entry
            telemetry['malformed_records'].append(entry)
            telemetry['malformed_records_skipped'] = len(malformed)
        malformed[key]['observations'].append(context)

    def listing_identity(item):
        problems = []
        if not isinstance(item, dict):
            problems.append('Listing must be an object')
        elif not isinstance(item.get('title'), str) or not item['title'].strip():
            problems.append('Listing missing title')
        try:
            path = _path(item) if isinstance(item, dict) else None
        except ValueError:
            path = None
        if path is None:
            problems.append('Listing missing or unusable externalPath')
        # An opaque raw fingerprint is only for pagination/audit accounting,
        # never a fabricated job/requisition ID. Identical unidentifiable rows
        # remain ambiguous and cannot artificially satisfy the source count.
        key = ('path', path) if path else ('malformed', json.dumps(item, sort_keys=True))
        return key, problems

    def client():
        if session is not None:
            return session
        if not hasattr(local, 'session'):
            local.session = requests.Session()
            with lock:
                owned_sessions.append(local.session)
        return local.session

    def request(method, url, body=None):
        for attempt in range(3):
            with lock:
                telemetry['request_count'] += 1
            try:
                kwargs = {'timeout': timeout}
                if body is not None:
                    kwargs['json'] = body
                response = getattr(client(), method)(url, **kwargs)
                with lock:
                    telemetry['http_status'] = response.status_code
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError('Workday response must be an object')
                return payload
            except (requests.RequestException, ValueError) as exc:
                code = getattr(getattr(exc, 'response', None), 'status_code', None)
                retryable = (isinstance(exc, (requests.Timeout, requests.ConnectionError))
                             or code in (429, 500, 502, 503, 504))
                with lock:
                    telemetry['request_errors'].append(dict(url=url, attempt=attempt + 1, error=str(exc)))
                if not retryable or attempt == 2:
                    raise
                with lock:
                    telemetry['retries'] += 1
                time.sleep(2 ** attempt)

    try:
        origin, endpoint = _endpoints(source)
        limit = source.get('page_size', 20)
        max_pages = source.get('max_pages', 1000)
        workers = source.get('detail_workers', 6)
        if any(type(x) is not int or x <= 0 for x in (limit, max_pages, workers)) or limit > 20 or workers > 16:
            raise ValueError('Invalid Workday page_size (1..20), max_pages, or detail_workers (1..16)')
        facets = source.get('applied_facets', {})
        query = source.get('search_text', '')
        if not isinstance(query, str) or not isinstance(facets, dict) or not all(
                isinstance(k, str) and isinstance(v, list) and all(isinstance(x, str) for x in v)
                for k, v in facets.items()):
            raise ValueError('Invalid Workday source-side search/facets')
        telemetry['query'] = dict(searchText=query, appliedFacets=facets)

        def page(offset):
            body = dict(appliedFacets=facets, searchText=query, limit=limit, offset=offset)
            payload = request('post', endpoint + '/jobs', body)
            if not isinstance(payload.get('jobPostings'), list):
                raise ValueError('Workday search missing jobPostings list')
            return payload

        def enumerate_pass():
            seen, signatures = {}, set()
            offset, expected = 0, None
            stats = dict(pages=0, rows=0, unique=0, duplicate_paths=0, stop_reason='')
            telemetry['passes'].append(stats)
            for _ in range(max_pages):
                payload = page(offset)
                items = payload['jobPostings']
                count = payload.get('total')
                if count is not None and (type(count) is not int or count < 0):
                    raise ValueError('Invalid Workday source count')
                if offset == 0:
                    expected = count
                    stats['source_count'] = count
                    if len(telemetry['passes']) == 1:
                        telemetry['source_count'] = count
                    # CXS can cap broad queries at 2000; count equality is unsafe there.
                    if count is not None and count >= 2000:
                        raise ValueError('Possible Workday 2000-result cap; configure narrower source facets before crawling')
                    if count == 0 and items:
                        raise ValueError('First-page zero count contradicts nonempty results')
                elif count not in (None, 0, expected):
                    raise ValueError('Workday source count changed during pagination')
                stats['pages'] += 1
                stats['rows'] += len(items)
                entries = [listing_identity(item) for item in items]
                signature = tuple(key for key, _ in entries)
                for index, (item, (key, problems)) in enumerate(zip(items, entries)):
                    if problems:
                        record_malformed(key, item, problems, phase='listing',
                                         pass_number=len(telemetry['passes']), offset=offset, index=index)
                    if key in seen:
                        stats['duplicate_paths'] += 1
                        telemetry['duplicate_listing_paths'] += 1
                    seen[key] = item
                stats['unique'] = len(seen)
                stats['malformed_unique'] = sum(bool(listing_identity(j)[1]) for j in seen.values())
                telemetry['jobs_seen'] = max(telemetry['jobs_seen'], len(seen))
                if not items or signature in signatures:
                    stats['stop_reason'] = 'empty_page' if not items else 'repeated_page'
                    if expected is not None and len(seen) != expected:
                        raise ValueError('Pagination stopped before source count was reached')
                    if expected is None and items:
                        raise ValueError('Repeated page without source count cannot establish completeness')
                    return seen, expected
                signatures.add(signature)
                if expected is not None and len(seen) >= expected:
                    if len(seen) != expected:
                        raise ValueError('Unique listings exceed source count')
                    terminal = page(offset + len(items))
                    terminal_items = terminal['jobPostings']
                    terminal_paths = set()
                    for index, item in enumerate(terminal_items):
                        key, problems = listing_identity(item)
                        terminal_paths.add(key)
                        if problems:
                            record_malformed(key, item, problems, phase='terminal_probe',
                                             pass_number=len(telemetry['passes']), offset=offset + len(items), index=index)
                    if terminal.get('total') not in (None, 0, expected) or terminal_paths - seen.keys():
                        raise ValueError('New jobs or count drift after reported end')
                    stats['terminal_probe_rows'] = len(terminal_items)
                    stats['stop_reason'] = 'count_and_empty_probe' if not terminal_items else 'count_and_repeated_probe'
                    return seen, expected
                offset += len(items)
            raise ValueError('Workday max_pages reached without completeness')

        first, count = enumerate_pass()
        second, second_count = enumerate_pass()
        if first.keys() != second.keys() or count != second_count:
            raise ValueError('Workday repeated passes disagree; retry after source stabilizes')
        if {k for k,v in first.items() if listing_identity(v)[1]} != {k for k,v in second.items() if listing_identity(v)[1]}:
            raise ValueError('Workday repeated passes disagree on malformed records')
        telemetry['source_count'] = count
        telemetry['pagination_complete'] = True
        telemetry['repeated_pass_consistent'] = True

        def detail(item):
            url = endpoint + _path(item)
            try:
                payload = request('get', url)
                return _normalize(source_key, source, origin, item, payload), None
            except _MalformedSourceRecord as exc:
                return None, dict(url=url, error=str(exc), failure_reason='malformed_source_record',
                                  raw_record=dict(listing=item, detail=payload))
            except Exception as exc:
                return None, dict(url=url, error=f'{type(exc).__name__}: {exc}')

        jobs = {}
        with ThreadPoolExecutor(max_workers=1 if session is not None else workers) as pool:
            valid_items = [item for item in second.values() if not listing_identity(item)[1]]
            telemetry['valid_listings'] = len(valid_items)
            for job, error in pool.map(detail, valid_items):
                if error:
                    if error.get('failure_reason') == 'malformed_source_record':
                        record_malformed(('detail', error['url']), error['raw_record'], [error['error']],
                                         phase='detail', url=error['url'])
                        continue
                    telemetry['detail_failures'].append(error)
                    continue
                if job['job_id'] in jobs:
                    telemetry['duplicate_job_ids'] += 1
                    previous = jobs[job['job_id']]
                    if any(previous[k] != job[k] for k in ('canonical_url', 'title', 'all_locations', 'full_job_description_raw')):
                        telemetry['detail_failures'].append(dict(url=job['canonical_url'], error='Conflicting postings share a requisition ID'))
                else:
                    jobs[job['job_id']] = job
                telemetry['jobs_extracted'] = len(jobs)
        if telemetry['detail_failures']:
            raise ValueError(f"{len(telemetry['detail_failures'])} Workday detail failures; incomplete output withheld")
        result = sorted(jobs.values(), key=lambda j: j['job_id'])
        validate_raw_jobs(result)
        telemetry['extraction_complete'] = not telemetry['malformed_records_skipped']
        telemetry['status'] = 'success'
        return result, telemetry
    except Exception as exc:
        message = f'{type(exc).__name__}: {exc}'
        telemetry['errors'].append(message)
        if not telemetry['pagination_complete']:
            telemetry['source_failures'].append(message)
        telemetry['status'] = 'failed'
        raise CrawlError(telemetry) from exc
    finally:
        telemetry['completed_at'] = utc_now_iso()
        for owned in owned_sessions:
            owned.close()
