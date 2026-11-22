---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Meta-Orchestrator
---

# Isolate Concurrent Work in Ephemeral Worktrunk Git Worktrees

## Context and Problem Statement

Concurrent contributors and parallel agents sharing one checkout risk staging collisions, mixed commits on `main`, and stale editable `.venv` resolution across branches. How should `nectR` isolate concurrent tasks while preserving `DEC-006` atomic SSH-signed history and workspace sandbox boundaries?

## Considered Options

* **Worktrunk (`git-wt`, `MIT OR Apache-2.0`) ephemeral `.worktrees/<branch-slug>/` + per-worktree `.venv` + `--no-squash` merges**
* **Shared single checkout with manual branch switching and file locks**
* **Sibling worktrees placed outside the repository root (`../`)**

## Decision Outcome

Chosen option: "Worktrunk (`git-wt`, `MIT OR Apache-2.0`) ephemeral `.worktrees/<branch-slug>/` + per-worktree `.venv` + `--no-squash` merges", because placing CLI worktrees under gitignored `.worktrees/` respects sandbox boundaries while `.config/wt.toml` runs ordered `[[pre-start]]` (`uv sync --frozen --extra dev`, `verify_commit_readiness.py`) and `[[pre-merge]]` (`mutation_gate diff`, `verify_orchestration_gate.py`) hooks. Merging with `--no-squash` preserves every SSH-signed `test -> feat -> refactor` commit (`DEC-006`). Automated subagents use agent harness shared-repo worktrees, and `.gitignore`, `ruff`, `pytest`, `detect-secrets`, and `nectr-docs tree` exclude `.worktrees`.

### Consequences

* Good, because each concurrent task gets an isolated index, working tree, and editable `.venv` `.pth` without cross-contamination.
* Good, because `git-wt merge main --no-squash` runs pre-merge verification and prunes worktrees automatically.
* Bad, because contributors must install `git-wt` (`MIT OR Apache-2.0`) and sync each worktree environment before testing.
