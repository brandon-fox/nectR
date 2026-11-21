# Delta Specification: External Workflow & n8n Governance Decisions

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: ADDED — n8n ("k8n") Off-Chain Workflow Boundary and Milestone 3 Options
The decision registry (`docs/planning/decisions.yaml`), MADR log (`docs/adr/`), and Milestone 3 roadmap (`docs/planning/roadmap.md`) SHALL clarify historical `"k8n"` references as `n8n` while keeping `DEC-009` locked to Mesa ABM, enforce an out-of-process `HiveServiceLayer` webhook boundary excluding `n8n` (Sustainable Use License) from Python packaging (`DEC-016`, `ADR-0016`), record a hybrid evaluation hypothesis (`EXP-006`), and list permissive-OSS Milestone 3 orchestration options.
- **Linked Scenario:** `Decision registry and Milestone 3 roadmap define n8n off-chain boundaries and options` in [decision_governance.feature](../../../../../features/decision_governance.feature#L26-L31)
