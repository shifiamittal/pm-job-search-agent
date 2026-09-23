"""Bounded public source detection. No benchmark, company-name rules or job crawling."""
from __future__ import annotations

import hashlib
import html
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import parse_qs, parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit

import requests

IMPLEMENTED = frozenset({"greenhouse", "ashby", "microsoft_custom"})
TOKEN = re.compile(r"^[\w-]+$")
JOB_DETAIL = re.compile(r"/(?:jobs?|positions?|details|results)/(?:[^/?#]*\d[^/?#]*)(?:/|$)", re.I)
SEARCH = re.compile(r"(?:open-positions|open-roles|search-results|all-jobs|jobsearch|/search(?:/|$)|/jobs/?$|/positions/?$)", re.I)


def clean_url(value: str, base: str = "") -> str:
    value = html.unescape(value).replace("\\/", "/").strip().rstrip(".,;)")
    p = urlsplit(urljoin(base, value))
    if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password:
        return ""
    return urlunsplit((p.scheme, p.netloc, p.path, p.query, ""))


def url_signal(url: str) -> tuple[str, str] | None:
    """Exact provider host patterns; never substring-match a lookalike domain."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    parts = [unquote(x) for x in p.path.split("/") if x]
    first = parts[0] if parts else ""
    if host in {"boards.greenhouse.io", "job-boards.greenhouse.io", "boards.eu.greenhouse.io", "job-boards.eu.greenhouse.io"}:
        token = parse_qs(p.query).get("for", [""])[0] if first == "embed" else first
        return "greenhouse", token if TOKEN.fullmatch(token) else ""
    if host == "boards-api.greenhouse.io" and len(parts) >= 3 and parts[:2] == ["v1", "boards"]:
        return "greenhouse", parts[2] if TOKEN.fullmatch(parts[2]) else ""
    if host == "jobs.ashbyhq.com":
        return "ashby", first if TOKEN.fullmatch(first) else ""
    if host == "api.ashbyhq.com" and parts[:2] == ["posting-api", "job-board"]:
        return "ashby", parts[2] if len(parts) > 2 and TOKEN.fullmatch(parts[2]) else ""
    if host.endswith(".myworkdayjobs.com"):
        tenant = host.split(".")[0]
        if parts[:2] == ["wday", "cxs"] and len(parts) >= 4:
            return "workday", parts[2] + "/" + parts[3]
        site = next((x for x in parts if not re.fullmatch(r"[a-z]{2}(?:-[A-Z]{2})?", x)), "")
        return "workday", tenant + ("/" + site if site and site not in {"job", "jobs"} else "")
    if host in {"jobs.lever.co", "jobs.eu.lever.co"}:
        return "lever", first if TOKEN.fullmatch(first) else ""
    if host == "api.lever.co" and parts[:2] == ["v0", "postings"]:
        return "lever", parts[2] if len(parts) > 2 and TOKEN.fullmatch(parts[2]) else ""
    if host == "ats.rippling.com":
        candidates = parts[1:] if first in {"en-US", "en-GB"} else parts
        token = candidates[0] if candidates else ""
        return "rippling", token if TOKEN.fullmatch(token) else ""
    if host == "apply.careers.microsoft.com" and (p.path.startswith("/careers") or p.path.startswith("/api/pcsx/")):
        return "microsoft_custom", "microsoft.com"
    return None


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = []
        self.base = ""

    def handle_starttag(self, tag, attrs):
        if tag == "base":
            self.base = dict(attrs).get("href", "")
        for key, value in attrs:
            if value and key in {"href", "src", "action", "component-url", "data-src"}:
                # Canonical/alternate locale links are not job-navigation evidence.
                if tag == "link" and dict(attrs).get("rel") in {"canonical", "alternate"}:
                    continue
                self.values.append((value, "component" if key == "component-url" else "script" if tag == "script" else "link"))


def extract_links(body: str, base: str) -> list[tuple[str, str]]:
    decoded = html.unescape(body).replace("\\/", "/").replace("\\u0026", "&").replace('\\"', '"')
    parser = Links()
    parser.feed(decoded)
    base = clean_url(parser.base, base) if parser.base else base
    values = parser.values + [(x, "embedded_url") for x in re.findall(r'https?://[^\s<>"\x27\\`]+', decoded)]
    # Only explicit module imports, not arbitrary webpack chunk-name fragments.
    values += [(x, "module_import") for x in re.findall(r'(?:from\s*|import\s*\(?\s*)["\x27]((?:/|\./)[^\s<>"\x27]+\.js)["\x27]', decoded)]
    result, seen = [], set()
    for value, kind in values:
        try:
            url = clean_url(value, base)
            if "{search_term_string}" in url:
                p = urlsplit(url)
                query = [(k, v) for k, v in parse_qsl(p.query) if "{search_term_string}" not in v]
                url = urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), ""))
        except ValueError:
            continue
        if url and url not in seen:
            seen.add(url)
            result.append((url, kind))
    return result


class PublicFetcher:
    """Small read-only requests, bounded bodies/retries; never retries a 403 challenge."""
    def __init__(self, session=None, timeout=20, max_bytes=6_000_000):
        self.session = session or requests.Session()
        self.timeout, self.max_bytes = timeout, max_bytes

    def __call__(self, url):
        attempts = []
        for attempt in range(2):
            try:
                with self.session.get(url, timeout=self.timeout, stream=True) as r:
                    attempts.append(r.status_code)
                    if r.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                        delay = r.headers.get("Retry-After", "1")
                        if not delay.isdigit() or int(delay) > 5:
                            return dict(url=url, final_url=r.url, status=r.status_code, html="", attempts=attempts,
                                        error="Retry-After exceeds bounded inspection wait; not retried")
                        time.sleep(max(1, int(delay)))
                        continue
                    content = bytearray()
                    for chunk in r.iter_content(65536):
                        content.extend(chunk)
                        if len(content) > self.max_bytes:
                            break
                    return dict(url=url, final_url=r.url, status=r.status_code,
                                redirects=[x.url for x in r.history], attempts=attempts,
                                truncated=len(content) > self.max_bytes,
                                html=bytes(content[:self.max_bytes]).decode(r.encoding or "utf-8", errors="replace"))
            except requests.RequestException as exc:
                attempts.append(type(exc).__name__)
                if attempt == 0 and isinstance(exc, (requests.Timeout, requests.ConnectionError)):
                    time.sleep(1)
                    continue
                return dict(url=url, status=None, html="", attempts=attempts, error=f"{type(exc).__name__}: {exc}")


def follow_priority(url: str, kind: str) -> int | None:
    p = urlsplit(url)
    if any(x in url for x in ["{", "}", "[", "]"]) or (p.hostname or "").endswith(("linkedin.com", "indeed.com", "glassdoor.com")):
        return None
    if re.search(r"\.(?:jpg|png|svg|css|pdf|woff2?|mp4|webp|ico|xml)(?:$)", p.path, re.I):
        return None
    if url_signal(url):
        return 0
    if re.match(r"^(?:jobs|careers|apply)\.", p.hostname or "") and p.path.rstrip("/") in {"", "/careers", "/jobs"}:
        return 1
    if JOB_DETAIL.search(p.path):
        return 1
    if SEARCH.search(p.path) and (re.search(r"career|job|position|role", p.path, re.I) or re.match(r"^(?:jobs|careers)\.", p.hostname or "")):
        return 2
    if p.path.endswith(".js"):
        if re.search(r"analytics|tracking|consent|one-trust|onetrust|otsdk|cookielaw|recaptcha|optimizely|transcend-cdn|datadog|qualified|Manifest|airgap|jquery|polyfill|framework|webpack|gtm|footer|navs|styles", url, re.I):
            return None
        if kind == "component":
            return 3
        return 3 if re.search(r"career|job|position", p.path.rsplit("/", 1)[-1], re.I) else 5
    if p.path.endswith(".json") and re.search(r"career|job|position", p.path, re.I):
        return 3
    if "/api/" in p.path and re.search(r"job|position|career", p.path, re.I):
        return 3
    return None


def detect_source(company: str, careers_url: str, *, fetcher=None, max_documents=12, max_pages=6, max_scripts=6) -> dict:
    """Only company + URL enter detection; company is a display label, never a feature."""
    fetcher = fetcher or PublicFetcher()
    start = clean_url(careers_url)
    if not start:
        raise ValueError("careers_url must be an absolute public HTTP(S) URL")
    evidence, audits, native = [], [], []
    signals = {}

    def observe(url, method, via):
        signal = url_signal(url)
        if signal:
            signals.setdefault(signal, []).append(dict(method=method, url=url, found_on=via))

    observe(start, "input_url", start)
    queue = [(0, 0, start, "input")]
    seen, page_keys, pages, scripts, order = set(), set(), 0, 0, 1
    while queue and len(audits) < max_documents:
        queue.sort()
        _, _, url, kind = queue.pop(0)
        if url in seen:
            continue
        script = urlsplit(url).path.endswith(".js")
        # Locale and search-query variants do not warrant repeated inspection.
        parsed = urlsplit(url)
        page_key = (parsed.hostname, re.sub(r"^/(?:[a-z]{2}(?:-[a-zA-Z]{2})?)/", "/", parsed.path).rstrip("/"))
        if not script and page_key in page_keys:
            continue
        if (script and scripts >= max_scripts) or (not script and pages >= max_pages):
            continue
        seen.add(url)
        if not script:
            page_keys.add(page_key)
        scripts += int(script)
        pages += int(not script)
        doc = fetcher(url)
        body = doc.get("html", "")
        final = doc.get("final_url", url)
        audit = {k: v for k, v in doc.items() if k != "html"}
        audit.update(body_sha256=hashlib.sha256(body.encode()).hexdigest(), inspected_characters=len(body))
        audits.append(audit)
        for redirect in doc.get("redirects", []) + [final]:
            observe(redirect, "redirect_or_response_url", url)
        if doc.get("status") != 200:
            continue
        if re.search(r"<title>\s*(?:just a moment|access denied|attention required)", body, re.I):
            audit["error"] = "Challenge page; not interpreted as careers content"
            continue
        links = extract_links(body, final)
        for linked, link_kind in links:
            observe(linked, "script_url" if script else link_kind, final)
        # Repeated typed source IDs in listing metadata identify the family,
        # but cannot establish a reusable board token by themselves.
        if len(re.findall(r'["\x27]greenhouseId["\x27]\s*:\s*\d+', body)) >= 2:
            signals.setdefault(("greenhouse", ""), []).append(dict(method="structured_source_ids", url=final, found_on=final))
        # Stop at unambiguous provider evidence. Generic vendor homepages do not
        # establish a board identifier, and must not stop further inspection.
        if any(identifier for (_, identifier) in signals):
            break
        job_links = sorted({u for u, _ in links if JOB_DETAIL.search(urlsplit(u).path)})
        if script and re.search(r'["\x27]/api/[^"\x27]*job_search', body):
            native.append(dict(method="public_search_api_in_script", url=final))
        if not script:
            if len(job_links) >= 2:
                native.append(dict(method="company_job_links", url=final, examples=job_links[:3]))
            elif re.search(r'["\x27]@type["\x27]\s*:\s*["\x27]JobPosting', html.unescape(body)):
                native.append(dict(method="job_posting_metadata", url=final))
            elif re.search(r"SearchAction|jobsearch|job-search|jobSearch|search-results", body) and re.search(r"career|job|position", final, re.I):
                native.append(dict(method="careers_search_surface", url=final))
        for linked, link_kind in links:
            priority = follow_priority(linked, link_kind)
            if priority is not None and linked not in seen:
                # Hashed page bundles usually follow framework bundles in HTML.
                queue.append((priority, -order if priority == 5 else order, linked, link_kind))
                order += 1
    families = {family for family, _ in signals}
    if len(families) == 1:
        family = next(iter(families))
        identifiers = {ident for fam, ident in signals if ident}
        identifier = next(iter(identifiers)) if len(identifiers) == 1 else ""
        evidence = [e for items in signals.values() for e in items][:8]
        confidence = "high" if identifier else "medium"
        method = evidence[0]["method"]
        note = "" if identifier else "Provider detected; reusable identifier missing or conflicting."
    elif len(families) > 1:
        family, identifier, confidence, method = "unknown", "", "low", "conflicting_providers"
        evidence = [e for items in signals.values() for e in items][:8]
        note = "Multiple ATS families exposed; cannot select authoritative source automatically."
    elif native:
        family, identifier, confidence, method = "company_native_custom", "", "medium", native[0]["method"]
        evidence = native[:4]
        note = "Company careers/search surface verified; underlying ATS and reusable identifier not established."
    else:
        family, identifier, confidence, method = "unknown", "", "low", "insufficient_evidence"
        note = "No reliable source evidence within bounded public inspection; access errors and limits are recorded."
    return dict(company=company, careers_url=careers_url, detected_source_type=family,
                detected_source_identifier=identifier, detection_method=method, confidence=confidence,
                evidence=evidence, adapter_available=family in IMPLEMENTED,
                source_ready=family in IMPLEMENTED and bool(identifier),
                identifier_note=note, requests=audits, inspected_documents=len(audits),
                captured_at=datetime.now(timezone.utc).isoformat())
