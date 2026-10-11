> Contract version: **1.2.0** (2026-10-02). Source: user-supplied plus approved baseline-qualification separation.
> “Role Shortlist Workflow — Current Agreed Implementation Specification”.
> This is the authoritative shortlist contract. Structural validation, the single-job runner,
> and sequential resumable batch execution are implemented. Shared v1 persistence and
> dashboard integration remain pending. See [migration status](../docs/shortlist_v1_migration.md).
> Workflow: **Role Discovery / Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation**.
> The agreed source text below is preserved verbatim. Versioned serialization and
> integration notes follow it; they introduce no additional selection policy.
> Normative structure: [schema.yaml](schema.yaml). Controller: [controller_validation.md](controller_validation.md).

# 4. Controller / Validation Rules

## Purpose

A shortlist decision is not accepted merely because the Decision Agent produced a label.

The controller must enforce completion and semantic consistency across the upstream stages.

---

## A. Required Workflow Completion Checks

Before accepting a shortlist decision, confirm:

```yaml
validation:
  role_understanding_complete: true
  career_mapping_complete: true
  shortlist_decision_complete: true
```

A decision cannot be accepted if:

- Role Understanding was skipped
- requirements were never identified
- evidence was never mapped
- material gaps were never considered

---

## B. Role-Analysis Validation

Confirm that Role Understanding contains:

- actual job-to-be-done
- major responsibility clusters
- critical hiring criteria
- actual scope analysis
- likely hiring-manager questions
- location/work-model data where available

Reject / rerun Role Understanding if analysis is primarily based on:

- job title
- AI keywords
- compensation
- company prestige

rather than actual responsibilities.

---

## C. Evidence-Grounding Validation

For every significant fit claim:

```yaml
evidence_check:
  role_requirement_identified: true
  career_evidence_identified: true
  evidence_source_exists: true
  capability_fit_classified: true
  domain_context_fit_classified: true
  limitations_preserved: true
```

Do not accept:

- unsupported metrics
- invented technologies
- invented management scope
- invented customer types
- invented domain ownership
- unsupported claims of direct experience

For each criterion, independently verify:

- `capability_fit` reflects whether the underlying work pattern is demonstrated;
- `domain_context_fit` reflects industry, customer type, product context, and operating environment;
- capability fit was not downgraded solely because domain/context differs;
- material domain/context differences remain explicit;
- direct capability claims are grounded in specific evidence;
- adjacent or transferable domain evidence was not rewritten as direct domain ownership.

A criterion may validly combine direct capability with transferable domain/context.
The controller must reject unsupported direct-capability claims even when domain fit
is direct, and reject direct-domain claims supported only by adjacency.

---

## D. Gap Validation

Every material specialist requirement must have one of:

- direct evidence
- transferable evidence with stated limitation
- explicit gap

No critical criterion can disappear merely because evidence is weak.

---

## E. Semantic Validation

The controller should check that conclusions remain semantically consistent with the underlying evidence.

Examples of invalid transformations:

- Patent AI Search → “owned consumer search”
- product revenue impact → “enterprise sales ownership”
- executive customer influence → “strategic partner portfolio ownership”
- deployment/orchestration experience → “owned Azure fleet configuration”
- seller recommendation system → “owned two-sided local-services marketplace”

The wording may generalize capability.

It may not change the nature of the experience.

---

## F. Shortlist-Decision Consistency Check

The final decision must logically follow the analysis.

Examples from current agreed behavior:

### Valid

`APPLY — PRIORITY`

when:
- work is directly aligned
- evidence is strong
- scope/career value is high

### Valid

`APPLY`

when:
- work is strongly adjacent
- evidence is credible but transferable
- gaps are manageable
- career value is worthwhile

### Valid

`DO NOT APPLY`

when:
- actual work represents a meaningful functional transition
- central requirements have material/fundamental evidence gaps
- career value does not justify the transition

### Invalid

`APPLY — PRIORITY`

when several central criteria are only hypothetical/unsupported.

---

## G. Selection-Policy Validation

Before accepting the shortlist decision confirm:

- AI and non-AI roles were treated equally based on work
- PM / PM-T / equivalent product titles were allowed
- Senior title was not automatically rejected
- Principal title was not automatically accepted
- US/India geography was not artificially restricted to Seattle/remote
- no unapproved compensation cutoff was introduced
- location/work model was surfaced separately
- eligibility uncertainty was not treated as known eligibility
- role scope was assessed independently of title

---

## H. Universal Downstream Resume Requirements

These are not shortlist criteria, but are already established universal resume-generation requirements and should remain available to the controller when the workflow continues downstream:

- one-page resume is the current universal target
- 10-point body text is the current universal requirement
- Manifest is the content source of truth
- template is formatting source only
- document generation has zero editorial authority
- no delivery before exact-content validation
- any content change requires a new manifest
- old-template wording not present in the manifest is leakage and must fail validation

These rules should **not** influence the shortlist decision itself.

---

# 5. State Passed to Resume Generation

## Purpose

Avoid recomputing work that has already been performed correctly during shortlisting.

The shortlist system should hand structured state directly to the resume-generation workflow.

---

# State From Role Understanding to Reuse

Pass:

```yaml
role_state:
  actual_job_to_be_done:
  major_responsibility_clusters:
  hiring_criteria:
  specialist_requirements:
  baseline_qualifications:
  actual_scope:
  likely_hiring_manager_questions:
  location:
  work_model:
```

These become the existing **Role Understanding Agent output** inside the resume-generation workflow.

Do not rerun Role Understanding unless:

- the JD changed
- important information was missing
- the shortlist analysis was explicitly invalidated
- a deeper resume-specific interpretation is required because the original output was incomplete

---

# State From Career / Requirements Mapping to Reuse

Pass:

```yaml
career_mapping_state:
  criteria_mapping:
  specialist_requirement_mapping:
  baseline_qualification_mapping:
  strongest_role_stories:
  meaningful_gaps:
  capability_domain_classification:
  overall_evidence_summary:
```

This should feed the downstream:

- Evidence Retrieval Agent
- Hiring Criteria Evidence Mapper
- Resume Strategy / Architecture Agent

---

# What Should Be Reused Directly

## Reuse the role criteria

Do not have the resume agent rediscover:

- what the role is
- what the critical requirements are
- which requirements are most important

unless there is a clear deficiency.

---

## Reuse strongest-evidence mappings

If Career Mapping already established:

> inventory placement → SPORT

or:

> Search/Relevance → Patent AI Search

the resume workflow should begin from that mapping rather than start from scratch.

Evidence Retrieval may expand the underlying source material, but should not casually replace the mapping without evidence.

---

## Reuse identified gaps

Do not allow downstream resume-writing agents to silently erase gaps.

If shortlist mapping said:

> direct Places/local-search ownership is a gap

the resume writer may emphasize adjacent Search/Relevance depth but must not rewrite the career history as direct Places experience.

---

## Reuse actual-scope interpretation

The Resume Strategy Agent should know whether the role was classified as:

- Principal-equivalent
- High-value Senior
- Standard Senior
- Below target

This helps determine positioning without rerunning level analysis.

---

# What Should NOT Be Recomputed Unless Necessary

Do not normally recompute:

1. **What the role actually is**
2. **Critical hiring criteria**
3. **Importance of those criteria**
4. **Likely hiring-manager screening questions**
5. **Capability-fit and domain/context-fit classifications**
6. **Known material gaps**
7. **Actual role scope / level interpretation**
8. **Shortlist decision**

The resume-generation workflow should consume these as upstream state.

---

# What Resume Generation Still Needs to Do

The downstream resume workflow may still perform deeper evidence retrieval because shortlist mapping is not necessarily detailed enough to write final bullets.

Current downstream flow remains:

1. Evidence Retrieval
2. Hiring Criteria Evidence Mapping
3. Resume Strategy / Architecture
4. Resume Writing
5. Content Freeze / Resume Manifest
6. Document / Artifact Generation
7. Exact Content Validation
8. Render / Page-Space Audit
9. Compression only if needed
10. Writer revision if compression changes content
11. New Manifest
12. Regenerate / revalidate
13. Final QA

The key architectural rule is:

> **Resume Generation elaborates and packages the already-approved role/evidence interpretation. It should not independently redefine the role or manufacture a different fit story.**

---

# End-to-End Controller State

A programmatic job record should therefore be able to carry at least:

```yaml
job:
  company:
  title:
  job_id:
  location:
  work_model:
  travel:
  jd_source:

role_understanding:
  actual_job_to_be_done:
  major_responsibility_clusters:
  hiring_criteria:
  specialist_requirements:
  actual_scope:
  likely_hiring_manager_questions:

career_requirements_mapping:
  criteria:
  specialist_requirement_mapping:
  strongest_role_stories:
  meaningful_gaps:
  overall_evidence_summary:

shortlist_decision:
  decision:
  actual_work_alignment:
  scope_assessment:
  evidence_strength:
  career_value:
  primary_reasons_to_pursue:
  key_gap_or_risk:
  location_work_model:
  eligibility_relocation_flag:
  decision_rationale:
  next_action:

validation:
  role_understanding_complete:
  career_mapping_complete:
  factual_grounding_passed:
  capability_domain_fit_check_passed:
  gaps_preserved:
  semantic_validation_passed:
  selection_policy_check_passed:
  shortlist_decision_accepted:
```

---

# Current Workflow Boundary

For the immediate programmatic shortlist system, the workflow ends at:

> **Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation**

Only accepted roles (`APPLY — PRIORITY` or `APPLY`) should automatically enter the resume-generation queue.

`HOLD / INVESTIGATE` should enter an unresolved-review queue.

`DO NOT APPLY` should stop.

No additional ranking/scoring framework has been added here because it is **not part of the currently agreed workflow**.


## Version 1.2.0 controller acceptance contract

Validate the serialized structure, then perform completion, role-analysis,
evidence-grounding, gap, semantic, decision-consistency, and selection-policy checks
(A–G above). Shape validation alone cannot establish semantic validity or factual
truth. No stage or controller implementation is included in this change.

1. Verify the full JD and all required inputs were available or explicitly marked
   unknown where the posting is silent. Check job identity and location/work-model
   copies agree. Require substantive outputs, not populated placeholders.
2. Check criterion IDs are unique and mappings cover the identical upstream ID set
   exactly once, without changing criterion meanings. Stories may reference only
   those IDs. Cover all material specialist requirements, every baseline qualification,
   and all meaningful gaps. Preserve each baseline requirement type and its
   required/preferred status.
3. Apply every `evidence_check` in section C separately to every significant fit claim.
   Inspect the identified sources, not just the existence of citation text. Preserve
   all limitations, ambiguity, and distinctions in section E. A disclosed lack of
   evidence is valid gap analysis; an unsupported positive claim is a failure.
   Verify `capability_fit` and `domain_context_fit` independently: domain difference
   cannot lower an otherwise grounded capability classification, but it must remain
   visible. Direct capability and direct domain claims each require appropriate evidence.
   Audit in three distinct collections: `evidence_checks` contains exactly one item
   per hiring criterion; `specialist_requirement_checks` contains exactly one item per
   specialist requirement; and `baseline_qualification_checks` contains exactly one
   item per baseline qualification. Reject duplicates, missing items, or extras within
   any category. Verify baseline evidence provenance and uncertainty separately. A
   future screening outcome may remain unknown and must not be rewritten as a career
   capability gap.
   `evidence_checks[].criterion_id` may contain only upstream
   `hiring_criteria[].criterion_id` values. Specialist requirement text and baseline
   qualification IDs must never be inserted there. Specialist completeness remains
   part of `career_mapping_complete`, its rationale, specialist mapping validation,
   specialist checks, and actionable `issues`; the separate collection does not weaken
   those checks.
4. Review Tests A–E and rationale against the upstream outputs. Review HOLD's exact
   unresolved issue, and distinguish explicit constraints from unknowns. Do not
   convert an invalid or incomplete analysis into `DO NOT APPLY`.
5. Set each validation flag only after its check. Set `shortlist_decision_complete`
   as well as the fields in the export's end-to-end state: it was required in section
   A even though omitted from the final abbreviated state block.
6. Accept only when all completion/pass flags are true. On failure, leave
   `shortlist_decision_accepted` false, identify the failed check and responsible
   stage in the controller review, and return that stage for correction; revalidate
   affected downstream stages. Do not queue any unaccepted record. An accepted HOLD
   or DO NOT APPLY is a valid completed analysis, not permission to prepare a resume.

The schema enforces the acceptance-flag implication. The controller must additionally
check all cross-stage equality, source support, semantic consistency, and policy rules
above; booleans cannot self-certify their own correctness.

### Serialization and handoff binding

`schema.yaml` is a JSON Schema Draft 2020-12 document serialized as YAML. Version
`1.2.0` describes completed stage state (accepted or rejected), not partial runner
checkpoints. `schema_version` is serialization metadata, not a selection dimension.
Required keys with unknown factual values use null; narrative analysis must explain
material unknowns. Empty lists mean assessed and none found, not skipped work.
Unspecified textual labels remain free text; this contract does not invent enums for
`eligibility_relocation_flag.status` or `key_gap_or_risk.severity`.

The optional `handoff` object contains the agreed `role_state` and
`career_mapping_state`, plus the unchanged `shortlist_decision` and `validation`, so
actual scope classification and decision are not lost. Its values are projections,
not new analysis:

| Handoff destination | Canonical source |
| --- | --- |
| `role_state.actual_job_to_be_done`, `major_responsibility_clusters`, `hiring_criteria`, `specialist_requirements`, `baseline_qualifications`, `actual_scope`, `likely_hiring_manager_questions` | Identically named `role_understanding` fields |
| `role_state.location`, `work_model` | `role_understanding.role_identity` fields, consistent with `job` |
| `career_mapping_state.criteria_mapping` | `career_requirements_mapping.criteria` |
| `career_mapping_state.specialist_requirement_mapping`, `baseline_qualification_mapping`, `strongest_role_stories`, `meaningful_gaps`, `overall_evidence_summary` | Identically named `career_requirements_mapping` fields |
| `career_mapping_state.capability_domain_classification` | Per-criterion projection of `criterion_id`, `capability_fit`, `domain_context_fit`, `overall_fit_assessment`, and `limitation_or_difference` from `criteria`; no reclassification |
| `shortlist_decision`, `validation` | Exact canonical objects; actual scope classification remains in `shortlist_decision.scope_assessment` |

Controller checks equality for every projection before future handoff. The full
canonical job record remains available so identity, travel and JD source are not
lost. Only accepted APPLY outcomes may carry a resume handoff. Deeper retrieval may
expand source material but must not silently replace the mapping or erase gaps.
The conditions for rerunning Role Understanding and all universal resume constraints
in the preserved source remain binding when that downstream workflow is enabled.

### Current integration status

`shortlist/` v1.2.0 is now the sole authoritative shortlist specification for new runs.
Historical v1.0.0 and v1.1.0 artifacts are validated against their frozen shapes and
are never rewritten or silently upgraded. Resume reuse fails closed when changed
contract hashes make a saved stage stale.
The [migration dependency map and status](../docs/shortlist_v1_migration.md) replaces
this appendix's original pre-migration conflict inventory. Legacy policy is retired;
no aliases or automatic conversions between old and new decisions exist.

`scripts/shortlist_contract.py` performs read-only schema and cross-stage structural
checks on supplied records. It is not a stage executor or semantic controller and
does not set acceptance flags. The v1.2 schema adds the approved baseline-qualification
separation without changing outcomes or decision rules. Batch execution, persistence,
review/resume queue generation and dashboard
sync remain blocked pending explicit integration. Historical data is preserved.

### Export ambiguities and implementation readiness

No ambiguity blocks these declarative files. Structural omissions are bound above:
completion flag union, gap field aliases, handoff aliases, unknown representation,
and per-criterion capability/domain projection. These are serialization choices,
not new decision criteria.

The export gives qualitative decision guidance rather than an exhaustive deterministic
truth table. It does not define thresholds for every combination of Tests A–E,
within-outcome ordering, stable internal identity when requisition ID is absent,
queue storage, controller diagnostic storage, or source-locator format. It also does
not define a closed enum for every descriptive field. A future runner must not
invent scoring, implicit legacy conversions, or eligibility policy to fill these
holes. Deterministic automatic decision rules, durable queue identity/storage, and
integration with the existing canonical/Sheet contract need explicit decisions before
those components can be implemented. Evidence retrieval is separately deferred.

Source attachment SHA-256 (original bytes): `9a21dd761c037e7531063aed8cd1a14bb34e4dd7142981c116ef522624d7d274`.
