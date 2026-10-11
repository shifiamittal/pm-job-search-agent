> Contract version: **1.2.0** (2026-10-02). Source: user-supplied plus approved baseline-qualification separation.
> “Role Shortlist Workflow — Current Agreed Implementation Specification”.
> This is the authoritative shortlist contract. Structural validation, the single-job runner,
> and sequential resumable batch execution are implemented. Shared v1 persistence and
> dashboard integration remain pending. See [migration status](../docs/shortlist_v1_migration.md).
> Workflow: **Role Discovery / Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation**.
> The agreed source text below is preserved verbatim. Versioned serialization and
> integration notes follow it; they introduce no additional selection policy.
> Normative structure: [schema.yaml](schema.yaml). Controller: [controller_validation.md](controller_validation.md).

# 2. Career / Requirements Mapping

## Purpose

Compare the hiring criteria produced by Role Understanding against **established career evidence**.

This is not resume writing.

This step answers:

> **How much evidence do we actually have that the candidate has done the work this role requires?**

It must distinguish direct evidence from transferable evidence and real gaps.

---

## Inputs

### Required

- `role_understanding.hiring_criteria`
- `role_understanding.specialist_requirements`
- `role_understanding.likely_hiring_manager_questions`
- established career evidence
- validated project evidence
- prior resumes / deep-dive artifacts where available

### Candidate evidence currently used by the workflow includes, among others

- Keystone Deep Enterprise / enterprise AI platform
- Keystone Enterprise Data Platform
- Forecasting Agent
- AI Evaluation / eval harness
- Patent AI Search
- Amazon ML Ops Platform
- Amazon Financial Services
- Amazon personalization / growth
- SPORT
- MOQ
- TRACE
- cross-functional / executive leadership evidence
- enterprise rollout and change-management evidence

Only use evidence that can actually be supported.

---

## How Requirements Are Identified

Do not independently recreate the role requirements.

Start from the hiring criteria already produced in **Role Understanding**.

For each criterion determine:

1. What capability does the role require?
2. Which established career story or artifact is the strongest evidence?
3. Is the underlying capability evidence direct, transferable, adjacent, or missing?
4. Is the domain/context evidence direct, transferable, adjacent, missing, or not applicable?
5. What limitation needs to be explicitly preserved?

---

## How Career Evidence Is Mapped

For each role criterion:

### 1. Select the strongest evidence

Map to a specific project, product, responsibility, or outcome.

Examples already used:

- Inventory optimization → SPORT
- cost-to-serve + CX trade-off → MOQ
- network intelligence → TRACE
- enterprise data platform → Keystone Data Platform
- canonical semantics → Keystone semantic layer
- developer platform → Amazon ML Ops
- AI-native workflow → Forecasting Agent
- search/relevance → Patent AI Search
- relevance evaluation → Patent AI Search + AI Evaluation
- consumer experimentation → Amazon Financial Services / personalization
- C-suite influence → Keystone CEO/CTO + enterprise COO/CFO/VP stakeholders
- distributed cross-functional execution → Amazon

---

### 2. Explain why the evidence maps

Do not merely name the project.

State the actual overlap between:

- role requirement
- candidate work

Example:

> SPORT involved identifying long-term unprofitable inventory and recommending movement from high-cost to lower-cost channels, which is directly adjacent to FBA inventory-placement decisions.

---

### 3. Preserve differences

If the experience is not the same problem/domain, explicitly state the difference.

Example:

> Patent AI Search proves retrieval/ranking/relevance experience, but it is not equivalent to large-scale consumer Places search.

This distinction is mandatory.

---

## Capability Fit and Domain / Context Fit

Assess two independent questions for every criterion.

### Capability fit

Classify whether the underlying skill or work pattern has been demonstrated:

- `direct`: substantially the same capability has been demonstrated.
- `transferable`: a closely related capability can credibly transfer, with the difference stated.
- `adjacent`: useful neighboring experience exists, but the required capability is not fully established.
- `gap`: the capability is not adequately established.

Capabilities include customer discovery, product strategy, developer/platform ownership,
roadmap prioritization, technical product definition, and distributed-team coordination.
Do not downgrade capability fit merely because the industry differs.

### Domain / context fit

Separately classify whether the evidence occurred in the same industry, customer type,
product context, or operating environment:

- `direct`: materially the same domain/context.
- `transferable`: a different context with a credible, explainable ramp.
- `adjacent`: some context overlap, but meaningful contextual distance remains.
- `gap`: a required domain/context is not established.
- `not_applicable`: the criterion does not materially depend on domain/context.

Example: customer-discovery capability can be `direct` while accounting-industry
context is `transferable`. Preserve both truths. A domain ramp is not a capability gap.

The terminology used in the workflow includes:

- `Very strong direct fit`
- `Strong fit`
- `Strong transferable fit`
- `Strong adjacent fit`
- `Moderate / gap`
- `Material gap`
- `Major gap`

The qualitative overall assessment should synthesize both fields without replacing them:

### Direct capability and context

The candidate performed substantially the same work/problem.

Example:

> Keystone Data Platform versus Microsoft Reporting & Data Platform.

---

### Adjacent / Transferable capability or context

The underlying product pattern is similar, but domain or implementation context differs.

Example:

> Amazon ML Ops deployment/orchestration experience versus Azure fleet-scale change management.

---

### Capability or domain/context gap

The requirement is not adequately established in career evidence.

Examples previously identified:

- direct customer reverse-logistics ownership
- large-scale consumer Places/local-search ownership
- 8+ years strategic partner portfolio ownership
- enterprise-sales/pipeline ownership
- fleet-scale rollback/remediation ownership

Do not hide gaps by rewriting adjacent evidence as direct evidence. A true capability
gap remains a capability gap. Preserve specialist/domain gaps separately where
meaningful, and never turn a domain ramp into a capability gap.

---

## How Gaps Are Represented

Every meaningful gap must specify:

```yaml
gap:
  requirement:
  severity:
  what_is_missing:
  closest_transferable_evidence:
  whether_it_is_fundamental_to_role:
```

Severity terminology already used:

- `Moderate / gap`
- `Material gap`
- `Major gap`

The narrative must distinguish:

> a domain ramp

from:

> a fundamental functional mismatch.

Example already established:

- lack of direct monetization-reporting ownership was considered a manageable domain ramp.
- lack of strategic-partner ownership and enterprise-sales ownership for Partner Development was considered a fundamental functional mismatch.

---

## Required Output Fields

```yaml
career_requirements_mapping:
  criteria:
    - criterion_id:
      criterion:
      role_requirement:
      strongest_evidence:
        project_or_role:
        evidence_summary:
        measurable_outcomes:
      capability_fit: direct | transferable | adjacent | gap
      domain_context_fit: direct | transferable | adjacent | gap | not_applicable
      overall_fit_assessment:
      limitation_or_difference:

  specialist_requirement_mapping:
    - requirement:
      evidence:
      assessment:
      gap_if_any:

  baseline_qualification_mapping:
    - qualification_id:
      requirement:
      requirement_type: education | experience_duration | certification | screening | work_authorization | other
      required_or_preferred: required | preferred
      evidence:
      assessment: met | likely_met | unknown | not_established | does_not_apply
      limitation_or_unknown:

  strongest_role_stories:
    - story:
      criteria_supported:
      why_relevant:

  meaningful_gaps:
    - requirement:
      severity:
      description:
      closest_transferable_evidence:
      fundamental_to_role: true | false

  overall_evidence_summary:
```

---

## Factual-Grounding Rules

### Evidence must already exist

Do not invent:

- responsibilities
- metrics
- team size
- direct reports
- technologies
- business ownership
- domain exposure

---

### Prefer validated evidence

If multiple historical versions conflict, use the currently validated version unless explicitly resolved otherwise.

---

### Do not convert adjacency into direct experience

Examples:

Do not say:

> owned local search

because Patent Search exists.

Do say:

> hands-on experience in retrieval, ranking, relevance evaluation, and AI-assisted search workflows.

---

### Revenue impact is not equivalent to sales ownership

This distinction was explicitly established during the Partner Development assessment.

Do not infer:

> enterprise sales ownership

from:

> products that generated revenue.

---

### Executive interaction is not automatically partnership ownership

Likewise:

> C-suite influence

does not equal:

> strategic technology-partner portfolio ownership.

---

### Use the strongest evidence, not every possible story

Career Mapping should identify the evidence hierarchy so downstream resume generation knows what to prioritize.

---



## Version 1.2.0 execution contract

### Candidate context supplied by the single-job runner

Use all five complete candidate-context files:

- `profile/candidate_profile.md`: high-level orientation.
- `profile/career_evidence.md`: primary synthesized evidence base.
- `profile/evidence_conflicts.md`: ambiguity/conflict guardrails.
- `profile/job_preferences.md`: shortlist-policy/preferences context, subject to the
  authoritative shortlist v1 policy; superseded legacy rules do not govern selection.
- `profile/candidate_confirmed_facts.md`: valid candidate-provided facts not
  independently source-validated.

Preserve `provenance_type` as `source_validated` or `candidate_confirmed`.
Candidate-confirmed facts remain `candidate_confirmed` when quoted from the synthesis;
do not promote them to documentary validation. Both types may support reasoning;
preserve conflicts and ownership limits. Candidate-confirmed facts do not require
independent documentary confirmation merely to be used.

### Mapping output

Produce `career_requirements_mapping` from the preceding stage's criteria. Preserve
criterion IDs and criterion meanings; cover every criterion exactly once and every
specialist requirement. Add `baseline_qualification_mapping` and cover every upstream
baseline qualification exactly once without changing its requirement, type, or
required/preferred status. Do not generate a new set of role requirements here.

For every baseline qualification, retain `qualification_id`, `requirement`,
`requirement_type`, and `required_or_preferred`; add `evidence`, `assessment`, and
`limitation_or_unknown`. Assessment is exactly `met`, `likely_met`, `unknown`,
`not_established`, or `does_not_apply`. Preserve source provenance for positive claims.
Do not infer credentials or missing employment periods. An approved total-experience
headline may support duration while any documented timeline ambiguity remains explicit.
A future screening outcome is `unknown` and is not a capability gap.

Use supplied established evidence only. No career-evidence retrieval mechanism is
implemented by this contract. Project names in the agreed examples are not evidence
sources by themselves. Put a traceable source locator (file/section or artifact/link)
and the supporting fact in the existing evidence text for every significant fit
claim. Controller review must be able to inspect that source. If it is unavailable,
do not assert support or set factual grounding to passed. Prefer currently validated
facts and preserve unresolved conflicts; do not resolve candidate facts by inference.

For every criterion, classify `capability_fit` and `domain_context_fit` independently.
Do not downgrade demonstrated capability solely because the industry, customer type,
product context, or operating environment differs. Surface that difference in
`domain_context_fit` and `limitation_or_difference`. A domain/context gap does not by
itself create a capability gap. `overall_fit_assessment` synthesizes the two fields;
it may not erase either one or act as a deterministic decision rule.

Keep confirmed facts, demonstrated experience, transfer, inference, and unknowns
explicit in prose. Knowledge is not production experience; a prototype is not a
production launch; team output is not personal ownership; estimates are not confirmed
impact. No invented dates, titles, certifications, or work authorization. Empty
`measurable_outcomes` means no supported measurable outcome, not zero impact.

The export's standalone `gap.what_is_missing` is serialized in
`meaningful_gaps[].description`; `whether_it_is_fundamental_to_role` is serialized
as `fundamental_to_role`. Preserve their exact meanings. Do not create duplicate
competing gap records. `limitation_or_difference` may be null only when no limitation
was found after review; for transferable/adjacent evidence explain the difference.
An explicit `gap` mapping may have null strongest-evidence fields, but must explain
what is unestablished and include any meaningful gap in `meaningful_gaps`.

The listed fit-assessment phrases are qualitative vocabulary, not a numeric scale
or a substitute for `capability_fit` or `domain_context_fit`. No automatic relationship
between overall fit wording, gap severity, and the final decision is defined.

Historical `1.0.0` artifacts retain `evidence_type` and `fit_assessment`; historical
`1.1.0` artifacts retain the capability/domain split without baseline fields. Neither
version is rewritten. New `1.2.0` runs use the split fields and baseline mapping above.
Proceed to [Shortlist Decision](shortlist_decision.md).
