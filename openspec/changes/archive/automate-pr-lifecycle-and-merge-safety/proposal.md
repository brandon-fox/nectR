# Proposal: Automate PR Lifecycle, Serial Rebase Queue, Auto-Merge, and 90% Merge-Safety Gates

## Problem Statement

While `nectR` enforces a `main` branch ruleset requiring signed commits, CodeQL, dependency license review, and CI test matrices, pull requests still require manual intervention across four failure modes:

1. **Manual Auto-Merge & Stale Queueing:** Newly opened PRs do not automatically enroll in squash auto-merge, and `BEHIND` PRs stall whenever `main` advances under `strict_required_status_checks_policy`.
2. **Merge Bubbles & Unsigned Rebase Conflicts:** Merging `main` into feature branches or using non-squash merges introduces merge commits on `main` or strips SSH commit signatures under `required_signatures`.
3. **Commitizen Release Drift:** Squash-merged PRs derive their `main` commit subject from the PR title, yet CI does not validate PR titles against Conventional Commits or reject merge commits inside PR branches.
4. **Coverage & Stateful Invariant Gaps:** Repository line coverage sits at `84%` without branch coverage (`--cov-branch`), leaving blockchain tampering paths in `HiveBlockchain.verify_chain()`, adversarial `HiveContractEngine` boundary guards, and stateful multi-step Hypothesis invariants untested.

## Motivation & Goals

- **Zero-Touch Safe Auto-Merge:** Automatically validate PR titles, enable verified squash auto-merge (`--auto --squash`) when checks are pending, or merge immediately when already `CLEAN`.
- **Always Rebase & Recheck Before Merging:** Advance `BEHIND` PRs serially (FIFO oldest-first, 1 PR at a time to avoid $O(N^2)$ CI storms) via `gh pr update-branch --rebase` using `PR_LIFECYCLE_TOKEN` so every required check and CodeQL re-runs on the rebased commit before merging.
- **Full PR Lifecycle Hygiene:** Automatically label and guide conflicted or malformed-title PRs, clear stale/conflict labels on recovery, and warn/close inactive PRs on a scheduled cadence.
- **90%+ Branch-Covered Safety Suite:** Raise the enforced coverage floor from `80%` line coverage to `90%` branch+line coverage (`--cov-branch --cov-fail-under=90`) and add adversarial chain/contract tests plus a Hypothesis `RuleBasedStateMachine` over multi-hive economy invariants.

## Scope

- Add `src/nectr/devtools/pr_lifecycle.py` (`nectr-pr-lifecycle` CLI + pure state machine).
- Add `.github/workflows/pr-lifecycle.yml` and a required `PR Merge-Safety Gate` job in `.github/workflows/license-and-security-scan.yml`.
- Extend `src/nectr/devtools/ci_parity.py` to enforce workflow parity, `pr-lifecycle.yml` presence, and the `90%` branch coverage gate.
- Add `tests/test_pr_lifecycle.py`, `tests/test_merge_safety_invariants.py`, and `tests/test_devtools_coverage.py`.
- Harden repository merge settings and the `main` GitHub Ruleset (`required_linear_history`, `squash`-only allowed merge method, `90%` minimum coverage, and `PR Merge-Safety Gate` required status check).
