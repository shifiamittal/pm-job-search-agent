# Canonical Resume Agent Workflow

## Purpose

Governing process:

> JD → understand role → assess fit → retrieve evidence → map evidence to hiring criteria → design resume architecture → write → freeze → generate → validate → render → compress only if needed → validate again

The system must not jump directly from a job description to resume writing.

# Stage 1 — Role Understanding

**Core question:** What is this job really about?

Inputs:
- JD
- company / team context
- title / level
- location / work model

Responsibilities:
- infer actual role archetype
- explain likely day-to-day work
- identify product / system context
- extract hiring-manager selection criteria
- separate must-haves from preferred capabilities
- interpret ambiguous JD language
- identify seniority / scope expectations
- identify likely hiring-manager questions

Outputs:
- actual job-to-be-done
- responsibility clusters
- hiring criteria + importance
- specialist requirements
- scope interpretation
- likely HM questions
- uncertainties

Boundary: do not tailor the candidate yet.

# Stage 2 — Fit Assessment

**Core question:** Should the candidate pursue this role?

Classify:
- direct fit
- transferable fit
- adjacent fit
- real gaps
- qualification gaps
- level mismatch
- geography / work-model mismatch

Outputs:
- Apply / Maybe / Skip
- direct-fit areas
- transferable-fit areas
- genuine gaps
- hard qualification concerns
- level considerations
- recommendation rationale

Boundary: do not write resume content.

# Stage 3 — Evidence Retrieval

**Core question:** What evidence do we actually have for each requirement?

Search:
- master resume
- prior resumes
- project artifacts
- interview notes
- strategy docs
- portfolio materials
- validated metrics
- candidate-authored evidence

Retrieve:
- story
- candidate ownership
- mechanism / what was built
- decision / trade-off
- impact
- source
- confidence
- conflicts / caveats

Prefer underlying artifacts over compressed resume bullets when detail is needed.

Boundary: retrieve evidence; do not choose final resume wording.

# Stage 4 — Hiring Criteria Evidence Mapping

**Core question:** For every hiring criterion, what is the strongest proof?

Map:

> hiring criterion → meaning → strongest direct evidence → secondary / transferable evidence → gap → source → confidence

Responsibilities:
- rank evidence by relevance
- select the strongest story
- label direct / transferable / adjacent / gap
- preserve genuine gaps
- avoid upgrading weak evidence

Recommended table:

| Hiring criterion | What it means | Strongest evidence | Secondary evidence | Gap | Evidence type | Confidence |
|---|---|---|---|---|---|---|

Boundary: choose which evidence wins; do not write final copy.

# Stage 5 — Resume Strategy / Architecture

**Core question:** What should appear on the page and in what structure?

Choose:
- source resume / template
- headline strategy
- summary themes
- experience order
- bullet architecture
- bullet IDs
- priority labels
- differentiators to preserve

Priority labels:
- `MUST_KEEP`
- `KEEP_SEPARATE`
- `CAN_COMBINE`
- `OPTIONAL`

`OPTIONAL` means removable only under actual page pressure.

Every important bullet gets a contract:
- bullet ID
- role / project
- criterion supported
- candidate ownership
- mechanism
- approved metric
- priority label
- source
- wording constraints

Boundary: design content architecture; do not create DOCX.

# Stage 6 — Resume Writing

**Core question:** How should the approved architecture be expressed?

Write:
- headline
- summary
- exact bullet copy
- competencies if needed

Recommended bullet pattern:

> ownership / action → what was built or changed → relevant mechanism / problem → measurable consequence

Writer may not:
- add / remove bullet IDs
- replace selected stories
- merge `KEEP_SEPARATE`
- change section order
- change validated metrics
- inflate scope
- invent ownership
- make page-fit decisions
- edit the Word file

Writer may:
- improve clarity
- tighten wording
- adapt terminology to the role
- improve sentence structure while preserving evidence

# Stage 7 — Content Freeze / Resume Manifest

**Core question:** What exact text is approved and immutable?

Manifest includes:
- headline
- summary
- section headers
- every bullet ID
- exact bullet text
- competencies
- education text if changed
- section order
- bullet order

After freeze:
- no wording changes
- no bullet removal
- no merging
- no old-template substitution
- no compression

Any approved content change requires a new manifest version.

# Stage 8 — Resume Document / Artifact Creation

**Core question:** How should frozen content be implemented without changing it?

Use:
- manifest = content source
- template = formatting source

Document Agent may preserve:
- styles
- margins
- font
- indentation
- hierarchy
- spacing
- hyperlinks

Zero editorial authority:
- no rewriting
- no shortening
- no bullet removal / merging
- no metric changes
- no section reordering
- no page-fit edits

# Stage 9 — Exact Content Validation

Validate before layout review.

Checks:
1. ID-level structural diff
2. exact text diff
3. old-template leakage check

Pass only if:
- every required ID exists
- every block matches the manifest
- no unapproved old content is present

# Stage 10 — Render

Render the exact validated document. No content changes.

# Stage 11 — Visual / Page-Space Audit

Inspect:
- page count
- clipping
- whitespace
- bullet density
- hierarchy
- formatting consistency
- line breaks
- visual prominence of important evidence

Do not compress because you expect overflow. Measure actual page pressure.

# Stage 12 — Compression Decision

Only if real overflow exists.

Compression order:
1. reduce Core Competencies detail
2. tighten summary
3. tighten sentence phrasing
4. combine `CAN_COMBINE`
5. remove `OPTIONAL`
6. reconsider `MUST_KEEP` / `KEEP_SEPARATE` only with explicit approval

Unused whitespace is evidence compression was premature.

# Stage 13 — Writer Revision

Any content compression returns to Resume Writing.

# Stage 14 — New Manifest Version

Any wording change requires a new manifest version.

# Stage 15 — Regenerate Artifact

Generate from new manifest. No editorial changes.

# Stage 16 — Re-run Exact Content Validation

Repeat structural diff, exact text diff, leakage check.

# Stage 17 — Re-render / Re-check Layout

Confirm desired page count, no clipping, clean hierarchy, no excessive whitespace.

# Stage 18 — Final QA

Verify:
- correct company / role / job ID
- correct headline
- all bullet IDs present
- exact-content validation passed
- no unsupported claims
- no unresolved metric accidentally used
- no wrong-company references
- no old-template leakage
- correct page count
- no broken layout
- correct filename

## Non-negotiable invariants

1. Manifest is the single source of truth for content.
2. Template is the single source of truth for formatting.
3. Document generation has zero editorial authority.
4. No resume is delivered unless exact-content validation passes.
5. Compression never occurs inside document generation.
6. Any content change requires a new manifest version.
7. Old template wording not present in the manifest is leakage.
8. Adjacent experience may be generalized but may not become direct experience.
9. Conflicting metrics stay unresolved until explicitly resolved.
10. Gaps may be positioned but not erased.

# Practical 7-agent implementation

- Agent A — Role Analyst: Role Understanding + Fit Assessment
- Agent B — Evidence Mapper: Evidence Retrieval + Hiring Criteria Mapping
- Agent C — Resume Strategist: source resume, summary contract, bullet contracts, priority hierarchy
- Agent D — Resume Writer: headline, summary, bullets, competencies
- Agent E — Content Freeze / Manifest
- Agent F — Resume Document Agent: formatting / rendering only
- Agent G — Validation & QA: exact diff, leakage, semantic audit, page-fit, compression recommendations, final QA
