# Resume Generation Agent — Canonical Instructions

This directory contains the canonical downstream resume-generation workflow recovered
from `Resume_Agent_Starter_Kit_v1` and integrated with the repository's newer shortlist
contract.

## Source-of-truth hierarchy

### Shortlisting
Use `../shortlist/` v1.2.0 exclusively for:
- Role Understanding
- Career / Requirements Mapping
- Shortlist Decision
- Controller / Validation

### Resume generation
Use this directory for accepted roles:
- `01_RESUME_AGENT_WORKFLOW.md` — canonical downstream workflow
- `03_CANDIDATE_EVIDENCE_BASE_TEMPLATE.md` — evidence-base structure
- `04_EVIDENCE_AND_TRUTHFULNESS_RULES.md` — grounding / anti-inflation rules
- `05_RESUME_OUTPUT_CONFIG_TEMPLATE.md` — output defaults
- `06_BOOTSTRAP_PROMPT.txt` — standalone ChatGPT bootstrap prompt
- `07_CONTROLLER_AND_QA_CHECKLIST.md` — stage gates / QA
- `08_TEMPLATE_USAGE_GUIDE.md` — manifest/template separation

`02_JOB_SEARCH_SHORTLIST_MODE.md` is an integration bridge to the newer shortlist
contract. It preserves `capability_fit`, `domain_context_fit`,
`overall_fit_assessment`, and `limitation_or_difference` from validated mappings.
The original starter-kit version is preserved under `docs/source_snapshots/`
for provenance only.

## Important runtime status

These files define the authoritative resume-generation **workflow and controller rules**.
The repository does not yet contain a complete programmatic resume-generation runner
covering Evidence Retrieval → Strategy → Writing → Manifest → DOCX → exact-content
validation → render/layout QA.

`APPLY — PRIORITY` and `APPLY` make controller-accepted roles eligible to continue.
`HOLD / INVESTIGATE` stops downstream work until resolved; `DO NOT APPLY` stops it.
An accepted shortlist result does not start automated resume generation. Downstream
execution occurs only when explicitly invoked/enabled within repository runtime policy.
Do not confuse availability of the workflow specification with runtime automation.
