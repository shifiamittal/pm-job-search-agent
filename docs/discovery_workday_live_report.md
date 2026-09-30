# Workday adapter live evaluation

Evaluated on 2026-09-30. Changes are uncommitted for review. No push was made.

## Architecture and independence

One adapter, `scripts/discovery/workday.py`, serves every configured tenant/site.
It performs CXS POST enumeration, two-pass listing consistency checks, count and
terminal-page validation, duplicate protection, concurrent GET detail retrieval,
normalization, and source-only telemetry. The discovery runner invokes the shared
PM title filter only after raw extraction. The adapter contains no company branches
or benchmark dependencies. Full HTML descriptions and every detail location are
preserved alongside the existing plain-text and joined-location fields.

All live runs retrieved **all jobs in the independently configured US/India source
scope**, with empty search text and no Product Management facet. They did not reuse
the earlier `product` search candidate lists. The counts below are scoped all-job
counts, not global board totals.

References entered only after raw retrieval and existing PM filtering:

| Company | Reference input | Rows | SHA-256 |
| --- | --- | --- | --- |
| Adobe | C:\Users\shifi\OneDrive\Documents\ChatGPT\pm-job-search-agent\data\evals\workday\adobe_product_management_snapshot.jsonl | 38 | 73d0f07b6dca914a6a6defb153043b95fe60f431db7b644e5090fae7c038ccd5 |
| NVIDIA | C:\Users\shifi\Downloads\nvidia_pm_candidate_review.xlsx — sheet Likely PM | 35 | ea55d92153d6f4275824493b750088cf470036ea2b0d5ba333e451b64c174429 |
| CrowdStrike | C:\Users\shifi\Downloads\crowdstrike_pm_candidate_review.xlsx — sheet Likely PM | 10 | 9815c5d484c2fc2114f3c562ebc6af28c54ef7cf8d50d96a6ef7d183ab44df72 |

The NVIDIA and CrowdStrike inputs are the independently prepared **Likely PM**
worksheets (35 and 10 rows), not the earlier 1,349- and 163-row broad snapshots.
Adobe uses the independent 38-row official-facet snapshot. All input hashes were
rechecked after evaluation; no reference files were modified or regenerated.

## Results

| Company | Raw jobs | PM candidates | PM benchmark matches | PM recall | Raw benchmark matches | Extras for review | Duplicate IDs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Adobe | 463 | 41 | 36/38 | 94.74% | 38/38 | 5 | 0 |
| NVIDIA | 1624 | 36 | 35/35 | 100.00% | 35/35 | 1 | 0 |
| CrowdStrike | 221 | 11 | 10/10 | 100.00% | 10/10 | 1 | 0 |

All benchmark IDs were retrieved in raw output. Adobe's two misses occur in the
unchanged title filter. NVIDIA and CrowdStrike have no missing benchmark IDs.
Extra candidates are unreviewed results, **not presumed false positives**.

### Missing candidate benchmark IDs

| Company | ID | Exact reference title | Failure stage |
| --- | --- | --- | --- |
| Adobe | R171808 | Senior Manager, Digital Monetization Growth | title_filter |
| Adobe | R171889 | Venture Lead, Creator Services - Adobe Incubator | title_filter |

Both Adobe titles lack the title signals recognized by the existing broad PM filter.
No new patterns or company-specific exceptions were added to increase recall.

### Extra candidates for human review

| Company | ID | Exact title | Official URL |
| --- | --- | --- | --- |
| Adobe | R168909 | Senior Product Manager,  Chief Accounting Office | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager---Chief-Accounting-Office_R168909-1 |
| Adobe | R169439 | Internal Product Manager 3 - Sales Performance Management | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Bangalore/Product-Manager-3_R169439 |
| Adobe | R169992 | Principal Product Manager - Order to Cash Platform (SAP BRIM) | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager---Order-to-Cash-Platform--SAP-BRIM-_R169992 |
| Adobe | R170043 | Product Manager - International Strategy & Product Management | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager_R170043-1 |
| Adobe | R171158 | Internal Product Manager 5 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Internal-Product-Manager-5_R171158 |
| NVIDIA | JR2010985 | Senior Silicon and System Product Lead | https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Silicon-and-System-Product-Lead_JR2010985 |
| CrowdStrike | R28919 | Sr. Manager, AI Product Owner, GTM Applications (Remote) | https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers/job/USA---Remote-AZ/Sr-Manager--AI-Product-Owner--GTM-Applications--Remote-_R28919 |

## Pagination and request quality

| Company | Source count | Pages per pass | Final in-range rows | Terminal probe | Duplicate listing paths | HTTP attempts | Retries | Source failures | Detail failures |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Adobe | 463 | 24 | 3 | count_and_repeated_probe | 0 | 513 | 0 | 0 | 0 |
| NVIDIA | 1624 | 82 | 4 | count_and_repeated_probe | 0 | 1790 | 0 | 0 | 0 |
| CrowdStrike | 221 | 12 | 1 | count_and_repeated_probe | 0 | 247 | 0 | 0 | 0 |

For each company, two complete passes produced identical unique listing paths and
the same source count. All terminal probes reset to already-seen results; none was
treated as new work. The final partial pages, source-count equality, unique IDs,
and repeated-pass consistency establish completeness for the configured query.
Every listing's detail was retrieved and normalized. There were no source or
detail failures and no silent partial exports. All source-reported counts are
below the adapter's conservative 2,000-result-cap guard.

| Company | Crawl start UTC | Crawl completion UTC |
| --- | --- | --- |
| Adobe | 2026-09-30T13:44:53.287691+00:00 | 2026-09-30T13:46:34.747527+00:00 |
| NVIDIA | 2026-09-30T13:44:52.676162+00:00 | 2026-09-30T13:51:22.759289+00:00 |
| CrowdStrike | 2026-09-30T13:44:50.272565+00:00 | 2026-09-30T13:45:43.431524+00:00 |

## Tests and regression protection

- Baseline before changes: **89 tests passed**.
- Final suite: **109 tests passed** using `.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py'`.
- New tests: **17 adapter/integration tests** in `scripts/test_workday.py` and **3 evaluation tests** in `scripts/test_eval_workday.py`.
- Coverage includes count/reset pagination, continuation zero totals, unknown-count
  exhaustion, early repeated pages, count drift, repeated-pass mismatch, max-page
  guard, possible result caps, malformed responses, retry/exhaustion, failed detail
  withholding, stable IDs, duplicate aliases/conflicts, exact raw HTML, multiple
  locations, canonical URLs, missing dates, source-config forwarding, listing/detail
  identity, dispatcher integration, prior-snapshot preservation, reference
  separation, raw-versus-filter recall, and stale/invalid evaluation handling.
- Existing suites pass: discovery/Greenhouse **17**, Ashby **12**, Microsoft **20**.
  Those adapters and `scripts/discovery/filters.py` have no file changes.
- Final saved outputs were revalidated against the shared raw schema, unique IDs,
  source counts, complete raw descriptions, location JSON, and the unchanged PM
  filter for every row. Benchmark hashes still match.
- During final review, the listing/detail posting-slug guard was added after the
  full live runs began. Its focused test passed and a fresh official listing/detail
  pair from each of the three companies passed the final normalizer (six extra
  HTTP requests, separate from the crawl counts above). The complete crawl was
  not repeated solely for that guard. Evaluation failure-reporting improvements
  were verified with synthetic tests after the live runs began.
- `git diff --check` passed. No existing adapter regression was observed.

## Files changed or added

| File | Purpose |
| --- | --- |
| `scripts/discovery/workday.py` | Reusable CXS adapter |
| `scripts/discovery/models.py` | Workday source type and optional raw-description/location fields |
| `scripts/discover_jobs.py` | Workday dispatch; existing candidate logic unchanged |
| `config/job_sources.yaml` | Tenant/site and US/India source facet configuration |
| `scripts/eval_workday.py` | Independent live evaluation and review artifacts |
| `scripts/test_workday.py` | Adapter and runner tests |
| `scripts/test_eval_workday.py` | Evaluation isolation and failure tests |
| `README.md` | Workday entry points and documentation links |
| `docs/discovery_workday.md` | Architecture, schema, configuration, limitations |
| `docs/discovery_workday_live_report.md` | This report |
| `data/evals/workday/adapter/{adobe,nvidia,crowdstrike}/` | Per-company raw jobs, candidates, crawl telemetry, metrics, missing jobs, extras JSONL/CSV |

Existing benchmark files, source-detector work, production discovery files,
candidate/resume data, shortlist logic, and Google Sheets were not changed.

## Remaining issues and unsupported patterns

1. Adobe's two candidate-stage misses need a separate decision about the generic
   filter. They are not retrieval failures and were not patched for this benchmark.
2. Unpartitioned CXS searches reporting **2,000 or more** results fail conservatively
   because of potential source caps. Automatic exhaustive partitioning is not
   implemented. Use independently configured narrower facets; these evaluations
   cover all jobs in US/India, not the three global boards.
3. Authenticated or non-CXS portals and custom Workday proxy hosts are unsupported.
   Adobe's Phenom Profession facet is not available in its CXS search; full scoped
   CXS retrieval avoids needing that facet.
4. Repeated-page results without a count, unstable two-pass identity sets, missing
   full descriptions, missing requisition IDs, and conflicting duplicate IDs fail
   visibly. A live capture is not an atomic source snapshot.
5. The seven extra PM candidates require human review. Nothing marks them false
   positives, applies fit scoring, or changes the benchmark.
