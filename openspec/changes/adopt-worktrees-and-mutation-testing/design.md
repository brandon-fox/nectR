# Design: Worktree Isolation & Tiered Mutation Testing (`dev-workflow`)

## Locked Architecture Decisions
1. **Clean Trunk + Ephemeral Task Worktrees:** The primary checkout remains clean on `main`. Every OpenSpec change and concurrent task runs in a short-lived worktree and is pruned immediately on merge.
2. **Hybrid Sandbox-Friendly Layout:** Automated subagents use agent harness isolated workspaces (shared-repo worktrees), while CLI and scripted tasks use `.worktrees/<branch-slug>/` inside the repo root so sandboxed paths never escape workspace boundaries.
3. **Worktrunk (`git-wt`) & Isolated Virtual Environments:** Worktrunk manages creation, hooks, and merge cleanup. User configuration sets `worktree-path = ".worktrees/{{ branch | sanitize }}"` and `merge.squash = false` for this repository; `.config/wt.toml` uses ordered `[[pre-start]]` steps to run `uv sync --frozen --extra dev` (giving every worktree its own editable `.pth` so `behave` imports that worktree's `src/nectr/`) and verify commit readiness, plus `[[pre-merge]]` to enforce mutation and orchestration gates.
4. **Commit-Preserving Merge (`--no-squash`):** `git-wt merge --no-squash` rebases onto `main`, runs `[[pre-merge]]` gates, fast-forwards `main`, and removes the worktree and branch while preserving every SSH-signed `test -> feat -> refactor` commit (`DEC-006`).
5. **Empirical 3-Worktree Mutation Spike & MADR ADRs:** `poodle`, `cosmic-ray`, and `mutmut` are evaluated in isolated spike worktrees on `contracts/engine.py` and `chain/ledger.py`, measuring Windows PowerShell parity, license/CVE compliance, infinite-loop timeout resilience (`_mine_header` / Merkle tree loops), file scoping, and throughput. Results feed `docs/experiments/mutation_engine_spike.md` and two `pyadr` ADRs.
6. **Lifecycle Placement (Zero Friction on RED/GREEN):**
   - `pre-commit`: runs fast pragma hygiene (`mutation_gate check-pragmas` + `pygrep`), **not** mutant execution.
   - `REFACTOR`, Worktrunk `[[pre-merge]]`, and `.githooks/pre-push`: run `mutation_gate diff` scoped to Python modules under `src/nectr/` modified since `merge-base`.
   - GitHub Actions (`.github/workflows/mutation-testing.yml`): runs diff-scoped checks on PRs to `main` and a full bounded-context sweep on push to `main` and nightly schedules.
7. **Bounded-Context Tiers & Timeout Semantics:**
   - **Tier 1 (`>= 85%`):** `src/nectr/contracts`, `src/nectr/chain`
   - **Tier 2 (`>= 75%`):** `src/nectr/services`, `src/nectr/devtools`
   - **Excluded:** `src/nectr/personas`, `src/nectr/ui`, `experiments`
   - **Scoring:** `score = (killed + timeout) / total * 100`. Per-mutant timeouts count as killed to guard against infinite-loop mutants; `total == 0` (no tiered source changes) passes cleanly.
8. **Anti-Gaming & Noise Filtering:** Configure the winning engine globally to skip low-value string-literal/log mutations where supported, absorb unavoidable floating-point tolerance equivalents within the tier buffer, and block inline suppression pragmas in `src/` via `pre-commit`.
9. **Rollout Sequence:** `main` starts clean with prior governance updates landed; this change executes from `.worktrees/feat-worktrees-and-mutation-testing/` with additive hook/workflow files to avoid colliding with concurrent CI changes.

## Invariants
- Every worktree maintains independent `.venv` editable resolution, `core.hooksPath = .githooks`, and SSH commit signing.
- Mutation thresholds can never be bypassed via source comments inside `src/`.
