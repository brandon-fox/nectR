# Tasks: Enforce OpenSpec-to-Feature Linking

- [x] Author OpenSpec proposal, design, tasks, and spec (`enforce-spec-feature-links`)
- [x] Add RED Behave scenario (`@red`) in `features/spec_linking.feature` and RED pytest (`xfail(strict=True)`) in `tests/test_spec_linking.py`
- [x] Implement `src/nectr/devtools/spec_links.py` and confirm `XPASS` failure
- [x] Remove `xfail`/`@red`, wire into `run_bdd_tdd_gate.py`, `.githooks/pre-commit`, `.pre-commit-config.yaml`, CI, and align `decision-governance/spec.md` + `openspec_tdd_checklist.md`
