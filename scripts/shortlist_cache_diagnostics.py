"""Offline prompt-prefix comparison and opt-in two-call cache probe.

This utility never executes a shortlist stage.  Its live mode sends two deliberately
small-output Responses requests that reuse the production Career Mapping prefix and
differ only in a tiny synthetic job suffix.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

import requests

import run_shortlist_job as runner
from shortlist_contract import load_schema
from shortlist_model import ResponsesModel, api_error_diagnostics


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = ROOT / "local_private" / "shortlist"
DEFAULT_DIAGNOSTIC_ROOT = ROOT / "local_private" / "cache_diagnostics"
MAPPING_STAGE = "career_requirements_mapping"


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _mapping_call(artifact):
    calls = [call for call in artifact.get("model_calls", [])
             if call.get("stage") == MAPPING_STAGE]
    if not calls:
        raise ValueError(f"Run {artifact.get('run_id')} has no Career Mapping call")
    return calls[-1]


def _mapping_timestamp(artifact):
    events = [event for event in artifact.get("history", [])
              if event.get("event") == "stage_completed" and
              event.get("stage") == MAPPING_STAGE]
    if not events:
        raise ValueError(f"Run {artifact.get('run_id')} has no timestamped Career Mapping completion")
    return events[-1]["at"]


def _mapping_context(artifact):
    return {
        "input_job": artifact["normalized_job"],
        "upstream": {"role_understanding": artifact["stage_outputs"]["role_understanding"]},
        "candidate_context": artifact["candidate_context"],
    }


def _first_difference(left, right, path="$"):
    if type(left) is not type(right):
        return {"path": path, "left_type": type(left).__name__,
                "right_type": type(right).__name__}
    if isinstance(left, dict):
        left_keys, right_keys = list(left), list(right)
        for index in range(max(len(left_keys), len(right_keys))):
            if index >= len(left_keys) or index >= len(right_keys):
                return {"path": path, "left_keys": left_keys, "right_keys": right_keys}
            if left_keys[index] != right_keys[index]:
                return {"path": path, "left_key": left_keys[index],
                        "right_key": right_keys[index]}
            key = left_keys[index]
            difference = _first_difference(left[key], right[key], f"{path}.{key}")
            if difference:
                return difference
        return None
    if isinstance(left, list):
        for index in range(max(len(left), len(right))):
            if index >= len(left) or index >= len(right):
                return {"path": path, "left_length": len(left), "right_length": len(right)}
            difference = _first_difference(left[index], right[index], f"{path}[{index}]")
            if difference:
                return difference
        return None
    if left != right:
        # Avoid copying job descriptions or candidate evidence into diagnostics.
        return {"path": path, "left_sha256": _sha(str(left)),
                "right_sha256": _sha(str(right))}
    return None


def compare_saved_runs(left, right):
    """Compare the exact saved request fingerprints without exposing prompt content."""
    left_call, right_call = _mapping_call(left), _mapping_call(right)
    left_context, right_context = _mapping_context(left), _mapping_context(right)
    left_suffix = ResponsesModel.mapping_prompt_parts(
        stage=MAPPING_STAGE, context=left_context, output_schema={})[1]
    right_suffix = ResponsesModel.mapping_prompt_parts(
        stage=MAPPING_STAGE, context=right_context, output_schema={})[1]
    first_character = next((index for index, pair in enumerate(zip(left_suffix, right_suffix))
                            if pair[0] != pair[1]), min(len(left_suffix), len(right_suffix)))
    left_at = datetime.fromisoformat(_mapping_timestamp(left))
    right_at = datetime.fromisoformat(_mapping_timestamp(right))
    earlier, later = sorted((left_at, right_at))
    left_cache = left_call.get("response", {}).get("prompt_cache", {})
    right_cache = right_call.get("response", {}).get("prompt_cache", {})
    shared_checks = {
        "requested_model": left_call.get("requested_model") == right_call.get("requested_model"),
        "returned_model": left_call.get("response", {}).get("model") == right_call.get("response", {}).get("model"),
        "instructions_sha256": left_call.get("instructions_sha256") == right_call.get("instructions_sha256"),
        "prompt_cache_key": left_cache.get("key") == right_cache.get("key"),
        "stable_prefix_sha256": left_cache.get("stable_prefix_sha256") == right_cache.get("stable_prefix_sha256"),
        "explicit_breakpoint": left_cache.get("explicit_breakpoint") == right_cache.get("explicit_breakpoint"),
        "max_output_tokens": left_call.get("response", {}).get("max_output_tokens") == right_call.get("response", {}).get("max_output_tokens"),
        "candidate_file_order": list(left["candidate_context"]) == list(right["candidate_context"]),
        "candidate_file_hashes": {
            name: item.get("sha256") for name, item in left["candidate_context"].items()
        } == {
            name: item.get("sha256") for name, item in right["candidate_context"].items()
        },
    }
    return {
        "diagnostic_version": 1,
        "runs": [left["run_id"], right["run_id"]],
        "stage": MAPPING_STAGE,
        "saved_request_fingerprints": {
            left["run_id"]: {
                "completed_at": left_at.isoformat(),
                "context_sha256": left_call.get("context_sha256"),
                "context_reconstruction_matches": runner._hash(runner._json(left_context)) == left_call.get("context_sha256"),
                "instructions_sha256": left_call.get("instructions_sha256"),
                "prompt_cache": left_cache,
                "usage": left_call.get("response", {}).get("usage"),
            },
            right["run_id"]: {
                "completed_at": right_at.isoformat(),
                "context_sha256": right_call.get("context_sha256"),
                "context_reconstruction_matches": runner._hash(runner._json(right_context)) == right_call.get("context_sha256"),
                "instructions_sha256": right_call.get("instructions_sha256"),
                "prompt_cache": right_cache,
                "usage": right_call.get("response", {}).get("usage"),
            },
        },
        "before_explicit_breakpoint": {
            "identical": all(shared_checks.values()),
            "checks": shared_checks,
            "stable_prefix_sha256": left_cache.get("stable_prefix_sha256"),
            "prompt_cache_key": left_cache.get("key"),
        },
        "payload_construction": {
            "model": left_call.get("requested_model"),
            "instructions": "top-level instructions; identical SHA-256 above",
            "text_format": "strict json_schema; derived deterministically from the stage schema that is also inside the hashed stable prefix",
            "reasoning_setting": "omitted",
            "verbosity_setting": "omitted",
            "service_tier_setting": "omitted (API default)",
            "prompt_cache_options": {"mode": "explicit", "ttl": "API default 30m"},
            "content_block_order": [
                "input[0].content[0]: stage + required schema + five candidate files",
                "explicit cache breakpoint at end of content[0]",
                "input[0].content[1]: input_job + upstream Role Understanding",
            ],
            "candidate_file_order": list(left["candidate_context"]),
        },
        "first_job_specific_difference": {
            "semantic": _first_difference(
                {key: value for key, value in left_context.items() if key != "candidate_context"},
                {key: value for key, value in right_context.items() if key != "candidate_context"}),
            "suffix_character_offset": first_character,
            "left_suffix_sha256": _sha(left_suffix),
            "right_suffix_sha256": _sha(right_suffix),
        },
        "completion_gap_seconds": (later - earlier).total_seconds(),
        "default_minimum_cache_lifetime_seconds": 1800,
        "outside_guaranteed_lifetime": (later - earlier).total_seconds() > 1800,
    }


def _post_probe(transport, payload):
    started = time.perf_counter()
    response = requests.post(
        "https://api.openai.com/v1/responses", json=payload,
        headers={"Authorization": "Bearer " + transport._api_key},
        timeout=transport.timeout, allow_redirects=False)
    elapsed = time.perf_counter() - started
    if response.status_code != 200:
        raise RuntimeError(json.dumps(api_error_diagnostics(response, transport._api_key),
                                      ensure_ascii=True))
    body = response.json()
    return {
        "response_id": body.get("id"), "status": body.get("status"),
        "model": body.get("model"), "service_tier": body.get("service_tier"),
        "usage": body.get("usage"), "prompt_cache_options": body.get("prompt_cache_options"),
        "prompt_cache_diagnostics": body.get("prompt_cache_diagnostics"),
        "elapsed_seconds": round(elapsed, 3),
    }


def run_live_probe(model="gpt-6-sol", *, timeout=180, max_output_tokens=32):
    """Run exactly two requests; outputs are ignored and never become shortlist state."""
    candidate = {name: {"content": runner._read_full(ROOT / name)}
                 for name in runner.CANDIDATE_FILES}
    for item in candidate.values():
        item["sha256"] = runner._hash(item["content"])
    contracts = {name: runner._read_full(ROOT / name) for name in runner.CONTRACT_FILES}
    instructions = runner._instructions(MAPPING_STAGE, contracts)
    schema = runner.stage_schema(load_schema(), MAPPING_STAGE)
    transport = ResponsesModel(model, timeout=timeout, max_output_tokens=max_output_tokens)

    def payload(label):
        context = {
            "input_job": {"company": f"Cache probe {label}", "title": "Diagnostic only",
                          "full_job_description_raw": f"Synthetic diagnostic suffix {label}."},
            "upstream": {"role_understanding": {"diagnostic_suffix": label}},
            "candidate_context": candidate,
        }
        result, metadata = transport.build_payload(
            stage=MAPPING_STAGE, instructions=instructions, context=context,
            output_schema=schema, model=model)
        return result, metadata

    first_payload, first_meta = payload("A")
    second_payload, second_meta = payload("B")
    if first_meta != second_meta or first_payload["input"][0]["content"][0] != second_payload["input"][0]["content"][0]:
        raise AssertionError("Diagnostic requests do not share an identical cache prefix")
    first = _post_probe(transport, first_payload)
    second_payload["prompt_cache_options"]["comparison_response_id"] = first["response_id"]
    second = _post_probe(transport, second_payload)
    return {
        "model": model,
        "request_count": 2,
        "cache_settings": first_payload.get("prompt_cache_options"),
        "prompt_cache_key": first_payload.get("prompt_cache_key"),
        "stable_prefix_sha256": first_meta["stable_prefix_sha256"],
        "max_output_tokens": max_output_tokens,
        "first": first,
        "second": second,
    }


def _load_run(root, run_id):
    path = root / run_id / "job_state.json"
    if not path.is_file():
        raise ValueError(f"Saved run not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", required=True)
    parser.add_argument("--run-b", required=True)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--live-probe", action="store_true",
                        help="Make exactly two mapping-prefix diagnostic API calls")
    parser.add_argument("--model", default="gpt-6-sol")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args(argv)
    report = compare_saved_runs(_load_run(args.run_root, args.run_a),
                                _load_run(args.run_root, args.run_b))
    if args.live_probe:
        report["live_probe"] = run_live_probe(args.model, timeout=args.timeout)
    output = args.output or (DEFAULT_DIAGNOSTIC_ROOT /
                             f"{args.run_a}--{args.run_b}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
