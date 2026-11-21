# Design: End-to-End Hook, CI Matrix, Scheduled Audit & Release Architecture

## Pipeline Chain Topology

```
[Local Commit] ──> .githooks/pre-commit + commit-msg (.pre-commit-config.yaml parity)
   │  - cygpath-safe .venv PATH resolution
   │  - git diff --cached -z | detect-secrets-hook & local-path regex
   │  - adrlint (lint, format --check, lock --check) + check-jsonschema (decisions.yaml)
   │  - nectr-decisions, nectr-citations, nectr-docs, nectr.devtools.spec_links, nectr-ci-parity
   │  - ruff check + ruff format --check + pymarkdown (incl. docs/theory, paper) + mypy --strict
   │  - conditional mkdocs build --strict (when docs/ or mkdocs.yml staged)
   │  - pytest + behave --tags=-red + cz check
   ▼
[Local Push] ────> .githooks/pre-push
   │  - full tracked-tree detect-secrets-hook (-z) & local-path scan
   │  - mkdocs build --strict + pytest + behave
   ▼
[PR / Push CI] ──> .github/workflows/ (concurrency-guarded, astral-sh/setup-uv --frozen)
   │  - Gate 1 (Quality, Governance & Coverage): uv sync --frozen --extra dev --extra research,
   │    adrlint, check-jsonschema, nectr-* checks, ruff, pymarkdown, lychee, mypy, mkdocs --strict,
   │    pytest --cov-fail-under=80 (coverage.xml), behave + nectr-ci-parity --forbid-red (on main)
   │  - Gate 2 (OS & Python Matrix): ubuntu-latest [3.11, 3.12, 3.13] + windows-latest [3.12]
   │  - Gate 3 (PR Dependency & License Review): dependency-review-action@v5 blocking GPL/AGPL/LGPL/SSPL
   ▼
[Scheduled] ─────> Daily 06:00 UTC Cron & Weekly Dependabot
   │  - Full uv.lock + .[research] pip-audit CVE & CycloneDX SBOM + pip-licenses report
   │  - detect-secrets scan baseline drift verification against .secrets.baseline
   │  - Weekly Dependabot updates for uv/pip and github-actions (auto-deleted on merge)
   ▼
[Release] ───────> .github/workflows/release.yml + roadmap-and-changelog.yml
      - Commitizen version bump / tag verification, CHANGELOG.md & OpenSpec status artifacts,
        and signed GitHub Release publication
```

## Domain Component: `src/nectr/devtools/ci_parity.py`
A read-only DevTools validator (`nectr-ci-parity` / `python -m nectr.devtools.ci_parity`) in the `devtools` bounded context that inspects:
- `.githooks/pre-commit`, `.githooks/pre-push`, `.githooks/commit-msg`
- `.pre-commit-config.yaml`
- `.github/workflows/*.yml`
- `features/*.feature` (`--forbid-red` mode enforced on `main` PRs and pushes)
- `docs/planning/decisions.schema.json` against `docs/planning/decisions.yaml` via `check-jsonschema`

## Architectural Invariants
1. **Local-CI Gate Parity:** Every static, governance, security, documentation, and test gate in `.githooks/` and `.pre-commit-config.yaml` MUST have an equivalent enforced step in `.github/workflows/`.
2. **Cross-Platform Shell & Path Determinism:** Shell hooks MUST resolve `.venv` (`Scripts` on Windows via `cygpath -u`, `bin` on POSIX) without requiring interactive shell activation and MUST process paths with null delimiters (`-z` / `xargs -0`).
3. **Locked Full-Extra Supply-Chain Audit:** CI MUST install from `uv.lock` (`--frozen`) with both `dev` and `research` extras so no optional scientific package bypasses `pip-licenses` or `pip-audit`.
4. **Main-Branch `@red` & Coverage Floor Integrity:** Feature branches MAY carry `@red` scenarios during Phase 1 RED, but any PR or push targeting `main` MUST fail if `@red` scenarios remain or if `src/nectr` line coverage drops below `80%` (matching GitHub Ruleset `27810615`).
5. **Zero Secret or Local-Path Leakage:** No workflow, hook, or test artifact may emit credentials, user home paths, or bypass flags (`--no-verify`).
6. **Remote Ruleset Alignment:** Repository `main` ruleset `27810615` requires signed commits, CodeQL, `>=80%` coverage, PR status checks (`Transitive License, CVE, Secret & Test Gate`, `PR Dependency & License Review`), and `delete_branch_on_merge: true`.
