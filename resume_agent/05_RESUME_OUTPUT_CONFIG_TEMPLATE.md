# Resume Output Configuration Template

Customize presentation per candidate. This is resume output configuration, not a
shortlist selection rubric. Titles, levels, geography, and work-model entries do
not override `../shortlist/` v1.2 or imply work authorization or relocation consent.
Resume configuration does not enable automated downstream execution.

```yaml
resume_config:
  target_roles:
    - Product Manager
    - Technical Product Manager

  target_levels:
    - Principal
    - Staff
    - Senior

  geography:
    include:
      - United States
      - India
    exclude: []

  work_model:
    acceptable:
      - Remote
      - Hybrid
      - Onsite
    notes:

  target_pages: 1
  body_font_pt: 10

  resume_style:
    density: concise
    tone: executive_and_technical
    bullet_style: outcome_oriented
    include_profile_summary: true
    include_core_competencies: true

  output_sections:
    - Header
    - Headline
    - Profile Summary
    - Experience
    - Core Competencies
    - Education

  filename_convention:
    pattern: "{CandidateName}_{Company}_{Role}_Resume.docx"

  evidence_policy:
    preserve_shortlist_mapping_fields:
      - capability_fit
      - domain_context_fit
      - overall_fit_assessment
      - limitation_or_difference
    preserve_gaps: true
    preserve_metric_conflicts: true
    no_invented_claims: true

  document_policy:
    manifest_is_content_source: true
    template_is_formatting_source: true
    document_agent_editorial_authority: false

  compression_policy:
    compress_only_after_render: true
    compression_order:
      - Core Competencies detail
      - Summary tightening
      - Sentence tightening
      - CAN_COMBINE bullets
      - OPTIONAL bullets
      - Reconsider MUST_KEEP only with approval
```

Notes:
- One page is a default, not a universal law.
- Do not shrink font to hide a content-strategy problem.
- Do not compress before measuring actual page pressure.
