---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Meta-Orchestrator
---

# Adopt pre-commit.ci for Cloud Hook Autofix and Autoupdate

## Context and Problem Statement

Local `.githooks/` and GitHub Actions workflows enforce full `uv`-locked verification, but contributors and isolated worktrees (`ADR-0017`) lacked instant cloud formatting autofixes and automated hook revision maintenance. Running `.pre-commit-config.yaml` directly on `pre-commit.ci` previously failed because every hook relied on `repo: local` (`language: system`), while default `[pre-commit.ci]` commit headers violate Commitizen `cz check` (`ADR-0001`).

## Considered Options

* **Split `pre-commit.ci` cloud execution (permissive remote + `pygrep` hooks) with `ci.skip` for `uv`-venv `language: system` hooks and Conventional Commit bot messages**
* **Run `pre-commit` exclusively inside GitHub Actions with bespoke bot push tokens**
* **Keep all hooks `repo: local` (`language: system`) without cloud autofix or autoupdate**

## Decision Outcome

Chosen option: "Split `pre-commit.ci` cloud execution (permissive remote + `pygrep` hooks) with `ci.skip` for `uv`-venv `language: system` hooks and Conventional Commit bot messages", because `pre-commit.ci` caches MIT/Apache-2.0 upstream hook repositories (`pre-commit-hooks`, `ruff-pre-commit`, `check-jsonschema`, entropy baseline scanner) and built-in `pygrep` rules for sub-second PR autofixes and weekly `chore/pre-commit-autoupdate` PRs. Workspace-venv `language: system` hooks remain in `ci.skip` and run in `.githooks/`, `.config/wt.toml`, and GitHub Actions (`DEC-018`). `nectr-ci-parity` enforces `ci:` settings, Conventional Commit bot messages (`style(pre-commit.ci): ...`, `chore(deps): ...`), `.worktrees` exclusions, and `.config/wt.toml` `[[pre-merge]]` checks.

### Consequences

* Good, because PRs receive signed Conventional Commit formatting autofixes and weekly pinned hook updates without custom CI tokens.
* Good, because `nectr-ci-parity` rejects unskipped `language: system` hooks, unapproved hook repos, or non-Conventional bot commit messages before merge.
* Bad, because contributors working in `.worktrees/<branch-slug>/` must `git pull --rebase` when `pre-commit-ci[bot]` pushes an autofix commit to their open PR branch.
