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

Do not silently reject roles based on location; classify location fit instead.

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

Also classify:
- AI-heavy
- AI-adjacent
- Non-AI

# 8. Gap taxonomy

Use:

NONE
Candidate already demonstrates the requirement strongly.

K — Knowledge gap
Relevant foundation exists but concept/technical knowledge needs strengthening.

V — Vocabulary gap
Underlying experience exists but candidate is not expressing it using the market's terminology.

E — Evidence gap
Candidate likely has capability but resume/portfolio/interview proof is weak.

X — Experience gap
Role genuinely requires substantial prior experience candidate does not possess.

Important:
Exact technology-name mismatch is NOT automatically an X gap.
Evaluate transferable experience.

# 9. Classification principles

Protect Principal/Staff-equivalent seniority.

Evaluate:
- actual scope, not title alone
- hard prerequisites vs preferred qualifications
- transferable experience
- likely interview probability
- compensation
- geography
- career capital
- future market value

Do not favor famous employers automatically.
Do not favor AI roles automatically.
Do not penalize banking, insurance, healthcare, retail, or other non-tech industries.

# 10. Scoring

Score each 1-5:

Experience Fit — 25%
Interview Probability — 20%
Level Fit — 15%
Compensation Fit — 15%
Career Capital — 15%
Location Fit — 10%

Convert to 0-100.

If compensation is unpublished, mark compensation confidence as low / unknown rather than inventing a number.

# 11. Application lanes

APPLY NOW
- strong current evidence
- correct level
- no major X gap
- viable geography/economics
- candidate could credibly interview now

APPLY + BRIDGE
- attractive role
- strong adjacent evidence
- main gap is K, V, or E
- bridge is realistic during interview preparation

BUILD TOWARD
- strategically interesting
- meaningful X gap exists
- current interview probability materially lower

SKIP
- unnecessary down-level
- major hard-domain mismatch
- weak economics
- impractical geography
- weak career value
- stale/closed job
- role is not meaningfully Product Management

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
- discovery_log.csv

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
7. score
8. update persistent data
9. generate review queue
10. summarize only new/high-priority changes

Do not produce long prose reports unless requested.

# 19. Current phase

CURRENTLY ENABLED:
- repository maintenance
- candidate-profile preparation
- job discovery
- job verification
- job normalization
- job classification
- scoring
- review-queue generation

CURRENTLY DISABLED:
- application submission
- application form filling
- resume editing
- outreach sending
- email sending
- LinkedIn messaging
- recruiter contact

These capabilities can only be enabled through explicit future instructions.
