# Proposal: Harden Pre-Existing Mutation Survivors (`harden-mutation-survivors`)

## Why

The initial Poodle tiered mutation gate establishes diff-scoped enforcement (`>= 85%` Tier 1, `>= 75%` Tier 2) plus non-regressing baseline floors on `main`. While `src/nectr/chain` already exceeds its Tier 1 target (`86.23%` vs `85.0%`), `src/nectr/contracts`, `src/nectr/services`, and `src/nectr/devtools` carry pre-existing mutation survivors (`850` total across `2250` trials prior to rebasing `adr.py` removal on `main`). Closing those gaps systematically eliminates blind spots without blocking concurrent feature work.

## Baseline Survivor Inventory (Post-Gate Initial Sweep)

| Tier / Package | Target | Recorded Floor | Actual Score | Killed / Timeout / Survived / Total | File Breakdown (Survived) |
| --- | --- | --- | --- | --- | --- |
| Tier 1 (`src/nectr/chain`) | `85.0%` | `85.0%` | `86.23%` | `112 / 7 / 19 / 138` | `ledger.py` (19) |
| Tier 1 (`src/nectr/contracts`) | `85.0%` | `77.0%` | `78.61%` | `261 / 0 / 71 / 332` | `engine.py` (71) |
| Tier 2 (`src/nectr/services`) | `75.0%` | `41.0%` | `42.31%` | `44 / 0 / 60 / 104` | `hive_service.py` (60) |
| Tier 2 (`src/nectr/devtools`) | `75.0%` | `57.0%` | `58.23%` | `976 / 0 / 700 / 1676` | `adr.py` (149), `decisions.py` (148), `citations.py` (146), `docs_sync.py` (114), `mutation_gate.py` (108), `spec_links.py` (35) |

Note: `adr.py` (`149` survivors) is superseded on `main` by `adrlint`, so `src/nectr/devtools` baseline floors must be re-baselined immediately after rebasing onto `main`.

## Mutator Distribution by Package

- **`src/nectr/chain` (`19` survived):** `Number` (12), `Keyword` (4), `FuncCall` (3).
- **`src/nectr/contracts` (`71` survived):** `Number` (43), `FuncCall` (11), `BinOp` (5), `Compare` (5), `Keyword` (3), `Return` (2), `AugAssign` (1), `DictArray` (1).
- **`src/nectr/services` (`60` survived):** `Number` (35), `FuncCall` (8), `BinOp` (7), `AugAssign` (3), `Compare` (3), `Keyword` (2), `Return` (2).
- **`src/nectr/devtools` (`700` survived):** `FuncCall` (293), `Number` (188), `Keyword` (79), `Compare` (40), `Return` (35), `BinOp` (30), `DictArray` (14), `Decorator` (10), `UnaryOp` (8), `AugAssign` (2), `Lambda` (1).

## Coordination with Parallel Changes

- **`adopt-mesa-abm-and-hypothesis`:** Stateful and property-based `hypothesis` tests targeting `HiveContractEngine` should execute first on `contracts/engine.py` and `services/hive_service.py` to collapse redundant numeric, binary-operator, and comparison survivors before hand-authoring residual unit assertions.
- **`main` Governance Rebase:** Re-baselining after `adr.py` removal avoids writing throwaway hardening tests against deleted code.

## Acceptance Criteria

1. Each hardened tier closes its remaining gap to target (`>= 85.0%` Tier 1, `>= 75.0%` Tier 2) with zero inline mutation-suppression pragmas in `src/`.
2. `[tool.nectr.mutation.baseline]` floors in `pyproject.toml` are ratcheted strictly upward via `floor(score) - 1` (never above `target`) as each tier improves.
3. All survivor-hardening tests preserve `pytest`, `behave --tags=-red`, and `mypy` gates.
