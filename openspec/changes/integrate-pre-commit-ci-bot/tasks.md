# Tasks: `integrate-pre-commit-ci-bot`

- [x] **Task 1 (Spec):** Author OpenSpec proposal, design, delta specs, and canonical `ci-and-hook-parity` / `dev-workflow` specs linked to Behave features.
- [x] **Task 2 (RED):** Add `@red` Behave scenarios in `features/ci_and_hook_parity.feature` and `features/dev_workflow.feature` plus `@pytest.mark.xfail(strict=True)` unit tests in `tests/test_ci_parity.py` and `tests/test_dev_workflow.py`.
- [x] **Task 3 (GREEN):** Implement `check_pre_commit_ci_config` in `src/nectr/devtools/ci_parity.py`, configure `.pre-commit-config.yaml` and `.config/wt.toml`, observe `XPASS`, and remove `xfail` / `@red`.
- [x] **Task 4 (Governance & REFACTOR):** Record and lock `ADR-0019` (`adrlint`) and `DEC-018` (`nectr-decisions`), sync docs (`nectr-docs sync`), verify `mkdocs build --strict`, and pass `mutation_gate diff` (`>= 75%` Tier-2).
