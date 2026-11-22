# Proposal: Integrate `pre-commit.ci` Cloud Bot Across Repo, Specs, Decisions & Worktrees

## Problem Statement

While `nectR` enforces local Git hooks (`.githooks/`) and full-environment GitHub Actions workflows (`license-and-security-scan.yml`, `mutation-testing.yml`), pull requests currently lack sub-second automated formatting remediation and scheduled hook revision maintenance:

1. **All-`local` `language: system` Hook Barrier:** Every hook in `.pre-commit-config.yaml` (except two `pygrep` regex checks) currently uses `repo: local` with `language: system`. Because `pre-commit.ci` executes inside an isolated, network-restricted container without running `uv sync --frozen --extra dev`, unskipped `language: system` hooks fail immediately in the cloud.
2. **Commitizen Release Breakage Risk:** Default `pre-commit.ci` commit messages (`[pre-commit.ci] auto fixes...` and `[pre-commit.ci] pre-commit autoupdate`) violate Conventional Commits and would break `cz check --rev-range` in `.github/workflows/release.yml` (`ADR-0001`).
3. **Worktree Drift & Pre-Merge Parity:** Ephemeral Worktrunk worktrees (`.worktrees/<branch-slug>/`, `ADR-0017`) need `.pre-commit-config.yaml` exclusion parity, pre-merge `nectr-ci-parity` validation in `.config/wt.toml`, and documented fast-forward/rebase reconciliation when `pre-commit-ci[bot]` pushes signed autofix commits to an open PR branch.

## Proposed Solution

1. **Split Cloud vs. System Hook Architecture (`.pre-commit-config.yaml`):**
   - Configure top-level `exclude: ^(\.worktrees|\.poodle-temp)/` and `ci:` settings with Conventional Commit bot messages (`style(pre-commit.ci): auto fixes from pre-commit hooks`, `chore(deps): pre-commit.ci weekly hook autoupdate`), `autoupdate_branch: "chore/pre-commit-autoupdate"`, `autoupdate_schedule: weekly`, and `submodules: false`.
   - Adopt pinned, MIT/Apache-2.0 upstream hook repositories (`pre-commit/pre-commit-hooks@v6.0.0`, `Yelp/detect-secrets@v1.5.0`, `python-jsonschema/check-jsonschema@0.39.0`, `astral-sh/ruff-pre-commit@v0.17.6`) aligned to `uv.lock` versions alongside zero-dependency `language: pygrep` hooks so `pre-commit.ci` executes fast lint/format/secret/schema checks and auto-fixes PRs.
   - Explicitly list every workspace-venv `language: system` hook in `ci.skip` so full-environment gates continue running deterministically in `.githooks/`, `.config/wt.toml`, and GitHub Actions.
2. **Automated `nectr-ci-parity` Enforcement (`src/nectr/devtools/ci_parity.py`):**
   - Add `check_pre_commit_ci_config(repo_root)` to verify `ci:` settings, Conventional Commit bot messages, permissive remote hook allowlisting, version pinning, worktree exclusions, and exact 1-to-1 `ci.skip` coverage for `language: system` hooks.
3. **Worktree & Governance Integration (`ADR-0019`, `DEC-018`, `.config/wt.toml`):**
   - Add `ci_parity = "uv run python -m nectr.devtools.ci_parity check"` to `.config/wt.toml` `[[pre-merge]]`.
   - Record MADR `ADR-0019` (`adrlint` locked) and fast operational rule `DEC-018` (`decisions.yaml` + `decision_log.md`).
