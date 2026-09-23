# Microsoft raw reference snapshot

Capture started: 2026-09-22T10:19:28.018432+00:00

Last artifact update: 2026-09-22T10:34:55.263821+00:00

Status: INCOMPLETE - stopped on source-count discrepancy

## Official mechanism

Careers UI: https://apply.careers.microsoft.com/careers

Listing endpoint: https://apply.careers.microsoft.com/api/pcsx/search

Parameters: domain=microsoft.com, query=empty, location=empty, start=offset.
No profession/title/location filters. Default source sortBy=timestamp.
Pagination: numeric start offsets incremented by returned record count.
Observed maximum page size: 10; num=100 also returned 10 (ignored/capped).
No documented larger limit was exposed in the public client.

Detail endpoint: https://apply.careers.microsoft.com/api/pcsx/position_details?position_id=<source ID>&domain=microsoft.com&hl=en

The public pcsxPwa.dc64c7415bcc1221.js bundle explicitly constructs both endpoints.
The UI source configuration restricts results to externally posted Open ATS roles
from successfactors with workflow templates 102-106. These are source-defined
publication criteria, not custom role filters. No PM filtering/classification was run.

## Counts and completeness

- Source-reported total at start: 2326
- Source-reported total on stopping page: 2327
- Exported unique source position IDs: 1800
- Exported records: 1800
- Successful listing responses/pages: 181 (last response detected count drift and was not appended; no terminal empty page reached)
- Snapshot listing HTTP attempts: 189
- Detail records exported: 0
- Snapshot detail HTTP attempts: 0
- Total snapshot HTTP attempts: 189
- Duplicate source IDs: {}
- Missing required fields: {"source_position_id": 0, "display_job_id": 0, "title": 0, "canonical_url": 0}
- Enumeration exhaustive: False
- Failure: RuntimeError: Source total changed from 2326 to 2327; stop for discrepancy review

Completeness requires unique IDs equal every page's source count plus an empty
terminal page. This is a live offset enumeration, not a server-locked transaction.
Source counts and offsets are preserved below for audit.
Seniority remains null if not exposed; no inference from titles. Primary location
uses detail.location when available, otherwise the source's first listed location.
All source listing fields are retained without interpretation. Detail-only fields
remain null in this partial capture.
Source status is explicitly attributed to the public page's basePositionFq, not
a per-job status field. Generic employer blogs/perks and logged-out user actions
would be omitted from source_detail. No detail enrichment was completed in this
partial capture; source_detail is empty and listing metadata is retained.

## Inspection requests before export
Five listing probes: two successful 10-record responses and three HTTP 429s.
One successful detail inspection. One HTML and two JavaScript HTTP reads, plus
one web-tool page inspection. These were not reused as snapshot pages.
A 60-second pause cleared the initial 429s. No Retry-After header was provided.

## Retrieval errors

```json
[
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 700
    },
    "status": 429,
    "at": "2026-09-22T10:21:57.163770+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 930
    },
    "status": 429,
    "at": "2026-09-22T10:23:46.721992+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1200
    },
    "status": 429,
    "at": "2026-09-22T10:25:43.307954+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1250
    },
    "status": 429,
    "at": "2026-09-22T10:26:57.604968+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1280
    },
    "status": 429,
    "at": "2026-09-22T10:28:04.314755+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1360
    },
    "status": 429,
    "at": "2026-09-22T10:29:20.682528+00:00",
    "retry_wait_seconds": 60
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1360
    },
    "status": 429,
    "at": "2026-09-22T10:30:21.077099+00:00",
    "retry_wait_seconds": 120
  },
  {
    "kind": "listing",
    "params": {
      "domain": "microsoft.com",
      "query": "",
      "location": "",
      "start": 1370
    },
    "status": 429,
    "at": "2026-09-22T10:32:23.252149+00:00",
    "retry_wait_seconds": 60
  }
]
```

## Listing page audit

```json
[
  {
    "start": 0,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:29.280511+00:00"
  },
  {
    "start": 10,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:30.819539+00:00"
  },
  {
    "start": 20,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:32.349931+00:00"
  },
  {
    "start": 30,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:34.593204+00:00"
  },
  {
    "start": 40,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:36.135722+00:00"
  },
  {
    "start": 50,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:38.347207+00:00"
  },
  {
    "start": 60,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:40.669804+00:00"
  },
  {
    "start": 70,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:42.814045+00:00"
  },
  {
    "start": 80,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:44.341167+00:00"
  },
  {
    "start": 90,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:46.591499+00:00"
  },
  {
    "start": 100,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:48.766825+00:00"
  },
  {
    "start": 110,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:50.946996+00:00"
  },
  {
    "start": 120,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:53.138857+00:00"
  },
  {
    "start": 130,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:55.342380+00:00"
  },
  {
    "start": 140,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:57.552852+00:00"
  },
  {
    "start": 150,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:19:59.068302+00:00"
  },
  {
    "start": 160,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:01.290131+00:00"
  },
  {
    "start": 170,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:03.475388+00:00"
  },
  {
    "start": 180,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:05.797369+00:00"
  },
  {
    "start": 190,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:08.045636+00:00"
  },
  {
    "start": 200,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:09.629187+00:00"
  },
  {
    "start": 210,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:11.784583+00:00"
  },
  {
    "start": 220,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:13.307418+00:00"
  },
  {
    "start": 230,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:15.489776+00:00"
  },
  {
    "start": 240,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:17.650229+00:00"
  },
  {
    "start": 250,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:19.820014+00:00"
  },
  {
    "start": 260,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:21.934466+00:00"
  },
  {
    "start": 270,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:24.128358+00:00"
  },
  {
    "start": 280,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:26.410949+00:00"
  },
  {
    "start": 290,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:28.591486+00:00"
  },
  {
    "start": 300,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:30.834546+00:00"
  },
  {
    "start": 310,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:33.073766+00:00"
  },
  {
    "start": 320,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:35.412134+00:00"
  },
  {
    "start": 330,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:37.644975+00:00"
  },
  {
    "start": 340,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:39.867161+00:00"
  },
  {
    "start": 350,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:42.102950+00:00"
  },
  {
    "start": 360,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:44.330832+00:00"
  },
  {
    "start": 370,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:45.905439+00:00"
  },
  {
    "start": 380,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:48.120965+00:00"
  },
  {
    "start": 390,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:50.359150+00:00"
  },
  {
    "start": 400,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:52.777330+00:00"
  },
  {
    "start": 410,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:55.087391+00:00"
  },
  {
    "start": 420,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:57.353863+00:00"
  },
  {
    "start": 430,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:20:59.587646+00:00"
  },
  {
    "start": 440,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:01.867461+00:00"
  },
  {
    "start": 450,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:04.082834+00:00"
  },
  {
    "start": 460,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:06.318950+00:00"
  },
  {
    "start": 470,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:08.588519+00:00"
  },
  {
    "start": 480,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:10.844377+00:00"
  },
  {
    "start": 490,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:13.055191+00:00"
  },
  {
    "start": 500,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:15.296648+00:00"
  },
  {
    "start": 510,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:16.896800+00:00"
  },
  {
    "start": 520,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:19.124149+00:00"
  },
  {
    "start": 530,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:21.339376+00:00"
  },
  {
    "start": 540,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:23.632845+00:00"
  },
  {
    "start": 550,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:25.868803+00:00"
  },
  {
    "start": 560,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:27.518259+00:00"
  },
  {
    "start": 570,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:29.705072+00:00"
  },
  {
    "start": 580,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:31.922963+00:00"
  },
  {
    "start": 590,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:34.436645+00:00"
  },
  {
    "start": 600,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:36.476119+00:00"
  },
  {
    "start": 610,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:38.700054+00:00"
  },
  {
    "start": 620,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:40.912010+00:00"
  },
  {
    "start": 630,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:43.137056+00:00"
  },
  {
    "start": 640,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:45.348382+00:00"
  },
  {
    "start": 650,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:46.917608+00:00"
  },
  {
    "start": 660,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:49.119132+00:00"
  },
  {
    "start": 670,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:51.381621+00:00"
  },
  {
    "start": 680,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:53.745226+00:00"
  },
  {
    "start": 690,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:21:56.163452+00:00"
  },
  {
    "start": 700,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:22:59.862104+00:00"
  },
  {
    "start": 710,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:02.050928+00:00"
  },
  {
    "start": 720,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:03.564249+00:00"
  },
  {
    "start": 730,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:05.798955+00:00"
  },
  {
    "start": 740,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:08.241978+00:00"
  },
  {
    "start": 750,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:10.461584+00:00"
  },
  {
    "start": 760,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:12.637199+00:00"
  },
  {
    "start": 770,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:14.841084+00:00"
  },
  {
    "start": 780,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:16.993641+00:00"
  },
  {
    "start": 790,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:19.295372+00:00"
  },
  {
    "start": 800,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:21.608680+00:00"
  },
  {
    "start": 810,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:23.119105+00:00"
  },
  {
    "start": 820,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:24.656593+00:00"
  },
  {
    "start": 830,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:26.857627+00:00"
  },
  {
    "start": 840,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:29.006849+00:00"
  },
  {
    "start": 850,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:31.151602+00:00"
  },
  {
    "start": 860,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:33.341363+00:00"
  },
  {
    "start": 870,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:35.591700+00:00"
  },
  {
    "start": 880,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:37.752222+00:00"
  },
  {
    "start": 890,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:39.934600+00:00"
  },
  {
    "start": 900,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:42.041964+00:00"
  },
  {
    "start": 910,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:43.560123+00:00"
  },
  {
    "start": 920,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:23:45.716441+00:00"
  },
  {
    "start": 930,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:49.078264+00:00"
  },
  {
    "start": 940,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:51.283511+00:00"
  },
  {
    "start": 950,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:52.773823+00:00"
  },
  {
    "start": 960,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:54.955092+00:00"
  },
  {
    "start": 970,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:57.294090+00:00"
  },
  {
    "start": 980,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:24:59.486770+00:00"
  },
  {
    "start": 990,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:01.679706+00:00"
  },
  {
    "start": 1000,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:04.060809+00:00"
  },
  {
    "start": 1010,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:05.604686+00:00"
  },
  {
    "start": 1020,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:07.795438+00:00"
  },
  {
    "start": 1030,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:09.987868+00:00"
  },
  {
    "start": 1040,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:11.523158+00:00"
  },
  {
    "start": 1050,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:13.055595+00:00"
  },
  {
    "start": 1060,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:15.374571+00:00"
  },
  {
    "start": 1070,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:16.906364+00:00"
  },
  {
    "start": 1080,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:18.421996+00:00"
  },
  {
    "start": 1090,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:21.615532+00:00"
  },
  {
    "start": 1100,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:24.124284+00:00"
  },
  {
    "start": 1110,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:26.357491+00:00"
  },
  {
    "start": 1120,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:28.560578+00:00"
  },
  {
    "start": 1130,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:30.144893+00:00"
  },
  {
    "start": 1140,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:31.726626+00:00"
  },
  {
    "start": 1150,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:33.879792+00:00"
  },
  {
    "start": 1160,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:35.391190+00:00"
  },
  {
    "start": 1170,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:37.598241+00:00"
  },
  {
    "start": 1180,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:39.890308+00:00"
  },
  {
    "start": 1190,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:25:42.106404+00:00"
  },
  {
    "start": 1200,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:26:47.842881+00:00"
  },
  {
    "start": 1210,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:26:49.494702+00:00"
  },
  {
    "start": 1220,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:26:51.720416+00:00"
  },
  {
    "start": 1230,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:26:53.957848+00:00"
  },
  {
    "start": 1240,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:26:56.604332+00:00"
  },
  {
    "start": 1250,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:27:59.407136+00:00"
  },
  {
    "start": 1260,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:28:01.787764+00:00"
  },
  {
    "start": 1270,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:28:03.313602+00:00"
  },
  {
    "start": 1280,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:05.981453+00:00"
  },
  {
    "start": 1290,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:08.198483+00:00"
  },
  {
    "start": 1300,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:10.095975+00:00"
  },
  {
    "start": 1310,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:11.661852+00:00"
  },
  {
    "start": 1320,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:13.185511+00:00"
  },
  {
    "start": 1330,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:15.355512+00:00"
  },
  {
    "start": 1340,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:17.526459+00:00"
  },
  {
    "start": 1350,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:29:19.678916+00:00"
  },
  {
    "start": 1360,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:32:22.249816+00:00"
  },
  {
    "start": 1370,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:25.665158+00:00"
  },
  {
    "start": 1380,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:27.888140+00:00"
  },
  {
    "start": 1390,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:30.061833+00:00"
  },
  {
    "start": 1400,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:32.595855+00:00"
  },
  {
    "start": 1410,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:34.147422+00:00"
  },
  {
    "start": 1420,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:36.389166+00:00"
  },
  {
    "start": 1430,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:38.592549+00:00"
  },
  {
    "start": 1440,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:40.815262+00:00"
  },
  {
    "start": 1450,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:42.988529+00:00"
  },
  {
    "start": 1460,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:45.202592+00:00"
  },
  {
    "start": 1470,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:47.586067+00:00"
  },
  {
    "start": 1480,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:49.114589+00:00"
  },
  {
    "start": 1490,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:51.346315+00:00"
  },
  {
    "start": 1500,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:53.733730+00:00"
  },
  {
    "start": 1510,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:55.420474+00:00"
  },
  {
    "start": 1520,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:33:57.781539+00:00"
  },
  {
    "start": 1530,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:00.028937+00:00"
  },
  {
    "start": 1540,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:02.279664+00:00"
  },
  {
    "start": 1550,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:03.919438+00:00"
  },
  {
    "start": 1560,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:06.172978+00:00"
  },
  {
    "start": 1570,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:08.426613+00:00"
  },
  {
    "start": 1580,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:10.786447+00:00"
  },
  {
    "start": 1590,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:13.054503+00:00"
  },
  {
    "start": 1600,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:15.591774+00:00"
  },
  {
    "start": 1610,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:17.147925+00:00"
  },
  {
    "start": 1620,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:19.332024+00:00"
  },
  {
    "start": 1630,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:21.549280+00:00"
  },
  {
    "start": 1640,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:23.093220+00:00"
  },
  {
    "start": 1650,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:24.656541+00:00"
  },
  {
    "start": 1660,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:26.862266+00:00"
  },
  {
    "start": 1670,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:29.112711+00:00"
  },
  {
    "start": 1680,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:31.300458+00:00"
  },
  {
    "start": 1690,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:33.514334+00:00"
  },
  {
    "start": 1700,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:35.763674+00:00"
  },
  {
    "start": 1710,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:37.303504+00:00"
  },
  {
    "start": 1720,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:38.839240+00:00"
  },
  {
    "start": 1730,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:41.029759+00:00"
  },
  {
    "start": 1740,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:42.706076+00:00"
  },
  {
    "start": 1750,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:44.880795+00:00"
  },
  {
    "start": 1760,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:47.145091+00:00"
  },
  {
    "start": 1770,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:49.323052+00:00"
  },
  {
    "start": 1780,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:50.838944+00:00"
  },
  {
    "start": 1790,
    "returned": 10,
    "total": 2326,
    "captured_at": "2026-09-22T10:34:52.564111+00:00"
  },
  {
    "start": 1800,
    "returned": 10,
    "total": 2327,
    "captured_at": "2026-09-22T10:34:54.960399+00:00"
  }
]
```

## Final validation and discrepancy

The source count changed from 2,326 to 2,327 during offset pagination. The capture
stopped immediately, before incorporating the changed-count page. This snapshot
is partial and must not be used as a complete Microsoft reference universe.
No job-detail enrichment batch was started because enumeration did not pass.
Profession, discipline and seniority are therefore null where absent from listing
records; one earlier detail inspection demonstrated some metadata is exposed by
the detail endpoint, but it is not represented as fully captured here.

Final equality check: **1800 unique exported IDs != 2327 latest source-reported jobs**.

The stopping page requested start=1800 and returned 10 records with count=2327.
JSONL and CSV both contain 1800 records with identical ordered source IDs.
No PM filter, title classification, discovery evaluation, production registry or integration change, commit, or push was performed.

API request accounting: 189 capture attempts + 5 listing probes + 1 detail probe = 195 API calls. There were 11 HTTP 429 responses total (8 during capture, 3 during inspection). Three additional HTTP reads inspected HTML/JavaScript; a separate web-tool read inspected the careers page.
