# Tasks: Harden Pre-Existing Mutation Survivors (`harden-mutation-survivors`)

## Phase 0: Post-Rebase Baseline Calibration

1. Run `uv run python -m nectr.devtools.mutation_gate full` after rebasing onto `main` (removing `adr.py`, adding `ci_parity.py`) and record updated `devtools` floor (`60.0%`) in `[tool.nectr.mutation.baseline]`.
2. Verify CI `.github/workflows/mutation-testing.yml` full sweep clears committed floors on `ubuntu-latest`.

## Phase 1: Tier 1 Core Invariants (`src/nectr/contracts`, `src/nectr/chain`)

1. Coordinate with `adopt-mesa-abm-and-hypothesis` `hypothesis` tests and verify which `contracts/engine.py` (`Number`, `BinOp`, `Compare`, `AugAssign`) mutants are killed automatically.
2. Write strict Red-Green tests in `tests/` for residual `contracts/engine.py` survivors (`71` pre-rebase) until `src/nectr/contracts` clears `85.0%`.
3. Raise `[tool.nectr.mutation.baseline]."src/nectr/contracts"` to `floor(score) - 1` (up to `85.0`).
4. Optionally harden the remaining `19` survivors in `src/nectr/chain/ledger.py` (`Number` / `Keyword` / `FuncCall`) to push Tier 1 chain score above `90%`.

## Phase 2: Tier 2 Services (`src/nectr/services`)

1. Audit the `60` surviving mutants in `src/nectr/services/hive_service.py` (`Number` 35, `FuncCall` 8, `BinOp` 7, `AugAssign` 3, `Compare` 3, `Keyword` 2, `Return` 2).
2. Add Red-Green service boundary tests until `src/nectr/services` clears `75.0%`, then ratchet `[tool.nectr.mutation.baseline]."src/nectr/services"` upward.

## Phase 3: Tier 2 Devtools (`src/nectr/devtools`)

1. Run targeted `poodle` sweeps on post-rebase `decisions.py`, `citations.py`, `docs_sync.py`, `mutation_gate.py`, `ci_parity.py`, and `spec_links.py` to prioritize `Compare`, `Return`, and `BinOp` survivors.
2. Add Red-Green devtools unit tests (killing redundant mutants or simplifying untestable dead code under REFACTOR) until `src/nectr/devtools` clears `75.0%`, then ratchet `[tool.nectr.mutation.baseline]."src/nectr/devtools"` upward.
