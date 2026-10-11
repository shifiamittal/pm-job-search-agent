# Optional Job Search / Shortlist Mode

Use this before resume tailoring when the candidate wants help deciding whether a role is worth pursuing.

Flow:

> Role Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation → STOP or CONTINUE

Decision options:
- `APPLY — PRIORITY`
- `APPLY`
- `HOLD / INVESTIGATE`
- `DO NOT APPLY`

## Step 1 — Role Understanding

Required output:

```yaml
role_understanding:
  role_identity:
    company:
    title:
    job_id:
    location:
    work_model:
    travel:
  actual_job_to_be_done:
    summary:
  major_responsibility_clusters:
    - name:
      description:
  hiring_criteria:
    - criterion_id:
      criterion:
      description:
      importance: Critical | Very high | High | Helpful
  specialist_requirements:
    - requirement:
      importance:
      notes:
  actual_scope:
    scope_signals:
      - ...
    scope_summary:
  likely_hiring_manager_questions:
    - ...
```

Evaluate actual work, not title.

## Step 2 — Career / Requirements Mapping

For each criterion:
1. What capability is required?
2. Which candidate story is strongest?
3. Is it direct, transferable, adjacent, or missing?
4. What limitation must stay explicit?
5. What source supports it?

Required output:

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
      evidence_type: direct | transferable | adjacent | gap
      fit_assessment:
      limitation_or_difference:
  specialist_requirement_mapping:
    - requirement:
      evidence:
      assessment:
      gap_if_any:
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

## Step 3 — Shortlist Decision

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

## Decision logic

`APPLY — PRIORITY`
- directly aligned work
- strong evidence
- high scope / career value
- manageable gaps

`APPLY`
- strongly adjacent
- credible but partly transferable evidence
- manageable gaps

`HOLD / INVESTIGATE`
- one unresolved issue could materially change the decision

`DO NOT APPLY`
- core function is different
- fundamental evidence gaps
- scope / career value does not justify transition

## Rules

- Actual work > title.
- AI branding is not a fit signal by itself.
- Senior does not automatically mean too junior.
- Principal does not automatically mean good fit.
- Geography / work model is separate from content fit.
- Revenue impact ≠ sales ownership.
- Executive interaction ≠ strategic account ownership.
- Adjacent evidence remains adjacent.
- Downstream writing may not erase known gaps.

## Handoff into resume workflow

Preserve:

```yaml
role_state:
  actual_job_to_be_done:
  major_responsibility_clusters:
  hiring_criteria:
  specialist_requirements:
  actual_scope:
  likely_hiring_manager_questions:
  location:
  work_model:

career_mapping_state:
  criteria_mapping:
  specialist_requirement_mapping:
  strongest_role_stories:
  meaningful_gaps:
  direct_vs_transferable_classification:
  overall_evidence_summary:
```
