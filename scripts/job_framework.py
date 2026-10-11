"""Deprecated legacy classification engine; historical reads only.

The sole decision contract for new runs is shortlist/ v1.2.0. Legacy generators/validators are
retired, not compatibility mappings. Single-job/batch execution exists; shared v1 persistence remains unimplemented.
"""
from __future__ import annotations

import csv
import json
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_legacy_jobs(root=ROOT):
    """Read every historical JSONL record without changing or validating old policy."""
    path = Path(root) / "data/jobs_raw.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_legacy_csv(path):
    """Read old columns verbatim, including reviewer fields and old classifications."""
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_canonical_jobs(root=ROOT):
    """Deprecated read alias only; returned records are NOT canonical shortlist v1."""
    warnings.warn("load_canonical_jobs reads legacy history only; use load_legacy_jobs", DeprecationWarning, stacklevel=2)
    return load_legacy_jobs(root)


def _blocked(component):
    # Lazy import keeps historical reads usable without shortlist dependencies.
    from shortlist_contract import integration_pending
    integration_pending(component)


def taxonomy(*args, **kwargs):
    _blocked("Legacy classification taxonomy")


def validate_job(*args, **kwargs):
    _blocked("Legacy classification validation; use validate_shortlist_record for supplied v1 state")


def validate_jobs(*args, **kwargs):
    _blocked("Legacy classification validation")


def review_queue(*args, **kwargs):
    _blocked("Legacy review queue generation")


def synthesize_skills(*args, **kwargs):
    _blocked("Legacy strategic skill synthesis")


def persist_discovery_run(*args, **kwargs):
    _blocked("Classified-job persistence and Sheet finalization")
