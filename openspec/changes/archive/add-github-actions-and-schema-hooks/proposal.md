# Proposal: End-to-End Local Hook, CI Pipeline, Scheduled Audit & Branch Governance Hardening (`add-github-actions-and-schema-hooks`)

## Why
Following baseline hook/coverage fixes landed in `#14`, a full review of `.githooks/`, `.pre-commit-config.yaml`, `.github/workflows/`, `.github/dependabot.yml`, and remote GitHub ruleset `27810615` identified remaining structural gaps across local, PR, scheduled, and release pipelines:

1. **Programmatic Local-CI Parity Guard:** While `#14` manually aligned `.githooks/`, `.pre-commit-config.yaml`, and `.github/workflows/`, there is no automated parity validator preventing future hook-vs-CI drift.
2. **Unlocked CI Installs & Unscanned `.[research]` Extras:** CI currently runs `pip install -e ".[dev]"` instead of `uv sync --frozen --extra dev --extra research`, leaving `uv.lock` unenforced in CI and `matplotlib`, `scipy`, and `pandas` outside `pip-licenses` and `pip-audit` scans.
3. **Single-OS / Single-Python Blind Spot:** `pyproject.toml` supports Python `>=3.11` and contributors develop on Windows, yet CI tests only `ubuntu-latest` on Python `3.12`.
4. **Main-Branch `@red` Leak & Remote Ruleset Gaps:** Feature branches may carry `@red` BDD scenarios during Phase 1 RED, but CI does not yet fail if lingering `@red` scenarios target `main`, and remote ruleset `27810615` does not yet require PR status checks (`Transitive License, CVE, Secret & Test Gate`, `PR Dependency & License Review`) or `delete_branch_on_merge: true`.
5. **Schema, Link, Scheduled Baseline & Release Gaps:** `docs/planning/decisions.yaml` lacks external `check-jsonschema` validation, `pymarkdown` omits `docs/theory/` and `paper/`, external/cross-doc links lack `lychee` checks, daily `06:00 UTC` cron does not verify `.secrets.baseline` drift, and Commitizen changelogs remain `## Unreleased` without automated tagged release workflows.

## Affected Bounded Contexts
- **DevTools & Governance (`src/nectr/devtools/`, `.githooks/`, `.pre-commit-config.yaml`, `.github/workflows/`, `.github/dependabot.yml`)**: Build, governance, verification, and release infrastructure only; zero coupling into `chain`, `contracts`, `services`, or `personas` domain logic.

## OSS License & CVE Audit
| Tool / Action | License | Status | Role |
| --- | --- | --- | --- |
| `astral-sh/setup-uv` | `MIT` | **Approved** | Deterministic `uv sync --frozen` & lockfile caching in CI |
| `check-jsonschema` | `Apache-2.0` | **Approved** | JSON Schema validation for `docs/planning/decisions.yaml` & workflows |
| `lycheeverse/lychee-action` | `Apache-2.0 OR MIT` | **Approved** | Fast Markdown & cross-document link checker across `docs/`, `paper/`, `openspec/` |
| `commitizen` | `MIT` | **Approved** | Conventional Commits gate, `cz bump`, and tagged release notes |
| `pytest-cov` | `MIT` | **Approved** | Enforces `>=80%` coverage floor and emits Cobertura `coverage.xml` |
| `detect-secrets` | `Apache-2.0` | **Approved** | Pre-commit, pre-push, PR, and daily scheduled baseline drift gate |
| `pip-licenses` & `pip-audit` | `MIT` / `Apache-2.0` | **Approved** | Full transitive SPDX license & CycloneDX SBOM / CVE auditing |

## Acceptance Criteria
1. `.githooks/pre-commit`, `.githooks/pre-push`, `.githooks/commit-msg`, `.pre-commit-config.yaml`, and `.github/workflows/` maintain programmatically verified gate parity (`src/nectr/devtools/ci_parity.py`) with cross-platform `.venv` `PATH` resolution (`cygpath -u`) and `-z` / `--cached` staged file handling.
2. CI installs locked dependencies deterministically via `astral-sh/setup-uv` (`uv sync --frozen --extra dev --extra research`) so `pip-licenses` and `pip-audit` cover all runtime, dev, and research extras.
3. CI executes a test matrix across Python `3.11`, `3.12`, and `3.13` on `ubuntu-latest` plus a `windows-latest` verification runner, with `concurrency` cancellation on stale PR runs.
4. Main-branch PR and push gates enforce `--cov=src/nectr --cov-report=xml:coverage.xml --cov-fail-under=80` and reject any remaining `@red`-tagged Behave scenarios targeting `main`.
5. `check-jsonschema` validates `docs/planning/decisions.yaml`, `pymarkdown` expands to `docs/theory/` and `paper/`, and `lychee` verifies links across `docs/`, `paper/`, and `openspec/`.
6. Daily `06:00 UTC` scheduled scans verify `.secrets.baseline` audit clean-state alongside CVE/license checks; `release.yml` automates tagged Commitizen (`cz bump`) releases; and remote `main` ruleset `27810615` requires PR status checks with `delete_branch_on_merge: true`.
