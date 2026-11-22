# Tasks: Automate PR Lifecycle & Merge-Safety Gates

- [x] 1. Create OpenSpec proposal, design, tasks, and linked `pr-lifecycle-and-safety` delta spec.
- [x] 2. Author RED Behave Gherkin feature (`features/pr_lifecycle_and_safety.feature`) and strict-`xfail` unit tests (`tests/test_pr_lifecycle.py`).
- [ ] 3. Implement `src/nectr/devtools/pr_lifecycle.py` (`nectr-pr-lifecycle` CLI, title check, rebase-linear merge-tree gate, serial rebase queue, auto-merge, conflict & stale management).
- [ ] 4. Add `.github/workflows/pr-lifecycle.yml`, add `PR Merge-Safety Gate` + `90%` branch coverage to `.github/workflows/license-and-security-scan.yml`, and extend `src/nectr/devtools/ci_parity.py`.
- [ ] 5. Add adversarial chain/contract boundary tests, Hypothesis `RuleBasedStateMachine` stateful invariants (`tests/test_merge_safety_invariants.py`), and devtools edge-case tests (`tests/test_devtools_coverage.py`).
- [ ] 6. Verify `XPASS` -> remove `xfail` & `@red`, confirm `>= 90%` branch+line coverage, `mypy --strict`, `pytest`, `behave`, and `detect-secrets` all pass.
- [ ] 7. Update repository merge settings and `main` ruleset (`required_linear_history`, `squash`-only, `90%` minimum coverage, `PR Merge-Safety Gate`), merge PR, and activate auto-merge lifecycle on open PRs.
