# Discovery Prompt

## Activation
Raw discovery is enabled when explicitly requested. Shortlist execution remains separate.

## Inputs
Use approved sources from `config/job_sources.yaml` and retain source-exposed location data.

## Instructions
Normalize source location fields, then apply `scripts/discovery/geography.py` as a hard
Phase-1 gate. Only records with an explicit United States or India location proceed to
PM-family filtering and shortlist input. Generic remote/global and missing locations are
not inferred into scope. Preserve them in geography diagnostics and keep raw source rows.

## Output
Keep raw source records unchanged. Filtered candidates retain all raw locations and add
normalized countries, geography status, scope boolean, and a deterministic reason.
