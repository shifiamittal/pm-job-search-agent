"""Sequentially orchestrate the existing single-job shortlist workflow over CSV/JSONL."""
from __future__ import annotations

import argparse
import csv
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

import run_shortlist_job as single
from shortlist_model import ResponsesModel


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BATCH_ROOT = ROOT / "local_private" / "shortlist_batches"
DEFAULT_STAGE_MODELS = {
    "role_understanding": "gpt-6-luna",
    "career_requirements_mapping": "gpt-6-sol",
    "shortlist_decision": "gpt-6-luna",
    "controller_validation": "gpt-6-luna",
}
SUMMARY_FIELDS = (
    "company", "title", "job_id", "requisition_id", "location", "canonical_url", "source",
    "decision", "actual_work_alignment", "scope_assessment", "evidence_strength", "career_value",
    "key_gap_or_risk", "decision_rationale", "controller_accepted", "review_order",
    "run_status", "failed_stage", "error_type", "error_message", "run_id",
    "role_model", "mapping_model", "decision_model", "controller_model",
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
    "reasoning_tokens", "elapsed_seconds",
)
FAILURE_FIELDS = (
    "company", "title", "job_id", "location", "input_index", "failed_stage",
    "error_type", "error_message", "run_id", "run_path",
)
USAGE_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                "output_tokens", "reasoning_tokens", "elapsed_seconds")


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _sha_json(value):
    return single._hash(single._json(value))


def _read_artifact(path):
    return json.loads((Path(path) / "job_state.json").read_text(encoding="utf-8"))


def _decode_csv(path):
    raw = Path(path).read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def load_batch_records(path):
    """Load every row independently; row-level validation failures remain isolatable."""
    path = Path(path)
    suffix = path.suffix.casefold()
    records = []
    if suffix == ".csv":
        previous_limit = csv.field_size_limit()
        try:
            csv.field_size_limit(max(previous_limit, 2**31 - 1))
            with io.StringIO(_decode_csv(path), newline="") as stream:
                reader = csv.DictReader(stream, strict=True)
                headers = reader.fieldnames or []
                if not headers:
                    raise ValueError("Batch CSV has no header")
                if len(set(headers)) != len(headers):
                    raise ValueError("Batch CSV has duplicate column names")
                for index, row in enumerate(reader, 1):
                    raw_hash = _sha_json(row)
                    try:
                        job = single.normalize_csv_row(path, row, index)
                        single.validate_input(job)
                        records.append({"input_index": index, "job": job,
                                        "input_sha256": _sha_json(job), "raw_sha256": raw_hash})
                    except (TypeError, ValueError) as exc:
                        records.append({"input_index": index, "job": None, "raw_sha256": raw_hash,
                                        "input_sha256": raw_hash,
                                        "load_error": {"type": type(exc).__name__, "message": str(exc)}})
        except csv.Error as exc:
            raise ValueError(f"Cannot parse batch CSV: {exc}") from None
        finally:
            csv.field_size_limit(previous_limit)
    elif suffix in (".jsonl", ".ndjson"):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            record_index = 0
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                record_index += 1
                raw_hash = single._hash(line)
                try:
                    value = json.loads(line)
                    job = single.normalize_input(
                        value, row_identity=f"{path.resolve().as_posix()}#line={line_number}")
                    records.append({"input_index": record_index, "source_line": line_number,
                                    "job": job, "input_sha256": _sha_json(job),
                                    "raw_sha256": raw_hash})
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    records.append({"input_index": record_index, "source_line": line_number,
                                    "job": None, "raw_sha256": raw_hash,
                                    "input_sha256": raw_hash,
                                    "load_error": {"type": type(exc).__name__, "message": str(exc)}})
    else:
        raise ValueError("Batch input must use .csv, .jsonl, or .ndjson")
    if not records:
        raise ValueError("Batch input contains no job records")
    return records


def _job_reuse_hash(job):
    if job is None:
        return None
    material = {key: value for key, value in job.items()
                if key not in ("row_identity", "internal_record_key")}
    return _sha_json(material)


def _contract_fingerprints(candidate_root=ROOT):
    contracts = {name: single._hash(single._read_full(ROOT / name))
                 for name in single.CONTRACT_FILES}
    candidate = {name: single._hash(single._read_full(Path(candidate_root) / name))
                 for name in single.CANDIDATE_FILES}
    schema = _sha_bytes((ROOT / "shortlist/schema.yaml").read_bytes())
    return {"contract_hashes": contracts, "candidate_context_hashes": candidate,
            "schema_sha256": schema}


def resolve_models(fallback=None, overrides=None, saved=None):
    if saved is not None and fallback is None and not any((overrides or {}).values()):
        return deepcopy(saved)
    models = ({stage: fallback for stage in single.STAGES} if fallback
              else deepcopy(saved or DEFAULT_STAGE_MODELS))
    for stage, value in (overrides or {}).items():
        if value:
            models[stage] = value
    return single.resolve_stage_models(None, models)


def _new_entry(record):
    job = record.get("job")
    entry = {
        "input_index": record["input_index"],
        "source_line": record.get("source_line"),
        "input_sha256": record["input_sha256"],
        "job_reuse_sha256": _job_reuse_hash(job),
        "internal_record_key": job.get("internal_record_key") if job else None,
        "job": deepcopy(job), "status": "pending", "run_id": None, "run_path": None,
        "failed_stage": None, "error_type": None, "error_message": None,
        "duplicate_of": None, "reused": False, "last_action": None,
    }
    if record.get("load_error"):
        entry.update({"status": "failed", "failed_stage": "input_validation",
                      "error_type": record["load_error"]["type"],
                      "error_message": record["load_error"]["message"],
                      "last_action": "input_rejected"})
    return entry


def _mark_duplicates(entries):
    seen = {}
    for entry in entries:
        fingerprint = entry.get("job_reuse_sha256")
        if not fingerprint or entry["status"] == "failed":
            continue
        if fingerprint in seen:
            entry["duplicate_of"] = seen[fingerprint]["input_index"]
        else:
            seen[fingerprint] = entry


def _artifact_usage(artifact):
    totals = {key: 0 for key in USAGE_FIELDS}
    has = {key: False for key in USAGE_FIELDS}
    for call in artifact.get("model_calls", []):
        telemetry = call.get("telemetry") or {}
        for key in USAGE_FIELDS:
            value = telemetry.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[key] += value
                has[key] = True
    return {key: round(totals[key], 3) if has[key] else None for key in USAGE_FIELDS}


def _mapping_usage(artifacts):
    result = {"input_tokens": 0, "cached_input_tokens": 0,
              "cache_write_input_tokens": 0, "calls": 0, "calls_with_cache_hits": 0}
    for artifact in artifacts:
        for call in artifact.get("model_calls", []):
            if call.get("stage") != "career_requirements_mapping" or not call.get("telemetry"):
                continue
            telemetry = call["telemetry"]
            result["calls"] += 1
            for key in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens"):
                value = telemetry.get(key)
                if isinstance(value, int) and not isinstance(value, bool):
                    result[key] += value
            if (telemetry.get("cached_input_tokens") or 0) > 0:
                result["calls_with_cache_hits"] += 1
    result["cache_hit_rate_by_tokens"] = (
        round(result["cached_input_tokens"] / result["input_tokens"], 6)
        if result["input_tokens"] else 0.0)
    return result


def _entry_artifact(batch_dir, entry):
    if not entry.get("run_path"):
        return None
    path = batch_dir / entry["run_path"]
    try:
        return _read_artifact(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _summary_row(entry, artifact, models):
    job = entry.get("job") or {}
    state = artifact.get("shortlist_state") if artifact else None
    decision = state.get("shortlist_decision", {}) if state else {}
    gap = decision.get("key_gap_or_risk") or {}
    gap_text = gap.get("description") or ""
    if gap.get("severity"):
        gap_text = f"{gap_text} [{gap['severity']}]".strip()
    accepted = (state.get("validation", {}).get("shortlist_decision_accepted")
                if state else None)
    usage = _artifact_usage(artifact or {})
    outcome = decision.get("decision")
    review_order = ({"APPLY — PRIORITY": 1, "APPLY": 2,
                     "HOLD / INVESTIGATE": 3, "DO NOT APPLY": 4}.get(outcome, 5)
                    if entry["status"] == "accepted" else 5)
    return {
        "company": job.get("company"), "title": job.get("title"),
        "job_id": job.get("job_id"), "requisition_id": job.get("requisition_id"),
        "location": job.get("location"), "canonical_url": job.get("canonical_job_url"),
        "source": job.get("source"), "decision": outcome,
        "actual_work_alignment": (decision.get("actual_work_alignment") or {}).get("classification"),
        "scope_assessment": (decision.get("scope_assessment") or {}).get("classification"),
        "evidence_strength": (decision.get("evidence_strength") or {}).get("classification"),
        "career_value": (decision.get("career_value") or {}).get("classification"),
        "key_gap_or_risk": gap_text, "decision_rationale": decision.get("decision_rationale"),
        "controller_accepted": accepted, "review_order": review_order,
        "run_status": entry["status"], "failed_stage": entry.get("failed_stage"),
        "error_type": entry.get("error_type"), "error_message": entry.get("error_message"),
        "run_id": entry.get("run_id"),
        "role_model": models["role_understanding"],
        "mapping_model": models["career_requirements_mapping"],
        "decision_model": models["shortlist_decision"],
        "controller_model": models["controller_validation"], **usage,
    }


def _write_csv(path, fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    single._write(path, stream.getvalue())


def _refresh_manifest(manifest, batch_dir):
    entries = manifest["jobs"]
    counts = {status: sum(entry["status"] == status for entry in entries)
              for status in ("pending", "running", "accepted", "rejected", "failed")}
    manifest.update({
        "completed_jobs": counts["accepted"] + counts["rejected"],
        "accepted_jobs": counts["accepted"], "controller_rejected_jobs": counts["rejected"],
        "failed_jobs": counts["failed"],
        "skipped_reused_jobs": sum(bool(entry.get("reused")) for entry in entries),
        "pending_jobs": counts["pending"] + counts["running"], "updated_at": _now(),
    })
    artifacts, seen_runs = [], set()
    for entry in entries:
        if entry.get("run_id") and entry["run_id"] not in seen_runs:
            artifact = _entry_artifact(batch_dir, entry)
            if artifact:
                artifacts.append(artifact)
                seen_runs.add(entry["run_id"])
    total = {key: 0 for key in USAGE_FIELDS}
    present = {key: False for key in USAGE_FIELDS}
    for artifact in artifacts:
        usage = _artifact_usage(artifact)
        for key, value in usage.items():
            if value is not None:
                total[key] += value
                present[key] = True
    manifest["usage"] = {
        "totals": {key: round(total[key], 3) if present[key] else None for key in USAGE_FIELDS},
        "mapping": _mapping_usage(artifacts),
    }


def persist_batch(manifest, batch_dir):
    """Atomically refresh the manifest and all review projections."""
    _refresh_manifest(manifest, batch_dir)
    single._write(batch_dir / "manifest.json", single._json(manifest))
    rows = [_summary_row(entry, _entry_artifact(batch_dir, entry), manifest["stage_models"])
            for entry in manifest["jobs"]]
    _write_csv(batch_dir / "shortlist_summary.csv", SUMMARY_FIELDS, rows)
    single._write(batch_dir / "shortlist_summary.jsonl",
                  "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows))
    failures = []
    for entry, row in zip(manifest["jobs"], rows):
        if entry["status"] != "failed":
            continue
        failures.append({**row, "input_index": entry["input_index"],
                         "run_path": entry.get("run_path")})
    _write_csv(batch_dir / "failures.csv", FAILURE_FIELDS, failures)


def _apply_artifact(entry, artifact, batch_dir, run_dir, *, action):
    entry.update({
        "status": artifact["status"], "run_id": artifact["run_id"],
        "run_path": Path(run_dir).resolve().relative_to(batch_dir.resolve()).as_posix(),
        "last_action": action,
    })
    error = artifact.get("error") or {}
    entry["failed_stage"] = error.get("stage")
    entry["error_type"] = error.get("type")
    entry["error_message"] = error.get("message")


def _sync_duplicate(entry, primary):
    for key in ("status", "run_id", "run_path", "failed_stage", "error_type", "error_message"):
        entry[key] = primary.get(key)
    entry["reused"] = True
    entry["last_action"] = "duplicate_reused"


def _validate_resume(manifest, input_path, input_hash, fingerprints, models, settings):
    checks = {
        "input file path": str(Path(input_path).resolve()) == manifest["input_source"],
        "input file hash": input_hash == manifest["input_sha256"],
        "stage model configuration": models == manifest["stage_models"],
        "model settings": settings == manifest["model_settings"],
        "shortlist contracts": fingerprints["contract_hashes"] == manifest["contract_hashes"],
        "shortlist schema": fingerprints["schema_sha256"] == manifest["schema_sha256"],
        "candidate context": fingerprints["candidate_context_hashes"] == manifest["candidate_context_hashes"],
    }
    failed = [name for name, valid in checks.items() if not valid]
    if failed:
        raise ValueError("Batch resume blocked because " + ", ".join(failed) + " changed")


def plan_batch(records, models, input_path, max_jobs=None, manifest=None):
    selected = records[:max_jobs] if max_jobs is not None else records
    reusable = 0
    if manifest:
        reusable = sum(entry["status"] in ("accepted", "rejected") for entry in manifest["jobs"])
    else:
        seen = set()
        for record in selected:
            fingerprint = _job_reuse_hash(record.get("job"))
            if fingerprint and fingerprint in seen:
                reusable += 1
            elif fingerprint:
                seen.add(fingerprint)
    return {"input_source": str(Path(input_path).resolve()), "total_input_jobs": len(records),
            "selected_jobs": len(selected), "reusable_jobs": reusable,
            "new_or_incomplete_jobs": len(selected) - reusable, "stage_models": models,
            "model_calls": 0, "dry_run": True}


def create_manifest(records, input_path, input_hash, models, settings, fingerprints,
                    *, max_jobs=None, batch_id=None):
    selected = records[:max_jobs] if max_jobs is not None else records
    entries = [_new_entry(record) for record in selected]
    _mark_duplicates(entries)
    created = _now()
    return {
        "artifact_version": "shortlist-batch-v1", "batch_id": batch_id or uuid4().hex,
        "input_source": str(Path(input_path).resolve()), "input_sha256": input_hash,
        "input_format": Path(input_path).suffix.casefold().lstrip("."),
        "created_at": created, "started_at": created, "updated_at": created,
        "completed_at": None, "status": "running", "stage_models": deepcopy(models),
        "model_settings": deepcopy(settings), **deepcopy(fingerprints),
        "total_input_jobs": len(records), "selected_jobs": len(selected),
        "max_jobs": max_jobs, "completed_jobs": 0, "accepted_jobs": 0,
        "controller_rejected_jobs": 0, "failed_jobs": 0, "skipped_reused_jobs": 0,
        "pending_jobs": len(selected), "usage": {}, "jobs": entries, "history": [],
    }


def execute_batch(manifest, batch_dir, model, *, candidate_root=ROOT):
    """Run primaries sequentially and checkpoint every row; one failure never stops peers."""
    batch_dir = Path(batch_dir)
    runs_dir = batch_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    by_index = {entry["input_index"]: entry for entry in manifest["jobs"]}
    persist_batch(manifest, batch_dir)
    for entry in manifest["jobs"]:
        if entry.get("duplicate_of") is not None:
            primary = by_index[entry["duplicate_of"]]
            if primary["status"] != "pending" and primary["status"] != "running":
                _sync_duplicate(entry, primary)
                persist_batch(manifest, batch_dir)
            continue
        if entry["status"] in ("accepted", "rejected"):
            entry["reused"] = True
            entry["last_action"] = "skipped_completed"
            persist_batch(manifest, batch_dir)
            continue
        if entry["status"] == "failed" and entry.get("failed_stage") == "input_validation":
            persist_batch(manifest, batch_dir)
            continue
        entry["status"] = "running"
        entry["last_action"] = "resuming" if entry.get("run_path") else "starting"
        if not entry.get("run_id"):
            entry["run_id"] = uuid4().hex
            entry["run_path"] = (Path("runs") / entry["run_id"]).as_posix()
        persist_batch(manifest, batch_dir)
        run_dir = batch_dir / entry["run_path"]
        try:
            if (run_dir / "job_state.json").is_file():
                completed_dir = single.resume_job(
                    run_dir, model, candidate_root=candidate_root,
                    stage_models=manifest["stage_models"])
                action = "resumed"
            else:
                completed_dir = single.run_job(
                    entry["job"], model, output_root=runs_dir,
                    candidate_root=candidate_root, stage_models=manifest["stage_models"],
                    run_id=entry["run_id"])
                action = "completed"
            artifact = _read_artifact(completed_dir)
            _apply_artifact(entry, artifact, batch_dir, completed_dir, action=action)
        except single.RunError as exc:
            artifact = _read_artifact(exc.run_dir)
            _apply_artifact(entry, artifact, batch_dir, exc.run_dir, action="failed")
        except Exception as exc:
            if not (run_dir / "job_state.json").is_file():
                entry["run_id"] = None
                entry["run_path"] = None
            entry.update({"status": "failed", "failed_stage": "batch_orchestration",
                          "error_type": type(exc).__name__, "error_message": str(exc),
                          "last_action": "failed"})
        persist_batch(manifest, batch_dir)
        for duplicate in manifest["jobs"]:
            if duplicate.get("duplicate_of") == entry["input_index"]:
                _sync_duplicate(duplicate, entry)
                persist_batch(manifest, batch_dir)
    manifest["completed_at"] = _now()
    manifest["status"] = "completed_with_failures" if any(
        entry["status"] == "failed" for entry in manifest["jobs"]) else "completed"
    manifest["history"].append({"event": "batch_finished", "at": manifest["completed_at"],
                                "status": manifest["status"]})
    persist_batch(manifest, batch_dir)
    return batch_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Geography-filtered CSV or JSONL universe")
    source.add_argument("--resume-batch", help="Batch ID beneath --batch-root")
    parser.add_argument("--batch-root", type=Path, default=DEFAULT_BATCH_ROOT)
    parser.add_argument("--max-jobs", type=int, help="Process only the first N input records")
    parser.add_argument("--dry-run", action="store_true", help="Print a plan without model calls or writes")
    parser.add_argument("--model", help="Fallback model for all stages")
    parser.add_argument("--role-model")
    parser.add_argument("--mapping-model")
    parser.add_argument("--decision-model")
    parser.add_argument("--controller-model")
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--timeout", type=int)
    args = parser.parse_args(argv)
    if args.max_jobs is not None and args.max_jobs < 1:
        parser.error("--max-jobs must be positive")
    if args.resume_batch and not re.fullmatch(r"[0-9a-f]{32}", args.resume_batch):
        parser.error("--resume-batch must be a 32-character hexadecimal batch ID")
    if args.resume_batch and args.max_jobs is not None:
        parser.error("--max-jobs is fixed when a batch is created and cannot change on resume")
    overrides = {
        "role_understanding": args.role_model,
        "career_requirements_mapping": args.mapping_model,
        "shortlist_decision": args.decision_model,
        "controller_validation": args.controller_model,
    }
    try:
        if args.resume_batch:
            batch_dir = args.batch_root / args.resume_batch
            manifest = json.loads((batch_dir / "manifest.json").read_text(encoding="utf-8"))
            input_path = Path(manifest["input_source"])
            models = resolve_models(args.model, overrides, saved=manifest["stage_models"])
            settings = {"timeout": args.timeout if args.timeout is not None else manifest["model_settings"]["timeout"],
                        "max_output_tokens": args.max_output_tokens if args.max_output_tokens is not None else manifest["model_settings"]["max_output_tokens"]}
        else:
            input_path = args.input
            models = resolve_models(args.model, overrides)
            settings = {"timeout": args.timeout if args.timeout is not None else 180,
                        "max_output_tokens": args.max_output_tokens if args.max_output_tokens is not None else 12000}
        raw = input_path.read_bytes()
        input_hash = _sha_bytes(raw)
        records = load_batch_records(input_path)
        fingerprints = _contract_fingerprints()
        if args.resume_batch:
            _validate_resume(manifest, input_path, input_hash, fingerprints, models, settings)
            if args.dry_run:
                print(json.dumps(plan_batch(records, models, input_path, manifest=manifest), indent=2))
                return 0
            manifest["status"] = "running"
            manifest["completed_at"] = None
            manifest["history"].append({"event": "batch_resumed", "at": _now()})
        else:
            if args.dry_run:
                print(json.dumps(plan_batch(records, models, input_path, args.max_jobs), indent=2))
                return 0
            manifest = create_manifest(records, input_path, input_hash, models, settings,
                                       fingerprints, max_jobs=args.max_jobs)
            batch_dir = args.batch_root / manifest["batch_id"]
            batch_dir.mkdir(parents=True, exist_ok=False)
        transport = ResponsesModel(next(iter(models.values())), timeout=settings["timeout"],
                                   max_output_tokens=settings["max_output_tokens"])
        execute_batch(manifest, batch_dir, transport)
        print(f"{manifest['status']}: {batch_dir}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    sys.exit(main())
