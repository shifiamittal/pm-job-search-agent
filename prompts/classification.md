# Shortlist v1 entrypoint

The authoritative role-evaluation contract for new runs is `shortlist/` v1.2.0.
Read and execute these stages in order; do not duplicate their decision rules here:

1. [Role Understanding](../shortlist/role_understanding.md)
2. [Career / Requirements Mapping](../shortlist/career_requirements_mapping.md)
3. [Shortlist Decision](../shortlist/shortlist_decision.md)
4. [Controller / Validation](../shortlist/controller_validation.md)

Use the full supplied JD and established supplied candidate evidence. Produce the
structured state in [schema.yaml](../shortlist/schema.yaml). No automatic evidence
retrieval, batch execution, legacy lane conversion, or downstream action is implied.
Do not accept a decision merely because it passes structural validation.
See [migration status](../docs/shortlist_v1_migration.md) for blocked consumers.
