---
name: openspec-bdd-tdd
description: >-
  Executes the mandatory Outside-In OpenSpec -> Behave BDD -> Strict TDD
  (Red-Green-Refactor with xfail_strict) -> DDD development lifecycle. Use before
  implementing any new feature, bugfix, or refactor in nectR.
---

# Outside-In OpenSpec + BDD + Strict TDD + DDD

Follow this exact sequence for every feature, fix, or refactor.

## Steps

1. **Pre-Action Security Scan & OpenSpec Proposal:**
   Create `openspec/changes/<change-id>/` following [openspec_tdd_checklist.md](./references/openspec_tdd_checklist.md). Specs (`spec.md`) MUST state requirement intent/invariants and link directly to `features/<domain>.feature` and `features/steps/<domain>_steps.py` (never hardcode user stories in `spec.md`).
2. **RED Phase (Tests First with Expected Failure):**
   Add outside-in Gherkin scenarios in `features/` (tag unimplemented scenarios `@red`) and unit tests in `tests/` marked `@pytest.mark.xfail(strict=True, reason="RED: ...")`. Run [run_bdd_tdd_gate.py](./scripts/run_bdd_tdd_gate.py):
   ```bash
   uv run python .agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py --phase red
   ```
   Commit atomically: `test(<scope>): add RED tests for <change-id>`.
3. **GREEN Phase (Implement -> Confirm XPASS -> Remove `xfail`):**
   Implement minimal DDD-compliant code in `src/nectr/`. Run `uv run pytest` to observe `XPASS` failure (`xfail_strict = true`), remove `@pytest.mark.xfail(...)` and `@red`, then run:
   ```bash
   uv run python .agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py --phase green
   ```
   Commit atomically: `feat(<scope>): implement <change-id>`.
4. **REFACTOR Phase:**
   Clean up while preserving DDD boundaries, re-run `--phase refactor`, and commit `refactor(<scope>): <summary>`.

## Validation

- Confirm `run_bdd_tdd_gate.py --phase all` exits `0` (`detect-secrets`, `pytest`, and `behave` all pass 100%).
