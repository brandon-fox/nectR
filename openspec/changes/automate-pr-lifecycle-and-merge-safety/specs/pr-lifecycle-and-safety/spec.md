# Delta Specification: Automated PR Lifecycle, Serial Rebase & Merge-Safety Gates (`pr-lifecycle-and-safety`)

## Linked Behavior & Executable Steps

- **Feature File:** [features/pr_lifecycle_and_safety.feature](../../../../../features/pr_lifecycle_and_safety.feature)
- **Step Definitions:** [features/steps/pr_lifecycle_and_safety_steps.py](../../../../../features/steps/pr_lifecycle_and_safety_steps.py)

## Requirements

### Requirement: ADDED — Conventional PR Title, Rebase-Linear History, and Clean Merge-Tree Gate

Every pull request targeting `main` SHALL pass a required `PR Merge-Safety Gate` verifying that the PR title conforms to Commitizen Conventional Commits, the branch contains zero merge commits relative to `origin/main` (enforcing rebase-on-change), `uv lock --check` succeeds, and `git merge-tree` simulates a clean conflict-free merge.

- **Linked Scenario:** `PR merge-safety gate enforces Conventional Commit titles, linear rebased history, and conflict-free merge trees` in [pr_lifecycle_and_safety.feature](../../../../../features/pr_lifecycle_and_safety.feature#L6-L10)

### Requirement: ADDED — Automatic Squash Auto-Merge Enrollment & Serial FIFO Rebase Queue

Eligible non-draft, same-repository PRs without opt-out labels (`do-not-merge`, `wip`, `hold`) SHALL automatically enroll in verified squash auto-merge (or merge immediately if already `CLEAN`), and `BEHIND` PRs SHALL rebase onto `main` serially in FIFO creation order when `PR_LIFECYCLE_TOKEN` is present without stranding checks under fallback `GITHUB_TOKEN`.

- **Linked Scenario:** `PR lifecycle planner enables auto-merge and rebases behind PRs serially with token safety` in [pr_lifecycle_and_safety.feature](../../../../../features/pr_lifecycle_and_safety.feature#L12-L16)

### Requirement: ADDED — Automated Conflict Labeling, Fork Isolation, and Stale PR Lifecycle Management

Conflicted PRs SHALL receive a `merge-conflict` label and idempotent rebase instructions (cleared automatically upon clean rebase), untrusted fork PRs SHALL NOT trigger write actions without explicit approval, and inactive non-exempt PRs SHALL be labeled `stale` after 14 days and closed after 7 additional days of inactivity.

- **Linked Scenario:** `PR lifecycle planner isolates untrusted forks, labels merge conflicts, and manages stale PRs` in [pr_lifecycle_and_safety.feature](../../../../../features/pr_lifecycle_and_safety.feature#L18-L22)

### Requirement: ADDED — 90% Branch Coverage Floor & Stateful Multi-Hive Invariant Fuzzing

CI and repository rulesets SHALL enforce at least `90%` combined line-and-branch test coverage (`--cov-branch --cov-fail-under=90`) backed by adversarial PoUW-PoW chain tampering checks, smart contract boundary assertions, and Hypothesis stateful property-based invariant fuzzing across multi-hive barter, Queen separation of powers, and Guard Bee bridges.

- **Linked Scenario:** `Stateful property fuzzing and adversarial chain-contract checks preserve all protocol invariants` in [pr_lifecycle_and_safety.feature](../../../../../features/pr_lifecycle_and_safety.feature#L24-L28)
