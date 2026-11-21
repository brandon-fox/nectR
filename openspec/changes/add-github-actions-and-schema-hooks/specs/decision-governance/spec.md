# Delta Specification: Decision Governance CI & Schema Hooks

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: MODIFIED — Local-CI Parity & JSON Schema Validation
All `adrlint` MADR checks (`lint`, `format --check`, `lock --check`), `decisions.yaml` schema validation (`check-jsonschema`), and `nectr-decisions check` gates SHALL run identically in `.pre-commit-config.yaml`, `.githooks/`, and GitHub Actions (`ci.yml`, `pr-policy.yml`).
- **Linked Scenario:** `Repository MADR records pass adrlint validation, lock check, and verbosity limits` in [decision_governance.feature](../../../../../features/decision_governance.feature#L6-L9)
