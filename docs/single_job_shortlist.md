# Single-job shortlist runner — full-context baseline

`scripts/run_shortlist_job.py` executes one normalized job through the authoritative
`shortlist/` v1.2.0 stages. It contains no batch loop, retrieval/index, new score, or
deterministic decision rule. The v1 schema and stage documents are unchanged.

## Architecture

1. Validate one input object and read all five complete candidate-context files once for this
   run. Preserve the input and full context snapshot with content hashes.
2. **Role Understanding:** a fresh model request receives the full JD, original
   metadata and authoritative contracts. It does not receive candidate history.
3. **Career / Requirements Mapping:** a fresh request receives Role Understanding
   plus the complete contents of `candidate_profile.md`, `career_evidence.md`,
   `evidence_conflicts.md`, `job_preferences.md`, and `candidate_confirmed_facts.md`.
   Candidate-confirmed facts retain their distinct provenance. Nothing is retrieved selectively,
   summarized in advance, pruned, indexed, or fetched from linked sources.
4. **Shortlist Decision:** a fresh request consumes the upstream role/mapping state,
   full JD and all five candidate files. It proposes one of the four v1 outcomes.
5. **Controller Validation:** a separate request inspects the full sources, conflicts,
   outputs and evidence excerpts, using checks A–G from the controller contract. It
   returns v1 flags, per-flag rationales, per-criterion evidence checks, and actionable
   issues identifying the stage to correct. It does not rewrite the decision.
6. Code validates stage shapes against definitions from `shortlist/schema.yaml`,
   source excerpt existence, original identity, final cross-stage references, and
   controller consistency. It saves the complete v1 state and readable projection.

Four calls run sequentially. There is no reused conversation, `previous_response_id`,
server-side conversation, or accumulated context from another job. The transport
uses `store: false`, disables automatic input truncation, and exposes no model tools.
No model is silently selected. `--model` or `SHORTLIST_MODEL` supplies the
backward-compatible fallback. `--role-model`, `--mapping-model`,
`--decision-model`, and `--controller-model` can override it independently.

Career Mapping renders its unchanged instructions and complete candidate context
before job-specific metadata and Role Understanding output. Supported Responses API
models receive an explicit cache breakpoint after that stable prefix; other models
retain the same stable-first ordering and cache key for automatic prompt caching.
The artifact records returned cached-token usage rather than assuming a cache hit.

All four stages use Responses Structured Outputs with `text.format.type` set to
`json_schema` and `strict: true`. The API schema is derived from each unchanged
authoritative stage schema. Required fields, enums, types, references and supported
constraints are retained. Unsupported `if`/`then`/`allOf` semantic conditions are
omitted only from the API projection and remain enforced by the unchanged local
schema validator. See [official OpenAI documentation](https://developers.openai.com/api/docs/guides/structured-outputs).
Refusals, incomplete responses, malformed JSON and failed local checks stop execution;
no output is coerced into a decision. No hidden repairs or model fallback are implemented.

## Capability-level evidence and conflict handling

Each mapped criterion uses existing v1 fields:

- `role_requirement`: the actual capability required;
- `strongest_evidence.evidence_summary`: specific work/decisions/outcomes, why they
  demonstrate the capability, and a supplied source-file/section locator;
- `strongest_evidence.project_or_role`: project/role provenance;
- `limitation_or_difference`, `capability_fit`, and `domain_context_fit`: material differences and the current v1.2
  independent capability/domain assessments. `overall_fit_assessment` summarizes
  these without replacing either dimension.

The mapping response also includes operational `evidence_provenance`, one entry per
criterion with `source_path` and verbatim supporting `quote` entries. These live in
the run envelope, not as new v1 schema fields. Non-gap evidence needs provenance;
pure missing-evidence gaps may have empty source lists. Code checks each quote exists
in the full supplied file and its path remains in the evidence summary. The controller
must assess the meaning and adequacy of the evidence, not only quote existence.
Specialist requirements retain source locators in their existing evidence text and
are included in the controller audit.

The conflicts file is passed intact to Mapping, Decision and Controller. Prompts
require unresolved conflicts and ownership limitations to remain explicit. The full
preferences file is also passed intact, with its legacy selection/scoring rules
explicitly superseded by v1. The runner does not resolve conflicting facts by code
or fetch a linked resume/project source to fill a gap. Full context is the baseline
for a later retrieval comparison.

## Input and invocation

Input is one UTF-8 JSON object, not an array or JSONL batch:

```json
{
  "company": "Employer name",
  "job_id": "Employer requisition ID or null",
  "title": "Exact title",
  "location": "Location text or null",
  "posted_date": null,
  "canonical_job_url": "https://employer.example/jobs/id",
  "source": "Official employer or ATS source",
  "full_job_description_raw": "The complete unabridged posting goes here."
}
```

Use JSON null for genuinely unknown job IDs/locations. Posting date, posting URL
and source metadata are optional. Company, title, and the full JD remain required;
job_id/requisition_id and location may be omitted, blank, or null. Missing
URLs never block shortlisting. `job.jd_source` retains a supplied URL or source;
otherwise it records that the full JD was user-supplied, without claiming live
verification or inventing a URL. The v1 schema is unchanged.
Optional `work_model` and `travel` values are preserved when supplied; otherwise Role
Understanding may extract them from explicit JD facts. Every additional original
metadata field is preserved in the envelope. No discovery adapter changes,
HTML retrieval, or live-job verification are added. CSV column mappings are confined
to input loading.

For a clean clone, first create a virtual environment from the repository root:

```powershell
python -m venv .venv
```

Then install the requirements and run from the repository root in PowerShell, using
`OPENAI_API_KEY` already set securely in the environment and explicitly chosen
API-accessible models. Do not commit the key or environment files:

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-shortlist.txt
.\.venv\Scripts\python.exe scripts/run_shortlist_job.py `
  --input C:\path\to\job-1.json `
  --role-model gpt-6-luna `
  --mapping-model gpt-6-sol `
  --decision-model gpt-6-luna `
  --controller-model gpt-6-luna
```

Repeat that command independently for `job-2.json` through `job-5.json`, or use the
separate [batch orchestrator](batch_shortlist.md). A repeated single-job command creates a fresh run directory; it never overwrites
or continues the previous run. Keep model and token-budget settings constant for the
five-job baseline. Optional `--max-output-tokens` defaults to 12000 and `--timeout`
to 180 seconds per model request. Context/output limits fail explicitly; evidence is
never truncated to fit. Increase the budget or choose an appropriate model explicitly
if necessary. Four API requests can incur usage costs per successful execution.

Alternatively, select one exact discovery `job_id` from a CSV:

```powershell
.\.venv\Scripts\python.exe scripts/run_shortlist_job.py `
  --csv C:\path\to\workday_pm_candidates.csv `
  --job-id "company:requisition-id" --model $env:SHORTLIST_MODEL
```

`--input` and `--csv` are mutually exclusive. In CSV mode, select exactly one row
using either `--job-id` or `--row N` (1-based data row, excluding the header). External
IDs are not required for `--row`; company, title and full JD are still required.
CSV text is read as UTF-8 (with optional BOM), with a strict Windows-1252 fallback
for Windows/Excel exports. Full JD text is never replaced or dropped on decoding.
The lookup must match exactly one row. Missing IDs, duplicate matches, or missing
required fields fail before model creation. Discovery `canonical_url`, `source_key`
(or `source_type`), and `posting_date` populate `canonical_job_url`, `source`, and
`posted_date`; already normalized columns take precedence when nonempty. Original
discovery columns are retained. Missing/blank URLs become null; missing source
metadata is labeled with the input CSV filename as provenance, not an employer URL. Blank optional dates/work-model/travel and blank
locations become null. Missing location columns are allowed. The
`full_job_description_raw` column is required and preserved verbatim, including
multiline text; `description` is never substituted. Older summary-only discovery
CSVs without the full JD cannot be used. No discovery code or runner stages change.

Default outputs are ignored under `local_private/shortlist/<random_run_id>/` because
they include complete candidate context. `--output-root` can select another directory;
review privacy before choosing a tracked directory. Keys are read only from the
environment and never written into prompts or artifacts.

## Stable internal identity

`normalize_input()` requires only `company`, `title` and `full_job_description_raw`.
Optional metadata is preserved when present; absent/blank values become null.
A supplied `requisition_id` can populate `job_id` if `job_id` is absent; neither is
created from the internal key. If both are supplied, both are retained.

Every normalized input has a separate `internal_record_key` with the form
`shortlist:<normalized-company>:<normalized-title>:<16-character-hash>`.
The hash includes normalized company/title and `row_identity`. CSV row identity is
its resolved file path plus 1-based data-row number; the normalized JSON retains
that identity, so moving the JSON does not change its key. Reordering or moving the
original CSV changes newly derived row identities. For JSON without row identity,
use the provided external ID, otherwise a hash of the full JD. Identical standalone
records therefore share an internal key; each execution still has a unique `run_id`.
This is identity metadata, not a fit score or an external requisition ID.

Artifacts preserve `input_job` as received and add `normalized_job` and the separate
`internal_record_key`. The inner v1 `job.job_id` stays null when the external ID is
unknown. The closed shortlist v1 schema and all stage/decision rules are unchanged.

## Output structure

```text
<run_id>/
  job_state.json        Original input, context snapshot, audit and complete state
  shortlist_state.json Standalone object validated against shortlist/schema.yaml
  review.md             Concise human-readable projection of the same state
```

The envelope avoids modifying v1's closed schema to accommodate original metadata:

```json
{
  "artifact_version": "single-job-v1",
  "run_id": "unique-run-id",
  "model": "explicitly-selected-model",
  "stage_models": {
    "role_understanding": "gpt-6-luna",
    "career_requirements_mapping": "gpt-6-sol",
    "shortlist_decision": "gpt-6-luna",
    "controller_validation": "gpt-6-luna"
  },
  "status": "accepted",
  "input_job": {"company": "...", "full_job_description_raw": "..."},
  "candidate_context": {"profile/career_evidence.md": {"content": "complete file", "sha256": "..."}},
  "contract_hashes": {},
  "schema_sha256": "...",
  "completed_stages": ["role_understanding", "career_requirements_mapping", "shortlist_decision", "controller_validation"],
  "stage_outputs": {},
  "model_calls": [],
  "usage_summary": {"stages": {}, "totals": {}},
  "shortlist_state": {
    "schema_version": "1.2.0",
    "job": {},
    "role_understanding": {},
    "career_requirements_mapping": {},
    "shortlist_decision": {},
    "validation": {}
  },
  "controller_review": {},
  "error": null
}
```

This is an abbreviated shape, not a valid sample record. All five full candidate
files, full stage outputs, specific provenance, check rationales, issues, request
hashes, model response IDs and returned usage are retained in an actual artifact.
Usage token counts are operational metadata, never job scores.

`review.md` shows company/title, actual work, every hiring criterion and its importance,
specific strongest evidence, project provenance, direct/transferable/adjacent/gap
classification, limitations, meaningful gaps, scope, decision/rationale, separate
location/eligibility, validation flags and any required corrections.

Exit codes: **0** = model controller accepted the analysis (including a valid HOLD or
DO NOT APPLY); **2** = completed but controller rejected; **1** = invalid input,
configuration, transport or execution failure. An accepted analysis is not application
authorization. There are no resume queues, downstream actions or Sheet writes.

On a stage failure, `job_state.json` and `review.md` retain partial progress and the
failed stage; no standalone completed `shortlist_state.json` is published. On semantic
rejection, the complete proposed state is saved with acceptance false and correction
instructions. Correct the identified issue and rerun independently; this baseline
does not silently revise evidence or automatically loop through repairs.

## Evaluation readiness and limits

### Resume one failed or interrupted run

From the repository directory, resume the saved COUNT run without calling its
completed Role Understanding or Career Mapping stages again:

```powershell
.\.venv\Scripts\python.exe scripts/run_shortlist_job.py --resume-run 3001e7153a6f4e4e81a41590c6494bdd --model gpt-6-astra --max-output-tokens 24000 --timeout 600
```

`--resume-run` is exclusive with `--input` and `--csv`, and resolves a run ID beneath
`--output-root` (default `local_private/shortlist`). Resume verifies input/context,
prompt/spec, schema, and recorded model-setting hashes before any model call or
artifact mutation. Changed inputs require a new run of the stale stage and its
downstream stages; the runner does not silently invalidate or recompute checkpoints.
Completed runs cannot be resumed. A lock prevents concurrent resume attempts.

New runs record per-stage model identities/settings and output hashes. Resume checks
the model for each completed stage independently. A different model for an unfinished
downstream stage does not invalidate earlier completed work, and every model call and
stage-completion history event preserves the requested and returned model identity.
Older v1 runs are checked
using their saved request/context hashes, candidate-content hashes, spec hashes,
requested model and per-response output-token limits. Their unrecorded timeout is
treated as a transport setting, not inferred as historical fact, and this limitation
is recorded in resume history. No old output or failure is rewritten in place:
each resume retains a `before-resume-*.json` snapshot; `job_state.json` accumulates
failure/retry/resume history and the final status. `progress.log` is appended.

HTTP 408/429/500/502/503/504, connection failures (except TLS certificate errors),
and timeouts receive at most three retries of the failed stage only.
HTTP 429 uses the server `Retry-After` (seconds or HTTP-date) when valid, including
zero. Without a usable header, 429 delays are 15, 30, and 60 seconds plus 0–20%
additive jitter (15–18, 30–36, and 60–72 seconds). Other transient errors retain
2, 4, and 8 seconds, or the longer server `Retry-After`.
A requested delay over 300 seconds stops the run for later manual resume rather
than retrying before the server permits. Delays and attempt counts are logged.
Malformed JSON, incomplete generation (except content filtering), and wire-schema
failures receive at most one automatic retry within the existing four-attempt ceiling.
The input, model, evidence, output limit and policy do not change for a retry. Completed
JSON is checked against the API wire schema; full contract and semantic checks remain
downstream. Provenance failures, semantic validation failures, refusals and controller
rejection are not retried. Each failed request retains its classification, safe API
diagnostics, available token/cache usage and latency in history. Missing usage remains
unknown. Completed stage state is written only once after validation.

Provenance `sources[].quote` contains source text only (the existing validator tolerates
whitespace differences, not wording changes). Put paraphrased or derived findings in
the existing evidence/limitation prose, retain file/section citations, and provide
separate exact spans for every source used. Grounding remains subject to controller
review; calling an unsupported claim a paraphrase does not make it valid.

### Live evaluation

Before five-job validation, choose one model accessible to the configured API account,
provide five normalized inputs with full JDs, and ensure outbound API access and the
local requirements are installed. An environment key's presence alone does not prove
account permissions, model access or quota.

Offline tests exercise all stages using deterministic model doubles, including the
HTTP request/response contract. They do not establish live model quality or agreement
with prior manual ChatGPT assessments. No live evaluation job is selected or submitted
by the implementation tests. Review capability granularity, conflicts, transfer and
decision consistency in the five-job human assessment. Model-based validation remains
fallible; schema and quote checks cannot prove that an interpretation is correct.

The old classification finalizer, historical CSVs/JSONL, dashboard, discovery adapters,
filters, source mapping, benchmarks, candidate files and resume/application systems
are unchanged. Selective career-evidence retrieval is not built.

## Implementation files and verification

Created: `scripts/run_shortlist_job.py`, `scripts/shortlist_model.py`,
`scripts/test_shortlist_runner.py`, and this guide. Updated:
`scripts/requirements-shortlist.txt`, `AGENTS.md`, `README.md`, and the follow-up
status in `docs/shortlist_v1_migration.md`. Earlier uncommitted migration work remains
in place; these are the changes belonging to the single-job runner request.

Full offline suite on 2026-10-01: **140 tests passed, 0 failures** using:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

Checks cover the four-stage successful path, exact v1 validation, full unpruned
candidate context and conflicts, capability provenance/excerpts, independent and
repeated job isolation, controller rejection, inconsistent acceptance, missing JD/
context, fabricated quotations, incomplete/malformed/refused model responses, CLI
invocation, and stateless HTTP parameters. All pre-existing tests remain unchanged.
`git diff --check` passed. A content-hash audit confirmed **402 protected/existing
files unchanged**, including all shortlist contracts/schema, five candidate files,
historical records, discovery/benchmarks, and pre-existing tests. No live LLM call,
commit, push, job-dashboard write, or downstream action was performed for this build.

## Canonical identity and atomic hiring criteria

The six normalized intake fields `company`, `job_id`, `title`, `location`, `work_model`,
and `travel` are runtime-owned facts. Every stage receives the same `canonical_identity`.
The runner injects `role_identity` and decision `location_work_model` directly from intake
before validating or passing outputs downstream; null remains null even if JD prose names
a city, work model or travel requirement. Intake enrichment must occur explicitly before a
run. No model-produced identity value is authoritative. Raw responses remain separately in
`raw_stage_outputs`, with raw and bound hashes recorded for audit. Semantic outputs and
controller acceptance are never repaired by this binding. Resume validates canonical copies
and prompt/context fingerprints; old runs with changed prompts require a fresh run.

Role Understanding must separate materially different hiring capabilities into unique atomic
criteria, reusing existing criteria instead of creating duplicates. Growth, market disruption,
consumer-product team leadership and product launch must not share one fit label when they
require different evidence. This uses the existing schema and per-criterion mapping/controller
checks. Baseline degree/years/OR-equivalent qualification logic stays intact. The mapping
stage cannot label a whole compound capability direct on evidence for only one component.
Atomic decomposition remains a semantic model task audited by the unchanged controller;
offline tests do not establish that a future live model response will pass.
