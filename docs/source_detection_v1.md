# Source detection v1: benchmark results

Implemented detection/evaluation only. No adapters, production source configuration,
job-discovery outputs, approved job benchmarks or downstream classification were modified.
The user approved the source detector and the two source-map corrections described below.

## Results

Capture: 2026-09-23T11:09:56.561867+00:00 to 2026-09-23T11:10:58.360829+00:00 (UTC).
Final capture inspected 98 documents with 98 request attempts (redirect hops are recorded separately).

| Metric | Result |
|---|---:|
| Companies | 25 |
| High-confidence source-type accuracy | 14/20 (70.00%) |
| Overall source-type agreement | 17/25 (68.00%) |
| Identifier accuracy (compatible) | 11/11 (100.00%) |
| Identifier accuracy (exact normalized) | 9/11 (81.82%) |
| Unknown rate | 8/25 (32.00%) |
| Existing-adapter family coverage | 10/25 (40.00%) |
| Family plus identifier ready | 9/25 (36.00%) |

Identifier comparison includes only the 11 rows with non-empty expected and
detected identifiers. Two Workday benchmark values specify only a tenant or site:
Adobe `adobe` matches `adobe/external_experienced`; NVIDIA `NVIDIAExternalCareerSite`
matches `nvidia/NVIDIAExternalCareerSite`. Both count as compatible, not exact.
Microsoft `microsoft.com / pcsx` is explicitly normalized to `microsoft.com`.
The 14 missing/unverified identifiers are excluded from that denominator and
listed in summary.json. They are not identifier successes.

Adapter coverage measures the family only; it does not prove a successful live job
crawl. Stripe has Greenhouse metadata but no verified board token, so only nine
companies have both family support and an identifier. OpenAI is unresolved in
this independent detector because its entry page returned 403; its existing Ashby
integration is unchanged. Unknown detections are not evidence that an ATS is absent.

## Unsupported companies grouped by detected source

| Type | Count | Companies |
|---|---:|---|
| workday | 2 | Adobe, NVIDIA |
| lever | 0 | - |
| rippling | 0 | - |
| company_native_custom | 5 | Google, Meta, Amazon, Apple, Atlassian |
| unknown | 8 | OpenAI, Databricks, Uber, Dropbox, Salesforce, Rippling, Perplexity, xAI |

## Every mismatch / unresolved detection

| Company | Expected | Detected | Benchmark confidence | Evidence and assessment |
|---|---|---|---|---|
| OpenAI | ashby (openai) | unknown (-) | High | [Entry page](https://openai.com/careers/) returned HTTP 403; detector access limitation, not evidence the benchmark is wrong. |
| Databricks | greenhouse (databricks) | unknown (-) | Medium | [Entry page](https://www.databricks.com/company/careers) and 4 linked documents yielded no reliable ATS signal within the cap; detector limitation, benchmark remains unverified. |
| Uber | company_native_custom (Uber Careers) | unknown (-) | High | [Entry page](https://www.uber.com/global/en/careers/list/) returned HTTP 406; detector access limitation, not evidence the benchmark is wrong. |
| Dropbox | company_native_custom (Dropbox Jobs) | unknown (-) | High | [Entry page](https://jobs.dropbox.com/) returned HTTP 403; detector access limitation, not evidence the benchmark is wrong. |
| Salesforce | company_native_custom (Salesforce Careers) | unknown (-) | High | [Entry page](https://careers.salesforce.com/en/jobs/) and 7 linked documents yielded no reliable ATS signal within the cap; detector limitation, benchmark remains unverified. |
| Rippling | rippling (rippling) | unknown (-) | High | [Entry page](https://www.rippling.com/careers) and 7 linked documents yielded no reliable ATS signal within the cap; detector limitation, benchmark remains unverified. |
| Perplexity | ashby (perplexity) | unknown (-) | High | [Entry page](https://www.perplexity.ai/careers) returned HTTP 403; detector access limitation, not evidence the benchmark is wrong. |
| xAI | company_native_custom (xAI Careers) | unknown (-) | Low | [Entry page](https://x.ai/careers) returned HTTP 403; detector access limitation, not evidence the benchmark is wrong. |

## Approved benchmark corrections

Only two benchmark rows were corrected with user approval:

- Airbnb: `Greenhouse`, identifier `airbnb`, adapter available `Yes`.
  Its [official job page](https://careers.airbnb.com/positions/8184174/) exposes
  [the Greenhouse board embed](https://boards.greenhouse.io/embed/job_board/js?for=airbnb).
- Snowflake: `Ashby`, identifier `snowflake`, adapter available `Yes`.
  Its [official careers search](https://careers.snowflake.com/us/en/search-results)
  exposes `jobs.ashbyhq.com/snowflake` postings.

Both retain High confidence and now MATCH on the fresh live rerun. Source URLs and
all other benchmark rows are unchanged. Eight UNKNOWN results remain; there are
no resolved source-type or identifier disagreements. No detector logic was changed
for these corrections.

## Medium/Low benchmark review and proposed corrections

No Medium/Low row has a conflicting stronger direct provider detection warranting
a proposed label correction. Meta and Atlassian agree at the custom-front-end
level but their backends/identifiers remain unresolved. Stripe agrees on Greenhouse
using repeated typed `greenhouseId` listing metadata; its token remains blank.
Databricks (Medium) and xAI (Low) are unresolved. All five remain review cases.

## Implementation and limits

- Detector inputs are only company (display label) and careers URL. There is no
  company-name lookup, benchmark-label seeding, LLM inference, registry write or job crawl.
- Exact provider domains and path patterns support Greenhouse, Ashby, Workday,
  Lever, Rippling and Microsoft. Provider links may be found after redirects,
  on a job page, in structured metadata, or in a public linked script.
- Maximum 12 documents: at most six pages and six scripts, each at most 6 MB.
  Fetches have 20-second request timeouts and at most one transient retry.
  403/406 responses are not retried or bypassed. Query/locale variants deduplicate.
- HTML base URLs and literal module imports are respected. No guessed board tokens,
  guessed public API endpoints or full job-board enumeration are used.
- High confidence requires a direct provider URL plus an unambiguous identifier.
  Medium covers unresolved identifiers, structured source IDs or a custom search
  surface. Unknown uses low confidence. Conflicting providers remain unknown.
- A provider URL identifies its family/configuration, not current job availability.
  A custom/native classification describes the observed careers interface only;
  the underlying ATS may still exist behind client-side rendering or an apply flow.
- Unsupported rendered application behavior is a real limit: Databricks, Salesforce
  and Rippling were reachable but unresolved. OpenAI, Uber, Dropbox, Perplexity and
  xAI returned access errors. No browser automation or search-engine fallback is used.
- Evidence retains URLs, response status, redirects, body hashes and capture times;
  full page bodies/cookies/session data are not saved in the repository.

## Benchmark preservation

The original downloaded CSV is untouched. The repository benchmark differs only
in the two user-approved rows above (type, identifier, adapter availability and
evidence notes). The runner does not rewrite it. Type spelling aliases are
normalized only in evaluation output.
Corrected benchmark SHA-256: `c08158276fe77b66af7266b6f554fa906adc8cf812c709ff96363109b83ca057`.

## Tests

**83 total, 83 passed, 0 failed, 0 observed regressions**: 67 existing tests plus
16 focused source-detection tests. Coverage includes all six ATS URL families,
custom/unknown fallbacks, identifier extraction, confidence, ambiguous providers,
blocked content, script/redirect evidence, base URLs, bounded traversal, query/locale
deduplication, partial Workday identifiers and benchmark isolation/preservation.
`git diff --check` passed.

## Recommendation

Build **Workday** next: it adds two directly identified unsupported companies,
Adobe and NVIDIA, increasing family coverage from 10/25 to 12/25 (40% to 48%).
Custom/native combines five distinct interfaces and is not one reusable adapter.
No Lever or Rippling family was directly verified in this run; eight unknown
companies should be investigated before projecting additional coverage.

## Files added/modified

- Modified: `README.md`
- Added: `scripts/discovery/source_detection.py`
- Added: `scripts/detect_sources.py`
- Added: `scripts/test_source_detection.py`
- Added: `data/evals/source_detection/target_company_source_map_v1.csv`
- Added: `data/evals/source_detection/latest/results.csv`
- Added: `data/evals/source_detection/latest/summary.json`
- Added: `data/evals/source_detection/latest/mismatches.csv`
- Added: `data/evals/source_detection/latest/evidence.jsonl`
- Added: `docs/source_detection_v1.md`

Run: `python scripts/detect_sources.py --benchmark data/evals/source_detection/target_company_source_map_v1.csv`.
