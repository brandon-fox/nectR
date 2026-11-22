# Proposal: Harden CI Action Runtimes, Cache Isolation & Review Policies (`harden-ci-action-runtimes-and-review`)

## Why
Debugging PR `#15` (`License, Security & Quality Scan` run `44954272716` and subsequent `main` run `44955510951`) revealed workflow-level defects and noisy deprecations in `.github/workflows/` unrelated to PR content:

1. **Link Scope & Workspace Output Hygiene (`lychee`):** Archived OpenSpec changes (`openspec/changes/archive/`) shift relative directory depth when archived, and raw deep-research dumps (`docs/theory/research/`) contain synthetic placeholder URLs and bot-gated links (`202`/`203`/`405`). While `8a3ed7b` excluded those paths from `lychee`, `lychee-action@v2` still writes `lychee/out.md` inside `$GITHUB_WORKSPACE` before `pytest`, `behave`, and `ci_parity` run. Redirecting `output` to `${{ runner.temp }}/lychee-out.md` keeps the checkout clean.
2. **Deprecated Node.js 20 Action Runtimes:** `astral-sh/setup-uv@v5` (used across all 3 workflows) and `softprops/action-gh-release@v2` target Node.js 20, generating 5-6 deprecation annotations per run and Node `DEP0040`/`DEP0169` warnings. Upgrading to `astral-sh/setup-uv@v10.4.0` and `softprops/action-gh-release@v3` moves all workflows to native Node 24.
3. **Concurrent `setup-uv` Cache Key Collisions:** `license-and-security-scan` (`--extra dev --extra research`) and `test-matrix (ubuntu-latest / 3.12)` (`--extra dev`) share the same default `setup-uv` cache key, causing `Failed to save: Unable to reserve cache...` races in `44955510951`. Distinct `cache-suffix` values isolate each job's wheel cache.
4. **Deprecated `deny-licenses` & Unknown Action Licenses:** `actions/dependency-review-action@v5` warns that `deny-licenses` is deprecated (issue `#938`/`#997`) and flags `astral-sh/setup-uv` as `Unknown License` (`Null`). Replacing `deny-licenses` with a positive MIT-compatible SPDX `allow-licenses` list and explicit `allow-dependencies-licenses` for audited `MIT`/`Apache-2.0` GitHub Actions (`setup-uv`, `action-gh-release`, `lychee-action`) enforces stronger compliance without warnings.
5. **MkDocs Warning Noise:** Setting `NO_MKDOCS_2_WARNING: "1"` in the strict docs build step keeps CI logs concise.

## Affected Bounded Contexts
- **DevTools & CI Governance (`src/nectr/devtools/ci_parity.py`, `.github/workflows/*.yml`, `features/`, `tests/`):** Workflow validation and pipeline infrastructure only; zero coupling into `chain`, `contracts`, `services`, or `personas`.

## OSS License & CVE Audit
- `astral-sh/setup-uv@v10.4.0` — `MIT` (verified via GitHub API)
- `softprops/action-gh-release@v3` — `MIT` (verified via GitHub API)
- `lycheeverse/lychee-action@v2` — `Apache-2.0` (verified via GitHub API)
- `actions/dependency-review-action@v5` — `MIT` (unchanged)

## Acceptance Criteria
1. All `.github/workflows/*.yml` files use Node 24-compatible action versions (`astral-sh/setup-uv@v10.4.0`, `softprops/action-gh-release@v3`) with zero Node 20 runtime targets.
2. Concurrent `setup-uv` jobs specify distinct `cache-suffix` values (`dev-research`, `dev`, `lint`) to prevent cache reservation collisions.
3. `actions/dependency-review-action@v5` enforces positive permissive SPDX `allow-licenses` and explicit `allow-dependencies-licenses` for audited MIT/Apache-2.0 actions instead of deprecated `deny-licenses`.
4. `lychee` excludes `openspec/changes/archive/` and `docs/theory/research/`, writes `output: ${{ runner.temp }}/lychee-out.md`, and `mkdocs build --strict` sets `NO_MKDOCS_2_WARNING: "1"`.
5. `nectr.devtools.ci_parity` programmatically enforces these workflow runtime and hygiene invariants in both unit tests and Behave acceptance tests.
