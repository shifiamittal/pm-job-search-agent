# 1. Purpose
This repository is a persistent Product Management job-search agent for Shifia Mittal.

Primary responsibilities:
- discover senior Product Management jobs
- verify that roles are live
- normalize job data
- deduplicate jobs
- classify roles against Shifia's background
- maintain durable job-search data
- generate a prioritized review queue

Later phases may support applications and outreach, but those actions are disabled until explicitly enabled.

# 2. Source-of-truth hierarchy

For candidate facts:
1. profile/candidate_profile.md
2. profile/career_evidence.md
3. approved resume source files
4. approved portfolio artifacts

Never infer or invent candidate experience.

For job facts:
1. official employer careers page
2. official ATS page
3. verified public company/recruiter posting
4. other discovery sources

Prefer canonical employer/ATS URLs.

# 3. Candidate evidence rules

Separate:
- confirmed fact
- demonstrated experience
- transferable/adjacent experience
- inference
- unknown

Never convert:
- adjacent experience into direct experience
- knowledge into production experience
- a prototype into a launched production system
- team output into personal ownership unless supported
- estimated business impact into confirmed impact

If evidence is ambiguous, mark it ambiguous.

Never invent:
- metrics
- titles
- dates
- technologies
- domain experience
- compensation
- work authorization information
- certifications

# 4. Job discovery scope

Search senior PM roles across all industries, not just AI.

Target title families:
- Principal Product Manager
- Principal PM-T / Principal Product Manager Technical
- Staff Product Manager
- Lead Product Manager
- Group Product Manager
- Product Lead

Conditionally include:
- Senior Product Manager
- Director Product Management
- Product Manager

only when scope, compensation, company title convention, or JD indicates Principal/Staff-equivalent responsibility.

Do not down-rank non-AI roles merely for being non-AI.

# 5. Geography

Primary US:
- Seattle / Bellevue / Redmond
- San Francisco Bay Area
- New York
- Remote US
- other strong US opportunities

India:
- Bengaluru
- Hyderabad
- NCR
- Mumbai
- Pune
- Remote India
- other unusually strong opportunities

Do not silently reject roles based on location; describe location friction in the decision rationale.

# 6. Industry scope

Include:
- Big Tech
- Enterprise Software
- Data / Developer Infrastructure
- Banking
- Fintech
- Payments
- Insurance
- Healthcare
- Retail / Commerce
- Travel
- Marketplaces
- Cybersecurity
- Telecom / Media
- Industrial
- Supply Chain / Logistics
- Energy
- Real Estate
- Education
- AI-native
- other enterprises with meaningful PM organizations

# 7. Role clusters

Assign one primary cluster:
- AI / Agents / Evals
- Data / ML Platform
- Enterprise / Developer Platform
- Fintech / Payments / Credit
- Marketplace / Supply Chain / Operations
- Growth / Monetization / Consumer
- Search / Retrieval / Knowledge
- Security / Risk
- Generic Principal / Staff Product
- Other

Classify technology orientation separately as GenAI / Agentic AI, Classical ML / Data Science, Data / Infrastructure, Non-AI, or Mixed. Keep business domain distinct from technology and role cluster.

# 8. Gap taxonomy

Use full text: No Material Gap, Knowledge Gap, Vocabulary Gap, Evidence Gap, or Experience Gap. Record whether the gap is Non-gating, Soft, or Hard, and explain exactly what is missing. Exact tool mismatch and preferred qualifications are not automatically experience gaps. Evaluate transferable experience and distinguish direct evidence from inference.

# 9. Classification principles

Protect Principal/Staff-equivalent seniority.

Evaluate:
- actual scope, not title alone
- hard prerequisites vs preferred qualifications
- transferable experience
- credible screening prerequisites
- compensation
- geography
- career capital
- future market value

Do not favor famous employers automatically.
Do not favor AI roles automatically.
Do not penalize banking, insurance, healthcare, retail, or other non-tech industries.

# 10. Explicit reasoning

Do not calculate numeric job-fit or priority scores. Capture exact JD facts before interpreting the mandate, functional requirements, domain fit and strength, evidence, gap, timing, strategic skill overlap, and decision. If compensation or posting date is unpublished, say so rather than estimating it. Display the exact company title and level without shorthand. Use [classification rubric](config/classification_rubric.md) and [taxonomy](config/role_taxonomy.yaml) for the current allowed values.

# 11. Application lanes

Apply Now: credible fit, no meaningful pre-interview capability work.

Apply Now + Bridge: **apply immediately**, with interview preparation or strategic AI skill-building in parallel. Learnable domain knowledge usually does not delay an application.

Build Toward: use sparingly only when present credibility is materially insufficient and a recurring, strategically useful capability is worth building.

Skip: unnecessary down-level, weak economics/location, stale role, non-PM job, or a hard niche mismatch with little strategic leverage. An Experience Gap alone does not force Skip.

# 12. Job verification

Never fabricate a role.

Whenever possible:
- verify against employer career page or official ATS
- capture requisition ID
- capture posted date
- capture compensation if explicitly published
- capture canonical URL

If a role appears stale or unavailable:
mark status appropriately.

# 13. Deduplication

Preferred unique key:
company + requisition ID

Fallback:
normalized company + normalized role + normalized location

When duplicate postings exist:
retain canonical official source and record alternate discovery source if useful.

# 14. Data mutation rules

Do not modify:
- candidate_profile.md
- career_evidence.md
- classification rules

during normal discovery runs.

Those require explicit user instruction.

Discovery may update:
- jobs_raw.jsonl
- jobs_master.csv
- review_queue.csv
- skills_synthesis.csv
- discovery_log.csv

After a successful canonical write, update the same configured Google Sheet. A Sheet failure leaves local data intact and is reported separately.

Never delete historical job records silently.
Mark closed/stale instead.

# 15. Human review

For classification:
record uncertainty rather than forcing confidence.

For future application automation:
Codex may eventually fill application forms, but MUST stop before final submission for full human review.

For future outreach:
research and drafting may be automated.
Actual outreach actions remain disabled until explicitly enabled.

# 16. Web interaction safety

Never:
- bypass access controls
- use scraped credentials
- store cookies/session tokens in Git
- violate website access restrictions
- fabricate contact information

# 17. Git rules

Before modifying files:
- confirm working tree state

After a coherent change:
- commit with a descriptive message

Never:
- force push
- rewrite published history
- delete user changes without permission
- commit credentials, secrets, cookies, browser sessions, or .env files

Prefer small, auditable commits.

# 18. Run behavior

Every discovery/classification run should:
1. state the search scope
2. discover jobs
3. verify them
4. deduplicate
5. normalize
6. classify
7. explain domain transfer, gap, strategic skill and application posture without scores
8. update persistent local data
9. generate review queue and skills synthesis
10. sync the persistent Google Sheet after successful local writes; report a sync failure without discarding local data
11. summarize only new/high-priority changes

Do not produce long prose reports unless requested.

# 19. Current phase

CURRENTLY ENABLED:
- repository maintenance
- candidate-profile preparation
- job discovery
- job verification
- job normalization
- job classification
- explicit domain/gap/skill classification
- review-queue generation
- skills synthesis and persistent dashboard synchronization

CURRENTLY DISABLED:
- application submission
- application form filling
- resume editing
- outreach sending
- email sending
- LinkedIn messaging
- recruiter contact

These capabilities can only be enabled through explicit future instructions.
