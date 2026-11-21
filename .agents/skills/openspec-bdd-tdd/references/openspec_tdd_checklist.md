# OpenSpec, Behave BDD & Strict TDD Checklist

## 1. OpenSpec Change Structure
Every behavioral change requires `openspec/changes/<change-id>/`:
- `proposal.md` — problem statement, motivation, scope
- `design.md` — DDD bounded context impact and invariants
- `tasks.md` — atomic checklist
- `specs/<domain>/spec.md` — formal requirement intent/invariants linked directly to `features/<domain>.feature` and `features/steps/<domain>_steps.py` (never hardcode user stories or Given/When/Then blocks in `spec.md`)

## 2. Strict TDD (`xfail_strict = true`) Protocol
1. **RED:** Write failing tests decorated with `@pytest.mark.xfail(strict=True, reason="RED: <spec-id>")`. Tag new unimplemented `.feature` scenarios with `@red`. `pytest` exits `0` (`xfailed`).
2. **GREEN:** Implement minimal code in `src/nectr/`. Running `pytest` MUST fail with `XPASS` (proving the test flipped from fail to pass). Remove `xfail` and `@red`, then verify `pytest` and `behave` both exit `0`.
3. **REFACTOR:** Improve design while keeping `pytest` and `behave` 100% green.
