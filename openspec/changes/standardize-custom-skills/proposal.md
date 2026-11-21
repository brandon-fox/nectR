# Change Proposal: Standardize Custom Skills & Enforce Static Type Checking

## Summary
Standardize all 7 custom skills under `.agents/skills/` to conform to the Antigravity Skills specification (`SKILL.md` frontmatter, `scripts/`, `references/`, `## Validation`), eliminate regular expressions in shared validation/hygiene helpers in favor of linear `str.find`/`frozenset` logic, enforce Google Python Style Guide explicit typing, and integrate `mypy --strict` into pre-commit hooks.

## Motivation
- Custom skills previously had only `SKILL.md` files without `scripts/` or `references/`, and lacked `when`-trigger phrasing in `description`.
- Cross-platform support (Linux, macOS, Windows) requires Python stdlib helper scripts backed by a DRY shared module (`.agents/lib/skill_common.py`).
- Static type safety (`mypy --strict`) must be verified on every commit via `.pre-commit-config.yaml` and `.githooks/pre-commit`.

## Scope
- `.agents/lib/skill_common.py`
- `.agents/skills/*/SKILL.md`, `scripts/*.py`, `references/*.md`
- `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `.githooks/pre-commit`
- `tests/test_skills_spec.py`
