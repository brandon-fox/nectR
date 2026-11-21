# Tasks: `harden-ci-action-runtimes-and-review`

1. **[x] OpenSpec Proposal & Spec Linking:**
   - Create `openspec/changes/harden-ci-action-runtimes-and-review/` (`proposal.md`, `design.md`, `tasks.md`, `specs/ci-and-hook-parity/spec.md`) linked directly to `features/ci_and_hook_parity.feature` and `features/steps/ci_and_hook_parity_steps.py`.

2. **[x] Phase 1 — RED (`xfail_strict = true` & `@red`):**
   - Add `@red` acceptance scenario in `features/ci_and_hook_parity.feature` covering Node 24 runtimes, `setup-uv` cache isolation, positive `allow-licenses` + `allow-dependencies-licenses`, `runner.temp` `lychee` output, and `NO_MKDOCS_2_WARNING`.
   - Add strict failing unit tests in `tests/test_ci_parity.py` marked `@pytest.mark.xfail(strict=True, reason="RED: harden-ci-action-runtimes-and-review")`.
   - Run `uv run python .agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py --phase red` and commit atomically (`test(ci): add RED tests for workflow runtime and review hygiene`).

3. **[x] Phase 2 — GREEN (Implement -> Confirm `XPASS` -> Remove `xfail` & `@red`):**
   - Implement `check_workflow_action_hygiene` and CLI integration in `src/nectr/devtools/ci_parity.py`.
   - Update `.github/workflows/license-and-security-scan.yml`, `.github/workflows/release.yml`, and `.github/workflows/roadmap-and-changelog.yml`.
   - Update `features/ci_and_hook_parity.feature` and `features/steps/ci_and_hook_parity_steps.py`.
   - Confirm `pytest` hits `XPASS` under `xfail_strict = true`, then remove `@pytest.mark.xfail(...)` and `@red`.
   - Run `run_bdd_tdd_gate.py --phase green`, `nectr-ci-parity check --forbid-red ...`, `ruff`, `mypy`, `mkdocs build --strict`, `detect-secrets`, and commit (`feat(ci): upgrade action runtimes to Node 24, isolate uv caches, and switch to SPDX allow-licenses`).

4. **[x] Phase 3 — REFACTOR & Verification:**
   - Review `ci_parity.py` and workflow YAML clarity, run full `--phase all` and security audit, and open PR against `main`.
