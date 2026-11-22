# Delta Specification: Worktree Exclusion & Pre-Merge `pre-commit.ci` Parity (`dev-workflow`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/dev_workflow.feature](../../../../../features/dev_workflow.feature)
- **Step Definitions:** [features/steps/dev_workflow_steps.py](../../../../../features/steps/dev_workflow_steps.py)

## Requirements

### Requirement: MODIFIED — Worktrunk Pre-Merge `ci_parity` Gate & `.pre-commit-config.yaml` Exclusion
`.pre-commit-config.yaml` SHALL exclude `.worktrees` and `.poodle-temp` from hook traversal, and `.config/wt.toml` `[[pre-merge]]` SHALL run `uv run python -m nectr.devtools.ci_parity check` alongside the diff mutation gate and orchestration gate before merging worktree branches into `main`.
- **Linked Scenario:** `Worktrunk pre-merge hooks enforce pre-commit.ci parity and pre-commit excludes worktrees` in [dev_workflow.feature](../../../../../features/dev_workflow.feature#L39-L43)
