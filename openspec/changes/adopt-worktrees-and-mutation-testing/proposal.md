# Proposal: Adopt Worktree Isolation & Tiered Mutation Testing (`adopt-worktrees-and-mutation-testing`)

## Why

Concurrent multi-agent development in a single working tree risks staging collisions, cross-branch file contamination, and mixed commits on `main`. Simultaneously, line coverage alone cannot verify that unit and invariant tests actually catch subtle boundary regressions (off-by-one balances, fee-routing sign flips, or collusion decay bypasses) in `nectR`'s deterministic smart contracts and consensus ledger.

Embedding ephemeral Git worktrees (via Worktrunk `git-wt`) and tiered, diff-scoped mutation testing directly into the Outside-In (`OpenSpec -> Behave BDD -> Strict TDD -> DDD`) workflow isolates every task and verifies test strength continuously without slowing down `RED` or `GREEN` TDD iterations.

## Affected Bounded Contexts

- **DevTools & Governance (`src/nectr/devtools/`, `.githooks/`, `.pre-commit-config.yaml`, `.config/wt.toml`, `.github/workflows/mutation-testing.yml`, `pyproject.toml`, `.gitignore`)**
- **Workflow Rules, Skills & Planning Docs (`AGENTS.md`, `.agents/`, `docs/adr/`, `docs/experiments/`, `docs/planning/`, `openspec/`)**

## OSS License & CVE Audit

| Tool / Package | License | Status | Notes |
| --- | --- | --- | --- |
| Worktrunk (`git-wt`) | `MIT OR Apache-2.0` | **Approved** | External Rust CLI binary for git worktree lifecycle & hooks (not a Python dependency) |
| `poodle` | `MIT` | **Spike Candidate** | Cross-platform multi-threaded Python mutation engine using isolated temp copies |
| `cosmic-ray` | `MIT` | **Spike Candidate** | SQLite session-based AST mutation framework |
| `mutmut` (v3+) | `BSD-3-Clause` | **Spike Candidate** | `os.fork()`-based mutation runner (Unix/WSL/Linux CI only) |

## Acceptance Criteria

1. `.worktrees/` is gitignored and excluded from `ruff`, `pytest`, and `detect-secrets` scans; `.config/wt.toml` provisions isolated per-worktree `uv` environments and enforces pre-merge verification gates.
2. A 3-worktree empirical spike benchmarks `poodle`, `cosmic-ray`, and `mutmut` against `src/nectr/contracts/engine.py` and `src/nectr/chain/ledger.py`, documented in `docs/experiments/mutation_engine_spike.md` and two `pyadr` MADR ADRs (`<= 70` lines, `<= 380` words).
3. `nectr.devtools.mutation_gate` enforces tiered kill-score thresholds (`>= 85%` for `contracts/` and `chain/`; `>= 75%` for `services/` and `devtools/`; excluding `personas/`, `ui/`, and `experiments/`) in diff-scoped `REFACTOR`, Worktrunk `pre-merge`, `pre-push`, and `.github/workflows/mutation-testing.yml`, while rejecting inline suppression pragmas in `pre-commit`.
4. All surviving Tier-1/Tier-2 mutants revealed by the initial full sweep are killed via behavioral boundary tests without weakening thresholds or adding pragmas.
