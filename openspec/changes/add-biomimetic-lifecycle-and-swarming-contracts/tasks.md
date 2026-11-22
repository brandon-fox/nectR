# Tasks: `add-biomimetic-lifecycle-and-swarming-contracts`

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

- [ ] 1. **Dependencies & Formal Spec Gate:** Add `icontract` to `pyproject.toml`; author `specs/quint/hive_invariants.qnt` encoding `D-01` through `D-08`; verify `pip-licenses` and `pip-audit`.
- [ ] 2. **Phase 1 — RED:** Add Gherkin scenarios to `features/protocol_invariants.feature` and step definitions to `features/steps/protocol_invariants_steps.py`; add `@pytest.mark.xfail(strict=True)` unit and Hypothesis state-machine tests in `tests/test_invariants.py`; commit `test(contracts): add RED tests for biomimetic lifecycle and swarming`.
- [ ] 3. **Phase 2 — GREEN:** Implement `DemurrageAccumulator`, `WaggleTrembleController`, `QMPHealthAndSupersedureFSM`, `TemporalPolyethismGovernor`, 3-door Senior graduation sinks, and `SwarmBivouacEscrow` in `src/nectr/contracts/engine.py`; observe `XPASS(strict)`, remove `xfail` and `@red`, verify `pytest` and `behave` exit `0`; commit `feat(contracts): implement Phase 2 biomimetic lifecycle and swarming contracts`.
- [ ] 4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict` and changed-line mutation score, merge delta spec into `openspec/specs/protocol-invariants/spec.md`, and archive change.
