# Phase-1 discovery geography gate

Discovery preserves every raw source record in `raw_all_jobs.jsonl`. Before a record can
enter the PM candidate universe or a shortlist input, `scripts/discovery/geography.py`
classifies its complete source location set. A record is in scope when at least one
location is deterministically identified as United States or India.

Country metadata is preferred when supplied. Otherwise the gate recognizes exact country
aliases, US state names/codes, reviewed city-only variants, Indian state/city variants,
and known out-of-scope countries. It does not use fuzzy matching. Generic remote/global
labels and absent locations become `geography_unknown`. Conflicting or malformed country
metadata also fails closed as unknown.

Candidate records add `all_locations_raw`, `normalized_countries`,
`geography_in_scope`, `geography_status`, and `geography_reason`. Out-of-scope and unknown
records are written to separate diagnostic JSONL files. Raw source files are unchanged.

Filter an existing consolidated CSV without calling source adapters:

```powershell
.\.venv\Scripts\python.exe scripts/filter_discovery_geography.py `
  --input data\discovery\workday_universe\2026-09-30\workday_pm_candidates.csv `
  --output-dir local_private\geography\workday-2026-09-30
```

The command writes `shortlist_input_us_india`, `geography_excluded`, and
`geography_unknown` in both CSV and JSONL formats plus `geography_summary.json`.
