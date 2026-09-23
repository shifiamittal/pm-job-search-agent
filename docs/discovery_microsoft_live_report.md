# Microsoft Careers discovery: availability review

Nothing committed or pushed. The approved 63-role benchmark is unchanged.

## Updated live result

| Source | Reference | Candidates | Found | Missed | Recall | Benchmark-match precision |
|---|---:|---:|---:|---:|---:|---:|
| Anthropic | 19 | 19 | 19 | 0 | 100.00% | 100.00% |
| OpenAI | 10 | 10 | 10 | 0 | 100.00% | 100.00% |
| Microsoft | 63 | 69 | 63 | 0 | 100.00% | 91.30% |

Microsoft precision against the fixed benchmark is 63/69 = 91.30%. This is
benchmark-match precision: extras are not automatically proven false positives.
The five disputed requisitions still resolve with positive public source evidence.
One additional requisition, 200041062, appeared since the preceding 77-record crawl.
Its detail response also verifies availability. The result is therefore 69, not 63.

## Official retrieval and audit

- Search: `https://apply.careers.microsoft.com/api/pcsx/search`.
- Parameters: `domain=microsoft.com`, empty `query` and `location`,
  `filter_profession=product management`, numeric `start` offset.
- Details: `https://apply.careers.microsoft.com/api/pcsx/position_details`;
  `domain=microsoft.com`, `position_id=<source ID>`, `hl=en`.
- Capture: `2026-09-23T08:52:52.628986+00:00` to `2026-09-23T08:59:29.083261+00:00`.
- Run: `a24e4c18e24440d4a39646f7b269fddc`.
- Source total and unique raw Microsoft records: **78 / 78**.
- Eight populated pages (seven of 10, last of 8), empty terminal page,
  two matching boundary checks: **11 search requests**.
- **69 detail requests**, all available; **80 requests total**, no errors/retries.
- One enumeration pass; no duplicate IDs or count drift.
- Combined raw records: 1508; combined candidates: 98.

All 78 facet records remain in raw output. Six are outside US/India; one fails
the unchanged PM title filter (200055117, Senior Director, Creator Monetization - Minecraft).
The two internships, 200052636 and 200050323, remain raw but are excluded from
live candidates. All remaining 69 passed detail verification.

## Five disputed records and one newly observed extra

Each row below returned matching source position/requisition IDs, a full job
description and `applyAction.status=log_in`; HTTP/body status 200, no fallback.
The separate direct checks of the five disputed careers pages also returned
HTTP 200 and matching job titles. Generic application-notification template text
containing "no longer" was not a job-specific closure signal.
Public endpoint availability conflicts with the reported manual-search result.
No application was attempted; these signals do not prove an application can be
completed. No unsupported stale labels or benchmark-specific exclusions were added.

| Requisition | Position ID | Exact title | Microsoft posting |
|---|---|---|---|
| 200041062 | 1970393556911401 | Principal Product Manager | [Posting](https://apply.careers.microsoft.com/careers/job/1970393556911401) |
| 200052288 | 1970393556982604 | Principal Product Manager | [Posting](https://apply.careers.microsoft.com/careers/job/1970393556982604) |
| 200057176 | 1970393557004133 | Senior Product Manager | [Posting](https://apply.careers.microsoft.com/careers/job/1970393557004133) |
| 200056147 | 1970393556999868 | Principal Product Manager | [Posting](https://apply.careers.microsoft.com/careers/job/1970393556999868) |
| 200055645 | 1970393556998398 | Principal Product Manager- Copilot | [Posting](https://apply.careers.microsoft.com/careers/job/1970393556998398) |
| 200044401 | 1970393556940372 | Principal Product Manager | [Posting](https://apply.careers.microsoft.com/careers/job/1970393556940372) |

Direct five-record detail payload/page evidence:
[microsoft_availability_verification.json](../data/discovery/microsoft_availability_verification.json).
Latest per-job checks, page audits and original source listings:
[crawl_runs.jsonl](../data/discovery/crawl_runs.jsonl).

## Availability mismatch regression and validation

The adapter now excludes missing/removed (404/410), explicit fallback and closed
detail responses from live candidates while preserving raw records. Uncertain
identity or absent positive evidence is marked unknown and excluded, not mislabeled
stale. Verification status persists across later combined-output regeneration.
Internships are excluded by Microsoft title or source employment type.

Full suite: **67 tests passed, 0 failures**. The new regression verifies a live
search listing with a 404/fallback detail response remains raw but cannot enter
live output; separate tests cover uncertain identity and internship exclusion.
Combined eval: **92/92 found**, zero misses. Anthropic remains 19/19 and OpenAI
10/10 using saved snapshots. Their benchmark, raw and candidate records match
HEAD; their adapters and the shared title filter are unchanged. Downstream
classification was not changed or run. `git diff --check` passed.

## Authoritative benchmark import and authorized correction

The user confirmed that Downloads/microsoft_pm_reference_final_reviewed.csv is
authoritative and explicitly authorized verifying/correcting the duplicate ID.
Original CSV SHA-256:
`25905e898c377d1e1d7be4eaaf5e8a4d467845735d5944254aab6f4eeab88adc`.

The CSV has 63 approved requisitions, but initially only 62 distinct position IDs.
The official live facet verifies:

| Requisition | Location | Verified position ID |
|---|---|---|
| 200043757 | United States, Washington, Redmond | 1970393556938152 |
| 200045393 | India, Telangana, Hyderabad | 1970393556944421 |

For requisition 200045393, corrected the duplicated position ID 1970393556938152
to 1970393556944421 and its URL to
https://apply.careers.microsoft.com/careers/job/1970393556944421.
This is the only approved-job identity correction. Titles/locations/requisitions
remain human-approved source values. The original downloaded CSV is untouched.
The standalone imported JSONL and shared reference dataset now contain exactly
63 unique Microsoft IDs/requisitions, including manual addition 200055927 /
1970393556999250, Principal Product Manager, India, Telangana, Hyderabad.
Existing 19 Anthropic and 10 OpenAI reference rows are unchanged.

## Review artifacts

- [Implementation notes](discovery_microsoft.md)
- [Latest raw jobs](../data/discovery/raw_all_jobs.jsonl)
- [Latest live candidates](../data/discovery/raw_pm_candidates.jsonl)
- [Latest eval](../data/evals/latest/summary.json)
- [Source-only run snapshot](../data/discovery/runs/a24e4c18e24440d4a39646f7b269fddc/raw_all_jobs.jsonl)

Earlier snapshots and pre-existing independent benchmark-construction artifacts
are preserved. The source is not transactionally locked; counts and boundary
checks cannot prove that every middle-page record remained unchanged throughout
capture. Existing serialized, non-transactional multi-file export limits remain.
