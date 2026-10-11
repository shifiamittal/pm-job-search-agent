# Resume Output Configuration Template

Customize per candidate.

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
    direct_vs_transferable_required: true
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
