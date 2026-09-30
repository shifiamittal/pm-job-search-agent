# CrowdStrike Workday reference capture

## Result and scope

**163 unique official jobs exported and verified.** This is a **broader candidate universe**, not PM-only ground truth: CrowdStrike's public Workday facets do not expose a Product Management family. The fallback is the official **`product` keyword search AND (United States of America OR India)**, with no job-family restriction. All matches are retained, including engineering, sales, marketing, and other non-PM roles.

The snapshot is authoritative for membership in that source query. It does not establish that all rows are PM roles or certify semantic PM-family coverage for roles the keyword engine does not match. Independent human review is needed before treating it as a PM-only benchmark. No repository PM filter or local title-based exclusion was applied.

Capture began: **2026-09-30T13:18:40.688021+00:00**. Detail verification ended: **2026-09-30T13:19:19.167693+00:00** (UTC). This is a bounded capture interval, not an atomic database snapshot.

## Official source and tenant

- Official landing page: https://www.crowdstrike.com/en-us/careers/ — its View job postings link points to the Workday site below.
- Workday base: https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers
- Tenant **`crowdstrike`**, site **`crowdstrikecareers`**, verified in the current Workday page configuration.
- Search: **POST https://crowdstrike.wd5.myworkdayjobs.com/wday/cxs/crowdstrike/crowdstrikecareers/jobs**.
- Body: `appliedFacets`, `searchText`, `limit`, `offset`. Response: `total`, `jobPostings`, `facets`.
- Details: **GET https://crowdstrike.wd5.myworkdayjobs.com/wday/cxs/crowdstrike/crowdstrikecareers** + the official listing's `externalPath`.
- Canonical URLs are the detail source's `jobPostingInfo.externalUrl`. Requisition ID, title, primary location, additional locations, and date are read from `jobReqId`, `title`, `location`, `additionalLocations`, and `startDate` respectively. Relative posted labels are preserved separately, never converted to estimated dates.

## Facet inspection and universe definition

The source exposes `Job_Family` (Job Family), `workerSubType` (Job Type), `locationCountry` (Location Country), and `locations` (Locations). The full Job Family list returned during inspection was:

| Official family | ID |
| --- | --- |
| Product Engineering | cb19f044639b1001f6a02595bc920000 |
| Sales | 1408861ee6e2017e954d08f7b000f40b |
| Professional Services | 1408861ee6e201dd8f7601f7b000f00b |
| Engineering | 1408861ee6e201641be2c2f6b000c00b |
| Information Technology | 1408861ee6e20197f95adbf6b000d20b |
| Services | 1408861ee6e201df327f0ff7b000fa0b |
| Finance | 1408861ee6e201d8b5decef6b000ca0b |
| Intelligence | 1408861ee6e201d67af3e0f6b000d60b |
| Marketing | 1408861ee6e20177a63efbf6b000ec0b |
| Human Resources | 1408861ee6e20164b2b5d4f6b000ce0b |
| Customer Support | 1408861ee6e201739a99bbf6b000bc0b |
| Administration | 1408861ee6e201d4db6ea7f6b000ae0b |
| Legal | 1408861ee6e201ed65abf4f6b000e60b |
| Intern | 1408861ee6e2015adbe3e7f6b000de0b |
| Facilities | 1408861ee6e201e6d8ddc8f6b000c60b |

No Product Management value was returned. **Product Engineering is not a clean Product Management facet**; selecting it would impose an unverified family restriction and could exclude PM roles elsewhere. It was not used.

Country filter values, both verified in the source facets:

| Country | locationCountry ID |
| --- | --- |
| United States of America | bc33aa3152ec42d4995f4791a106ed09 |
| India | c4f78be1a8f14da0ab49ce1162348a5e |

The single-word `product` query is the broad product-oriented fallback. Narrower exploratory queries with the same geography returned 62 (`product manager`) and 104 (`product management`); both also included non-PM titles. The selected query returned 163. Those query counts were not added together or described as PM-only counts. No category, level, seniority, job type, or fit restriction was applied.

Exact request at offset zero:

```json
{
  "appliedFacets": {
    "locationCountry": [
      "bc33aa3152ec42d4995f4791a106ed09",
      "c4f78be1a8f14da0ab49ce1162348a5e"
    ]
  },
  "limit": 20,
  "offset": 0,
  "searchText": "product"
}
```

Country selections are OR within the source facet and combined with the keyword search. All exposed locations of matching jobs are retained, including any outside the target countries; no primary-country-only post-filter was used.

## Completeness and verification

| Check | Result |
| --- | --- |
| Source count, first pass | 163 |
| Source count, repeated pass | 163 |
| Exported records / unique requisition IDs | 163 / 163 |
| Duplicate IDs | 0 |
| Pages per complete pass | 9 |
| Offsets | 0 through 160, step 20 |
| Final in-range page size | 3 |
| Repeated-pass ID differences | 0 |
| Detail responses verified | 163 |
| Requisition ID mismatches | 0 |
| Detail posted=true | 163 |
| Detail canApply=true | 163 |
| Detail request failures | 0 |
| Missing explicit US/India detail location | 0 |
| CSV/JSONL field equivalence | Passed for every row |

Pagination: the API uses zero-based `offset` and `limit=20`. Subsequent pages expose `total=0`; the first-page total is the count control. At offset 163, the source **reset to the first 20 results, exactly matching page zero**. Completeness is supported by the final partial page, unique IDs equal to the source count, and an independent repeat of every in-range page yielding the identical set. Out-of-range results were not appended to the export.

Detail location memberships: `{'United States of America': 139, 'India': 24}`. Jobs can have both countries.

**Enumeration is believed complete for the documented official search and country filters at capture time.** A pure PM-only universe cannot be claimed from this broad keyword source. No prior employer reference set, aggregator, fit score, or resume logic influenced membership.

## Errors, retries, and requests

- Capture requests: **182 logical HTTP requests**, **182 HTTP attempts**, **0 retries**, **0 recorded HTTP/transport errors**. These comprise two complete paginated passes, one out-of-range probe, and 163 detail lookups.
- Preliminary scripted requests: **5 successful requests** (Workday HTML, unfiltered facets, three keyword probes). Total scripted HTTP attempts: **187**. One separate web-tool read of the official careers landing page is excluded from that scripted total.
- Recorded errors: `[]`.
- No repository code was modified and no dependencies were installed. Temporary scripts used Python's standard-library HTTP client. The pagination behavior was checked against this employer's returned responses.

## Detail exceptions

None. All IDs, listing/detail titles, posted/applicable flags, and explicit US/India locations passed validation.

## Artifacts and preservation

- `data/evals/workday/crowdstrike_product_management_snapshot.csv`: 163 rows, with JSON-encoded arrays and facet maps in CSV cells.
- `data/evals/workday/crowdstrike_product_management_snapshot.jsonl`: the same 163 records plus exact request, raw search record, and raw Workday detail record for audit.
- `retrieved_at` records listing retrieval; `detail_retrieved_at` records per-job verification. `posted_date` preserves the exact source date; an empty value means unavailable.
- Only the requested CSV, JSONL, and this report were created in the repository. Existing Adobe/NVIDIA snapshots and other untracked work were preserved. No adapter, Greenhouse, Ashby, Microsoft, Workday production code, PM filter, production discovery output, classification, resume logic, or Google Sheet was changed.
- No discovery eval, commit, or push. No repository code changes required a test-suite run. Structural validation covered every exported record and both complete listing passes.
