# Purpose and authoritative shortlist contract

This repository is Shifia Mittal's persistent Product Management job-search agent.
Discovery finds and verifies roles; role evaluation and shortlisting use **shortlist/
v1.2.0 as the sole authoritative contract for new runs**.

Read, in order:
1. [Role Understanding](shortlist/role_understanding.md)
2. [Career / Requirements Mapping](shortlist/career_requirements_mapping.md)
3. [Shortlist Decision](shortlist/shortlist_decision.md)
4. [Controller / Validation](shortlist/controller_validation.md)
5. [Structured state schema](shortlist/schema.yaml)
6. For accepted roles only, [Resume Generation Agent](resume_agent/README.md)

Workflow: Role Discovery / Intake → Role Understanding → Career / Requirements
Mapping → Shortlist Decision → Validation.

The only shortlist outcomes are:
- `APPLY — PRIORITY`
- `APPLY`
- `HOLD / INVESTIGATE`
- `DO NOT APPLY`

These files define role understanding, evidence mapping, decision semantics,
validation, and output shape. Do not maintain a parallel rubric here. Do not infer
new decisions by translating historical classifications. No numeric fit, priority,
or location scores, compensation cutoff, company gate, or automatic AI preference.
Use actual work and scope; Principal-equivalent is the default target and high-value
Senior roles are eligible under v1. Geography is broad US/India; report work model,
travel, relocation and eligibility separately from role fit.

## Authority and migration status

[Migration note](docs/shortlist_v1_migration.md) records deprecated consumers and
current integration status. `config/classification_rubric.md` and
`prompts/classification.md` are pointers only. `config/role_taxonomy.yaml` contains
non-decision metadata and asset names, not shortlist rules.

`profile/job_preferences.md` is preserved as a historical source of confirmed facts
and expressed preferences. Its old location scoring, title/economics gates, lane
labels, and automatic technology preferences are superseded by shortlist v1 and
must not govern current selection. Keep genuine candidate facts and uncertainties;
do not infer work authorization or relocation willingness from geographic scope.
Historical data, calibration annotations, older reports, and the original conflict
inventory in the shortlist controller are not live policy.

## Source of truth and candidate evidence

For candidate facts use, in order:
1. `profile/candidate_profile.md`
2. `profile/career_evidence.md`
3. Approved resume source files
4. Approved portfolio artifacts

Respect `profile/evidence_conflicts.md` and currently validated evidence. Separate
confirmed facts, demonstrated experience, adjacent/transferable experience,
inference, and unknowns. Do not convert adjacency into direct experience, knowledge
into production experience, prototypes into launched production systems, team
output into personal ownership, or estimated impact into confirmed impact.

Never invent metrics, titles, dates, technologies, domain experience, compensation,
work authorization, certifications, responsibilities, or management scope. Preserve
ambiguity. Source names or examples in the specification do not themselves prove
candidate experience. Do not retrieve or rewrite career evidence as part of this
migration or ordinary discovery.

## Discovery and job facts

Search PM / PM-T and equivalent product work across AI and non-AI industries.
Do not use title, employer prestige, or technology keywords as substitutes for
actual-work analysis. Discovery adapters and PM-family filtering are separate
intake systems; do not reinterpret their inclusion as a shortlist decision.

Job fact source order:
1. Official employer careers page
2. Official ATS page
3. Verified public company/recruiter posting
4. Other discovery sources

Never fabricate a role. Prefer canonical employer/ATS URLs. Capture requisition ID,
posting date, compensation and currency when published, exact title/level, location,
work model, source, live/closed status, and verification timestamp. Explicitly mark
unpublished or unknown facts. Preserve business domain, technology orientation,
and role cluster as separate descriptive metadata where used.

Deduplicate by company + requisition ID, otherwise normalized company + role +
location. Retain canonical sources and useful discovery provenance. Never silently
delete history; mark closed/stale when appropriate.

## Data mutation and current runtime boundary

Do not modify candidate profiles, career evidence, conflicts, preferences, or the
shortlist specification during normal discovery without explicit instruction.

Raw discovery can continue writing its own artifacts under `data/discovery/`.
The historical classification files `jobs_raw.jsonl`, `jobs_master.csv`,
`review_queue.csv`, `skills_synthesis.csv`, calibration annotations and lane-change
history are read-only legacy snapshots until an explicit v1 persistence migration.
They are not the v1 review queue. No silent relabeling or compatibility conversions.
The authorized single-job runner saves isolated artifacts under ignored
`local_private/shortlist/<run_id>/`; this does not activate legacy persistence,
dashboard synchronization or downstream actions.

Legacy classification finalization, calibration reprocessing, queue/skill generation,
and dashboard writes are blocked pending v1 persistence/dashboard integration. Do not bypass
these guards or use legacy functions to satisfy a discovery run. Report the blocked
integration separately from successful raw intake.

Future v1 persistence must preserve history and user feedback, then update the same
configured Google Sheet after successful canonical writes. A future Sheet failure
must not discard local data. This obligation does not activate the currently blocked
writer or authorize creating a replacement spreadsheet.

## Review and enabled scope

Enabled: repository maintenance, raw discovery/verification/normalization,
manual shortlist v1 analysis, the single-job full-context runner
(`scripts/run_shortlist_job.py`), and read-only validation of completed v1 records.
A schema check cannot certify factual grounding or semantic correctness; controller
review remains mandatory. Report uncertainty instead of forcing confidence. Model-based controller review in
the single-job runner is not independent human verification. For this baseline, pass
all five complete candidate-context files into Career Mapping without retrieval or
pruning: `candidate_profile.md`, `career_evidence.md`, `evidence_conflicts.md`,
`job_preferences.md`, and `candidate_confirmed_facts.md` under `profile/`.
See [single-job runner](docs/single_job_shortlist.md) for invocation and output details.

Implemented for shortlist execution: single-job and sequential resumable batch runners.
Not implemented: selective evidence retrieval, v1 persistence/queue integration, a complete
programmatic resume-generation runner, and v1 dashboard integration. The canonical
resume-generation workflow and QA/controller instructions are available under
`resume_agent/` for accepted roles. Source-document read-only sync remains independent
and requires its normal explicit source selection.

Disabled as automated actions: application form filling/submission, automated resume artifact
generation/editing, outreach sending, email, LinkedIn messaging, and recruiter contact.
Resume-generation analysis and drafting may follow `resume_agent/`; this does not imply a
programmatic resume runner or authorization to send/submit. Future activation needs explicit
user instruction. Any future application automation must stop before final submission
for full human review. An APPLY outcome is not authorization to send or submit.

## Web and Git safety

Never bypass access controls, use scraped credentials, violate site restrictions,
fabricate contact information, or store credentials, secrets, cookies, browser
sessions, or `.env` files in Git.

Before modifying files, inspect the working tree. Preserve user changes. Never force
push or rewrite published history. Prefer small, auditable changes. Do not commit or
push this migration until the user reviews it and authorizes that action.

## Run reporting

State scope; discover, verify, deduplicate and normalize when discovery is requested.
When shortlisting is requested, follow the versioned stages and validation without
adding scores or old classification obligations. Explain blockers and the current
persistence boundary. Summarize new/high-priority changes concisely; do not produce
long reports unless requested.
