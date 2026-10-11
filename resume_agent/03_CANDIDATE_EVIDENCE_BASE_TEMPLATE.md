# Candidate Evidence Base Template

Populate this only from uploaded career files or explicit candidate confirmation.

## 1. Candidate Overview

```yaml
candidate:
  name:
  current_title:
  years_of_experience:
  target_roles:
  target_levels:
  preferred_locations:
  work_model_preferences:
  work_authorization_notes:
  relocation_preferences:
```

## 2. Career Timeline

```yaml
roles:
  - company:
    title:
    dates:
    location:
    team_or_org:
    formal_direct_reports:
    cross_functional_team_scope:
    products_owned:
    primary_customers:
    domains:
```

Do not infer formal direct reports from cross-functional leadership.

## 3. Project / Product Evidence

```yaml
projects:
  - project_id:
    project_name:
    company:
    role:
    business_context:
    customer_problem:
    candidate_ownership:
    product_strategy:
    what_was_built:
    technical_or_operating_mechanism:
    cross_functional_partners:
    key_decisions:
    key_tradeoffs:
    experimentation:
    rollout:
    adoption:
    metrics:
    business_outcomes:
    customer_outcomes:
    leadership_evidence:
    unresolved_conflicts:
    source_files:
    confidence:
```

## 4. Capability Index

Track evidence under:
- Product Strategy
- Customer Discovery
- AI / ML
- Data / Platforms
- Experimentation
- Metrics / Economics
- Leadership
- Domain Expertise

## 5. Metric Ledger

```yaml
metric_ledger:
  - metric_id:
    project:
    metric:
    value:
    definition:
    population_or_denominator:
    time_period:
    source:
    status: validated | candidate-confirmed | unresolved
    conflicting_versions:
      - ...
```

## 6. Claim Ledger

For claims linked to shortlist criteria, copy the four mapping fields below verbatim
from the validated v1.2 state with stable criterion IDs. These are role-specific
references, not a new fit assessment. Keep `criterion_mappings: []` for general
claims that have no role mapping; do not infer classifications. Preserve nulls
and limitations. Additional evidence must not silently overwrite upstream state.

```yaml
claim_ledger:
  - claim:
    source:
    confidence:
    criterion_mappings:
      - criterion_id:
        capability_fit:
        domain_context_fit:
        overall_fit_assessment:
        limitation_or_difference:
    approved_for_resume: true | false
    caveat:
```

## 7. Known Conflicts / Ambiguities

```yaml
conflicts:
  - topic:
    version_a:
    source_a:
    version_b:
    source_b:
    resolution_status:
    safe_language:
```

Never silently reconcile.

## 8. Strongest Career Stories

```yaml
strongest_stories:
  - story_name:
    use_for_questions:
      - ...
    core_decision:
    stakes:
    actions:
    result:
    learning:
    source:
```

## 9. Genuine Gaps

```yaml
gaps:
  - capability_or_domain:
    severity:
    what_is_missing:
    closest_transferable_experience:
    fundamental_for_target_roles: true | false
```

## 10. Candidate-Confirmed Facts

```yaml
candidate_confirmed_facts:
  - fact:
    date_confirmed:
    scope:
    notes:
```

Keep candidate-confirmed facts distinguishable from artifact-derived evidence.
