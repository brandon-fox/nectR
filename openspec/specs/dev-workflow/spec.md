# Specification: Isolated Worktrees and Tiered Mutation Gate (`dev-workflow`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/dev_workflow.feature](../../../features/dev_workflow.feature)
- **Step Definitions:** [features/steps/dev_workflow_steps.py](../../../features/steps/dev_workflow_steps.py)

## Requirements

### Requirement: Worktree Directory Isolation Across Repository Scanners
All ephemeral CLI worktrees placed under `.worktrees/` SHALL be ignored by Git and excluded from `ruff`, `pytest`, `detect-secrets`, and `nectr-docs tree` directory traversal.
- **Linked Scenario:** `Worktree directory is excluded from git, ruff, pytest, detect-secrets, and tree sync` in [dev_workflow.feature](../../../features/dev_workflow.feature#L6-L9)

### Requirement: Worktrunk Lifecycle Bootstrap and Pre-Merge Enforcement
The committed Worktrunk project configuration (`.config/wt.toml`) SHALL use ordered `[[pre-start]]` hooks to install isolated per-worktree `uv` environments and verify commit readiness, and ordered `[[pre-merge]]` hooks to run the diff-scoped mutation gate, `nectr-ci-parity` (`pre-commit.ci` & workflow parity), and orchestration verification gate before landing changes on `main`, while `.pre-commit-config.yaml` SHALL exclude `.worktrees` and `.poodle-temp` from hook traversal.
- **Linked Scenarios:**
  - `Worktrunk project config provisions isolated environments and enforces merge gates` in [dev_workflow.feature](../../../features/dev_workflow.feature#L11-L15)
  - `Worktrunk pre-merge hooks enforce pre-commit.ci parity and pre-commit excludes worktrees` in [dev_workflow.feature](../../../features/dev_workflow.feature#L39-L43)

### Requirement: Inline Mutation Suppression Pragma Ban
Production source files under `src/` SHALL NOT contain inline mutation suppression pragmas, and violations SHALL be rejected during pre-commit checks with offending `path:line` locations reported.
- **Linked Scenario:** `Inline mutation suppression pragmas in src are rejected` in [dev_workflow.feature](../../../features/dev_workflow.feature#L17-L20)

### Requirement: Tiered Changed-Line Diff Mutation Targets
Diff-scoped mutation gating (`REFACTOR`, `pre-merge`, `pre-push`, and PR CI) SHALL map mutants onto changed hunk line ranges (`git diff -U0`), count per-mutant timeouts as killed, enforce `>= 85%` on Tier-1 contexts (`src/nectr/contracts/`, `src/nectr/chain/`) and `>= 75%` on Tier-2 contexts (`src/nectr/services/`, `src/nectr/devtools/`), and pass cleanly when only excluded contexts (`src/nectr/personas/`, `src/nectr/ui/`, `experiments/`) or non-source files change.
- **Linked Scenarios:**
  - `A Tier-1 change whose changed-line mutants score below 85% fails the diff gate` in [dev_workflow.feature](../../../features/dev_workflow.feature#L22-L25)
  - `Changes outside tiered source contexts pass with no tiered source changes` in [dev_workflow.feature](../../../features/dev_workflow.feature#L34-L37)

### Requirement: Ratcheting Full-Sweep Baseline Floors
Full-sweep mutation checks (`push` to `main`, nightly CI) SHALL evaluate each tiered context against committed baseline floors in `pyproject.toml` that only ratchet upward as test suites harden.
- **Linked Scenario:** `A full sweep below a committed baseline floor fails, and at or above the floor passes` in [dev_workflow.feature](../../../features/dev_workflow.feature#L27-L32)
