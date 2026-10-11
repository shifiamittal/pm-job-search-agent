"""Deterministic US/India geography normalization for discovery candidates."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter

TARGET_COUNTRIES = {"US", "IN"}

COUNTRY_ALIASES = {
    "us": "US", "u s": "US", "usa": "US", "u s a": "US",
    "united states": "US", "united states of america": "US",
    "india": "IN",
    "united kingdom": "GB", "uk": "GB", "great britain": "GB", "england": "GB",
    "canada": "CA", "canadian": "CA", "singapore": "SG", "australia": "AU", "ireland": "IE",
    "netherlands": "NL", "japan": "JP", "germany": "DE", "france": "FR",
    "spain": "ES", "italy": "IT", "brazil": "BR", "mexico": "MX",
    "china": "CN", "hong kong": "HK", "united arab emirates": "AE", "uae": "AE",
    "israel": "IL", "portugal": "PT", "malaysia": "MY", "philippines": "PH",
    "turkey": "TR", "hungary": "HU", "poland": "PL", "egypt": "EG",
    "norway": "NO", "belgium": "BE", "switzerland": "CH", "sweden": "SE",
    "denmark": "DK", "czech republic": "CZ",
}

US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
US_STATE_CODES = set(US_STATES.values())

# City-only values occur in reviewed source exports. Exact membership is intentional.
US_CITIES = {
    "atlanta", "austin", "bellevue", "boston", "chicago", "dallas", "denver",
    "houston", "lehi", "los angeles", "miami", "mountain view", "new york",
    "new york city", "palo alto", "redmond", "san francisco", "san jose", "seattle",
    "sunnyvale", "washington dc",
}
INDIA_CITIES = {
    "ahmedabad", "bangalore", "bengaluru", "chennai", "delhi", "gurgaon",
    "gurugram", "hyderabad", "kolkata", "mumbai", "new delhi", "noida", "pune",
}
INDIA_STATES = {
    "andhra pradesh", "delhi", "gujarat", "haryana", "karnataka", "maharashtra",
    "rajasthan", "tamil nadu", "telangana", "uttar pradesh", "west bengal",
}
FOREIGN_CITIES = {
    "amsterdam": "NL", "belfast": "GB", "berlin": "DE", "dublin": "IE", "london": "GB",
    "singapore": "SG", "sydney": "AU", "tokyo": "JP", "toronto": "CA",
    "vancouver": "CA",
}
GENERIC_REMOTE = {
    "remote", "global", "worldwide", "anywhere", "remote americas", "remote emea",
    "remote apac", "americas", "emea", "apac",
}
COUNTRY_FIELDS = ("country", "country_code", "location_country", "locationCountry", "countries")


def _norm(value) -> str:
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def _values(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (json.JSONDecodeError, TypeError):
            return [text]
    return [part.strip() for part in re.split(r"\s*\|\s*|\s*;\s*", text) if part.strip()]


def raw_locations(job: dict) -> list[str]:
    """Return all source locations without overwriting or collapsing their text."""
    for field in ("all_locations_raw", "all_locations", "locations"):
        if field in job and job.get(field) not in (None, "", []):
            values = _values(job.get(field))
            if values:
                return list(dict.fromkeys(values))
    values = _values(job.get("location"))
    return list(dict.fromkeys(values))


def _country_value(value: str, *, metadata: bool = False) -> str | None:
    normalized = _norm(value)
    if normalized in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[normalized]
    if metadata:
        codes = {"in": "IN", "ind": "IN", "us": "US", "usa": "US", "gb": "GB",
                 "ca": "CA", "sg": "SG", "au": "AU", "ie": "IE", "nl": "NL",
                 "jp": "JP", "de": "DE", "fr": "FR", "es": "ES", "it": "IT",
                 "br": "BR", "mx": "MX", "cn": "CN", "hk": "HK", "ae": "AE"}
        codes.update({"il": "IL", "pt": "PT", "my": "MY", "ph": "PH", "tr": "TR",
                      "hu": "HU", "pl": "PL", "eg": "EG", "no": "NO", "be": "BE",
                      "ch": "CH", "se": "SE", "dk": "DK", "cz": "CZ"})
        if normalized in codes:
            return codes[normalized]
    return None


def location_country(location: str) -> tuple[str | None, str]:
    """Classify one location using exact country/state/city tokens, never fuzzy matching."""
    normalized = _norm(location)
    if not normalized:
        return None, "blank"
    if normalized in GENERIC_REMOTE:
        return None, "ambiguous_remote"
    for alias, country in sorted(COUNTRY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"(?:^|\s){re.escape(alias)}(?:$|\s)", normalized):
            return country, "explicit_country"
    parts = [_norm(part) for part in str(location).split(",") if _norm(part)]
    if len(parts) > 1:
        for part in parts[1:]:
            upper = part.upper()
            if part in US_STATES or upper in US_STATE_CODES:
                return "US", "us_state"
    if normalized in US_STATES or normalized.upper() in US_STATE_CODES:
        return "US", "us_state"
    raw_codes = re.findall(r"(?:^|[\s,|/-])([A-Z]{2})(?=$|[\s,|/-])", str(location))
    if any(code in US_STATE_CODES for code in raw_codes):
        return "US", "us_state"
    if any(re.search(rf"(?:^|\s){re.escape(state)}(?:$|\s)", normalized) for state in US_STATES):
        return "US", "us_state"
    if any(re.search(rf"(?:^|\s){re.escape(state)}(?:$|\s)", normalized) for state in INDIA_STATES):
        return "IN", "india_state"
    if any(re.search(rf"(?:^|\s){re.escape(city)}(?:$|\s)", normalized) for city in US_CITIES):
        return "US", "known_city"
    if any(re.search(rf"(?:^|\s){re.escape(city)}(?:$|\s)", normalized) for city in INDIA_CITIES):
        return "IN", "known_city"
    for city, country in sorted(FOREIGN_CITIES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"(?:^|\s){re.escape(city)}(?:$|\s)", normalized):
            return country, "known_city"
    return None, "unrecognized"


def classify_geography(job: dict) -> dict:
    locations = raw_locations(job)
    metadata_present = [field for field in COUNTRY_FIELDS if field in job and job.get(field) not in (None, "", [])]
    metadata_values = [item for field in metadata_present for item in _values(job.get(field))]
    metadata_countries = {_country_value(item, metadata=True) for item in metadata_values}
    malformed_metadata = bool(metadata_values) and None in metadata_countries
    metadata_countries.discard(None)

    location_results = [location_country(location) for location in locations]
    location_countries = {country for country, _ in location_results if country}
    conflict = bool(metadata_countries and location_countries and
                    not (location_countries <= metadata_countries or metadata_countries <= location_countries))
    if malformed_metadata or conflict:
        countries = sorted(metadata_countries | location_countries)
        status, reason = "geography_unknown", "conflicting_or_malformed_country_metadata"
    else:
        countries = sorted(metadata_countries or location_countries)
        if TARGET_COUNTRIES & set(countries):
            status, reason = "in_scope", "explicit_us_or_india_location"
        elif countries:
            status, reason = "out_of_scope", "known_locations_outside_us_india"
        else:
            status, reason = "geography_unknown", "missing_or_ambiguous_location"
    return {
        "all_locations_raw": locations,
        "normalized_countries": countries,
        "geography_in_scope": status == "in_scope",
        "geography_status": status,
        "geography_reason": reason,
    }


def enrich_geography(job: dict) -> dict:
    return {**job, **classify_geography(job)}


def geography_summary(jobs: list[dict]) -> dict:
    rows = [classify_geography(job) for job in jobs]
    counts = Counter(country for row in rows for country in row["normalized_countries"])
    return {
        "total_jobs_before_geography_gate": len(rows),
        "jobs_kept": sum(row["geography_status"] == "in_scope" for row in rows),
        "jobs_excluded": sum(row["geography_status"] == "out_of_scope" for row in rows),
        "jobs_geography_unknown": sum(row["geography_status"] == "geography_unknown" for row in rows),
        "counts_by_country": dict(sorted(counts.items())),
    }
