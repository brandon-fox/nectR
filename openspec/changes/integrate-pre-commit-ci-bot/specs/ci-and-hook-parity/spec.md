# Delta Specification: `pre-commit.ci` Cloud Bot & System-Hook Skip Parity (`ci-and-hook-parity`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature)
- **Step Definitions:** [features/steps/ci_and_hook_parity_steps.py](../../../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: ADDED — `pre-commit.ci` Cloud Bot Split Execution & Conventional Commit Policy
`.pre-commit-config.yaml` SHALL configure top-level `exclude` for `.worktrees` and `.poodle-temp`, top-level `ci` settings enabling PR autofixes and weekly `chore/pre-commit-autoupdate` PRs with Commitizen-valid Conventional Commit messages (`style(...)` / `chore(...)`) and `submodules: false`, pinned MIT/Apache-2.0 upstream hook repositories (`pre-commit/pre-commit-hooks`, `Yelp/detect-secrets`, `python-jsonschema/check-jsonschema`, `astral-sh/ruff-pre-commit`), and an exact `ci.skip` set covering all `repo: local` `language: system` hooks while keeping remote and `pygrep` hooks active in `pre-commit.ci`.
- **Linked Scenario:** `pre-commit.ci bot configuration enforces Conventional Commit autofixes, weekly autoupdates, and system-hook skips` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L31-L35)
