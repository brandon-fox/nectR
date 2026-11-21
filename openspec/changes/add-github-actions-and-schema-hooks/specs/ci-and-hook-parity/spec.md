# Specification: End-to-End Hook, CI Matrix, Scheduled Audit & Release Parity (`ci-and-hook-parity`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature)
- **Step Definitions:** [features/steps/ci_and_hook_parity_steps.py](../../../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: ADDED — Cross-Platform Local Hook & Pre-Commit Parity with CI
`.githooks/pre-commit`, `.githooks/pre-push`, `.githooks/commit-msg`, and `.pre-commit-config.yaml` SHALL resolve `.venv` executables across Windows Git Bash (`cygpath -u`) and POSIX without manual activation, scan staged files null-delimited (`-z`) against the git index (`--cached`), and mirror every security, governance, lint, format, type, documentation (`mkdocs build --strict`), and test gate enforced in `.github/workflows/`.
- **Linked Scenario:** `Local git hooks and pre-commit config maintain gate parity with GitHub Actions workflows` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L7-L10)

### Requirement: ADDED — Deterministic `uv.lock` Full-Extra Installs & Multi-OS/Python Matrix
GitHub Actions CI SHALL install dependencies deterministically from `uv.lock` via `astral-sh/setup-uv` (`uv sync --frozen --extra dev --extra research`) so `pip-licenses` and `pip-audit` audit all runtime, dev, and research packages, and SHALL execute unit and BDD suites across Python `3.11`, `3.12`, and `3.13` on `ubuntu-latest` plus `windows-latest`.
- **Linked Scenario:** `CI matrix enforces deterministic uv.lock installs across Python versions, OS runners, and research extras` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L12-L16)

### Requirement: ADDED — Main-Branch `@red` Merge Guard & 80% Coverage Floor
Pull requests and pushes targeting `main` SHALL fail if any `.feature` file retains an unimplemented `@red` scenario tag and SHALL enforce `--cov=src/nectr --cov-report=xml:coverage.xml --cov-fail-under=80` to satisfy GitHub Ruleset `27810615`.
- **Linked Scenario:** `Main-branch merge guard rejects unimplemented @red BDD scenarios and enforces 80 percent coverage floor` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L18-L22)

### Requirement: ADDED — Scheduled Baseline Drift, Expanded SPDX Review & Tagged Releases
Scheduled daily (`06:00 UTC`) workflows SHALL verify `.secrets.baseline` drift alongside CVE/license audits, PR dependency reviews SHALL deny `GPL-*`, `AGPL-*`, `LGPL-*`, and `SSPL-1.0` variants, and `release.yml` SHALL automate Commitizen versioned changelogs and GitHub Releases on version tags.
- **Linked Scenario:** `Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L24-L28)
