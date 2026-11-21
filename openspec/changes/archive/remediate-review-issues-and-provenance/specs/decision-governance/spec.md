# Delta Specification: Dual-Track Decision Governance (`MODIFIED`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## MODIFIED Requirements

### Requirement: Zero-CVE MIT MADR Engine and Proposed ADR Support (`#6`, `#11`)
All MADR records SHALL be managed by the zero-CVE, pure-MIT `nectr.devtools.adr` engine (`pyadr` CLI entry point) with zero GPL/Artistic dependencies, supporting `--allow-proposed` checks for branch-stage `proposed` ADRs and documented `.adr` keys (`records-dir`) in `docs/adr/lifecycle_guide.md`.
- **Linked Scenario:** `Proposed ADR is permitted only when allow-proposed flag is active` in [decision_governance.feature](../../../../../features/decision_governance.feature#L22-L26)
