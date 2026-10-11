> Contract version: **1.2.0** (2026-10-02). Source: user-supplied plus approved baseline-qualification separation.
> “Role Shortlist Workflow — Current Agreed Implementation Specification”.
> This is the authoritative shortlist contract. Structural validation, the single-job runner,
> and sequential resumable batch execution are implemented. Shared v1 persistence and
> dashboard integration remain pending. See [migration status](../docs/shortlist_v1_migration.md).
> Workflow: **Role Discovery / Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → Validation**.
> The agreed source text below is preserved verbatim. Versioned serialization and
> integration notes follow it; they introduce no additional selection policy.
> Normative structure: [schema.yaml](schema.yaml). Controller: [controller_validation.md](controller_validation.md).

# Role Shortlist Workflow — Current Agreed Implementation Specification

## Purpose

This specification captures the **current agreed shortlist workflow exactly as established in the working chat**.

It is intended to sit between job discovery and the downstream resume-generation workflow.

Current flow:

**Role Discovery / Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → STOP or CONTINUE**

If the decision is `APPLY — PRIORITY` or `APPLY`, continue to:

**Evidence Retrieval → Hiring Criteria Evidence Mapping → Resume Strategy / Architecture → Resume Writing → Manifest → Document Generation → Validation / QA → Outreach**

If the decision is `HOLD / INVESTIGATE`, stop downstream execution until the unresolved issue is answered.

If the decision is `DO NOT APPLY`, stop the workflow.

### Current scope decisions already agreed

- Include **AI and non-AI PM / PM-T roles**, including equivalent product titles, when the actual responsibilities align with established career evidence.
- Target **Principal or equivalent scope** by default.
- Selectively include **Senior PM roles** when their actual scope, responsibilities, strategic importance, or career value justify pursuing them.
- Evaluate **actual work and scope**, not title or AI keywords.
- Phase 1 includes **broad US and India locations**.
- Do not restrict selection to Seattle or US-remote roles.
- Do not introduce an unapproved compensation cutoff.
- Always report location, work model, relocation considerations, and eligibility concerns separately from role fit.
- Broad geographic inclusion does **not** imply work authorization or willingness to relocate.
- The previously discussed company-shortlist gate is **not part of the current implemented shortlist workflow**. It was explicitly deferred for now.

---

# 1. Role Understanding

## Purpose

Determine what the job **actually is**, independent of title wording, AI keywords, or employer branding.

The output should explain:

> What will this person actually spend most of their time doing?

and:

> What will the hiring manager actually evaluate?

This step is the source of truth for role interpretation downstream.

---

## Inputs

### Required

- Full job description / job posting
- Job title
- Company
- Job ID, if available
- Location
- Work model, if stated
- Travel, if stated
- Required qualifications
- Preferred qualifications

### Optional

- Additional employer-provided role context
- Team / organization description
- Compensation information included in the posting
- Hiring-platform metadata such as profession, discipline, role type, level, etc.

---

## Exact Analysis Steps

### Step 1 — Determine the actual job-to-be-done

Answer:

> **What is this job really about?**

Do not restate the job title.

Describe the core work in plain product terms.

Examples from the established workflow included formulations such as:

- “Principal PM-T responsible for the intelligence layer behind FBA inventory placement, seller economics, reverse logistics, and network optimization.”
- “Senior strategic account / business-development leader responsible for growing Microsoft’s business through a portfolio of major software-company partners.”
- “Senior Product Manager owning the shared data and reporting foundation for Microsoft AI Monetization.”
- “Cloud infrastructure platform PM focused on safe change management across Azure at massive scale.”
- “Consumer Search + AI product role focused on Places.”

The purpose is to identify the **actual functional archetype**.

---

### Step 2 — Decompose the role into major jobs / responsibility clusters

Group the JD into the few major types of work the person is expected to perform.

Examples previously used:

- inventory/network optimization
- seller + customer economics
- AI-native systems
- Principal cross-org architecture
- data-platform ownership
- canonical metrics / semantic layer
- developer-platform ownership
- change-management lifecycle
- search/relevance
- consumer decision experiences
- strategic partner ownership
- enterprise sales / pipeline

Do not create categories merely because keywords appear in the posting.

The categories must describe actual work.

---

### Step 3 — Identify the core hiring criteria

Reduce the JD into the smallest useful set of criteria that explain what the hiring manager needs to see.

For every criterion identify:

- criterion name
- what it means in this role
- importance

Importance terminology already used:

- `Critical`
- `Very high`
- `High`
- `Helpful`

Do not artificially force every role to have the same number of criteria.

---

### Step 4 — Identify specialist requirements separately

Call out qualifications that are more specific than general PM ability.

Examples:

- Search and Relevance systems
- reverse logistics
- developer/orchestration platforms
- enterprise sales
- strategic partner ownership
- semantic models / canonical metrics
- FinOps
- local/Places search

These become especially important during Career / Requirements Mapping.

---

### Step 5 — Determine actual scope / level

Evaluate role scope from responsibilities, not title.

Scope signals previously used include:

- breadth of charter
- global / cross-geography responsibility
- cross-org ownership
- number/type of stakeholder organizations
- executive influence
- strategic vs execution-only ownership
- foundational platform ownership
- business/economic accountability
- long-term strategy responsibility

Do **not** assume:

- `Principal` title = automatically Principal scope
- `Senior` title = automatically below target

Role Understanding should produce enough information for the Shortlist Decision step to classify actual scope later as:

- `Principal-equivalent`
- `High-value Senior`
- `Standard Senior`
- `Below target`

---

### Step 6 — Identify likely hiring-manager screening questions

Convert the role into a small number of concrete questions such as:

- Has she actually worked on inventory / fulfillment optimization problems like ours?
- Can she operate at Principal scope across Seller, CX, economics, Science, and Engineering?
- Does she bring genuinely current AI capability rather than only traditional ML experience?
- Has she actually owned a developer or infrastructure platform?
- Does she understand deployment/change-management mechanics deeply enough?
- Has she built shared enterprise data platforms?
- Has she defined canonical entities, business metrics, semantic models, and reusable datasets?
- Has she actually owned major strategic partners?
- Can she carry commercial responsibility?
- Does she have direct Search / Relevance systems experience?

These questions become the bridge into Career / Requirements Mapping.

---

## Required Output Fields

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

  baseline_qualifications:
    - qualification_id:
      requirement:
      requirement_type: education | experience_duration | certification | screening | work_authorization | other
      required_or_preferred: required | preferred
      notes:

  actual_scope:
    scope_signals:
      - ...
    scope_summary:

  likely_hiring_manager_questions:
    - ...
```

---

## Important Rules / Constraints

### Actual work over title

Always assess what the person will actually do.

Do not use:

- title matching
- AI keyword matching
- company prestige
- compensation

as substitutes for understanding the work.

---

### AI is not automatically a fit signal

An AI-branded role may be poorly aligned.

A non-AI role may be highly aligned.

Example established in the workflow:

- Microsoft Partner Development Manager had strong seniority and AI/cloud exposure, but actual work was partner sales / business development, not product management.

---

### Senior roles are not automatically rejected

A Senior PM role can still be strategically attractive if the actual work has:

- foundational platform ownership
- broad organizational scope
- highly relevant domain depth
- significant career value

Example already established:

- Microsoft Senior PM — Reporting & Data Platform was treated as high-value despite the Senior title because the actual platform problem was unusually aligned.

---

### Do not infer unstated requirements

If the posting does not establish something, label it unknown rather than inventing it.

---



## Version 1.2.0 execution contract

Run these six steps in their stated order using the full posting supplied at intake.
Produce `role_understanding`; do not produce a shortlist decision here. Required
and preferred qualifications remain distinct in the source; importance describes
hiring significance, not whether the employer made a qualification mandatory.
Retain the exact employer title. An interpreted scope label never replaces it.

The source examples are illustrations of the agreed analysis, not fresh verification
of a job or evidence of a candidate claim. Do not classify a live role from an example.
An absent job ID, work model, travel statement, or qualification section is unknown,
not an invented requirement. Record unknown facts explicitly. Full JD/source context
must remain available to the controller; this contract does not fetch postings.

The number of criteria is role-specific; there is no four-criterion minimum or fixed
count. Specialist requirements may be an empty list only after actual consideration.
Preserve every explicit baseline qualification in `baseline_qualifications`, including
degrees, minimum experience duration, required certifications, mandatory screening or
background checks, explicit work authorization, and other hard eligibility conditions.
Give each item a stable `qualification_id`. Keep employer-stated preferred qualifications
as `preferred`; never promote them to `required`. Ordinary capabilities belong in
`hiring_criteria`, and domain expertise belongs in `specialist_requirements`. Screening
is eligibility evidence, not a career capability. An empty baseline list means the full
JD was reviewed and none was stated.

Preserve compound minimum qualifications without dropping their logic. For example,
`Bachelor's Degree AND 8+ years ... OR equivalent experience` must retain the degree,
minimum duration, and equivalent-experience alternative together. Role Understanding is
incomplete if any explicit mandatory qualification is absent from its appropriate field.
Do not create a duplicate when the same mandatory qualification is already represented.
Proceed to [Career / Requirements Mapping](career_requirements_mapping.md).
