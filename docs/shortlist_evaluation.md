# Shortlist Golden Set v1.2 evaluator

This is an evaluation wrapper, not another shortlist implementation. It does not change the
authoritative v1.2 contract, candidate evidence, model transport, prompts, or shortlist decisions.
It defaults to validation/dry-run with zero model calls. No live benchmark is authorized by this
implementation task.

## Frozen data and validation

The active default is `evals/shortlist/golden/v1_2/`, copied byte-for-byte from the supplied
self-contained v1.2 ZIP. The previous `v1_1/` remains an unchanged historical input and is no
longer the default. All 12 human-approved references, including decisions, are unchanged.
The supplied `integrity.json` records each source hash, byte count, status and origin;
`package_integrity.json` additionally pins all 16 supplied files without modifying their bytes.
Validation checks all 12 unique source mappings against both the JSON and source manifest.
It also detects package drift, index mismatch, duplicate identities, invalid enums and missing
sources. No live posting is fetched. The evaluator never writes to the golden directory.

The reference schema is deliberately smaller than `shortlist_state.json`. Earlier references use
string gaps and `capability` names; later references include structured gaps, and Cisco uses
`criterion` names. The loader validates both supplied shapes **without changing or completing them**.
It validates capability/domain enums from the current contract. It preserves optional
`overall_fit_assessment` and `limitation_or_difference`; it does not invent these for compact
references. Fresh outputs must pass the complete v1.2 validator, including those fields.
The nine earlier cases lack separate human-review metadata; approval provenance is the user-supplied
frozen dataset. Cisco includes explicit human-approval metadata, checked against the frozen decision.

| Sources | Supplied provenance |
|---|---|
| Four Microsoft roles, R37, COUNT, Cisco 2024434 and 2024101 | Eight exact frozen historical/user-supplied sources |
| Flexport 8158027, Flexport 8110066, Amazon 10499366 | Three official same-job-ID recoveries; not byte-for-byte historical snapshots |
| Cisco 2023232 | Partial frozen historical source; only Role Understanding completeness is provisional |

All 12 cases are self-contained and can be prepared for execution. Hash verification establishes
identity with this supplied packet, not independent proof that recovered postings equal their
historical evaluated versions. The recovery provenance remains visible as a validation warning;
those three cases retain normal scoring, as supplied. Nine references continue to rely on the
user-supplied frozen dataset for approval provenance rather than separate review metadata.

## Architecture and result policy

1. `shortlist_golden.py` validates read-only data and prepares normalized inputs using the existing
   runner's `normalize_input`. It supports an unambiguous embedded `full_job_description_raw`, or a
   local `sources/<exact_jd_file>` matching the recorded hash. No golden reference enters the runner.
2. `eval_shortlist.py` calls existing `run_shortlist_job.run_job`: Role Understanding, Career Mapping,
   Decision, Controller. All five full candidate files and existing prompt/cache behavior remain intact.
3. Deterministic checks use `shortlist_contract.validate_shortlist_record`, the existing controller
   schema/consistency checks, all-four-stage completion, acceptance flags, exact input identity, and
   exact decision comparison. `APPLY` is not `APPLY â€” PRIORITY`; `HOLD / INVESTIGATE` is not `DO NOT APPLY`.
4. Offline judging requires completed, structurally valid Role Understanding, Career Mapping and
   Decision outputs matching the assembled state and exact normalized input. Controller rejection,
   a controller technical failure, or a golden decision mismatch does not block diagnostic judging.
   Incomplete or malformed first-three-stage outputs do block it. Its packet holds
   the frozen reference/JD, fresh role/mapping/decision, controller result, and relevant evidence quotes
   already checked by the runner, deterministic checks and any execution error. It excludes full candidate files, repository content and unrelated runs.
5. The judge returns exactly five dimensions with PASS/WARN/FAIL, reason, discrepancy, materiality and
   failure kind. Local JSON Schema and materiality checks are mandatory. The judge uses the same
   strict `json_schema` conversion and wire validation as the four shortlist stages through the
   existing transport. No direct SDK transport or semantic repair call is used.
6. Cisco 2023232 gets `PROVISIONAL` for Role Understanding completeness only. Its other four dimensions
   remain normal. Missing source fidelity alone cannot fail its case or the release gate.
7. Exact decision mismatch always fails. Material semantic errors can fail despite a matching label;
   minor semantic differences warn. Cosmetic wording/order/example differences must not fail.
   Controller verdict/issues and `production_usable` are retained separately from semantic dimensions.
   Rejected or failed production runs remain unusable, regardless of judge scores. Golden mismatch
   never changes production acceptance, but always fails the benchmark. Any deterministic case
   failure keeps the release gate at FAIL. The semantic hard gates remain: exact decisions; no material unsupported
   career claims; no material capability/domain regressions; no decision-changing missed requirements;
   no decision-changing lost gaps. `INCOMPLETE` is evaluation readiness, not a new shortlist outcome or
   additional quality gate. Unevaluated cases can never produce a release PASS.

## CLI (safe commands for this task)

```powershell
.\.venv\Scripts\python.exe -B scripts/eval_shortlist.py --help
.\.venv\Scripts\python.exe -B scripts/eval_shortlist.py --validate
.\.venv\Scripts\python.exe -B scripts/eval_shortlist.py --dry-run --telemetry-root local_private/shortlist
.\.venv\Scripts\python.exe -B -m unittest discover -s scripts -p 'test_shortlist*.py' -v
```

Validation/dry-run return exit code **0** when all 12 v1.2 inputs validate. The historical v1.1
input still returns exit code 2 for its nine missing sources. Neither path constructs a model client, reads an API
key, runs discovery, or writes fresh benchmark outputs. `--execute` is the separate explicit paid-call
path for future authorization; it also requires both `--model` and `--judge-model`. It is not run now.

## Persistence and resume

Default output is ignored `local_private/shortlist_evals/<run_id>/`, containing `manifest.json`,
`summary.json`, `summary.csv`, `failures.md`, `usage.json`, `per_case/`, `judge_packets/`, and isolated
`shortlist_runs/`. These may contain candidate evidence; keep them out of Git. Summaries retain all
dataset cases, including pending ones, so a partial run cannot appear to pass the full release gate.

Resume with the same dataset/models and `--resume <run-directory>` on the future execution command.
The manifest pins data, all candidate files, contracts, relevant implementation files, model settings,
and judge prompt/schema. Completed result files are checksummed and reused. Incomplete shortlist
stages use the runner's existing validated resume mechanism, not a fresh replacement run. The judge
attempt is checkpointed **before** the call: interruption or invalid output cannot silently cause a
second paid judge request on resume. Within a running invocation, a classified technical failure
may receive one bounded retry. Each attempt is checkpointed with outcome, safe API diagnostics,
available usage and latency. A valid semantic result, including WARN/FAIL, is never retried.
Inspect uncertain outcomes manually. No auto-reset exists.

## Call count, caching and cost

- Full 12-case baseline: **48 shortlist calls + at most 12 judge calls = 60** without retries.
- The existing runner allows up to four attempts per stage for transient failures; structural
  generation failures allow one retry within that ceiling. **192 shortlist attempts + 24 judge
  attempts = 216 maximum** for one complete execution; manual runner resumption may add attempts.
- Structurally complete first-three-stage outputs may be judged despite controller/deterministic
  failures; this never promotes production acceptance. The judge allows one technical retry
  for incomplete/malformed/wire-schema output or retryable transport/API failures, with the same
  request and a maximum server-requested wait of 300 seconds. HTTP 400 and semantic results are
  not retried. Semantic materiality validation remains outside the retry loop.
- Existing shortlist mapping-prefix caching is reused unchanged. Cached input/total input is reported
  from returned telemetry, including failed attempts; missing telemetry is counted and is not
  represented as a cache hit or a known zero cost.
- Two existing accepted four-stage runs yield an illustrative 12-case shortlist-only average of
  **1,699,152 input tokens and 197,532 output tokens**. This is not a quote: historical runs covered only a small sample,
  model/context mixes can differ, and judge packet sizes depend on future fresh outputs.
- Dollar estimates remain unknown until models/rates are selected. Use per-model uncached input,
  cached input and output rates. Failed transport attempts may be billable without telemetry.
  Reasoning tokens are part of output totals and are not counted twice.

## Files proposed by this implementation

Added only (no existing shortlist/runtime/policy files modified):

- `scripts/shortlist_golden.py`: immutable dataset/source/index validation and input preparation.
- `scripts/eval_shortlist.py`: existing-runner orchestration, deterministic checks, one-call judge,
  result aggregation, usage, resume and CLI.
- `scripts/test_shortlist_eval.py`: synthetic offline tests, network-prohibited evaluator fixtures.
- `docs/shortlist_evaluation.md`: this architecture, usage, cost and blocker report.
- `evals/shortlist/golden/v1_2/shortlist_golden_v1_2.json`, `index.csv`, `README.md`: supplied immutable references/index/notes.
- `evals/shortlist/golden/v1_2/integrity.json`: supplied source hashes, sizes and provenance.
- `evals/shortlist/golden/v1_2/package_integrity.json`: added full-package byte hashes.
- `evals/shortlist/golden/v1_2/sources/`: all 12 supplied JD snapshots, unchanged.
- Historical `evals/shortlist/golden/v1_1/`: retained unchanged, superseded as the default input.

Private validation/dry-run/test reports live under `local_private/shortlist_eval_validation/` and are
not proposed Git files. Existing application-agent and discovery/source-mapping work is unrelated
and remains untouched. No staging, commit or push is part of this task.

## Validation results (2026-10-12)

Dataset validation: 12 unique frozen references, matching index and valid decision/mapping enums.
All 12 source mappings, SHA-256 hashes, byte counts and provenance entries match. All references
and decisions match v1.1. Dry-run prepares all 12 inputs; Cisco 2023232 is provisional for only
Role Understanding completeness. No live model/judge calls, staging, commits or pushes.

Validation and dry-run exited 0; CLI help passed. All 16 supplied files remain byte-identical
to the ZIP. Regression coverage: 129 existing shortlist tests passed; all 19 evaluator tests
passed on the final recheck (25.755 seconds). The initial combined 148-test run had one resume
fingerprint error because a cost-report string was edited during the run; the stable-file
evaluator recheck passed. No shortlist logic or golden decisions changed.

## Explicit pilot selection

Repeat `--case-id` to execute only the named cases, in that order. Unknown or duplicate IDs
are rejected. Selection and stage models are pinned in the resume manifest. A pilot summary
covers only the selected cases and is not a full 12-case release result.
`--production-models` reuses `run_shortlist_batch.DEFAULT_STAGE_MODELS`: role/decision/controller
use gpt-6-luna, mapping uses gpt-6-sol. The judge model remains explicit.
The approved three-case pilot uses `--judge-model gpt-6-sol` and these IDs:
`microsoft_200051931`, `microsoft_200015839`, `flexport_8110066`. Baseline: 12 shortlist calls
and at most three judge calls, before existing runner retries. Runtime outputs remain private.
Historical v1.1 is retained locally unchanged; only the self-contained v1.2 packet is included
in the evaluator commit. Tests do not require the obsolete local packet.
