# Specification: Living Documentation, Domain Glossary, Persona Extras & Repo Hygiene

## Linked Behavior & Executable Steps
- **Feature File:** [features/docs_and_hygiene.feature](../../../features/docs_and_hygiene.feature)
- **Step Definitions:** [features/steps/docs_and_hygiene_steps.py](../../../features/steps/docs_and_hygiene_steps.py)

## Requirements

### Requirement: Canonical Domain Glossary & IDE-Agnostic Onboarding (`#12`)
Public onboarding documentation (`README.md`) SHALL define or link all domain acronyms (`MV=PQ`, `PoUW-PoW`) in `docs/glossary.md`, avoid IDE lock-in instructions, and treat `.agents/skills/` as optional shipped tooling with explicit installation instructions.
- **Linked Scenario:** `Repository glossary and README define core terms without IDE lock-in` in [docs_and_hygiene.feature](../../../features/docs_and_hygiene.feature#L6-L9)

### Requirement: Living Directory Spaces, Dynamic `mkdocs.yml` Nav & Zero Orphan Pages (`#9`)
Workspace documentation SHALL replace hardcoded ASCII directory trees with an auto-synced bounded-context index (`nectr-docs`), synchronize `mkdocs.yml` ADR navigation entries, and reject orphaned Markdown files under `docs/`.
- **Linked Scenario:** `Docs synchronization passes with zero orphaned docs pages and synced README spaces` in [docs_and_hygiene.feature](../../../features/docs_and_hygiene.feature#L11-L14)

### Requirement: Git Ignore Hygiene, LF Normalization & Persona Dependency Split (`#5`, `#8`, `#10`)
`HANDOFF.md` SHALL remain untracked in Git, `.gitattributes` SHALL enforce consistent LF line endings, and `pyproject.toml` SHALL split optional dependencies by user persona (`test`, `lint`, `security`, `docs`, `research`, `dev`).
- **Linked Scenario:** `Repository git tracking, LF attributes, and persona extras conform to hygiene policy` in [docs_and_hygiene.feature](../../../features/docs_and_hygiene.feature#L16-L19)
