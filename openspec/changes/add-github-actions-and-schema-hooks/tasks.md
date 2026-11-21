# Tasks: `add-github-actions-and-schema-hooks`

1. **[x] Phase 0 — Baseline Hook, Coverage & Workflow Fixes (Landed in `#14`):**
   - Hardened `.githooks/pre-commit`, `.githooks/pre-push`, and `.githooks/commit-msg` with `cygpath -u` `.venv` `PATH` resolution, `-z` / `--cached` staged file scanning, and `mkdocs build --strict`.
   - Split `ruff-check` and `ruff-format-check` and added `mkdocs-build-strict` in `.pre-commit-config.yaml`.
   - Added `concurrency`, `pip` caching, `--cov-fail-under=80` (`coverage.xml`), expanded SPDX `deny-licenses` (including `LGPL-*`), and `openspec/changes/archive/*` exclusion in `.github/workflows/` + `.gitignore`.

2. **[ ] Dependencies & OSS License Gate:**
   - Add `check-jsonschema` (`Apache-2.0`) to `[project.optional-dependencies] lint` in `pyproject.toml`, run `uv lock`, and verify zero CVEs and 100% permissive transitive licenses via `uv run pip-licenses` and `uv run pip-audit`.
   - Author `docs/planning/decisions.schema.json` matching `src/nectr/devtools/decisions.py` validation rules.

3. **[ ] Phase 1 — RED (`xfail_strict = true` & `@red`):**
   - Commit `@red` acceptance scenarios in `features/ci_and_hook_parity.feature` and step stubs in `features/steps/ci_and_hook_parity_steps.py`.
   - Write strict failing unit tests in `tests/test_ci_parity.py` decorated with `@pytest.mark.xfail(strict=True, reason="RED: add-github-actions-and-schema-hooks")` covering:
     - `.githooks/` <-> `.pre-commit-config.yaml` <-> `.github/workflows/` gate parity
     - `astral-sh/setup-uv` `--frozen --extra dev --extra research` and Python `3.11`–`3.13` + `windows-latest` matrix presence
     - `--forbid-red` main-branch guard rejecting `@red` feature scenarios and requiring `>=80%` XML coverage
     - `check-jsonschema` validation on `docs/planning/decisions.yaml`, `lychee` link check, daily `.secrets.baseline` drift check, and `release.yml` Commitizen workflow
   - Run `uv run python .agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py --phase red` and commit atomically: `test(ci): add RED parity, matrix, and main-branch guard tests`.

4. **[ ] Phase 2 — GREEN (Implement -> Confirm `XPASS` -> Remove `xfail` & `@red`):**
   - Implement `src/nectr/devtools/ci_parity.py` (`check_pipeline_parity`, `check_no_red_scenarios`, CLI entrypoint `nectr-ci-parity`).
   - Update `.github/workflows/license-and-security-scan.yml` to use `astral-sh/setup-uv` (`uv sync --frozen --extra dev --extra research`), add the Python `3.11`/`3.12`/`3.13` + `windows-latest` matrix, enforce `nectr-ci-parity --forbid-red` on `main` PRs/pushes, run `check-jsonschema` on `docs/planning/decisions.yaml`, expand `pymarkdown` to `docs/theory` and `paper`, add `lycheeverse/lychee-action`, and verify `.secrets.baseline` drift in daily cron.
   - Add `.github/workflows/release.yml` for Commitizen (`cz bump` / tag changelog & GitHub Release automation) and wire `check-jsonschema`, `nectr-ci-parity`, and `pymarkdown` updates into `.githooks/pre-commit` and `.pre-commit-config.yaml`.
   - Implement full Behave step definitions in `features/steps/ci_and_hook_parity_steps.py`.
   - Run `uv run pytest` to confirm `XPASS` failure under `xfail_strict = true`, then remove `@pytest.mark.xfail(...)` from `tests/test_ci_parity.py` and `@red` from `features/ci_and_hook_parity.feature`.
   - Run `uv run python .agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py --phase green` and `uv run mkdocs build --strict`; commit atomically: `feat(ci): enforce uv-locked CI matrix, schema/link gates, and @red guard`.

5. **[ ] Phase 3 — REFACTOR, Remote Ruleset Alignment & Archive:**
   - With maintainer approval, update remote GitHub Ruleset `27810615` (`pull_request` + `required_status_checks`), enable `delete_branch_on_merge: true` on `brandon-fox/nectR`, and prune stale merged `origin/dependabot/*` branches.
   - Promote `specs/ci-and-hook-parity/spec.md` and merge delta specs into `openspec/specs/decision-governance/spec.md` and `openspec/specs/spec-linking/spec.md`, archive `openspec/changes/add-github-actions-and-schema-hooks/` under `openspec/changes/archive/`, and commit `docs(spec): promote ci-and-hook-parity spec and archive change`.
