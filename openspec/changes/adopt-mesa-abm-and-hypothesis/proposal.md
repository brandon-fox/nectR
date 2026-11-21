# Proposal: Adopt Mesa ABM and Hypothesis Property-Based Testing (`adopt-mesa-abm-and-hypothesis`)

## Why
`src/nectr/personas/simulator.py` currently uses a custom epoch loop for the 6 Behavioral Persona Sub-Agents, and `HiveContractEngine` invariants are verified only on fixed test cases. Migrating epoch orchestration to `mesa` and adding `hypothesis` property-based tests improves academic reproducibility and catches edge-case invariant violations.

## Affected Bounded Contexts
- **Behavioral Economy & Personas (`src/nectr/personas/`)** — primary target.
- **Verification (`tests/`)** — property-based invariant fuzzing against `HiveContractEngine`.
- **Architectural Decision:** [ADR-0010](../../../docs/adr/0010-adopt-mesa-abm-and-hypothesis-invariant-testing.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `mesa` | `Apache-2.0` | **Approved** | Standard Python ABM framework (`Model`, `Agent`, `DataCollector`) |
| `hypothesis` | `MPL-2.0` | **Approved** | Property-based testing; `MPL-2.0` is on nectR's allowed list (`dev` optional dep) |

## Acceptance Criteria
1. `run_multi_hive_persona_simulation()` delegates agent scheduling and metric collection to `mesa.Model` and `mesa.DataCollector` with deterministic RNG seeding.
2. `hypothesis` stateful/property tests verify supply conservation, Queen Separation of Powers, and `RAW_POLLEN` spending rules across arbitrary transaction sequences.
3. Transitive dependencies pass `pip-licenses` and `pip-audit`.
