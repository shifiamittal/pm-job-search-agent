# Job Search / Shortlist Mode — Integration Bridge

## Authority

The Resume Agent Starter Kit originally included a standalone shortlist mode. That
source is preserved verbatim under:

`docs/source_snapshots/resume_agent_starter_kit_v1/02_JOB_SEARCH_SHORTLIST_MODE.md`

It is **superseded for new runs** by the repository's newer shortlist contract:

1. `../shortlist/role_understanding.md`
2. `../shortlist/career_requirements_mapping.md`
3. `../shortlist/shortlist_decision.md`
4. `../shortlist/controller_validation.md`
5. `../shortlist/schema.yaml`

Current shortlist contract version: **1.2.0**.

Do not reintroduce the legacy single `evidence_type` field from the original
starter kit. New runs must classify `capability_fit` and `domain_context_fit`
separately and preserve `overall_fit_assessment`, `limitation_or_difference`,
and baseline qualifications per the v1.2 schema.

## Handoff to resume generation

`APPLY — PRIORITY` and `APPLY` make a role eligible to continue into resume generation
only after shortlist controller validation accepts the result.
`HOLD / INVESTIGATE` stops downstream work until the unresolved issue is resolved.
`DO NOT APPLY` stops downstream work.

An accepted shortlist result does not imply automated resume-generation execution.
Downstream execution occurs only when explicitly invoked/enabled within repository
runtime policy; an APPLY outcome is not authorization to generate artifacts, send, or submit.

The resume workflow should reuse approved upstream state rather than recomputing it:

- actual job-to-be-done
- responsibility clusters
- hiring criteria and importance
- specialist requirements
- baseline qualifications
- actual scope
- likely hiring-manager questions
- criterion evidence mappings, with their stable `criterion_id` references
- `capability_fit`
- `domain_context_fit`
- `overall_fit_assessment`
- `limitation_or_difference`
- strongest role stories
- meaningful gaps
- shortlist decision and controller validation

Consume the validated v1.2 handoff without renaming outcomes, collapsing mapping
fields, or changing their values (including nulls). Deeper resume evidence is
supplemental; any proposed upstream change must return through shortlist validation.

Resume generation may retrieve deeper evidence for writing, but it may not silently
change the role interpretation, erase gaps, or turn domain adjacency into direct experience.
