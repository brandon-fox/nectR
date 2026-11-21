# Delta Specification: CI Action Runtimes, Cache Isolation & Dependency Review (`ci-and-hook-parity`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature)
- **Step Definitions:** [features/steps/ci_and_hook_parity_steps.py](../../../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: MODIFIED — Permissive SPDX Allowlist & Action License Exclusions in PR Review
PR dependency review (`actions/dependency-review-action@v5`) SHALL replace deprecated `deny-licenses` with an explicit MIT-compatible SPDX `allow-licenses` list (`MIT`, `MIT-0`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `BSD-3-Clause-Clear`, `0BSD`, `Zlib`, `ISC`, `PSF-2.0`, `Python-2.0`, `MPL-2.0`, `Unlicense`, `CC0-1.0`) and `allow-dependencies-licenses` for audited permissive GitHub Actions lacking Dependency Graph SPDX metadata (`pkg:githubactions/astral-sh/setup-uv`, `pkg:githubactions/softprops/action-gh-release`, `pkg:githubactions/lycheeverse/lychee-action`).
- **Linked Scenario:** `Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L21-L24)

### Requirement: ADDED — Node 24 Action Runtimes, Isolated `setup-uv` Caches & Clean Workspace Link/Docs Steps
All `.github/workflows/*.yml` files SHALL pin Node 24-compatible action versions (`astral-sh/setup-uv@v10.4.0`, `softprops/action-gh-release@v3`), assign distinct `cache-suffix` values per job (`dev-research`, `dev`, `lint`) to avoid cache reservation conflicts, direct `lychee-action@v2` output to `${{ runner.temp }}/lychee-out.md` while excluding `openspec/changes/archive/` and `docs/theory/research/`, and set `NO_MKDOCS_2_WARNING: "1"` for `mkdocs build --strict`.
- **Linked Scenario:** `GitHub Actions workflows enforce Node 24 runtimes, isolated uv caches, clean lychee temp outputs, and SPDX allow-list review` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L26-L29)
