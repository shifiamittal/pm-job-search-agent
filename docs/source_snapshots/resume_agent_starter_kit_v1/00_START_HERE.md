# Resume Agent Starter Kit — START HERE

## What this kit is

This kit turns a fresh ChatGPT conversation into a structured resume-tailoring workflow.

Core principle:

> Do not jump directly from a job description to a rewritten resume.

Instead, separate role understanding, fit assessment, evidence retrieval, evidence mapping, resume strategy, writing, content freeze, document generation, validation, layout review, and final QA.

## What the new user should upload

Required:
- Master resume
- Most recent resume
- Full job description

Strongly recommended:
- Older resumes
- Project deep-dives
- Interview-prep documents
- Performance reviews
- Strategy documents
- Product / launch summaries
- Portfolio materials
- Metrics / impact notes
- Preferred resume template, if available

Do not rewrite these files first. The agent should retrieve evidence from the originals.

## Files in this kit

- `01_RESUME_AGENT_WORKFLOW.md` — canonical end-to-end workflow
- `02_JOB_SEARCH_SHORTLIST_MODE.md` — optional apply / skip workflow before resume tailoring
- `03_CANDIDATE_EVIDENCE_BASE_TEMPLATE.md` — structure for the candidate's own evidence base
- `04_EVIDENCE_AND_TRUTHFULNESS_RULES.md` — anti-hallucination / evidence rules
- `05_RESUME_OUTPUT_CONFIG_TEMPLATE.md` — configurable output defaults
- `06_BOOTSTRAP_PROMPT.txt` — paste into a fresh ChatGPT conversation
- `07_CONTROLLER_AND_QA_CHECKLIST.md` — stage gates and final QA
- `08_TEMPLATE_USAGE_GUIDE.md` — how to reuse formatting without leaking old content

## Recommended setup in ChatGPT

1. Start a fresh ChatGPT conversation.
2. Upload this kit plus the candidate's career files.
3. Paste `06_BOOTSTRAP_PROMPT.txt`.
4. Build the candidate evidence base first.
5. Review / correct factual issues.
6. Then provide a target job description.

## Two supported modes

### Resume-only mode
> JD → Role Understanding → Fit Assessment → Evidence Retrieval → Hiring Criteria Mapping → Resume Strategy → Writing → Manifest → DOCX → Validation → Layout Audit → Final QA

### Job-search mode
> Role Intake → Role Understanding → Career / Requirements Mapping → Shortlist Decision → STOP or CONTINUE

Accepted roles then enter the resume workflow.

## Important rule

The candidate's uploaded career files are the only source of truth for their experience.

Examples inside this kit are process examples only. They are never evidence about the candidate.
