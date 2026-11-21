# Specification: OpenSpec-to-Feature Single Source of Truth Linking

## Linked Behavior & Executable Steps
- **Feature File:** [features/spec_linking.feature](../../../features/spec_linking.feature)
- **Step Definitions:** [features/steps/spec_linking_steps.py](../../../features/steps/spec_linking_steps.py)

## Requirements

### Requirement: No Hardcoded User Stories or Scenarios in `spec.md`
All `spec.md` files under `openspec/` SHALL NOT contain inline `#### Scenario:` headers or `GIVEN`/`WHEN`/`THEN`/`AND` blocks.
- **Linked Scenario:** `Spec with hardcoded Given/When/Then scenario is rejected` in [spec_linking.feature](../../../features/spec_linking.feature#L6-L9)

### Requirement: Mandatory Links to Existing `.feature` and `_steps.py` Files
Every `spec.md` under `openspec/` SHALL contain valid relative links to at least one existing `features/*.feature` file and at least one existing `features/steps/*_steps.py` file.
- **Linked Scenarios:**
  - `Spec without feature or step links is rejected` in [spec_linking.feature](../../../features/spec_linking.feature#L11-L14)
  - `Repository OpenSpec files pass spec-to-feature link validation` in [spec_linking.feature](../../../features/spec_linking.feature#L16-L19)
