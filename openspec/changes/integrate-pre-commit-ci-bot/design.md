# Design: `pre-commit.ci` Split-Execution & Worktree Governance

## Bounded Context Impact

- **Affected Context:** `src/nectr/devtools/` (`ci_parity.py`), `.pre-commit-config.yaml`, `.config/wt.toml`, `docs/adr/`, `docs/planning/`.
- **Zero Domain Coupling:** Core protocol bounded contexts (`src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, `src/nectr/personas/`) remain untouched.

## Architectural Invariants

1. **Permissive Remote Hook Allowlist (`DEC-007`):** Only MIT/Apache-2.0 upstream hook repositories (`pre-commit/pre-commit-hooks`, `Yelp/detect-secrets`, `python-jsonschema/check-jsonschema`, `astral-sh/ruff-pre-commit`) pinned to immutable version tags may appear in `.pre-commit-config.yaml`.
2. **Deterministic `ci.skip` Partition** — Every `repo: local` hook using `language: system` MUST appear in `ci.skip`, while cloud-capable remote and `pygrep` hooks (`ruff-check`, `ruff-format`, entropy baseline scanner, `check-jsonschema`, `forbid-local-paths`, `forbid-mutation-pragmas`) remain active in `pre-commit.ci` and unknown IDs in `ci.skip` are rejected.
3. **Commitizen Release Compatibility (`ADR-0001`):** Both `ci.autofix_commit_msg` and `ci.autoupdate_commit_msg` MUST conform to Conventional Commits (`style(...)` / `chore(...)`) so `cz check --rev-range` in `.github/workflows/release.yml` never fails on `pre-commit-ci[bot]` commits.
4. **Worktree Exclusion & Pre-Merge Gate (`ADR-0017`):** `.pre-commit-config.yaml` top-level `exclude` MUST omit `.worktrees` and `.poodle-temp`, and `.config/wt.toml` `[[pre-merge]]` MUST execute `uv run python -m nectr.devtools.ci_parity check` before landing worktree branches onto `main`.
