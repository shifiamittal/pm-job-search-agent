# PM-family benchmark correction and live regression evaluation

Capture date: 2026-09-30. Production Python files and source configuration were SHA-256 checked before/after and unchanged. All 111 existing tests passed. No commits or pushes. Historical frozen v1 references and evaluations remain intact. The active revised reference for this evaluation is `data/evals/workday/workday_pm_reference_frozen_v2.csv`.

## Adobe benchmark change

Removed R171808 (Senior Manager, Digital Monetization Growth) and R171889 (Venture Lead, Creator Services - Adobe Incubator), as explicitly approved: neither title matches the broad PM-family title definition. Retained the original 36 qualifying Adobe references and added only the five requested independently source-verified roles. This is a benchmark-definition revision, not an improvement to the adapter or filter. The revised Adobe reference is informed by discovered candidates and must not be presented as a new independent holdout.

Original reference SHA-256: `6bdb82c429e4101543bb803b8ca6a5a0307b500858901984952c7d2dfcf7c592`.
Revised reference SHA-256: `2dd641c4e4712c3c7a2c4508c932aa3b5dd1235254869d1087926584a2cdc002`.

| Job ID | Exact title | Location | Live | Public source | PM title | Added |
|---|---|---|---|---|---|---|
| R168909 | Senior Product Manager,  Chief Accounting Office | San Jose ; Lehi | HTTP 200, canApply=True | True | Product Manager | True |
| R169439 | Internal Product Manager 3 - Sales Performance Management | Bangalore | HTTP 200, canApply=True | True | Product Manager | True |
| R169992 | Principal Product Manager - Order to Cash Platform (SAP BRIM) | San Jose | HTTP 200, canApply=True | True | Product Manager | True |
| R170043 | Product Manager - International Strategy & Product Management | San Jose ; San Francisco | HTTP 200, canApply=True | True | Product Manager | True |
| R171158 | Internal Product Manager 5 | San Jose | HTTP 200, canApply=True | True | Product Manager | True |

Verification evidence is saved in `data/evals/pm_family_v2/adobe_verification/`, including official CXS URLs, timestamps, and full responses. Country descriptors are United States of America or India; presence in the fresh configured public CXS crawl establishes external discoverability. Internal in a title was not interpreted as an internal-only job. NVIDIA and CrowdStrike reference rows are identical to v1. Product Lead and Product Owner remain positive signals.

## Fresh evaluation

| Company | Benchmark | Raw | PM | Matches | Recall | Extras | Duplicate output IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| Anthropic | 19 | 638 | 17 | 17 | 89.47% | 0 | 0 |
| OpenAI | 10 | 835 | 12 | 10 | 100.00% | 2 | 0 |
| Microsoft | 63 | 82 | 70 | 49 | 77.78% | 21 | 0 |
| Adobe | 41 | 463 | 41 | 41 | 100.00% | 0 | 0 |
| NVIDIA | 35 | blocked | n/a | n/a | n/a | n/a | unknown |
| CrowdStrike | 10 | 221 | 11 | 10 | 100.00% | 1 | 0 |

Metrics are known-positive benchmark recall. Extras are unreviewed, not false positives. Benchmark IDs enter only evaluation and the approved reference-maintenance step; no retrieval or filter logic reads them.

## Every remaining miss and extra

| Company | Difference | Job ID | Title | Location |
|---|---|---|---|---|
| Anthropic | Missing | 5407337008 | Product Manager, Beneficial Deployments (Labs) | San Francisco, CA ; New York City, NY |
| Anthropic | Missing | 5406106008 | Product Manager, Growth | San Francisco, CA ; New York City, NY ; Seattle, WA |
| OpenAI | Extra | 2b5c3a30-8e8b-4845-be40-0617b0c9fd43 | Rosalind Life Sciences Product Manager | San Francisco |
| OpenAI | Extra | 137e3df0-2bd4-4ad4-8edb-8455a7fdc912 | Product Manager, Technology Vertical | San Francisco |
| Microsoft | Missing | 200035179 (source 1970393556859707) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Missing | 200049390 (source 1970393556971845) | Principal Product Manager | India, Telangana, Hyderabad |
| Microsoft | Missing | 200044192 (source 1970393556939407) | Principal Product Manager - Azure Speech (CoreAI) | United States, Washington, Redmond |
| Microsoft | Missing | 200055495 (source 1970393556995531) | Principal Product Manager, AI Infrastructure | United States, Multiple Locations, Multiple Locations |
| Microsoft | Missing | 200048258 (source 1970393556960709) | Principal Product Manager- Early Adoption | United States, Washington, Redmond |
| Microsoft | Missing | 200040513 (source 1970393556875687) | Product Manager II - Microsoft Foundry | United States, Washington, Redmond |
| Microsoft | Missing | 200056377 (source 1970393557000257) | Senior Product Management | United States, Washington, Redmond |
| Microsoft | Missing | 200042335 (source 1970393556924396) | Senior Product Manager | United States, Washington, Redmond |
| Microsoft | Missing | 200045393 (source 1970393556944421) | Senior Product Manager | India, Telangana, Hyderabad |
| Microsoft | Missing | 200055557 (source 1970393556995633) | Senior Product Manager | United States, Washington, Redmond ; United States, Texas, Austin |
| Microsoft | Missing | 200055734 (source 1970393556998551) | Senior Product Manager | United States, Washington, Redmond |
| Microsoft | Missing | 200050160 (source 1970393556978354) | Senior Product Manager- M365 Messaging | United States, Washington, Redmond |
| Microsoft | Missing | 200053485 (source 1970393556986887) | Senior Technical Product Manager | United States, Washington, Redmond |
| Microsoft | Missing | 200044665 (source 1970393556941507) | Senior/Principal Product Manager-Advertiser Intelligence (Diagnostics & Keywords) | United States, California, Mountain View ; United States, Washington, Redmond ; United States, New York, New York |
| Microsoft | Extra | 200055464 (source 1970393556995454) | Senior Product Manager | United States, Multiple Locations, Multiple Locations |
| Microsoft | Extra | 200056128 (source 1970393556999840) | Senior Product Manager | United States, Washington, Redmond ; United States, California, Mountain View ; United States, New York, New York |
| Microsoft | Extra | 200056978 (source 1970393557002302) | Senior Product Manager - Windows Personal Experiences | United States, Washington, Redmond |
| Microsoft | Extra | 200058424 (source 1970393557014478) | Senior Technical Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200057949 (source 1970393557007853) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200058038 (source 1970393557008067) | Principal Product Manager, Microsoft Clarity | United States, Washington, Redmond ; United States, California, Mountain View |
| Microsoft | Extra | 200056608 (source 1970393557001321) | Principal Product Manager - Dynamics 365 Contact Center | United States, Washington, Redmond |
| Microsoft | Extra | 200058347 (source 1970393557008723) | Senior Product Manager and Principal Product Manager (Multiple Positions) - D365 Contact Center | United States, Washington, Redmond |
| Microsoft | Extra | 200057506 (source 1970393557006543) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200045861 (source 1970393556948020) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200057516 (source 1970393557006552) | Senior Technical Product Manager - CISO Security Engineering | United States, Multiple Locations, Multiple Locations |
| Microsoft | Extra | 200056672 (source 1970393557001429) | Principal Product Manager | United States, Multiple Locations, Multiple Locations |
| Microsoft | Extra | 200048797 (source 1970393556962217) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200051927 (source 1970393556982046) | Principal Product Manager, AI Monetization, Ads & Creatives, Copilot | United States, Washington, Redmond ; United States, California, Mountain View ; United States, New York, New York |
| Microsoft | Extra | 200041693 (source 1970393556916180) | Principal Product Manager, Agent 365 Security & Governance | United States, Washington, Redmond |
| Microsoft | Extra | 200057309 (source 1970393557004779) | Principal Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200051298 (source 1970393556980893) | Principal Product Manager, Dataverse | United States, Washington, Redmond |
| Microsoft | Extra | 200041062 (source 1970393556911401) | Principal Product Manager | India, Karnataka, Bangalore |
| Microsoft | Extra | 200052288 (source 1970393556982604) | Principal Product Manager | United States, California, Mountain View ; United States, Washington, Redmond |
| Microsoft | Extra | 200057176 (source 1970393557004133) | Senior Product Manager | United States, Washington, Redmond |
| Microsoft | Extra | 200055645 (source 1970393556998398) | Principal Product Manager- Copilot | United States, Washington, Redmond ; United States, California, Mountain View |
| CrowdStrike | Extra | R28919 | Sr. Manager, AI Product Owner, GTM Applications (Remote) | USA - Remote, AZ |

Anthropic missing IDs were absent from the full fresh raw board, not excluded by PM title filtering. All 14 Microsoft misses were also absent from the fresh raw profession-facet records by both source position ID and requisition ID; no replacement source IDs for those requisitions were found. Microsoft recovered from one HTTP 429 on its first enumeration request; all 70 candidate availability checks succeeded. Absence from the public board is not a separate detail-page closure determination.

## Failures and completeness

NVIDIA: current crawl blocked at offset 240 by official source row `{ "bulletFields": ["JR2025784"] }`, missing title and externalPath. A second direct official request reproduced the malformed row. Source reported 1,623 jobs; adapter had recorded 240 unique valid listing paths before failing. No raw snapshot was published and current recall/extras/missing IDs/duplicate completeness cannot be asserted. The saved v1 result (1,624 raw, 36 candidates, 35/35 matches, one extra JR2010985) is historical only. The adapter was not changed or bypassed.

Adobe: initial full two-pass listing found 463 jobs, but six detail requests exhausted retries with HTTP 429. The first attempt recorded 43 retry requests and six exhausted detail failures. That failed attempt is preserved as `adobe/crawl_attempt1.json`. The retry uses the existing `detail_workers=1` option only; persistent configuration, retrieval logic, and pagination are unchanged. Final status is recorded below.

### Anthropic

- Capture: 2026-09-30T15:55:56.105792+00:00 to 2026-09-30T15:55:58.109386+00:00.
- Status: success; requests: 1; source errors: []; detail failures/nonavailable checks: [].
- Retries: not separately exposed; pagination complete: see adapter telemetry (non-Workday).

### OpenAI

- Capture: 2026-09-30T15:55:56.112253+00:00 to 2026-09-30T15:55:57.101419+00:00.
- Status: success; requests: 1; source errors: []; detail failures/nonavailable checks: [].
- Retries: not separately exposed; pagination complete: see adapter telemetry (non-Workday).

### Microsoft

- Capture: 2026-09-30T15:55:56.114783+00:00 to 2026-09-30T16:03:43.099250+00:00.
- Status: success; requests: 83; source errors: [{"phase": "enumeration", "parameters": {"domain": "microsoft.com", "query": "", "location": "", "start": 0, "filter_profession": "product management"}, "attempt": 1, "at": "2026-09-30T15:55:56.114783+00:00", "http_status": 429, "error": "HTTPError: 429 Client Error: Too Many Requests for url: https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=&start=0&filter_profession=product+management"}]; detail failures/nonavailable checks: [].
- Retries: not separately exposed; pagination complete: see adapter telemetry (non-Workday).

### Adobe

- Capture: 2026-09-30T15:58:49.770911+00:00 to 2026-09-30T16:04:53.225976+00:00.
- Status: success; requests: 513; source errors: []; detail failures/nonavailable checks: [].
- Retries: 0; pagination complete: True.

### NVIDIA

- Capture: 2026-09-30T15:55:56.120029+00:00 to 2026-09-30T15:56:09.616818+00:00.
- Status: failed; requests: 13; source errors: ["ValueError: Invalid Workday externalPath"]; detail failures/nonavailable checks: [].
- Retries: 0; pagination complete: False.

### CrowdStrike

- Capture: 2026-09-30T15:55:56.126455+00:00 to 2026-09-30T15:56:35.857513+00:00.
- Status: success; requests: 247; source errors: []; detail failures/nonavailable checks: [].
- Retries: 0; pagination complete: True.

## Human review

Review the NVIDIA malformed-source failure before any future adapter change. Review remaining benchmark misses against source drift and review extras without assuming filter defects. NVIDIA JR2010985 and CrowdStrike R28919 remain valid PM-family signals and need no filter change. No reference changes beyond the explicitly approved Adobe correction were made. Full summaries, raw jobs, candidates, missing IDs, extras, original failure, and telemetry are under `data/evals/pm_family_v2/`.
