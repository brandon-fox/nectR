# Design: Survivor Hardening & Upward-Only Baseline Ratchet (`harden-mutation-survivors`)

## Baseline Floor Noise Margin & Ratchet Procedure

1. **Formula:** Every committed entry in `[tool.nectr.mutation.baseline]` is calculated from a verified `uv run python -m nectr.devtools.mutation_gate full` run on clean `main` as `max(0.0, min(tier_target, math.floor(actual_score) - 1.0))`.
2. **Rationale for `-1` Margin:** Poodle execution timings differ slightly between local Windows workstations and GitHub-hosted Linux runners (`ubuntu-latest`), occasionally shifting whether borderline slow tests trigger `Trial Exceeded Timeout`. Subtracting `1.0` percentage point absorbs runner timing variance without permitting semantic regressions.
3. **Upward-Only Ratchet:** Whenever a hardening PR or scheduled `main` sweep raises `floor(actual_score) - 1.0` above the committed baseline floor, maintainers raise `[tool.nectr.mutation.baseline]` to the new value (capped at the tier target `85.0%` / `75.0%`). Floors may never be lowered unless source files are removed or refactored out of the tier.

## Phased Hardening Strategy

1. **Rebase & Re-Baseline First:** After `adopt-worktrees-and-mutation-testing` rebases onto `main` (which removes `adr.py`), recompute `[tool.nectr.mutation.baseline]` from a fresh full sweep.
2. **Tier 1 Priority (`contracts/engine.py` — `71` survivors):** Coordinate with `adopt-mesa-abm-and-hypothesis` so `hypothesis` stateful properties exercise arithmetic tolerances, fee rates, reserve bounds, and error messages; then add targeted unit tests for any surviving `FuncCall`, `Keyword`, and `Return` mutants. Remaining `chain/ledger.py` survivors (`19`, predominantly numeric constants) can be hardened afterward toward `90%+`.
3. **Tier 2 Services (`services/hive_service.py` — `60` survivors):** Assert exact pass-through parameters, boundary fees, and error messages in `HiveServiceLayer` wrappers until full-module score reaches `>= 75.0%`.
4. **Tier 2 Devtools (`decisions.py`, `citations.py`, `docs_sync.py`, `mutation_gate.py`, `spec_links.py`):** Prioritize `FuncCall`, `Compare`, `Return`, and `BinOp` mutants around subprocess error handling, exit-code checks, and filesystem boundary conditions. Many surviving `Keyword`/`FuncCall` mutations on logging or CLI help text remain benign until dead options are simplified.

## Specification Delta

Behavioral invariants for upward-only baseline ratcheting and zero-pragma survivor hardening are specified in [specs/dev-workflow/spec.md](specs/dev-workflow/spec.md), linked directly to the executable BDD specification under [features/dev_workflow.feature](../../../features/dev_workflow.feature) and [features/steps/dev_workflow_steps.py](../../../features/steps/dev_workflow_steps.py).
