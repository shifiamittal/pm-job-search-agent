# Shortlist v1 migration

`shortlist/` **v1.2.0 is the authoritative role-evaluation and shortlist contract for new runs**.
No legacy label is an alias for a v1 decision. No shortlist logic is redesigned.

**Current implementation:** the [single-job full-context runner](single_job_shortlist.md)
and [sequential resumable batch runner](batch_shortlist.md) are implemented. Both use
all five required candidate-context files, including `profile/candidate_confirmed_facts.md`.
The migration record below describes the earlier boundary; current execution adds
isolated local artifacts and model-based controller review.
Shared legacy persistence/queues, legacy reprocessing, skill synthesis and
dashboard sync remain blocked. No v1 analysis/decision rules or schema were changed.

## Pre-change dependency map (2026-10-01)

| Layer | Files / dependency | Finding and migration disposition |
| --- | --- | --- |
| Operating instructions | `AGENTS.md` → `config/classification_rubric.md`, `config/role_taxonomy.yaml` | Competing lanes, gap taxonomy, economics and level rules. Replace with v1 pointers. |
| Prompt | `prompts/classification.md` | TODO stub; replace with a thin stage entrypoint. |
| Scope configuration | `config/search_config.yaml` | Principal-equivalence/economics gate and narrow other-India rule. Defer evaluation to v1; broad US/India scope. Not consumed by discovery adapters. |
| Candidate preferences | `profile/job_preferences.md` | Location scores, stricter Senior gate and old lane wording. File stays untouched; operating instructions explicitly supersede those policy passages. Candidate facts remain facts. |
| Legacy engine | `scripts/job_framework.py` | Flat schema, old enum validation, minimum four requirements, lane-sorted queue, AI skill catalog, canonical writes and Sheet sync. Retain historical reads; retire decision/generation/writes. |
| Calibration | `scripts/reprocess_calibration_jobs.py` → annotations → framework | Generates old decisions, including forced Skip for closed roles. Disable generation/reprocessing; retain read-only annotations. |
| Finalizer | `scripts/finalize_discovery.py` → framework → dashboard | Merges classified data, writes historical canonical files and syncs Sheet. Block pending real v1 runner/persistence integration. |
| Dashboard | `scripts/sync_job_dashboard.py`; `config/google_sheets.yaml` | Old lane tabs and columns; even rewrites Build Toward to Skip on display. Retire writer and translation; preserve identity and raw feedback. |
| Historical data | `data/jobs_raw.jsonl`, `jobs_master.csv`, `review_queue.csv`, `skills_synthesis.csv`, `calibration_annotations.yaml`, `calibration_lane_changes.csv`, `discovery_log.csv` | Preserve bytes and all records. They remain historical artifacts, not new v1 decisions. |
| Tests | `scripts/test_job_framework.py` | Enforces old enums, gap/bridge gates, old queue/synthesis and dashboard writes. Replace with authority, history and fail-closed regressions. |
| Documentation | `README.md`; `docs/discovery_v1_live_report.md` | README advertises old live pipeline. Update README. Discovery report is a historical report, not current policy; leave unchanged. |
| Authoritative specification | `shortlist/*.md`, `shortlist/schema.yaml` | Keep v1 analysis/decision/schema unchanged. Update only integration annotations and replace the outdated conflict appendix with this migration-status link. |
| Independent source sync | `scripts/sync_google_docs.py`, `scripts/sync_google_sheets.py`, corresponding tests | Google Docs/Sheet-to-Markdown evidence source sync, not the job dashboard. No migration needed; unchanged. |
| Independent discovery | `scripts/discover_jobs.py`, `scripts/discovery/*`, `config/job_sources.yaml`, evaluation scripts/tests | Raw intake/PM-family filtering do not import the legacy engine. Preserve unchanged. |
| Source maps and benchmarks | `scripts/map_*`, `data/source_registry/*`, `data/evals/*`, associated docs/tests | Unrelated source mapping/benchmark work. Preserve unchanged. Matches for “Skip”/classification here describe source/discovery facts, not a shortlist decision framework. |

Dependency direction before migration:

```text
AGENTS / rubric / taxonomy / search config / preferences -> human classification
annotations -> reprocess_calibration_jobs -> job_framework
classified JSONL -> finalize_discovery -> job_framework
job_framework -> jobs_raw / jobs_master / review_queue / skills_synthesis / log
job_framework -> sync_job_dashboard -> configured Google Sheet
sync_job_dashboard -> legacy feedback -> job_framework persistence
shortlist/ v1 -> no existing LLM stage executor
raw discovery / source sync / source mapping -> independent systems
```

This map was recorded before changing instructions or runtime code. The pre-existing
untracked source-mapping work and `shortlist/` files are preserved. Implementation
status and verification results follow below.

## Files migrated

| Files | Change |
| --- | --- |
| `AGENTS.md` | Sole v1 authority, explicit precedence over old preference policy, data/history boundaries and pending integrations. |
| `prompts/classification.md` | Thin entrypoint to the four versioned stages and schema. |
| `config/classification_rubric.md` | Deprecated redirect; competing rubric removed. |
| `config/role_taxonomy.yaml` | Removed decision/gap/bridge/posture enums; descriptive metadata and existing asset lists retained. |
| `config/search_config.yaml` | Broad US/India evaluation scope and v1 reference; old outputs marked historical and finalization pending. Discovery adapters do not consume this config. |
| `config/google_sheets.yaml` | Sync disabled with migration reason; existing ID, URL and title retained exactly. |
| `README.md` | Current authority, historical-data status, validation command and blocked consumers documented. |
| `shortlist/role_understanding.md`, `career_requirements_mapping.md`, `shortlist_decision.md`, `controller_validation.md` | Integration annotations updated only; original exported workflow text preserved verbatim. `shortlist/schema.yaml` is byte-for-byte unchanged. |
| `scripts/job_framework.py` | Historical JSONL/CSV readers; former validators, queue/synthesis generators and persistence APIs now raise an explicit integration error. |
| `scripts/reprocess_calibration_jobs.py` | Read-only annotation access retained; legacy conversion/reprocessing blocked. |
| `scripts/finalize_discovery.py` | Old classified-job merge/finalizer blocked before input reads or writes. |
| `scripts/sync_job_dashboard.py` | Writer/OAuth/formatting/lane-conversion code retired; CLI/API blocked. Supplied historical feedback can be copied without losing labels, unknown IDs or conflicting rows. No remote fetch/write occurs. |
| `scripts/shortlist_contract.py` (new) | Reads the authoritative YAML as JSON Schema Draft 2020-12; validates supplied completed records and cross-stage references/identity/handoff equality. No decision generation or acceptance certification. |
| `scripts/requirements-shortlist.txt` (new) | PyYAML and jsonschema dependencies for read-only validation/tests. |
| `scripts/test_job_framework.py`, `scripts/test_shortlist_contract.py` (new) | History preservation, authority, explicit write barriers and v1 schema/consistency regressions. |
| `docs/shortlist_v1_migration.md` (new) | Dependency map, migration disposition and verification. |

No files were deleted. The old decision-generating implementations and rubric were
removed from their live paths, which now provide either historical reads, redirects,
or explicit blocking errors. Git history retains the original implementations.
The deprecated `load_canonical_jobs()` read alias emits a warning and returns original
legacy records unchanged; it is not a decision-conversion shim.

## Legacy compatibility fields retained

All existing data files and rows remain byte-for-byte unchanged. These fields remain
only inside historical artifacts, not as accepted v1 output fields:

- `application_lane`, `application_posture`, `primary_gap`, `gap_gating`, `gap_rationale`;
- `domain_fit`, `domain_requirement_strength`, `domain_transfer_rationale`;
- `bridge_action`, `bridge_timing`, `strategic_skill_overlap`, `skill_build_priority`, `skill_tags`;
- flat `role_mandate`, `key_functional_requirements`, `hard_prerequisites`, `candidate_relevant_evidence`, `key_gaps_risks`, `decision_rationale`;
- `recommended_resume_variant`, `recommended_portfolio_artifact` and skill-synthesis columns;
- annotation `lane`/`posture`/`gap`/`gating` and historical `previous_lane`/`calibrated_lane`;
- user feedback/overrides, notes, workflow/application/outreach status, identifiers,
  dates, source links and all other historical fields.

The existing Sheet's lane tabs and recommendation columns are also historical. They
are not renamed, rewritten or presented as fresh v1 results by any local runtime.
The old Build Toward-to-Skip display conversion is removed. Human feedback is not a
model outcome and must never silently override or regenerate v1 classifications.
No new v1 record is written to the old flat CSVs/JSONL. `shortlist/schema.yaml` rejects
legacy decision fields and accepts the four new outcomes without translating them.

## Consumers awaiting integration

| Consumer | Blocking reason / required future work |
| --- | --- |
| Shortlist stage executor | `run_shortlist_job.py` executes the four authoritative stages; `run_shortlist_batch.py` sequentially orchestrates that same path. Selective evidence retrieval remains deferred. |
| Canonical finalizer / persistence | Need explicit v1 storage and stable identity/deduplication when employer IDs are absent, coexistence with historical records, update rules and feedback ownership. No existing record has been reclassified. |
| Review / resume queues | Need accepted v1 state and persistence integration. Use only agreed outcome routing and priority ordering; no new within-outcome ranking. HOLD review remains distinct from resume eligibility. |
| Skill synthesis | The former AI-focused strategic-build catalog is retired. V1 does not specify this output; no replacement skill taxonomy or scoring is invented. |
| Dashboard / Sheet sync | Need reviewed v1 projection, lossless retrieval/preservation of all existing remote feedback, historical/new view separation and same-Sheet updates after successful local writes. Changing the configuration flag cannot enable the retired writer. |

Future implementation must run the real four stages and controller validation on
supplied JD/evidence. Do not rename old lanes into v1 outcomes or assume a historical
recommendation supplies any of the required stage state. On a later authorized
persistence integration, preserve local data on Sheet failure and retain the existing
spreadsheet identity. No selective evidence retrieval, legacy resume runner,
application or outreach behavior is added here.

## Verification and risks

Full suite command:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

**128 tests passed, 0 failures** on 2026-10-01. This includes all unchanged discovery,
PM-family filtering, source mapping, benchmark-evaluation, and candidate-source sync
tests, plus the migration and v1 structural-validation tests. The first run caught a
new test's incorrect assumption that the real history contained a Build Toward row;
the test now verifies all old labels with synthetic fixtures, without altering data.

Preservation audit: **400 protected/historical files unchanged**, including candidate
profiles/evidence/preferences, historical jobs and feedback, raw discovery data,
source mappings, benchmarks, adapters, unrelated tests and source-sync code. All
exported shortlist workflow sections are preserved verbatim and the v1 schema bytes
are unchanged. `git diff --check` passed. No real Google Sheet/network synchronization,
classification run, resume/application activity, commit or push occurred. Installing
the schema validator in the ignored local venv was the only package-network operation.

Operational changes are intentional: callers of retired finalization/reprocessing/
synthesis/dashboard APIs now fail loudly, and existing remote views remain stale
historical views until integrated. External scripts importing removed helper APIs
may require updates; there is no silent fallback. Read-only structural validation
cannot prove source truth, semantic reasoning, or that asserted pass flags are honest.
The semantic controller remains required even when validation succeeds. Protected
preferences retain superseded historical policy text; current instructions explicitly
exclude those passages from selection policy. Other pre-existing untracked work is
untouched. This migration is ready for review; do not commit or push until authorized.
