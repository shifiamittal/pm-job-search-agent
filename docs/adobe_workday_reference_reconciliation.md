# Adobe Workday reference reconciliation

Capture: **2026-09-30T11:43:08.0943332Z** (UTC). Final complete-set check: **2026-09-30T11:43:41.9958478Z**.
This is a benchmark-construction snapshot for human review, not approved ground truth.

## Source and scope

- Official careers source: https://careers.adobe.com/us/en/search-results
- Verified Workday base: https://adobe.wd5.myworkdayjobs.com
- Tenant: `adobe`. Site: `external_experienced`. Both were read from the current Workday page configuration and confirmed through job details.
- Adobe Careers search is Phenom-backed. Its **Profession** facet, `profession = Product Management`, defines this universe. The separate **Teams** field is `category`; it is not the requested Product Management facet.
- Source-side countries: `country = [United States of America, India]` (OR within country, AND with profession). Empty keyword/subsearch. No title, seniority, experience-level, repository PM, or fit filters.
- Exact search endpoint used: **POST https://careers.adobe.com/widgets**, `ddoKey = refineSearch`. JSON response: `refineSearch.totalHits`, `hits`, `data.jobs`. Pagination: zero-based `from` and requested `size`.
- Workday CXS search mechanism verified: **POST https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs**, JSON `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`. Pagination uses `limit`/`offset`. Its public `jobFamilyGroup` facet contains broader categories, with no Product Management value. No guessed PM facet was used.
- Workday country facet names/IDs observed: `locationCountry`, United States of America `bc33aa3152ec42d4995f4791a106ed09`, India `c4f78be1a8f14da0ab49ce1162348a5e`. These were inspected, but the actual universe uses the careers country filters above.
- Workday detail validation: GET `https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced` + the job path from each official apply link. Canonical URLs use the returned `jobPostingInfo.externalUrl`.
- Initial all-job totals differed: Careers 547, Workday 552. This snapshot proves completeness for the exact official Careers Profession + geography universe, not identity between both all-job catalogs or every Workday PM-like title.

Exact successful full-response payload:

```json
{
  "lang": "en_us",
  "pageName": "search-results",
  "selected_fields": {
    "country": [
      "United States of America",
      "India"
    ],
    "profession": [
      "Product Management"
    ]
  },
  "sortBy": "Most recent",
  "counts": true,
  "from": 0,
  "ddoKey": "refineSearch",
  "jobs": true,
  "keywords": "",
  "subsearch": "",
  "country": "us",
  "deviceType": "desktop",
  "size": 100,
  "all_fields": [
    "profession",
    "country"
  ]
}
```

## Counts

| Measure | Count |
| --- | --- |
| Current source-reported Product Management + US/India result count | 38 |
| Exported unique requisition IDs | 38 |
| Earlier user-observed count | 46 |
| Net count drift relative to earlier observation | -8 |
| Prep rows / unique Adobe IDs | 28 / 28 |
| Already present in prep | 16 |
| Missing from prep | 22 |
| Prep absent from current filtered universe | 12 |
| Materially changed shared records | 1 |
| Changed exact titles / location sets / material URL targets | 0 / 1 / 0 |
| Nonmaterial URL representation differences | 10 |

Drift of -8 is only a count comparison. Without the earlier complete 46-ID set, it does not establish which eight postings changed. The 12 absent prep rows are absent from this exact filtered universe; absence alone does not prove closure, and no historical records were deleted.

## Pagination, validation, and errors

Enumeration is believed **complete for the stated source filter at capture time**.

- First paginated pass: offsets 0, 10, 20, 30, 40 with size 10 returned 10, 10, 10, 8, 0 rows. Every response reported 38, but only 36 distinct IDs were collected. Count-only pagination would have missed jobs.
- A second pass using the UI's `Most recent` sort value returned the same page sizes but only 34 distinct IDs. The source continued to return unstable ordering; the sort string was not treated as proof of deterministic ordering.
- Recovery: one response with `from=0,size=100` returned **38 rows and 38 unique IDs**, matching `totalHits=38`. A second full response returned the identical 38-ID set. An exact-end request at `from=38,size=100` returned zero rows while retaining total 38. Both smaller-page ID sets are subsets of the complete response.
- Careers UI independently showed **38 results** with Product Management, India, and United States of America selected.
- All 38 Workday detail responses matched their requisition IDs and exact careers titles; all 38 exposed `posted=true` and `canApply=true`.
- Every record has a source-exposed US or India location. R170403 has London as its primary location and New York as an additional location, so it remains included. No primary-country-only post-filter was applied.
- Directors, nonstandard titles, and the university role remain in the export because Adobe's facet included them. No repository PM filter was invoked.
- Request accounting: **64 scripted HTTP attempts: 63 completed HTTP responses and 1 local socket-denied attempt**. The successful responses comprise 1 Careers HTML, 1 Workday HTML, 1 Workday search/facet request, 1 incorrectly nested Careers payload, 1 corrected filtered probe, 10 small-page requests, 2 full-response requests, 1 exact-end request, 38 Workday job-detail requests, and 7 abbreviated-route equivalence checks. A separate web-tool page retrieval and browser verification were also used; browser asset/background request counts were not instrumented, so an exact all-tools network total is unavailable.
- Errors/retries: the first shell Careers GET was blocked by local network permissions and succeeded when retried with approved network access. One HTTP-200 exploratory request had incorrectly nested parameters and produced zero hits against the unfiltered total of 547; it was discarded and corrected. Two incomplete small-page passes were discarded in favor of the verified full responses. No HTTP failures occurred in the final capture or 38 detail checks. One local console print failed due to Windows character encoding and was rerun with escaped Unicode; file output uses UTF-8.

## Prep workbook and comparison method

Read-only input: `C:/Users/shifi/Downloads/adobe_workday_benchmark_prep_v1.xlsx`, worksheet **Adobe Benchmark Prep**, rows **2–29**, columns **A:I**. Other workbook instruction cells are reference content; the current user request controls scope.

SHA-256 before and after reading: `d72a85963310607001d173d9a5a52d5cd80d6bd6c122d7c1386f0879ce751364`. Workbook unchanged.

Join key: exact Adobe requisition ID. Exact titles were compared. Locations were compared as city sets after ignoring order and country/state expansions; the concatenated Frame.io addresses in R171116 were split at their country labels. This is comparison normalization only; exported source location strings remain unchanged. A location difference can reflect incomplete prep rather than a subsequent employer edit.

Seven prep Workday URLs omit the city path component. GET requests to the corresponding abbreviated CXS routes returned the same requisition ID and same canonical URL, so those are nonmaterial URL aliases. Locale prefixes also do not change identity. Three Adobe Careers URLs identify the same requisitions as the verified Workday links; portal choice is not counted as a material URL target change. These 10 literal URL differences are documented below, not silently discarded.

## A. Missing from prep — 22

| ID | Exact title / canonical source | All source locations |
| --- | --- | --- |
| R167714 | [Senior Growth Product Manager](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Lehi/Senior-Growth-Product-Manager_R167714-1) | Lehi, Utah, United States of America; San Jose, California, United States of America |
| R168742 | [Principal Product Manager - Firefly Foundry Studio](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Principal-Product-Manager---Firefly-Foundry-Studio_R168742) | San Francisco, California, United States of America; Seattle, Washington, United States of America; New York, New York, United States of America; San Jose, California, United States of America |
| R168905 | [Principal Product Manager, Research and AI - Data](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--Research-and-AI---Data_R168905) | San Jose, California, United States of America; New York, New York, United States of America; San Francisco, California, United States of America |
| R168906 | [Principal Product Manager, Research and AI - Foundations](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--Research-and-AI---Foundations_R168906-1) | San Jose, California, United States of America; New York, New York, United States of America; San Francisco, California, United States of America |
| R169989 | [Product Manager - Business Model Strategy](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Product-Manager---Business-Model-Strategy_R169989) | San Francisco, California, United States of America |
| R170048 | [Principal Product Manager, Adobe Express](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Principal-Product-Manager--Adobe-Express_R170048-1) | San Francisco, California, United States of America; Seattle, Washington, United States of America |
| R170140 | [Principal Product Manager, Lightroom Mobile AI Assistant & AI Tools](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--Lightroom-Mobile-AI-Assistant---AI-Tools_R170140-1) | San Jose, California, United States of America; San Francisco, California, United States of America |
| R170403 | [Principal Product Manager, 3P Embed Partnerships (Sports & Commercial)](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/London/Principal-Product-Manager--3P-Embed-Partnerships--Sports---Commercial-_R170403) | London, London, City of, United Kingdom; New York, New York, United States of America |
| R170555 | [Principal Product Manager, AI Brand Visibility](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--AI-Brand-Visibility_R170555) | San Jose, California, United States of America; San Francisco, California, United States of America |
| R170683 | [Principal Product Manager, Emerging Design Experiences](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--Emerging-Design-Experiences_R170683-1) | San Jose, California, United States of America; San Francisco, California, United States of America |
| R170742 | [Senior Product Manager, Growth](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager--Growth_R170742) | San Jose, California, United States of America |
| R170844 | [Senior Product Manager, Data Platform - Knowledge & Retrieval](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager--Data-Platform---Knowledge---Retrieval_R170844-1) | San Jose, California, United States of America |
| R171074 | [Principal Product Manager - AI for Engineering](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Seattle/Principal-Product-Manager---AI-for-Engineering_R171074) | Seattle, Washington, United States of America; New York, New York, United States of America; San Francisco, California, United States of America; San Jose, California, United States of America |
| R171088 | [Pro Design Principal Product Manager, Growth](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Pro-Design-Principal-Product-Manager--Growth_R171088) | San Jose, California, United States of America |
| R171115 | [Principal Product Manager, Frame.io](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Principal-Product-Manager--Frameio_R171115) | San Jose, California, United States of America; New York, New York, United States of America; San Francisco, California, United States of America |
| R171225 | [Director of Product Management, Adobe Lightroom Creative Pro](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Remote-California/Director-of-Product-Management--Adobe-Lightroom-Creative-Pro_R171225) | Remote, California, United States of America |
| R171377 | [Director Product Management (IC), GenAI Model Customization](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Director-Product-Management--IC---GenAI-Model-Customization_R171377-1) | San Francisco, California, United States of America; San Jose, California, United States of America |
| R171464 | [Principal Product Manager, Media Generation Experience](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Principal-Product-Manager--Media-Generation-Experience_R171464) | San Francisco, California, United States of America; San Jose, California, United States of America |
| R171542 | [Senior Product Manager, Privacy Engineering](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager--Privacy-Engineering_R171542) | San Jose, California, United States of America; San Francisco, California, United States of America |
| R171808 | [Senior Manager, Digital Monetization Growth](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Manager--Digital-Monetization-Growth_R171808-1) | San Jose, California, United States of America |
| R171889 | [Venture Lead, Creator Services - Adobe Incubator](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Venture-Lead--Creator-Services---Adobe-Incubator_R171889) | San Jose, California, United States of America; San Francisco, California, United States of America |
| R171900 | [2027 MBA University Graduate - Product Manager](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/XMLNAME-2027-MBA-University-Graduate---Product-Manager_R171900) | San Jose, California, United States of America; San Francisco, California, United States of America |

## B. Prep absent from current universe — 12

| ID | Prep title / URL | Prep location |
| --- | --- | --- |
| R163564 | [Senior Director, Product Management, AI Brand Experiences](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Senior-Director--Product-Management--AI-Brand-Experiences_R163564) | San Jose |
| R165397 | [Director, Product Management](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Director--Product-Management_R165397) | San Jose \| Seattle \| San Francisco |
| R166263 | [Sr. Director, Product Management AI Platforms (AEP)](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Sr-Director--Product-Management-AI-Platforms--AEP-_R166263-2) | San Jose |
| R166319 | [Dir, Product Management Business Applications](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Dir--Product-Management-Business-Applications_R166319) | San Jose |
| R169439 | [Internal Product Manager 3 - Sales Performance Management](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Bangalore/Product-Manager-3_R169439) | Bangalore |
| R170010 | [Product Manager - Global Insights & Growth Strategies](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Product-Manager---Global-Insights---Growth-Strategies_R170010-1) | San Jose |
| R170043 | [Product Manager - International Strategy & Product Management](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager_R170043-1) | San Jose \| San Francisco |
| R170311 | [Sr. Director, Product Management - Data Platforms](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Sr-Director--Product-Management---Data-Platforms_R170311) | San Jose |
| R170777 | [Product Manager](https://careers.adobe.com/us/en/job/R170777/Product-Manager) | Noida, Uttar Pradesh, India |
| R170985 | [Product Manager - International Strategy](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Product-Manager---International-Strategy_R170985) | San Jose \| San Francisco |
| R171155 | [Senior Product Manager](https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Senior-Product-Manager_R171155) | San Jose |
| R171407 | [Product Manager (Growth - B2B Enterprise)](https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Bangalore/Product-Manager--Growth---B2B-Enterprise-_R171407) | Bangalore |

## C. Materially changed shared records — 1

| ID | Field | Prep | Current official source |
| --- | --- | --- | --- |
| R171312 | All locations | San Francisco, California, United States of America | San Francisco, California, United States of America; San Jose, California, United States of America |

R171312, **Senior Product Manager, Creative Agents**, additionally exposes San Jose. Exact title is unchanged. This is a confirmed difference from prep, not proof of when Adobe added the location.

### Nonmaterial URL aliases — 10

| ID | Prep URL | Verified canonical Workday URL | Reason not counted as material |
| --- | --- | --- | --- |
| R165611 | https://careers.adobe.com/us/en/job/R165611/Director-Product-Manager | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Group-Product-Manager--Manager-Product-Management_R165611-1 | Adobe Careers and Workday representations of same requisition |
| R167941 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Senior-Product-Manager_R167941 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Noida/Senior-Product-Manager_R167941 | Abbreviated Workday route resolves to same ID and canonical URL |
| R169401 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Senior-Product-Manager_R169401 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Senior-Product-Manager_R169401 | Abbreviated Workday route resolves to same ID and canonical URL |
| R169714 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Principal-Product-Manager--Adobe-Express_R169714-1 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Seattle/Principal-Product-Manager--Adobe-Express_R169714-1 | Abbreviated Workday route resolves to same ID and canonical URL |
| R170115 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Senior-Product-Manager--Adobecom-for-business_R170115 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Lehi/Senior-Product-Manager--Adobecom-for-business_R170115 | Abbreviated Workday route resolves to same ID and canonical URL |
| R170204 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Product-Manager_R170204 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Product-Manager_R170204 | Abbreviated Workday route resolves to same ID and canonical URL |
| R170346 | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/Director-of-Product-Management---Adobe-Builders-eXperience--ABX-_R170346-1 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Director-of-Product-Management---Adobe-Builders-eXperience--ABX-_R170346-1 | Abbreviated Workday route resolves to same ID and canonical URL |
| R171116 | https://careers.adobe.com/us/en/job/R171116/Senior-Product-Manager-Frame-io | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Product-Manager--Frameio_R171116 | Adobe Careers and Workday representations of same requisition |
| R171141 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Director-Product-Management--Firefly-Foundry_R171141 | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Director-Product-Management--Firefly-Foundry_R171141 | Abbreviated Workday route resolves to same ID and canonical URL |
| R171312 | https://careers.adobe.com/us/en/job/R171312/Senior-Product-Manager-Creative-Agents | https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Senior-Product-Manager--Creative-Agents_R171312 | Adobe Careers and Workday representations of same requisition |

## Artifacts and scope preservation

- `data/evals/workday/adobe_product_management_snapshot.csv`: 38 records; arrays serialized as JSON within CSV cells.
- `data/evals/workday/adobe_product_management_snapshot.jsonl`: the same 38 records, with exact search payload, original Careers record, and original Workday jobPostingInfo retained per record for audit.
- `posted_date` preserves the Careers timestamp; `workday_posted_date` preserves Workday's startDate. Neither is estimated. `source_facet_value` records query membership because individual search records do not expose a profession field; `source_category` preserves the separate Teams value.
- No production output, classification, candidate profile, adapter, source mapping, PM filter, Google Sheet, or prep workbook was changed. No discovery eval was run. No commit or push was made.
- No repository code was touched; the temporary extraction/reconciliation script stayed outside the repository. No test-suite run was required. Validation checked counts, unique IDs, repeated full-set equality, source exhaustion, all 38 detail identities, geography inclusion, reconciliation set identities, CSV/JSONL equivalence, and the input workbook hash.
