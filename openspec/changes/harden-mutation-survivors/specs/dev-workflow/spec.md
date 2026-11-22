# Delta Specification: Survivor Hardening & Upward-Only Baseline Ratchet (`dev-workflow`)

## Linked Behavior & Executable Steps

- **Feature File:** [features/dev_workflow.feature](../../../../../features/dev_workflow.feature)
- **Step Definitions:** [features/steps/dev_workflow_steps.py](../../../../../features/steps/dev_workflow_steps.py)

## MODIFIED Requirements

### Requirement: Upward-Only Baseline Floor Ratchet With Runner Noise Margin

Every committed entry in `[tool.nectr.mutation.baseline]` SHALL be computed from a verified full mutation sweep as `max(0.0, min(tier_target, floor(actual_score) - 1.0))` and SHALL only ratchet upward toward its tier target (`>= 85.0%` Tier 1, `>= 75.0%` Tier 2) as module test suites harden, never regressing unless source modules are removed from the tier.

- **Linked Scenario:** `A full sweep below a committed baseline floor fails, and at or above the floor passes` in [dev_workflow.feature](../../../../../features/dev_workflow.feature#L27-L32)

## ADDED Requirements

### Requirement: Zero-Pragma Survivor Hardening Across Tiered Modules

Pre-existing mutation survivors in Tier-1 (`src/nectr/contracts`, `src/nectr/chain`) and Tier-2 (`src/nectr/services`, `src/nectr/devtools`) modules SHALL be eliminated solely through deterministic unit, property-based, and BDD acceptance tests without introducing inline mutation-suppression pragmas under `src/`.

- **Linked Scenarios:**
  - `Inline mutation suppression pragmas in src are rejected` in [dev_workflow.feature](../../../../../features/dev_workflow.feature#L17-L20)
  - `A Tier-1 change whose changed-line mutants score below 85% fails the diff gate` in [dev_workflow.feature](../../../../../features/dev_workflow.feature#L22-L25)
