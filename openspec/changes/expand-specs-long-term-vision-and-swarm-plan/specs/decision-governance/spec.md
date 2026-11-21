# Specification Delta: Expanded MADR & Fast Decision/Experiment Registry (`decision-governance`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: MODIFIED — Federated NATS/CQRS and Campus Compliance MADR & Fast Decision Coverage
The decision governance registry SHALL include accepted, `adrlint`-locked MADR 4.0 records for NATS Leaf Node / CQRS Knowledge Graph isolation (`ADR-0014`) and Zero-PII FERPA/GDPR/Title IV campus compliance (`ADR-0015`), alongside locked operational presets (`DEC-001` through `DEC-015`) and multi-arm simulation hypotheses (`EXP-001` through `EXP-005`) in `docs/planning/decisions.yaml`.
- **Linked Scenario:** `Repository MADR records pass adrlint validation, lock check, and verbosity limits` in [decision_governance.feature](../../../../../features/decision_governance.feature#L6-L9)
