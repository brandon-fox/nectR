# Tasks: `adopt-mesa-abm-and-hypothesis`

1. **Dependencies & License Gate:** Add `mesa` to `pyproject.toml` (and `hypothesis` to `dev` optional deps); run `pip-licenses` and `pip-audit`.
2. **Phase 1 — RED:** Expand `features/persona_abm_simulation.feature` and `features/steps/persona_abm_simulation_steps.py`; add `xfail(strict=True)` tests in `tests/test_persona_mesa_and_hypothesis.py`; commit `test(personas): ...`.
3. **Phase 2 — GREEN:** Implement `HiveMesaModel`, `PersonaBeeAgent`, and `hypothesis` invariant suite; remove `@red` and `xfail`; verify `pytest` and `behave` pass; commit `feat(personas): ...`.
4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge `specs/persona-abm-simulation/spec.md` into `openspec/specs/`, and archive this change.
