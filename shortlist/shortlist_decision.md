> Contract version: **1.2.0** (2026-10-02). Source: user-supplied plus approved baseline-qualification separation.
> “Role Shortlist Workflow — Current Agreed Implementation Specification”.
> This is the authoritative shortlist contract. Structural validation, the single-job runner,
> and sequential resumable batch execution are implemented. Shared v1 persistence and
> dashboard integration remain pending. See [migration status](../docs/shortlist_v1_migration.md).
> Workflow: **Role Discovery / Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation**.
> The agreed source text below is preserved verbatim. Versioned serialization and
> integration notes follow it, including approved quality clarifications below.
> Normative structure: [schema.yaml](schema.yaml). Controller: [controller_validation.md](controller_validation.md).

# 3. Shortlist Decision

## Purpose

Make the explicit decision:

> **Given the actual scope of this role, the candidate's evidence fit, and its career value, is this role worth spending time applying to?**

The Shortlist Decision consumes Role Understanding and Career / Requirements Mapping.

It does **not** redo those workflows.

---

# Exact Decision Framework

The agreed decision framework contains five tests.

---

## Test A — Actual-Work Alignment

Question:

> Is the majority of the job built around capabilities for which we have meaningful career evidence?

Allowed classifications:

- `Directly aligned`
- `Strongly adjacent`
- `Meaningful functional transition`
- `Misaligned`

This is the most important test.

---

## Test B — Scope / Level

Classify the actual role scope as:

- `Principal-equivalent`
- `High-value Senior`
- `Standard Senior`
- `Below target`

### Rules

Principal or equivalent scope is the default target.

A Senior PM role can pass if actual scope or career value justifies pursuing it.

Do not reject a role because its title says `Senior`.

Do not accept a role because its title says `Principal`.

---

## Test C — Evidence Strength

Question:

> Do we already have sufficiently strong evidence for the role's most important hiring criteria?

Allowed classifications:

- `Strong direct evidence`
- `Strong with transferable evidence`
- `Material evidence gaps`
- `Fundamental mismatch`

This test must rely on Career / Requirements Mapping.

Reason separately from `capability_fit` and `domain_context_fit`. Directly demonstrated
capability must not be downgraded solely because the domain/context differs. Domain
distance must still be surfaced as a ramp, risk, specialist gap, or blocker when it
matters to the role. Consider actual-work alignment, capability fit, domain/context
fit, scope, gaps, career value, and blockers together; no combination creates an
automatic outcome.

It must not ask whether a resume can be worded convincingly.

The test is:

> Do we actually have the evidence?

---

## Test D — Career Value

Especially important for Senior roles.

Evaluate whether the role:

- strengthens the Principal trajectory
- deepens a strategically useful domain
- strengthens AI / platform / product credentials
- creates meaningful business or platform ownership
- has unusually large scope despite title
- adds a capability that compounds the candidate's career profile
- offers strategically useful team/company exposure

Career-value classifications already used:

- `High`
- `Meaningful`
- `Limited`

Career value must be based on the work, not company prestige alone.

---

## Test E — Blockers / Unresolved Constraints

Always report separately:

- geography
- work model
- travel
- relocation
- work authorization requirement if explicitly known
- other stated eligibility requirements

These must not silently alter the fit assessment.

Example:

> Strong role fit, but requires four days/week in Redmond.

is different from:

> Weak role fit.

---

# Decision Categories

Exactly four shortlist outcomes were agreed.

## `APPLY — PRIORITY`

Use when there is:

- strong evidence
- appropriate/high-value scope
- strong career value

These roles receive downstream resume/outreach work first.

---

## `APPLY`

Use when the role is worth pursuing, but:

- evidence is more transferable
- fit is somewhat less distinctive
- domain gap exists
- career value is meaningful but not top priority

Proceed downstream.

---

## `HOLD / INVESTIGATE`

Use when one unresolved issue could materially change the decision.

Examples:

- unclear actual scope
- unclear reporting line
- questionable level
- unclear eligibility
- ambiguous responsibilities

The decision output must state exactly what must be resolved.

Downstream resume-generation work stops until it is resolved.

---

## `DO NOT APPLY`

Use when there is a substantive reason such as:

- actual work is materially outside the candidate's target career function
- a central required capability lacks meaningful supporting evidence
- role is materially below target without compensating career value
- a hard explicit eligibility/location constraint prevents pursuit

Do not use `DO NOT APPLY` merely because a role is:

- non-AI
- Senior instead of Principal
- outside Seattle
- not remote
- below an invented compensation threshold

---

# Handling Specific Selection Dimensions

## Seniority

Default target:

> Principal or equivalent.

Senior PM roles may be selected when their:

- actual scope
- responsibilities
- strategic importance
- career value

justify pursuing them.

Previously established example:

**Microsoft Reporting & Data Platform**

- Senior title
- classified as `High-value Senior`
- `APPLY — PRIORITY`

because actual work and career alignment were unusually strong.

---

## Geography

Current Phase 1:

- broad US
- India

Do not restrict selection to:

- Seattle
- US remote

Always report:

- role location
- remote/hybrid/in-office status
- relocation implication
- known eligibility constraint

Geographic inclusion does not establish:

- work authorization
- willingness to relocate

---

## Compensation

No compensation cutoff currently exists.

Do not invent one.

Compensation can be reported if supplied, but it is not currently a shortlist decision rule.

---

## Role Scope

Actual work dominates title.

The decision must use Role Understanding's actual job-to-be-done and scope analysis.

---

## Career Evidence

Decision must use mapped evidence from Career / Requirements Mapping.

Do not make a positive decision based on hypothetical resume positioning.

---

## Gaps

Differentiate:

### Manageable / transferable gap

Example:

> Microsoft Search Places — no direct local-search ownership, but strong search/relevance and AI evidence.

May still produce `APPLY`.

### Fundamental functional gap

Example:

> Microsoft Partner Development — core job is partner sales / BD, while candidate evidence is fundamentally product leadership.

Produced `DO NOT APPLY`.

---

## Career Value

Career value can justify pursuing a Senior role.

It does not override a fundamental functional mismatch.

---

# Required Shortlist Decision Output

```yaml
shortlist_decision:
  decision: APPLY — PRIORITY | APPLY | HOLD / INVESTIGATE | DO NOT APPLY

  actual_work_alignment:
    classification: Directly aligned | Strongly adjacent | Meaningful functional transition | Misaligned
    rationale:

  scope_assessment:
    classification: Principal-equivalent | High-value Senior | Standard Senior | Below target
    rationale:

  evidence_strength:
    classification: Strong direct evidence | Strong with transferable evidence | Material evidence gaps | Fundamental mismatch
    rationale:

  career_value:
    classification: High | Meaningful | Limited
    rationale:

  primary_reasons_to_pursue:
    - ...

  key_gap_or_risk:
    description:
    severity:

  location_work_model:
    location:
    work_model:
    travel:

  eligibility_relocation_flag:
    status:
    details:

  decision_rationale:

  next_action:
```

This corresponds to the standardized output previously agreed:

- `Application Decision`
- `Actual-work alignment`
- `Scope assessment`
- `Evidence strength`
- `Career value`
- `Primary reasons to pursue`
- `Key gap/risk`
- `Location/work model`
- `Eligibility/relocation flag`
- `Decision rationale`
- `Next action`

---



## Version 1.2.0 execution contract

Produce `shortlist_decision` by applying Tests A–E in their stated order to the
completed upstream analysis. Do not use legacy application lanes, posture labels,
gap gating, learning priorities, numeric scores, or a company-shortlist gate here.
Keep the four outcomes exactly as written, including the em dash in `APPLY — PRIORITY`.

A label is a proposed decision until [Validation](controller_validation.md) accepts
it. `HOLD / INVESTIGATE` must identify the decision-changing unresolved issue and
what evidence or answer is needed in `decision_rationale` and `next_action`.
Uncertainty is not a known disqualification. A hard eligibility/location blocker
requires explicit supporting facts; keep actual role fit separate from feasibility.
Compensation may be reported but cannot decide the shortlist outcome.

Do not infer rejection just from a gap severity label or acceptance just from a scope
label. Career value cannot override a fundamental functional mismatch. Examples in
the agreed text are consistency illustrations, not an exhaustive decision table.

Consume both `capability_fit` and `domain_context_fit` for every criterion. A domain
ramp does not become a capability gap; a true capability gap remains a capability
gap. Explain material domain/context distance without erasing direct capability, and
do not rewrite adjacent domain exposure as direct ownership. The decision must reason
from actual-work alignment, both fit dimensions, scope, meaningful gaps, career value,
and blockers without deterministic thresholds.

Consume `baseline_qualification_mapping` separately from capability fit,
domain/context fit, scope, career value, and blockers. A clearly unmet required
qualification may materially affect the decision. An unknown qualification must be
surfaced but does not automatically force rejection. Do not turn a future screening
unknown into a career capability gap or invent a new deterministic threshold.

Future routing after successful validation: `APPLY — PRIORITY` and `APPLY` are eligible
for the resume queue, with priority roles first; `HOLD / INVESTIGATE` goes to unresolved
review; `DO NOT APPLY` stops. No within-outcome ranking has been agreed. This change
creates no queues, runner, resume execution, application activity, or outreach.

### Approved qualitative decision principles (2026-10-13)

`APPLY` means worth pursuing. `APPLY — PRIORITY` means an unusually strong use of
application effort because actual work, evidence strength, appropriate scope and
career value align especially well without fundamental gaps. Explain that distinction
in the rationale. High-value Senior scope and a manageable domain ramp do not alone
cap a role at APPLY. Priority does not require identical industry experience or a
Principal title; title, prestige, AI branding and fit labels alone cannot establish it.

A fundamental specialist-domain evidence gap central to the actual job can justify
`DO NOT APPLY` despite strong general PM/platform capabilities and high career value.
A product-function mismatch is not required. Explain the absent operating knowledge,
its centrality to the work and why the specific transferable evidence does not bridge
it. Career value cannot compensate for that demonstrated fundamental shortfall.

This is not an automatic domain gate. Preferred or noncentral domain differences with
strong transfer can still support APPLY. Neither a domain name, gap severity nor a
`fundamental_to_role` flag mechanically decides the outcome. Reconcile every material
gap with the actual work and evidence; preserve direct capability independently from
domain distance. Centrality of a requirement alone does not prove an unbridgeable gap.

Carry production-maturity limits and unresolved authorization/sponsorship conflicts
forward. In `eligibility_relocation_flag.details`, distinguish canonical unknowns,
JD posting constraints and candidate feasibility unknowns. Never settle a conflict by
selecting a favorable source. Unknown is not a confirmed blocker; use HOLD when an
unanswered question changes the decision and identify the precise question.
