# NVIDIA Workday reference capture

## Result and benchmark boundary

**1,349 unique official Workday records exported and detail-verified.** This is the complete **broad source-side `product` search + United States/India universe** captured below. It is **not a verified PM-only reference set**. NVIDIA exposes no clean Product Management category in the inspected public search facets. The requested filenames preserve the task naming, and each row explicitly labels the broad-universe definition.

The keyword engine returns engineering, marketing, production, and other roles, including jobs whose titles are not PM-family titles. All matches were retained. No repository PM filter, custom title-based exclusion, seniority exclusion, fit score, or downstream classification was applied. The snapshot is source-authoritative for membership in this query; semantic PM-family ground truth still requires independent human review. Exhaustive coverage of PM roles not matched by the source's `product` keyword cannot be certified.

Capture began: **2026-09-30T12:27:09.544681+00:00**. Detail verification completed: **2026-09-30T12:34:04.966645+00:00**. Timestamps are UTC; capture is a bounded live interval, not an atomic database transaction.

## Official source identification

- NVIDIA careers landing page: https://www.nvidia.com/en-us/about-nvidia/careers/ links to https://jobs.nvidia.com/careers.
- The current careers site links to `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/login`. The Workday landing-page configuration explicitly declares tenant **`nvidia`**, site **`NVIDIAExternalCareerSite`**.
- Base site: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
- Structured search: **POST https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs**.
- Search body fields: `appliedFacets`, `searchText`, `limit`, `offset`. Response fields: `total`, `jobPostings`, `facets`.
- Individual verification: **GET https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite** + each official search record's `externalPath`.
- Canonical URL comes from detail `jobPostingInfo.externalUrl`; requisition ID from `jobReqId`; exact title from `title`; primary/additional locations from `location` and `additionalLocations`; posted date from `startDate`. No dates were inferred from relative labels.

## Universe definition and facets

The broadest product-oriented query inspected was the single source-side keyword **`product`**, with the official geography facet **`locationHierarchy1`**:

| Facet label | Facet ID |
| --- | --- |
| India | 2fcb99c455831013ea52b82135ba3266 |
| United States | 2fcb99c455831013ea52fb338f2932d8 |

Both values are supplied together in the same geography facet. No job category, job type, time type, location type, or seniority restriction was added. Jobs matching through any source-exposed US/India location remain included; primary-location-only filtering was not used. All other locations exposed on matching jobs are preserved.

Exact first-page request:

```json
{
  "appliedFacets": {
    "locationHierarchy1": [
      "2fcb99c455831013ea52b82135ba3266",
      "2fcb99c455831013ea52fb338f2932d8"
    ]
  },
  "limit": 20,
  "offset": 0,
  "searchText": "product"
}
```

The Workday Job Category (`jobFamilyGroup`) values were:

| Source category | Source ID |
| --- | --- |
| Engineering | 0c40f6bd1d8f10ae43ffaefd46dc7e78 |
| Sales | 0c40f6bd1d8f10ae43ffcac5bbec7e90 |
| Operations | 0c40f6bd1d8f10ae43ffc3fc7d8c7e8a |
| Univ Employment | 0c40f6bd1d8f10ae43ffda1e8d447e94 |
| Program Manager | 0c40f6bd1d8f10ae43ffc668c6847e8c |
| Marketing | 0c40f6bd1d8f10ae43ffc19725ec7e88 |
| IT - Information Technology | 0c40f6bd1d8f10ae43ffbd1459047e84 |
| Research | 0c40f6bd1d8f10ae43ffc8817cf47e8e |
| Professional Services | e8bdc341a93101bd5f4d2b0a1c005e36 |
| Finance | 0c40f6bd1d8f10ae43ffb5dd06f47e7e |
| Human Resources | 0c40f6bd1d8f10ae43ffbac3680c7e82 |
| Business Development | 0c40f6bd1d8f10ae43ffac5fdfac7e76 |
| Legal | 0c40f6bd1d8f10ae43ffbf4412147e86 |
| Facilities | 0c40f6bd1d8f10ae43ffb3a6aaac7e7c |

**Program Manager is not Product Management** and was not substituted for it. NVIDIA's official careers UI also exposes these broad job categories, plus Job Title, Location Type, Job Type, Skills, and Time Type filters. Its Job Title filter selects individual titles, not a comprehensive PM family, so no handpicked list of title values was treated as an authoritative family facet.

Exploratory source counts with the same US/India geography:

| Search text | Reported count | Observation |
| --- | --- | --- |
| product | 1349 | Selected broad fallback |
| product manager | 753 | Includes non-PM results |
| product management | 753 | Includes non-PM results |
| "product manager" | 753 | Quotes did not isolate an exact PM-only phrase |
| "product management" | 753 | Quotes did not isolate an exact PM-only phrase |
| "product lead" | 1002 | Includes engineering/product security roles |
| "product owner" | 174 | Includes production and quality roles |

These counts describe separate source queries, not independent PM populations. They were not summed. The 1,349 count is not presented as NVIDIA's number of Product Managers. No Google, LinkedIn, aggregator, candidate profile, or earlier employer benchmark supplied membership or job facts.

## Completeness and detail verification

| Check | Result |
| --- | --- |
| Source-reported count at first-page capture | 1349 |
| Rows in first enumeration | 1349 |
| Unique IDs exported | 1349 |
| First-pass pages | 68 |
| Page offsets | 0 through 1340, step 20 |
| Final in-range page size | 9 |
| Duplicate IDs in first enumeration | 0 |
| Independent second-pass rows / unique IDs | 1349 / 1349 |
| IDs differing between full passes | 0 |
| Detail requisition IDs matched | 1349 |
| Detail posted=true | 1349 |
| Detail canApply=true | 1349 |
| Detail verification failures | 0 |
| Rows missing an explicit detail US/India location | 0 |
| CSV / JSONL records agree | True |

Workday reports `total=0` on later pages; the first-page total is the count control. A request at offset 1349 returned the first 20 records again, exactly matching page zero, with total 1349. **It did not return an empty page.** Exhaustion is established by the final partial page (9 rows at offset 1340), unique-ID count equal to the first-page total, and a second exhaustive pass yielding the identical ID set. No loop followed the out-of-range reset.

Location membership counts from detail fields (a job can belong to both): {'United States': 1157, 'India': 192}.

Enumeration is believed **complete for the documented source query and geography**, subject to live-source changes after capture. No stronger claim of a pure or exhaustive semantic PM family is made without a clean facet or subsequent independent review.

## Errors, retries, and request accounting

- Capture/verification HTTP attempts: **1486**, across **1486** logical requests. Status counts: `{200: 1486}`. Transport/HTTP errors recorded: **0**. Automatic retries: **0**.
- Before capture: **11 successful scripted exploratory requests** (two Careers HTML reads, one Workday HTML read, one unfiltered Workday facet query, seven keyword probes). Total scripted attempts including exploration: **1497**. One web-tool landing-page read and browser filter inspection also occurred; browser asset/background requests were not instrumented and are excluded from this scripted total.
- Temporary-script setup initially failed because the bundled Python lacked `requests`; it was changed to the standard-library HTTP client without installing anything. No network requests were issued by that failed launch.
- Two local completeness assertions exposed Workday's `total=0` continuation behavior and out-of-range reset. Saved pages were reused after correcting those assumptions; no records were discarded or counts forced. These were local validation errors, not HTTP failures or adapter changes.
- Errors, if any: `[]`.

## Verification exceptions

None. All detail identities, listing titles, posted/applicable flags, and explicit US/India locations passed the checks.

## Output and scope

- `data/evals/workday/nvidia_product_management_snapshot.csv`: 1349 records; arrays and facet maps stored as JSON within CSV fields.
- `data/evals/workday/nvidia_product_management_snapshot.jsonl`: the same records, with original search record, request payload, and Workday jobPostingInfo for audit.
- `retrieved_at` is the listing-page retrieval time, and `detail_retrieved_at` is the individual detail verification time. `posted_date` is the source's exact startDate; blanks would mean unavailable.
- Only these two snapshots and this report were created in the repository. Existing untracked files and Adobe artifacts were left intact. No production data, source maps, repository PM filtering, classification, adapter, or Google Sheet was modified.
- No discovery eval, commit, or push. Temporary capture and validation scripts stayed outside the repository. No repository code changed, so no existing test-suite run was required. Structural validation checked all rows, not just a sample.
