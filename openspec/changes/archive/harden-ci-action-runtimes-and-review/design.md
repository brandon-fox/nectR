# Design: CI Action Runtime, Cache Isolation & Dependency Review Hardening

## Architecture & DDD Boundaries
All changes stay strictly within the **DevTools & CI Governance** boundary (`src/nectr/devtools/ci_parity.py`, `.github/workflows/`, `tests/test_ci_parity.py`, `features/ci_and_hook_parity.feature`, `features/steps/ci_and_hook_parity_steps.py`). No domain context (`chain`, `contracts`, `services`, `personas`) is touched.

## Validator Design (`src/nectr/devtools/ci_parity.py`)
Add `check_workflow_action_hygiene(repo_root: Path) -> list[str]` (invoked from `check_pipeline_parity` / `main`) returning structured violation strings when any `.github/workflows/*.yml` violates:
1. **No Node 20 Deprecated Action Refs:** Reject `astral-sh/setup-uv@v[1-6]` and `softprops/action-gh-release@v[12]`.
2. **Cache Key Isolation:** Require distinct `cache-suffix` inputs on `setup-uv` steps across `license-and-security-scan` (`dev-research`), `test-matrix` (`dev`), and `roadmap-and-changelog` (`lint`).
3. **Positive SPDX Allowlist Review:** Require `allow-licenses` (containing `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `PSF-2.0`, `Python-2.0`, `MPL-2.0`, `0BSD`, `Zlib`, `Unlicense`, `CC0-1.0`) and `allow-dependencies-licenses` in `dependency-review`, while forbidding deprecated `deny-licenses`.
4. **Workspace-Clean `lychee` & Quiet `mkdocs`:** Require `openspec/changes/archive/` and `docs/theory/research/` exclusions plus `${{ runner.temp }}/lychee-out.md` output for `lychee-action@v2`, and `NO_MKDOCS_2_WARNING` alongside `mkdocs build --strict`.

## Invariants
1. Existing `check_pipeline_parity` synthetic workspace compatibility is preserved by keeping `check_workflow_action_hygiene` focused on repository workflow hygiene and exposing it explicitly for `nectr-ci-parity check`, unit tests, and BDD acceptance checks.
2. No PR document, research dump, or archived OpenSpec file needs mutation to satisfy CI link checks; the action configuration itself enforces proper scoping.
