# Specification Delta: Pact v4 & PactFlow Bi-Directional API and Event Contracts (`hive-persistence-api`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature)
- **Step Definitions:** [features/steps/hive_persistence_api_steps.py](../../../../../features/steps/hive_persistence_api_steps.py)

## Requirements

### Requirement: ADDED — Pact v4 HTTP & Async Message Verification + PactFlow `can-i-deploy` Gate (`ADR-0018`)
All `FastAPIHiveRouter` HTTP endpoints and `NATS JetStream` / CQRS domain event schemas (`AcceptedStatusGranted`, `SessionSettled`) SHALL be verified via `pact-python` v4 (`MIT`) consumer-driven HTTP and asynchronous message pacts offline in `pytest`/`behave`, and published alongside FastAPI's OpenAPI 3.1 schema to **PactFlow** with `can-i-deploy` gating when broker credentials are present in CI.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L9)
