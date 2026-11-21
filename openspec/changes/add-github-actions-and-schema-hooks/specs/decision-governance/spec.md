# Delta Specification: Decision Governance CI & Schema Hooks

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)
- **CI Parity Feature:** [features/ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature)
- **CI Parity Steps:** [features/steps/ci_and_hook_parity_steps.py](../../../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: MODIFIED — Local-CI Parity & JSON Schema Validation for `docs/planning/decisions.yaml`
All `adrlint` MADR 4.0 checks (`lint`, `format --check`, `lock --check`), `docs/planning/decisions.yaml` schema validation (`check-jsonschema` against `docs/planning/decisions.schema.json`), and `nectr-decisions check` gates SHALL run identically in `.pre-commit-config.yaml`, `.githooks/pre-commit`, and GitHub Actions workflows.
- **Linked Scenario:** `Repository MADR records pass adrlint validation, lock check, and verbosity limits` in [decision_governance.feature](../../../../../features/decision_governance.feature#L6-L9)
- **Linked Scenario:** `Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L24-L28)
