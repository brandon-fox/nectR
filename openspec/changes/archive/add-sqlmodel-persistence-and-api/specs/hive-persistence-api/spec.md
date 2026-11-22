# Specification: Hive Persistence & API (`hive-persistence-api`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature)
- **Step Definitions:** [features/steps/hive_persistence_api_steps.py](../../../../../features/steps/hive_persistence_api_steps.py)

## Requirements

### Requirement: ADDED — Hexagonal SQLModel Persistence & Alembic Migrations
`HiveServiceLayer` SHALL persist and reload Hive, `BeeAccount`, and `ServiceBarterSession` state through a `sqlmodel` repository adapter managed by `alembic` migrations without adding ORM dependencies to `src/nectr/contracts/`.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)

### Requirement: ADDED — FastAPI Service Endpoints & Structured Observability
`HiveServiceLayer` SHALL expose `fastapi` endpoints instrumented with `structlog` and `opentelemetry-sdk`, rolling back persistence transactions whenever `HiveContractEngine` raises a protocol invariant violation.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)
