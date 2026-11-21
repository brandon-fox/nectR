# Tasks: `add-n8n-workflow-roadmap-decisions`

- [x] 1. **OpenSpec Blueprint:** Author `proposal.md`, `design.md`, `tasks.md`, and `specs/decision-governance/spec.md` linked to `features/decision_governance.feature`.
- [x] 2. **Phase 1 — RED:** Add `@red` scenario to `features/decision_governance.feature`, step definitions in `features/steps/decision_governance_steps.py`, and `@pytest.mark.xfail(strict=True)` test in `tests/test_decision_governance.py`; verify `pytest`, `behave --tags=-red`, and commit `test(governance): ...`.
- [x] 3. **Phase 2 — GREEN:** Draft and lock `ADR-0016` via `adrlint`, update `DEC-009` + add `DEC-016` / `EXP-006` in `docs/planning/decisions.yaml`, render `decision_log.md`, expand Milestone 3 in `docs/planning/roadmap.md`, sync `docs/adr/index.md` + `mkdocs.yml`, confirm `XPASS(strict)`, remove `xfail`/`@red`, pass all gates, and commit `feat(governance): ...`.
- [ ] 4. **Phase 3 — REFACTOR & Promote:** Merge delta spec into `openspec/specs/decision-governance/spec.md`, archive change, verify full suite + `mkdocs build --strict`, push branch, and open PR.
