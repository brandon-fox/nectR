# Proposal: Mirror Local Governance Hooks into GitHub Actions & Schema Checks (`add-github-actions-and-schema-hooks`)

## Why
Local `.githooks/` and `.pre-commit-config.yaml` enforce `detect-secrets`, `mypy --strict`, `nectr.devtools.decisions check`, `nectr.devtools.spec_links`, `pytest`, and `behave`. Mirroring these gates into GitHub Actions (`ci.yml`, `security-and-licenses.yml`, `pr-policy.yml`, `release.yml`) and adding `check-jsonschema` + `lychee` prevents bypasses on PRs and releases.

## Affected Bounded Contexts
- **DevTools & Governance (`src/nectr/devtools/`, `.github/workflows/`, `.pre-commit-config.yaml`)**.

## OSS License & CVE Audit
| Tool / Package | License | Status | Notes |
| --- | --- | --- | --- |
| `check-jsonschema` | `Apache-2.0` | **Approved** | Validates `docs/decisions/decisions.yaml` against JSON Schema |
| `lychee` (`lycheeverse/lychee-action`) | `Apache-2.0 OR MIT` | **Approved** | Fast Markdown/docs broken-link checker in CI |
| `commitizen` | `MIT` | **Approved** | Already in `pyproject.toml`; automated changelog & tag releases |

## Acceptance Criteria
1. GitHub Actions workflows (`ci.yml`, `security-and-licenses.yml`, `pr-policy.yml`, `release.yml`) enforce all local `.githooks/` and `.pre-commit-config.yaml` checks on every PR and push.
2. `check-jsonschema` validates `docs/decisions/decisions.yaml` in pre-commit and CI.
3. `lychee` checks `docs/`, `paper/`, and `openspec/` links alongside `mkdocs build --strict`.
