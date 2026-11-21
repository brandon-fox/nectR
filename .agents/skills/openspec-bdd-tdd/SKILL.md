---
name: openspec-bdd-tdd
description: Executes the mandatory Outside-In OpenSpec -> Behave BDD -> Strict TDD (Red-Green-Refactor with xfail_strict) -> DDD development lifecycle.
---

# Outside-In OpenSpec + BDD + Strict TDD + DDD Skill

Follow this exact sequence for every feature, fix, or refactor (no exceptions):

1. **Pre-Action Security Scan:** `detect-secrets scan` / `pre-commit run --all-files`
2. **OpenSpec Proposal:** Create `openspec/changes/<change-id>/` with `proposal.md`, `design.md`, `tasks.md`, and `specs/<domain>/spec.md`.
3. **RED Commit (Tests First with Expected Failure):**
   - Add outside-in Gherkin scenarios to `features/<domain>.feature` and steps in `features/steps/`.
   - Add unit/invariant tests in `tests/` decorated with `@pytest.mark.xfail(strict=True, reason="RED: ...")`.
   - Run `python -m pytest` (must exit `0` with `xfailed`).
   - Commit atomically: `test(<scope>): add RED tests for <change-id>`.
4. **GREEN Commit (Implement -> Observe XPASS Failure -> Remove `xfail` -> Pass):**
   - Implement minimal DDD-compliant code in `src/nectr/`.
   - Run `python -m pytest` and observe `XPASS` failure (`xfail_strict = true` confirms the test flipped from failing to passing!).
   - Remove `@pytest.mark.xfail(...)` (and any `@red` tag in `.feature`).
   - Run `python -m pytest` and `python -m behave` (100% green).
   - Commit atomically: `feat(<scope>): implement <change-id>`.
5. **REFACTOR Commit:**
   - Clean up code while preserving DDD boundaries and keeping `pytest` + `behave` 100% green.
   - Commit atomically: `refactor(<scope>): <summary>`.
6. **Post-Action Gate:** Run `detect-secrets-hook --baseline .secrets.baseline` on changed files, `python -m pytest`, and `python -m behave`.
