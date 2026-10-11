# Sequential shortlist batch runner

`scripts/run_shortlist_batch.py` is a thin, durable orchestrator around the existing
single-job `run_job()` and `resume_job()` functions. It does not implement or alter
role interpretation, evidence mapping, shortlist decisions, controller validation,
schema checks, provenance checks, or transient retry policy.

The runner accepts a geography-filtered `.csv`, `.jsonl`, or `.ndjson` file and
processes selected rows sequentially. CSV rows use the same normalization adapter as
the single-job runner. Company, title, and `full_job_description_raw` remain required;
the URL, external ID, location, posted date, and source remain optional.

## First five jobs

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\run_shortlist_batch.py `
  --input .\local_private\geography\workday-2026-09-30\shortlist_input_us_india.csv `
  --max-jobs 5 `
  --role-model gpt-6-luna `
  --mapping-model gpt-6-sol `
  --decision-model gpt-6-luna `
  --controller-model gpt-6-luna
```

Those four models are also the batch defaults. `--model` remains a fallback that sets
all four stages, and any stage-specific option overrides its stage. `--dry-run` reads
and validates the input, reports total/selected/reusable counts and model configuration,
and creates no batch directory or model transport.

## Durable layout

```text
local_private/shortlist_batches/<batch_id>/
  manifest.json
  shortlist_summary.csv
  shortlist_summary.jsonl
  failures.csv
  runs/
    <run_id>/
      job_state.json
      shortlist_state.json  # only after a complete decision/controller path
      review.md
      progress.log
```

The manifest and all summary projections are written atomically after a job is marked
running and after each result. A planned per-job run ID is persisted before the first
model call, so an interrupted single-job run can be found and resumed without losing
its completed stages. Exact duplicate input records are executed once; later identical
rows reference the first run and are marked reused. Their usage is counted once.

`shortlist_summary.csv` contains identity, existing decision classifications, concise
rationale/risk, controller acceptance, failure diagnostics, per-stage models, and token/
elapsed telemetry. The review-order column only orders the four existing outcomes and
places failed/controller-rejected rows last; it is not a score or decision input.

`failures.csv` contains execution and input-validation failures. A completed controller
rejection remains `rejected` in the main summary and is not mislabeled as an execution
failure.

## Resume

```powershell
.\.venv\Scripts\python.exe scripts\run_shortlist_batch.py `
  --resume-batch <batch_id>
```

Resume verifies the exact input path and file hash, shortlist contract hashes, schema
hash, all five candidate-context hashes, per-stage models, timeout, and output-token
setting before any API call. It skips accepted and controller-rejected jobs, resumes
failed/interrupted per-job runs through `resume_job()`, and starts rows that never
created a run. A changed input file or incompatible contract/configuration blocks the
resume rather than reusing stale output. The original `--max-jobs` selection is fixed
in the manifest.

One job failure does not stop later jobs. Existing single-job bounded transient retries
remain active for the failed stage; schema, provenance, and semantic failures receive
no automatic retry within the same batch pass. An explicit batch resume is required
to attempt an incomplete saved job again.

The manifest aggregates every recorded model call, including calls from resumed runs.
It separately reports mapping input, cached-input and cache-write tokens, token hit rate,
mapping call count, and calls with cache hits. No currency cost is estimated.
