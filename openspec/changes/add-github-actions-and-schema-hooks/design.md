# Design: GitHub Actions CI & Schema/Link Hooks (`decision-governance`, `spec-linking`)

## Workflow & Hook Architecture
- **`ci.yml`:** Runs `ruff`, `mypy --strict`, `pytest`, `behave`, `nectr-decisions check`, `nectr.devtools.spec_links`, and `mkdocs build --strict` on PRs and pushes to `main`.
- **`security-and-licenses.yml`:** Runs `detect-secrets`, `pip-licenses`, `pip-audit`, and CycloneDX SBOM generation on schedule and dependency changes.
- **`pr-policy.yml`:** Enforces Conventional Commit PR titles, signed commits, and `lychee` link checks.
- **`release.yml`:** Automates `cz bump` / changelog updates on release tags.
- **`.pre-commit-config.yaml`:** Adds `check-jsonschema` hook for `docs/decisions/decisions.yaml`.

## Invariants
1. **Local-CI Parity:** Every gate in `.githooks/pre-commit` and `.githooks/pre-push` MUST have a matching CI step in `.github/workflows/`.
2. **Zero Secret Leaks:** CI workflows never print credentials or use `--no-verify`-style bypasses.
