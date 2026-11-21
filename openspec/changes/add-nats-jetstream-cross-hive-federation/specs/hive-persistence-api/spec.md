# Specification Delta: NATS Leaf Node JetStream Cross-Hive Federation & CQRS Read Model (`hive-persistence-api`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature)
- **Step Definitions:** [features/steps/hive_persistence_api_steps.py](../../../../../features/steps/hive_persistence_api_steps.py)

## Requirements

### Requirement: ADDED — Outbound NATS Leaf Node & JetStream Cross-Hive Proof Relay (`ADR-0014`)
`HiveServiceLayer` SHALL federate cross-Hive `AcceptedStatusGranted` and bridge settlement proofs asynchronously via `CrossHiveBridgePort` and `nats-py` JetStream domains over outbound Leaf Node connections (port `7422`), enforcing idempotent nonce deduplication, monthly export quotas, and clamped `[0.5x, 2.0x]` epoch FX rates.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)

### Requirement: ADDED — Event-Sourced CQRS Knowledge Graph Read-Model Isolation (`ADR-0014`)
Consensus block validation SHALL commit only a deterministic 32-byte `knowledge_graph_root` (`kg_root`) and emit post-commit domain events consumed asynchronously by the off-chain Knowledge Graph Telemetry projector so floating-point graph algorithms never execute inside on-chain contract validation.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)
