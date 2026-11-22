# Tasks: `add-pactflow-api-and-message-contracts`

- [ ] 1. **Dependencies & License Audit:** Add `pact-python>=4.2.0` to `[project.optional-dependencies].test` in `pyproject.toml`; verify `pip-licenses` and `pip-audit`.
- [ ] 2. **Phase 1 — RED:** Add Pact v4 HTTP & async message verification scenarios to `features/hive_persistence_api.feature` and `@pytest.mark.xfail(strict=True)` tests in `tests/test_pact_contracts.py`; commit `test(contracts): ...`.
- [ ] 3. **Phase 2 — GREEN:** Implement consumer/message Pact generators, local `FastAPIHiveRouter` + event provider verifiers, OpenAPI 3.1 exporter, and conditional PactFlow publish / `can-i-deploy` workflow steps in `.github/workflows/release.yml`; observe `XPASS(strict)`, remove `xfail` and `@red`, verify `pytest` and `behave` exit `0`; commit `feat(services): ...`.
- [ ] 4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge delta spec into `openspec/specs/`, and archive change.
