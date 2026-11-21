# Tasks: `add-sqlmodel-persistence-and-api`

1. **Dependencies & License Gate:** Add `sqlmodel`, `alembic`, `structlog`, and `opentelemetry-sdk` to `pyproject.toml`; run `pip-licenses` and `pip-audit`.
2. **Phase 1 — RED:** Expand `features/hive_persistence_api.feature` and `features/steps/hive_persistence_api_steps.py`; add `xfail(strict=True)` tests in `tests/test_hive_persistence_api.py`; commit `test(services): ...`.
3. **Phase 2 — GREEN:** Implement `HiveRepositoryPort`, `SQLModelHiveRepository`, `alembic` initial migration, `FastAPI` router, and `structlog`/`opentelemetry` hooks; remove `@red` and `xfail`; verify `pytest` and `behave` pass; commit `feat(services): ...`.
4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge `specs/hive-persistence-api/spec.md` into `openspec/specs/`, and archive this change.
