# Delta Specification: Spec-Linking, Markdown Scope & Documentation Link CI

## Linked Behavior & Executable Steps
- **Feature File:** [features/spec_linking.feature](../../../../../features/spec_linking.feature)
- **Step Definitions:** [features/steps/spec_linking_steps.py](../../../../../features/steps/spec_linking_steps.py)
- **CI Parity Feature:** [features/ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature)
- **CI Parity Steps:** [features/steps/ci_and_hook_parity_steps.py](../../../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: ADDED — Expanded Markdown Linting, Strict MkDocs & `lychee` Link Verification
Local hooks and GitHub Actions workflows SHALL enforce `nectr.devtools.spec_links`, `mkdocs build --strict`, `pymarkdown` across `docs/` (including `docs/theory/`) and `paper/`, and `lychee` link verification across `docs/`, `paper/`, and `openspec/` on every pull request and push to `main`.
- **Linked Scenario:** `Repository OpenSpec files pass spec-to-feature link validation` in [spec_linking.feature](../../../../../features/spec_linking.feature#L16-L19)
- **Linked Scenario:** `Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs` in [ci_and_hook_parity.feature](../../../../../features/ci_and_hook_parity.feature#L24-L28)
