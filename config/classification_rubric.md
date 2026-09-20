# Calibrated Job Classification Contract

Read [candidate profile](../profile/candidate_profile.md), [career evidence](../profile/career_evidence.md), [preferences](../profile/job_preferences.md), [evidence conflicts](../profile/evidence_conflicts.md), and [approved resume](../resumes/master/resume.md). Use the official employer/ATS posting for JD facts. Do not infer missing candidate experience, posting dates, pay, or work authorization. This framework has **no numeric job-fit or priority score**.

## Facts first

Record company and a concrete one- or two-sentence company brief; exact JD role title and exact level terminology; posting date, source and confidence; location and work arrangement; published compensation and currency; sector; canonical URL and source; current live/closed status and verification timestamp. If the official posting does not expose a date, use a reliable secondary listing with attribution and confidence or write `Not exposed`. Unpublished pay is `Not published`. Do not abbreviate or normalize displayed levels.

Keep `role_domain` (business/product context), `technology_orientation` (what technology the mandate actually centers on), and `role_cluster` (product-function archetype) independent. Use only the enumerated values in [taxonomy](role_taxonomy.yaml). A platform is not AI simply because an AI product might consume it later. Write a two- or three-line `role_mandate` explaining ownership, decisions, product surface, and outcomes. Extract about four to seven concrete `key_functional_requirements` from the JD. List only plausible screening conditions under `hard_prerequisites`; distinguish Required, Strongly Preferred, Preferred, and Not Material domain expertise.

## Transfer, evidence, and gap

Assess `domain_fit` as Direct, Adjacent, Bridgeable, or Niche / Far. Explain transfer in one specific sentence. Cite relevant experiences by project name in `candidate_relevant_evidence`; detailed designs and prototypes count as capability evidence without implying unverified production scale or personal coding. Respect unresolved conflicts. Explain the precise missing proof, knowledge, or direct experience in `gap_rationale`.

Choose one full-text `primary_gap`: No Material Gap, Knowledge Gap, Vocabulary Gap, Evidence Gap, or Experience Gap. A resume wording change alone is not a Vocabulary Gap. A preferred qualification or unfamiliar tool name alone is not an Experience Gap. Mark `gap_gating` Non-gating, Soft, or Hard based on the actual hiring screen, not the gap label. An Experience Gap does not itself force Skip.

`bridge_action` says what to prepare; `bridge_timing` says when. Learnable niche-domain concepts normally wait for an interview. Apply promptly when senior PM evidence is credible. `Apply Now + Bridge` explicitly means **apply immediately**, with preparation while waiting or before interviews. A pre-application bridge is exceptional and must have a concrete reason.

## Strategic learning and action

Use `strategic_skill_overlap` High, Medium, or Low for reuse of the missing skill across attractive senior AI PM roles. `skill_build_priority` is Build Now only for recurring high-leverage capabilities: AI evaluation, agents/orchestration, AI platform fundamentals, developer-facing AI APIs, RAG/retrieval, AI reliability/observability, and hands-on AI prototyping. Existing strengths may need Maintain / Package Better in synthesis, while a role record says No Build Needed. Interview Triggered covers learnable role-specific knowledge. Do Not Build covers niche gaps that do not support the desired path toward senior AI PM opportunities with approximately $500K total-compensation potential; this is a career aspiration, **not an estimated salary for any job**.

Assess `application_posture`: Strong Match, Credible Match, Stretch, or Skip. Then assign `application_lane`: Apply Now; Apply Now + Bridge; Build Toward; or Skip. Build Toward is rare and requires both insufficient current credibility and a strategically reusable skill worth building. Skip unnecessary down-levels, poor economics/location, stale roles, and niche hard mismatches with low leverage. Strong conventional non-AI PM roles may be Apply Now. A location outside Seattle is visible friction, not a numerical score or automatic rejection. Follow confirmed US and India preferences without assuming relocation willingness or India authorization. `decision_rationale` states the action and reason plainly.

Recommend one approved resume variant and portfolio artifact, without editing either. Preserve uncertainty about requirements, location, compensation, and candidate evidence. Keep local Git data canonical and the Google Sheet as the review layer. User overrides are review data; do not train or silently change classifications from them.
