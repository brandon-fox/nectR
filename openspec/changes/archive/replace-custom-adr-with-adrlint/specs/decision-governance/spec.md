# Delta Specification: OSS `adrlint` Governance (`MODIFIED`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## MODIFIED Requirements

### Requirement: MADR 4.0 Governance via External OSS `adrlint` (`#6`, `#11`)
Bespoke ADR engine code (`src/nectr/devtools/adr.py`) SHALL NOT exist in the repository; all MADR 4.0 structure, sequential numbering, formatting (`rumdl`), and semantic BLAKE3 immutability locking (`adrlint.lock`) SHALL be delegated to the external MIT-licensed OSS `adrlint` CLI configured by `.adrlint.toml`, while `nectr.devtools.decisions` adds only `--allow-proposed` branch gating and project verbosity caps.
- **Linked Scenario:** `OSS adrlint replaces bespoke ADR module and enforces lock and proposed gating` in [decision_governance.feature](../../../../../features/decision_governance.feature#L21-L24)
