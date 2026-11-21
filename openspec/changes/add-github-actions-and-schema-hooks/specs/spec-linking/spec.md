# Delta Specification: Spec-Linking & Documentation Link CI

## Linked Behavior & Executable Steps
- **Feature File:** [features/spec_linking.feature](../../../../../features/spec_linking.feature)
- **Step Definitions:** [features/steps/spec_linking_steps.py](../../../../../features/steps/spec_linking_steps.py)

## Requirements

### Requirement: ADDED — Automated Documentation & OpenSpec Link Checking in CI
GitHub Actions (`ci.yml`, `pr-policy.yml`) SHALL enforce `nectr.devtools.spec_links`, `mkdocs build --strict`, and `lychee` link verification on every pull request and push to `main`.
- **Linked Scenario:** `Repository OpenSpec files pass spec-to-feature link validation` in [spec_linking.feature](../../../../../features/spec_linking.feature#L16-L19)
