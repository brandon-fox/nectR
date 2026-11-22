# Design: PR Lifecycle State Machine, Token Safety, and Stateful Invariant Verification

## Bounded Context Impact

- **`src/nectr/devtools/` (`meta-orchestrator`):**
  - `pr_lifecycle.py` encapsulates pure PR lifecycle planning (`plan_pr_lifecycle_actions`), Conventional Commit PR title validation (`validate_pr_title`), local/CI git rebase-linearity & merge-tree checks (`verify_branch_merge_safety`), and a thin `GhCliAdapter` hexagonal port for GitHub CLI (`gh`) mutations.
  - `ci_parity.py` verifies `.github/workflows/pr-lifecycle.yml`, `PR Merge-Safety Gate`, and `--cov-branch --cov-fail-under=90`.
- **`src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`:**
  - Read-only verification via `tests/test_merge_safety_invariants.py` (adversarial boundary tests + Hypothesis `RuleBasedStateMachine` stateful property fuzzing). Zero behavioral coupling added to core domain modules.

## Key Architectural Invariants

1. **Rebase Branch + Verified Squash Merge:**
   - PR branches MUST stay linear relative to `origin/main` (`git rev-list --merges origin/main..HEAD` empty) and rebase onto `main` via `gh pr update-branch <N> --rebase`.
   - Final landing on `main` uses `--squash`, ensuring GitHub signs the resulting single Conventional Commit with its verified `web-flow` GPG key under `required_signatures` and `required_linear_history`.
2. **`GITHUB_TOKEN` Suppression Guard:**
   - Events triggered by `GITHUB_TOKEN` do not trigger `pull_request` (`synchronize`), `CodeQL`, or `push` workflows.
   - `pr-lifecycle.yml` prefers `secrets.PR_LIFECYCLE_TOKEN` and falls back to `github.token`. When running without `PR_LIFECYCLE_TOKEN` (`--has-pat` absent), `plan_pr_lifecycle_actions` emits `SKIP_REBASE_NO_PAT` instead of rebasing with `GITHUB_TOKEN`, preventing `BEHIND` PRs from being stranded with unscheduled required checks.
3. **Serial FIFO Rebase Queue without Head-of-Line Blocking:**
   - If an up-to-date eligible PR is already `CLEAN` or actively running checks (`checks_pending=True`), `BEHIND` PRs wait so CI runs $O(N)$ times rather than $O(N^2)$.
   - An up-to-date PR that has already failed checks (`UNSTABLE`, `checks_pending=False`) does NOT block healthy `BEHIND` PRs behind it.
4. **`CLEAN` vs Pending Auto-Merge GraphQL Handling:**
   - GitHub's `enablePullRequestAutoMerge` rejects PRs already in `CLEAN` state. `plan_pr_lifecycle_actions` routes `CLEAN` PRs to immediate `gh pr merge --squash --delete-branch` (`MERGE_CLEAN_NOW`) and pending PRs to `gh pr merge --auto --squash` (`ENABLE_AUTO_MERGE`).
5. **Untrusted Fork Isolation:**
   - PRs from external forks (`head_repo_full_name != repo_full_name`) are skipped by automated write/merge/rebase actions unless explicitly labeled `automerge:approved` by a maintainer.
