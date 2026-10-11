"""Stateless OpenAI Responses transport. No conversations, tools, or retrieval."""
import json
import os
import math
import re
import hashlib
from copy import deepcopy
from collections.abc import Mapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

SHORTLIST_STAGES = {"role_understanding", "career_requirements_mapping",
                    "shortlist_decision", "controller_validation"}


class ModelError(RuntimeError):
    """Sanitized transport failure with allowlisted API diagnostics, never a raw body."""

    def __init__(self, message, *, error_type=None, transient=False, retry_after=None, diagnostics=None):
        super().__init__(message)
        self.error_type = error_type or type(self).__name__
        self.transient = transient
        self.retry_after = retry_after
        self.diagnostics = diagnostics


def api_error_diagnostics(response, api_key):
    """Extract only error classification and operational headers; redact credentials."""
    def safe(value, limit=4096):
        if not isinstance(value, (str, int, float)):
            return None
        value = str(value)
        if api_key:
            value = value.replace(api_key, "[REDACTED]")
        value = re.sub(r"(?i)\bBearer\s+[^\s\"',;]+", "Bearer [REDACTED]", value)
        value = re.sub(r"\bsk-[A-Za-z0-9_-]+", "[REDACTED]", value)
        value = re.sub(
            r"(?i)(\b(?:authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|cookie|set-cookie)\b[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;]+)",
            r"\1[REDACTED]", value)
        value = re.sub(r"[\x00-\x1f\x7f]", " ", value)
        return value if len(value) <= limit else value[:limit] + " [TRUNCATED]"

    try:
        body = response.json()
    except (ValueError, TypeError):
        body = None
    error = body.get("error") if isinstance(body, dict) else None
    error = error if isinstance(error, dict) else {}
    headers = ({str(k).lower(): v for k, v in response.headers.items()}
               if isinstance(response.headers, Mapping) else {})
    rate_headers = ("x-ratelimit-limit-requests", "x-ratelimit-limit-tokens",
                    "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens",
                    "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens")
    return {"http_status": response.status_code,
            "error": {key: safe(error.get(key)) for key in ("code", "type", "message")},
            "retry_after": safe(headers.get("retry-after"), 512),
            "request_id": safe(headers.get("x-request-id"), 512),
            "rate_limit_headers": {key: safe(headers[key], 512) for key in rate_headers if key in headers}}


def retry_after_seconds(value):
    """Parse seconds or HTTP-date without retaining arbitrary response headers."""
    if not isinstance(value, str):
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
            seconds = (date - datetime.now(timezone.utc)).total_seconds()
        except (ValueError, TypeError, OverflowError):
            return None
    return max(0.0, seconds) if math.isfinite(seconds) else None


class ResponsesModel:
    def __init__(self, model, *, api_key=None, timeout=180, max_output_tokens=12000):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Specify --model or SHORTLIST_MODEL; no model is silently selected")
        self.model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY must be set in the environment")
        if timeout <= 0 or max_output_tokens <= 0:
            raise ValueError("Timeout and output-token limit must be positive")
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens

    @staticmethod
    def _compact(value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

    @classmethod
    def mapping_prompt_parts(cls, *, stage, context, output_schema):
        """Render mapping JSON with the unchanged candidate context as a stable prefix."""
        if stage != "career_requirements_mapping" or "candidate_context" not in context:
            return None
        stable = (
            '{"stage":' + cls._compact(stage) +
            ',"required_output_schema":' + cls._compact(output_schema) +
            ',"context":{"candidate_context":' + cls._compact(context["candidate_context"])
        )
        changing = {key: value for key, value in context.items() if key != "candidate_context"}
        suffix = "".join("," + cls._compact(key) + ":" + cls._compact(value)
                         for key, value in changing.items()) + "}}"
        return stable, suffix

    @staticmethod
    def _supports_explicit_cache_breakpoint(model):
        return bool(re.match(r"^gpt-(?:[6-9]|5\.(?:[6-9]|[1-9][0-9]))(?:-|$)", model))

    @staticmethod
    def structured_output_schema(output_schema):
        """Project the authoritative schema onto OpenAI's strict supported subset."""
        definitions = output_schema.get("$defs", {})
        unsupported = {"allOf", "not", "dependentRequired", "dependentSchemas",
                       "if", "then", "else"}

        root = {key: deepcopy(value) for key, value in output_schema.items()
                if key not in ("$schema", "$defs")}
        if set(root) == {"$ref"} and root["$ref"].startswith("#/$defs/"):
            root = deepcopy(definitions[root["$ref"].split("/")[-1]])

        needed = set()
        def find_refs(value):
            if isinstance(value, dict):
                ref = value.get("$ref")
                if isinstance(ref, str) and ref.startswith("#/$defs/"):
                    needed.add(ref.split("/")[-1])
                for child in value.values():
                    find_refs(child)
            elif isinstance(value, list):
                for child in value:
                    find_refs(child)

        find_refs(root)
        checked = set()
        while needed - checked:
            name = next(iter(needed - checked))
            if name not in definitions:
                raise ValueError(f"Stage schema references missing definition: {name}")
            checked.add(name)
            find_refs(definitions[name])
        if needed:
            root["$defs"] = {name: deepcopy(definitions[name]) for name in sorted(needed)}

        def sanitize(value, path="root"):
            if isinstance(value, dict):
                for key in unsupported:
                    value.pop(key, None)
                if value.get("type") == "object" or "properties" in value:
                    properties = value.get("properties", {})
                    if value.get("additionalProperties") is not False:
                        raise ValueError(f"Strict output object lacks additionalProperties:false at {path}")
                    if set(value.get("required", [])) != set(properties):
                        raise ValueError(f"Strict output object has optional fields at {path}")
                for key, child in value.items():
                    sanitize(child, f"{path}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    sanitize(child, f"{path}[{index}]")

        sanitize(root)
        if root.get("type") != "object":
            raise ValueError("Strict output schema root must be an object")
        return root

    def build_payload(self, *, stage, instructions, context, output_schema, model=None):
        selected_model = model or self.model
        structured = stage in SHORTLIST_STAGES
        payload = {
            "model": selected_model,
            "store": False,
            "truncation": "disabled",
            "max_output_tokens": self.max_output_tokens,
            "text": {"format": ({"type": "json_schema", "name": "shortlist_" + stage,
                                   "strict": True,
                                   "schema": self.structured_output_schema(output_schema)}
                                  if structured else {"type": "json_object"})},
            "instructions": instructions,
        }
        parts = self.mapping_prompt_parts(stage=stage, context=context, output_schema=output_schema)
        cache_metadata = None
        if parts is None:
            payload["input"] = [{"role": "user", "content": self._compact({
                "stage": stage, "context": context, "required_output_schema": output_schema,
            })}]
        else:
            prefix, suffix = parts
            cache_key = "shortlist-v1.1-mapping-" + hashlib.sha256(
                (instructions + "\0" + prefix).encode("utf-8")).hexdigest()[:24]
            payload["prompt_cache_key"] = cache_key
            explicit = self._supports_explicit_cache_breakpoint(selected_model)
            if explicit:
                payload["prompt_cache_options"] = {"mode": "explicit"}
                content = [
                    {"type": "input_text", "text": prefix,
                     "prompt_cache_breakpoint": {"mode": "explicit"}},
                    {"type": "input_text", "text": suffix},
                ]
            else:
                content = prefix + suffix
            payload["input"] = [{"role": "user", "content": content}]
            cache_metadata = {"key": cache_key,
                              "stable_prefix_sha256": hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
                              "explicit_breakpoint": explicit}
        return payload, cache_metadata

    def complete(self, *, stage, instructions, context, output_schema, model=None):
        payload, cache_metadata = self.build_payload(
            stage=stage, instructions=instructions, context=context,
            output_schema=output_schema, model=model)
        try:
            response = requests.post(
                "https://api.openai.com/v1/responses", json=payload,
                headers={"Authorization": "Bearer " + self._api_key},
                timeout=self.timeout, allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise ModelError("Model request failed (connection/timeout); no context was pruned",
                             error_type=type(exc).__name__,
                             transient=isinstance(exc, (requests.Timeout, requests.ConnectionError))
                             and not isinstance(exc, requests.exceptions.SSLError)) from None
        if response.status_code != 200:
            raise ModelError(f"Model request returned HTTP {response.status_code}; check model access, quota and context limits",
                             error_type=f"HTTP {response.status_code}",
                             transient=response.status_code in (408, 429, 500, 502, 503, 504),
                             retry_after=retry_after_seconds(response.headers.get("Retry-After")),
                             diagnostics=api_error_diagnostics(response, self._api_key))
        try:
            body = response.json()
            if body.get("status") != "completed":
                raise ModelError("Model response was incomplete or failed; no partial JSON accepted")
            texts = []
            for item in body.get("output", []):
                if item.get("type") == "message":
                    for block in item.get("content", []):
                        if block.get("type") == "refusal":
                            raise ModelError("Model refused the stage; no decision fabricated")
                        if block.get("type") == "output_text":
                            texts.append(block["text"])
            result = json.loads("".join(texts))
            if not isinstance(result, dict):
                raise ValueError("Expected one object")
            return result, {"response_id": body.get("id"), "model": body.get("model"),
                            "usage": body.get("usage"), "max_output_tokens": self.max_output_tokens,
                            "prompt_cache": cache_metadata}
        except (ValueError, TypeError, KeyError, AttributeError):
            raise ModelError("Model returned malformed JSON; no decision fabricated") from None
