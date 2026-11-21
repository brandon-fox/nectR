# Specification: Mesa ABM Simulation & Hypothesis Invariants (`persona-abm-simulation`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/persona_abm_simulation.feature](../../../../../features/persona_abm_simulation.feature)
- **Step Definitions:** [features/steps/persona_abm_simulation_steps.py](../../../../../features/steps/persona_abm_simulation_steps.py)

## Requirements

### Requirement: ADDED — Deterministic Mesa ABM Orchestration & Telemetry
Multi-hive persona simulations SHALL execute through a seeded `mesa.Model` and `mesa.DataCollector`, emitting reproducible Gini, velocity, collusion-decay, and Comb reserve series.
- **Linked Scenario:** `Seeded Mesa multi-hive simulation reproduces deterministic telemetry` in [persona_abm_simulation.feature](../../../../../features/persona_abm_simulation.feature#L6-L10)

### Requirement: ADDED — Hypothesis Property-Based Contract Invariant Verification
`HiveContractEngine` invariants (supply conservation, Queen Separation of Powers, and `RAW_POLLEN` certification gating) SHALL be verified via `hypothesis` property-based tests across randomized transaction sequences.
- **Linked Scenario:** `Seeded Mesa multi-hive simulation reproduces deterministic telemetry` in [persona_abm_simulation.feature](../../../../../features/persona_abm_simulation.feature#L6-L10)
