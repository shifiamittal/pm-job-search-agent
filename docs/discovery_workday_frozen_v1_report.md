# Workday frozen v1 evaluation

Evaluated on 2026-09-30 using the user-supplied, read-only
`C:\Users\shifi\Downloads\workday_pm_reference_frozen_v1.csv`.
SHA-256: `6bdb82c429e4101543bb803b8ca6a5a0307b500858901984952c7d2dfcf7c592`.
The reference contains 83 unique company/requisition identities. Its hash was
checked before and after each evaluation; the file was not modified.

This is an offline re-evaluation of the successful September 30 live crawls stored
under `data/evals/workday/adapter/`. No new source requests were made. Adobe's crawl
ran 13:44:53–13:46:34 UTC, NVIDIA's 13:44:52–13:51:22 UTC, and CrowdStrike's
13:44:50–13:45:43 UTC. These timestamps, rather than the evaluation time, describe
the freshness of the source data.

| Company | Raw jobs | PM candidates | PM matches | Recall | Extra candidates | Raw matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Adobe | 463 | 41 | 36 / 38 | 94.74% | 5 | 38 / 38 |
| NVIDIA | 1,624 | 36 | 35 / 35 | 100% | 1 | 35 / 35 |
| CrowdStrike | 221 | 11 | 10 / 10 | 100% | 1 | 10 / 10 |

Adobe's missing PM candidates are `R171808` (Senior Manager, Digital Monetization
Growth) and `R171889` (Venture Lead, Creator Services - Adobe Incubator). Both exist
in raw discovery; the unchanged repository title filter excludes them. No filter
exceptions were added. NVIDIA and CrowdStrike have no missing reference IDs.
Extras remain unreviewed candidates, not presumed false positives.

All three saved crawls report complete pagination with two consistent listing
passes, zero duplicate IDs, zero source/detail failures, and zero retries.
The source counts were 463, 1,624, and 221 respectively. Each pass reached its
source count and a terminal probe returned already-seen records. See the original
[live report](discovery_workday_live_report.md) for adapter architecture and source
limitations. Successful saved pagination does not establish current liveness at
any later time.

## Separation and artifacts

Only `scripts/eval_workday.py`, its tests, and evaluation documentation were changed
for frozen CSV support. Production discovery, source configuration, and PM filtering
were unchanged in this update. The evaluator loads validated saved raw jobs and
applies the existing title filter before reading benchmark rows. Benchmark IDs
are used solely for matching and missing/extras reports.

Outputs are in `data/evals/workday/frozen_v1/{adobe,nvidia,crowdstrike}/`: summary,
original crawl telemetry, raw and PM candidate JSONL, missing benchmark JSONL,
and extras CSV/JSONL. The previous live evaluation artifacts remain intact.
Each summary records reference path/hash, saved-crawl path, original crawl times,
and evaluation timestamp.

Example reproduction (substitute source/count for each company):

```powershell
.\.venv\Scripts\python.exe scripts/eval_workday.py --source adobe --reference C:\Users\shifi\Downloads\workday_pm_reference_frozen_v1.csv --expected-count 38 --saved-crawl-dir data/evals/workday/adapter/adobe --output-dir data/evals/workday/frozen_v1/adobe
```

Validation: `python -m unittest discover -s scripts -p "test_*.py"` passed all
111 tests, including Greenhouse, Ashby, Microsoft, Workday, and evaluation tests.
New tests cover combined CSV company selection, requisition-field mapping,
reference immutability, duplicate rejection, and saved-crawl validation.
No commits or pushes were made.
