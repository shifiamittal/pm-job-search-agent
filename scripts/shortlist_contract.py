"""Read-only validation of supplied shortlist v1 state; never creates decisions.

Schema/structural validation cannot establish factual grounding or semantic truth.
The controller specified in shortlist/controller_validation.md remains authoritative.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "shortlist/schema.yaml"

_US_STATES = {
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
_US_STATE_ALIASES = {**_US_STATES, **{code.casefold(): code for code in _US_STATES.values()}}
_COUNTRY_ALIASES = {
    "us": "US", "u s": "US", "usa": "US", "united states": "US",
    "united states of america": "US", "canada": "CA", "india": "IN",
    "united kingdom": "GB", "uk": "GB", "great britain": "GB",
}


def _location_part(value):
    return " ".join(re.sub(r"[^\w]+", " ", unicodedata.normalize("NFKC", value).casefold()).split())


def _normalized_location(value):
    if value is None:
        return None
    parts = [_location_part(part) for part in re.split(r"[,;|/]", value) if _location_part(part)]
    if not parts:
        return ("", frozenset(), frozenset(), frozenset())
    city = parts[0]
    states, countries, other = set(), set(), set()
    for qualifier in parts[1:]:
        if qualifier in _US_STATE_ALIASES:
            states.add(_US_STATE_ALIASES[qualifier])
            countries.add("US")
        elif qualifier in _COUNTRY_ALIASES:
            countries.add(_COUNTRY_ALIASES[qualifier])
        else:
            other.add(qualifier)
    return city, frozenset(states), frozenset(countries), frozenset(other)


def locations_equivalent(left, right):
    """Compare deterministic city/state/country identity without fuzzy matching."""
    if left is None or right is None:
        return left is right
    left_location, right_location = _normalized_location(left), _normalized_location(right)
    if left_location[0] != right_location[0]:
        return False
    for index in (1, 2):
        if left_location[index] and right_location[index] and left_location[index] != right_location[index]:
            return False
    # Unknown region/country qualifiers are never fuzzily discarded or equated to a state.
    if left_location[3] != right_location[3] and (left_location[3] or right_location[3]):
        return False
    return True


class ShortlistIntegrationPending(RuntimeError):
    """A retired consumer must not generate or publish legacy recommendations."""


def integration_pending(component):
    raise ShortlistIntegrationPending(
        f"{component} is blocked pending shortlist-runner integration. "
        "shortlist/ v1.2.0 is authoritative for new runs; legacy decisions are read-only history. "
        "See docs/shortlist_v1_migration.md. No data was written or synchronized."
    )


def _v11_schema(current):
    """Derive the frozen 1.1.0 shape for read-only historical validation."""
    legacy = copy.deepcopy(current)
    legacy["title"] = "Role Shortlist Workflow — version 1.1.0 (historical)"
    legacy["properties"]["schema_version"]["const"] = "1.1.0"
    for definition in ("role_understanding", "role_state"):
        legacy["$defs"][definition]["properties"].pop("baseline_qualifications")
        legacy["$defs"][definition]["required"].remove("baseline_qualifications")
    for definition in ("career_requirements_mapping", "career_mapping_state"):
        legacy["$defs"][definition]["properties"].pop("baseline_qualification_mapping")
        legacy["$defs"][definition]["required"].remove("baseline_qualification_mapping")
    legacy["$defs"].pop("baseline_qualification")
    legacy["$defs"].pop("baseline_qualification_mapping")
    return legacy


def _legacy_schema(current):
    """Derive the frozen 1.0.0 shape for read-only historical validation."""
    legacy = _v11_schema(current)
    legacy["title"] = "Role Shortlist Workflow — version 1.0.0 (historical)"
    legacy["properties"]["schema_version"]["const"] = "1.0.0"
    criterion = legacy["$defs"]["criterion_mapping"]
    fit_enum = criterion["properties"].pop("overall_fit_assessment")["enum"]
    criterion["properties"].pop("capability_fit")
    criterion["properties"].pop("domain_context_fit")
    criterion["properties"]["evidence_type"] = {"type": "string", "enum": ["direct", "transferable", "adjacent", "gap"]}
    criterion["properties"]["fit_assessment"] = {"type": "string", "enum": fit_enum}
    criterion["required"] = ["criterion_id", "criterion", "role_requirement", "strongest_evidence",
                             "evidence_type", "fit_assessment", "limitation_or_difference"]
    criterion["allOf"] = [
        {"if": {"properties": {"evidence_type": {"enum": ["direct", "transferable", "adjacent"]}}},
         "then": {"properties": {"strongest_evidence": {"properties": {
             "project_or_role": {"type": "string", "minLength": 1, "pattern": r"\S"},
             "evidence_summary": {"type": "string", "minLength": 1, "pattern": r"\S"}}}}}},
        {"if": {"properties": {"evidence_type": {"enum": ["transferable", "adjacent", "gap"]}}},
         "then": {"properties": {"limitation_or_difference": {"type": "string", "minLength": 1, "pattern": r"\S"}}}},
    ]
    validation = legacy["$defs"]["validation"]
    validation["properties"]["direct_vs_transferable_check_passed"] = validation["properties"].pop("capability_domain_fit_check_passed")
    validation["required"] = ["direct_vs_transferable_check_passed" if x == "capability_domain_fit_check_passed" else x
                              for x in validation["required"]]
    then_props = validation["allOf"][0]["then"]["properties"]
    then_props["direct_vs_transferable_check_passed"] = then_props.pop("capability_domain_fit_check_passed")
    check = legacy["$defs"]["evidence_check"]
    check["properties"].pop("capability_fit_classified")
    check["properties"].pop("domain_context_fit_classified")
    check["properties"]["direct_vs_transferable_classified"] = {"type": "boolean"}
    check["required"] = ["role_requirement_identified", "career_evidence_identified", "evidence_source_exists",
                         "direct_vs_transferable_classified", "limitations_preserved"]
    state = legacy["$defs"]["career_mapping_state"]
    projection = state["properties"].pop("capability_domain_classification")
    item = projection["items"]
    item["properties"].pop("capability_fit")
    item["properties"].pop("domain_context_fit")
    item["properties"].pop("overall_fit_assessment")
    item["properties"]["evidence_type"] = {"type": "string", "enum": ["direct", "transferable", "adjacent", "gap"]}
    item["required"] = ["criterion_id", "evidence_type", "limitation_or_difference"]
    state["properties"]["direct_vs_transferable_classification"] = projection
    state["required"] = ["direct_vs_transferable_classification" if x == "capability_domain_classification" else x
                         for x in state["required"]]
    return legacy


def load_schema(version="1.2.0"):
    from jsonschema import Draft202012Validator
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    if version == "1.2.0":
        return schema
    if version == "1.1.0":
        historical = _v11_schema(schema)
        Draft202012Validator.check_schema(historical)
        return historical
    if version == "1.0.0":
        legacy = _legacy_schema(schema)
        Draft202012Validator.check_schema(legacy)
        return legacy
    raise ValueError(f"Unsupported shortlist schema version: {version}")


def shortlist_outcomes():
    """Read exact outcome spellings from the authoritative schema."""
    return tuple(load_schema()["$defs"]["shortlist_decision"]["properties"]["decision"]["enum"])


def validate_shortlist_record(record):
    """Check shape and referential consistency without modifying or accepting state.

    Does NOT run role analysis, fetch evidence, confirm claims, set flags, decide,
    route, rank, write files, or certify controller acceptance.
    """
    from jsonschema import Draft202012Validator

    schema = load_schema(record.get("schema_version"))
    errors = sorted(Draft202012Validator(schema).iter_errors(record),
                    key=lambda error: str(list(error.absolute_path)))
    if errors:
        error = errors[0]
        path = ".".join(str(part) for part in error.absolute_path) or "record"
        raise ValueError(f"Invalid shortlist v1 structure at {path}: {error.message}")
    role = record["role_understanding"]
    mapping = record["career_requirements_mapping"]
    decision = record["shortlist_decision"]
    for key, value in role["role_identity"].items():
        if record["job"][key] != value:
            raise ValueError(f"Job identity mismatch: {key}")
    for key, value in decision["location_work_model"].items():
        matches = (locations_equivalent(role["role_identity"][key], value) if key == "location"
                   else role["role_identity"][key] == value)
        if not matches:
            raise ValueError(f"Decision location/work-model mismatch: {key}")

    criteria = role["hiring_criteria"]
    ids = [criterion["criterion_id"] for criterion in criteria]
    mapped_ids = [criterion["criterion_id"] for criterion in mapping["criteria"]]
    if len(set(ids)) != len(ids) or len(set(mapped_ids)) != len(mapped_ids):
        raise ValueError("Criterion IDs must be unique in each stage")
    if set(ids) != set(mapped_ids):
        raise ValueError("Career mapping must cover exactly the upstream criterion IDs")
    names = {criterion["criterion_id"]: criterion["criterion"] for criterion in criteria}
    for criterion in mapping["criteria"]:
        if criterion["criterion"] != names[criterion["criterion_id"]]:
            raise ValueError("Career mapping changed an upstream criterion name")
    for story in mapping["strongest_role_stories"]:
        if not set(story["criteria_supported"]) <= set(ids):
            raise ValueError("Story references an unknown criterion")
    requirements = [item["requirement"] for item in role["specialist_requirements"]]
    mapped_requirements = [item["requirement"] for item in mapping["specialist_requirement_mapping"]]
    if len(set(requirements)) != len(requirements) or len(set(mapped_requirements)) != len(mapped_requirements):
        raise ValueError("Specialist requirements must be unique in each stage")
    if sorted(requirements) != sorted(mapped_requirements):
        raise ValueError("Specialist requirements must be preserved in career mapping")
    if record["schema_version"] == "1.2.0":
        qualifications = {item["qualification_id"]: item for item in role["baseline_qualifications"]}
        mapped_qualifications = {item["qualification_id"]: item for item in mapping["baseline_qualification_mapping"]}
        if len(qualifications) != len(role["baseline_qualifications"]) or \
                len(mapped_qualifications) != len(mapping["baseline_qualification_mapping"]):
            raise ValueError("Baseline qualification IDs must be unique in each stage")
        if set(qualifications) != set(mapped_qualifications):
            raise ValueError("Baseline qualification mapping must cover exactly the upstream qualifications")
        for qualification_id, item in mapped_qualifications.items():
            upstream = qualifications[qualification_id]
            for field in ("requirement", "requirement_type", "required_or_preferred"):
                if item[field] != upstream[field]:
                    raise ValueError(f"Baseline qualification mapping changed upstream {field}")

    if "handoff" in record:
        # Compare only; do not generate or enqueue a handoff.
        expected_role = {key: value for key, value in role.items() if key != "role_identity"}
        expected_role.update({key: role["role_identity"][key] for key in ("location", "work_model")})
        expected_mapping = {key: value for key, value in mapping.items() if key != "criteria"}
        expected_mapping["criteria_mapping"] = mapping["criteria"]
        if record["schema_version"] == "1.0.0":
            expected_mapping["direct_vs_transferable_classification"] = [
                {key: criterion[key] for key in ("criterion_id", "evidence_type", "limitation_or_difference")}
                for criterion in mapping["criteria"]]
        else:
            expected_mapping["capability_domain_classification"] = [
                {key: criterion[key] for key in ("criterion_id", "capability_fit", "domain_context_fit",
                                                  "overall_fit_assessment", "limitation_or_difference")}
                for criterion in mapping["criteria"]]
        expected = {"role_state": expected_role, "career_mapping_state": expected_mapping,
                    "shortlist_decision": decision, "validation": record["validation"]}
        if record["handoff"] != expected:
            raise ValueError("Handoff must exactly preserve canonical upstream state")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="One already completed v1 JSON record")
    args = parser.parse_args()
    try:
        record = json.loads(args.input.read_text(encoding="utf-8-sig"))
        validate_shortlist_record(record)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Shortlist validation failed: {exc}\n")
    print("Schema and structural consistency passed. Factual/semantic controller review remains required; no state was changed.")


if __name__ == "__main__":
    main()
