# Specification: Read-Only Telemetry Dashboard UI (`telemetry-ui`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/telemetry_ui.feature](../../../../../features/telemetry_ui.feature)
- **Step Definitions:** [features/steps/telemetry_ui_steps.py](../../../../../features/steps/telemetry_ui_steps.py)

## Requirements

### Requirement: ADDED — Read-Only Telemetry Visualization Panels
`src/nectr/ui/` SHALL render Knowledge Graph, Collusion Matrix, Gini index, and Comb reserve views via `streamlit` and `networkx` from immutable telemetry snapshots without mutating ledger or contract state.
- **Linked Scenario:** `Read-only dashboard renders Hive telemetry without mutating ledger state` in [telemetry_ui.feature](../../../../../features/telemetry_ui.feature#L6-L10)
