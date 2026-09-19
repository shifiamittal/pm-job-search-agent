# Job Classification Rubric

Use [job preferences](../profile/job_preferences.md) for level, geography, work authorization, and strategy. Use [candidate profile](../profile/candidate_profile.md), [career evidence](../profile/career_evidence.md), [evidence conflicts](../profile/evidence_conflicts.md), and [approved resume](../resumes/master/resume.md) for candidate claims. Preferences supersede stale TBD statements in older profile documents. Verify the job against its employer or official ATS page; do not turn a search snippet into a verified open role.

## Record and verify the job

Store the employer, title, requisition ID when present, canonical URL, location/work mode, posted date if shown, requirements, pay as published, source, discovery and verification times. Record `posted_date` as blank when the employer does not publish it. An accessible live official posting is `live_verified`; otherwise distinguish `unverified`, `stale`, and `closed`. A search-result date is not automatically the posting date. Deduplicate by company + requisition ID, otherwise normalized company + role + location. Never invent compensation or requirements.

## Six component scores

Score each integer 1–5. Weighted priority = 20 × (0.25 × Experience Fit + 0.20 × Interview Probability + 0.15 × Level Fit + 0.15 × Compensation Fit + 0.15 × Career Capital + 0.10 × Location Fit). Preserve every component in the record. This is a relative prioritization heuristic, not a hiring prediction. The total never overrides a hard X gap or a clear down-level.

| Dimension | Weight | Scoring judgment |
| --- | --- | --- |
| Experience Fit | 25% | Map all demonstrated and transferable experience to hard requirements. 5 = strong direct evidence; 3 = credible adjacent evidence; 1 = major unmet requirements. Exact tool names and preferred qualifications alone do not create X gaps. |
| Interview Probability | 20% | Relative chance the current approved resume plausibly earns an interview, considering hard requirements, level, domain, title history, transferable proof, and specialization/competition. 5 = compelling current proof; 1 = remote prospect. |
| Level Fit | 15% | 5 = clear Principal/Staff-equivalent scope; 4 = comparable scope despite title; 3 = needs calibration; 2 = meaningful down-level likely; 1 = clear unnecessary down-level. Protect level. Conditional Senior PM, PM, or Director titles require explicit scope evidence. |
| Compensation Fit | 15% | Evaluate only published pay against senior PM market positioning and stated candidate preferences. Compensation floor/target remains TBD, so avoid precise personal-pay claims. If unpublished, score 3 (neutral), mark confidence LOW, and do not penalize solely for missing pay. |
| Career Capital | 15% | Assess ownership, strategy, skill accumulation, revenue/customer importance, market credibility, and 2–3 year PM value. AI or famous employer status alone never earns 5. |
| Location Fit | 10% | Follow the confirmed scoring below. Location alone should not force Skip during market calibration. |

Location guidance: US Seattle/Bellevue/Redmond or Seattle hybrid = 5; Remote US workable from Seattle ≈ 4; other strong US market for exploration ≈ 3; significant relocation or unclear flexibility = 2; impractical = 1. India Bengaluru = 5, Hyderabad = 4, other cities = 2–3 depending on opportunity. US permanent resident; no employer sponsorship required. India eligibility and willingness to relocate are unknown.

Compensation fields `comp_min`, `comp_max`, and `currency` contain only official published numbers and their currency. Do not infer annualization, equity, or a candidate floor. Confidence is HIGH for explicit official range, LOW for unpublished/ambiguous, and MEDIUM only for a clearly attributable but qualified official range.

## Gap classification

Choose one primary gap, with a short specific explanation: NONE, K (knowledge), V (vocabulary), E (evidence), or X (substantial direct experience missing). Set `hard_experience_gap` explicitly to true or false. Aspirational or preferred requirements should be weighed with judgment. For X, name the actual hard prerequisite and why the evidence does not meet it. Transferable experience counts even without identical tools.

## Application lane

- **APPLY NOW:** Appropriate Principal/Staff-equivalent level, strong current evidence, no major X gap, credible interview now, and viable location/economics.
- **APPLY + BRIDGE:** Attractive role with strong adjacent evidence; main K, V, or E gap can reasonably be addressed during interview preparation.
- **BUILD TOWARD:** Strategically interesting, with a meaningful X gap and materially lower interview probability now. Retain 3–5 such roles in the calibration review queue.
- **SKIP:** Unnecessary down-level, hard domain mismatch, clearly weak economics, impractical location, low-value or non-PM role, or stale/closed posting. Never skip because a role is non-AI.

Choose one resume variant and the strongest portfolio artifact from `role_taxonomy.yaml`; these are recommendations, not instructions to edit a resume. `classification_confidence` is HIGH/MEDIUM/LOW based on clarity of official requirements, evidence mapping, and missing information. An unverified live status lowers confidence.

## Review and uncertainty

For each classification, preserve the actual requirements, hard prerequisites, fit rationale, source URL, and the reason for the lane. Label unclear compensation, posted date, work mode, sponsorship, management scope, or hard prerequisites as unknown. Do not convert unknown into a negative claim. Include both AI and non-AI opportunities. Calibrate across sectors, levels, and geographies; do not choose only high-fit examples.
