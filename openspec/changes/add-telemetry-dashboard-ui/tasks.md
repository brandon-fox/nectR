# Tasks: `add-telemetry-dashboard-ui`

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

1. **Dependencies & License Gate:** Add `streamlit` (optional `ui` extra) to `pyproject.toml`; run `pip-licenses` and `pip-audit`.
2. **Phase 1 — RED:** Expand `features/telemetry_ui.feature` and `features/steps/telemetry_ui_steps.py`; add `xfail(strict=True)` tests in `tests/test_telemetry_ui.py`; commit `test(ui): ...`.
3. **Phase 2 — GREEN:** Implement read-only `TelemetrySnapshotLoader` and Streamlit panels in `src/nectr/ui/`; remove `@red` and `xfail`; verify `pytest` and `behave` pass; commit `feat(ui): ...`.
4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge `specs/telemetry-ui/spec.md` into `openspec/specs/`, and archive this change.
