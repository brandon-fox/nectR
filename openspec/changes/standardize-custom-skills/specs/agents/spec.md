# Specification: Custom Skills Conformance & Commit-Time Static Typing

## Requirements & Invariants
1. **Skill Package Structure:** Every directory under `.agents/skills/` MUST contain `SKILL.md`, at least one cross-platform Python helper in `scripts/*.py`, and at least one reference document in `references/*.md`.
2. **Frontmatter & Links:** `SKILL.md` MUST define `name` (matching directory name, lowercase hyphenated, `<= 64` chars), a third-person `description` stating *what* and *when* (`<= 1024` chars), relative links to `./scripts/` and `./references/` that resolve on disk, and a `## Validation` section.
3. **DRY & Zero-Regex Helpers:** Shared skill helper logic MUST reside in `.agents/lib/skill_common.py` using stdlib-only, linear-time, regex-free string/set checks.
4. **Strict Typing & Commit Gate:** All skill scripts, `.agents/lib/`, `src/`, and `tests/test_skills_spec.py` MUST pass `mypy --strict`, and `mypy` MUST be configured in both `.pre-commit-config.yaml` and `.githooks/pre-commit`.

## Verification
- BDD Feature: [features/skills_conformance.feature](../../../../../features/skills_conformance.feature)
- BDD Steps: [features/steps/skills_conformance_steps.py](../../../../../features/steps/skills_conformance_steps.py)
- Automated tests: [tests/test_skills_spec.py](../../../../../tests/test_skills_spec.py)
