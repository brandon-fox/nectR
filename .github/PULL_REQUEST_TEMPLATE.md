## Plan ID

<!-- e.g. HY2, TL3, CA3 -->

## Findings fixed

<!-- e.g. Finding 1, or N/A -->

## What changed

<!-- Summary of changes -->

## Red-first evidence

<!-- SHA or test output demonstrating failing test before fix -->

## Checks run

- [ ] `uv run pytest`
- [ ] `uv run behave --tags=-red`
- [ ] `uv run mypy src .agents/lib .agents/skills tests/test_skills_spec.py`
- [ ] `uv run nectr-docs check`
- [ ] `uv run nectr-decisions check`
- [ ] `uv run nectr-citations check`
- [ ] `uv run python -m nectr.devtools.spec_links`
- [ ] `git rev-list --merges origin/main..HEAD` is empty
- [ ] Zero path leaks (detect-secrets and local-path regex)

## Known limits

<!-- Document any known limitations, or None -->
