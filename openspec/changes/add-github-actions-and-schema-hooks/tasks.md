# Tasks: `add-github-actions-and-schema-hooks`

1. **Dependencies & License Gate:** Add `check-jsonschema` to `dev` optional deps (or pre-commit) and verify `pip-licenses` / `pip-audit`.
2. **Phase 1 — RED:** Add `xfail(strict=True)` workflow/hook parity tests in `tests/test_ci_parity.py` and Behave scenarios in `features/decision_governance.feature` / `features/spec_linking.feature`; commit `test(ci): ...`.
3. **Phase 2 — GREEN:** Author `.github/workflows/ci.yml`, `pr-policy.yml`, `release.yml`, update `security-and-licenses.yml`, and wire `check-jsonschema` + `lychee`; remove `xfail`; verify `pytest`, `behave`, and `mkdocs build --strict`; commit `ci(governance): ...`.
4. **Phase 3 — REFACTOR & Archive:** Merge delta specs into `openspec/specs/decision-governance/spec.md` and `openspec/specs/spec-linking/spec.md`, and archive this change.
