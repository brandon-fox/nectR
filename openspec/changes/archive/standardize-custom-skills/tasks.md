# Tasks: Standardize Custom Skills & Enforce `mypy --strict`

- [x] Create shared cross-platform, zero-regex utility `.agents/lib/skill_common.py`
- [x] Standardize all 7 custom skills in `.agents/skills/` (`SKILL.md` frontmatter, `scripts/*.py`, `references/*.md`, `## Validation`)
- [x] Add `mypy` (`MIT`) dev dependency in `pyproject.toml` / `uv.lock` and enforce `mypy --strict` in `.pre-commit-config.yaml` and `.githooks/pre-commit`
- [x] Add automated conformance and hook tests in `tests/test_skills_spec.py`
- [x] Verify `detect-secrets-hook`, `mypy --strict` (21 files), `pytest` (12 passed), `behave` (2 features, 7 scenarios), and `mkdocs build --strict`
- [ ] Unblock `.githooks/pre-commit` by resolving or isolating unrelated `tests/test_spec_linking.py` `XPASS(strict)` failures, then land atomic commits on `main`
