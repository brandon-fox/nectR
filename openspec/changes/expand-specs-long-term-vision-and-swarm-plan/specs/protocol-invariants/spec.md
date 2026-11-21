# Specification Delta: Complete D-01 through D-05 Protocol Invariants (`protocol-invariants`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/protocol_invariants.feature](../../../../../features/protocol_invariants.feature)
- **Step Definitions:** [features/steps/protocol_invariants_steps.py](../../../../../features/steps/protocol_invariants_steps.py)

## Requirements

### Requirement: ADDED — No Blind Transfers & Zero-nectR Reciprocal Skill Barter (D-01)
The `HiveContractEngine` SHALL prohibit blind token transfers lacking a `DirectionalServiceBarterContract` handshake (`tutor_id != learner_id`, `subject_id`, `duration_hours`, co-signed attestation) or explicit `Comb`/bridge transition, and SHALL require any `0-nectR` session to specify a non-empty `reciprocal_subject_id` for mutual skill-for-skill barter.
- **Linked Scenario:** `Zero-nectR session without reciprocal subject is rejected while reciprocal skill barter succeeds` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L33-L40)

### Requirement: ADDED — Cross-Hive Guard Bee Accepted Status & Clamped Epoch FX Corridor (D-04)
The `HiveContractEngine` SHALL reject cross-Hive `LIQUID_NECTR` bridge transfers until the migrating Bee achieves on-chain **Accepted Status** in the target Hive (by tutoring at least `accepted_status_peer_threshold` distinct host-Hive peers), and SHALL route the bridge toll (`5%` default) to the source Comb while clamping the Comb-per-active-bee exchange rate to `[0.5x, 2.0x]`.
- **Linked Scenario:** `Guard Bee blocks unaccepted Pollinator bridge and permits Accepted Status bridge with Comb toll` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L42-L51)
