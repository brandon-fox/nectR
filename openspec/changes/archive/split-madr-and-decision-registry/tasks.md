# Tasks: `split-madr-and-decision-registry`

- [x] 1. **Pre-Build OSS & License Audit:** Verify `pyadr` (`MIT`), `pydantic` (`MIT`), and `PyYAML` (`MIT`) transitive dependencies and Python 3.12 compatibility.
- [x] 2. **OpenSpec Proposal:** Author `proposal.md`, `design.md`, `tasks.md`, and `specs/decision-governance/spec.md`.
- [x] 3. **Dependency Setup:** Add `pyadr` to `[project.optional-dependencies] dev` via `uv add --optional dev pyadr` and verify `pip-audit` + `pip-licenses`.
- [x] 4. **Phase 1 — RED (BDD + Strict TDD):**
  - [x] Author `features/decision_governance.feature` (`@red`) and `features/steps/decision_governance_steps.py`.
  - [x] Author `tests/test_decision_governance.py` with `@pytest.mark.xfail(strict=True, ...)`.
  - [x] Verify `pytest` exits `0` (`xfailed`) and `behave --tags=-red` exits `0`; commit `test(governance): ...`.
- [x] 5. **Phase 2 — GREEN (Implementation & Migration):**
  - [x] Implement `src/nectr/devtools/decisions.py` and `nectr-decisions` CLI script.
  - [x] Initialize `.adr` and `docs/adr/0000`–`0007` MADR files + `docs/adr/index.md` via `pyadr`.
  - [x] Populate `docs/planning/decisions.yaml` (`DEC-001`–`DEC-007`, `EXP-001`) and render `docs/planning/decision_log.md`.
  - [x] Wire `nectr-decisions check` into `.pre-commit-config.yaml` and `.githooks/pre-commit`.
  - [x] Observe `XPASS` in `pytest`, remove `xfail` and `@red`, verify 100% green `pytest`, `behave`, `pyadr check-adr-repo`, and `mkdocs build --strict`; commit `feat(governance): ...`.
- [x] 6. **Phase 3 — REFACTOR & Spec Promotion:** Promote `specs/decision-governance/spec.md` into `openspec/specs/decision-governance/spec.md` and archive the completed change.
