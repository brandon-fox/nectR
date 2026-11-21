# Specification: Core nectR Protocol Invariants

## Purpose
Define the non-negotiable economic, cryptographic, and biomimetic invariants enforced by the `nectR` Smart Contracts (`src/nectr/contracts/`) and Hive Service Layer (`src/nectr/services/`).

## Linked Behavior & Executable Steps
- **Feature File:** [features/protocol_invariants.feature](../../../features/protocol_invariants.feature)
- **Step Definitions:** [features/steps/protocol_invariants_steps.py](../../../features/steps/protocol_invariants_steps.py)

> User stories and Given/When/Then scenarios are maintained exclusively in the linked `.feature` file above (never hardcoded in `spec.md`).

## Requirements

### Requirement: Queen Separation of Powers (D-02)
The `HiveContractEngine` SHALL prohibit any account holding `BeeRole.QUEEN` from acting as a `Tutor` in a `ServiceBarterSession` or receiving `CERTIFIED_WORKER_BEE` certification.
- **Linked Scenario:** `Queen Separation of Powers blocks Queen from tutoring` in [protocol_invariants.feature](../../../features/protocol_invariants.feature#L6-L10)

### Requirement: Restricted RAW_POLLEN Refinement (D-05)
The `HiveContractEngine` SHALL restrict `TokenState.RAW_POLLEN` spending exclusively to tutors holding `BeeRole.CERTIFIED_WORKER_BEE` certified for the session's `subject_id`, refining settled `RAW_POLLEN` into `TokenState.LIQUID_NECTR`.
- **Linked Scenarios:**
  - `RAW_POLLEN cannot be spent with an uncertified peer` in [protocol_invariants.feature](../../../features/protocol_invariants.feature#L12-L17)
  - `RAW_POLLEN refines into LIQUID_NECTR when settled with a Certified Worker Bee` in [protocol_invariants.feature](../../../features/protocol_invariants.feature#L19-L24)

### Requirement: Fee-to-Comb Rule & Supply Conservation (D-03)
Direct P2P tutoring settlement SHALL charge `0%` protocol fee. Dispute resolution by a `QUEEN` SHALL route `100%` of the dispute service fee into `comb_reserve` while strictly conserving total Hive supply.
- **Linked Scenario:** `Queen dispute resolution routes 100% of fees to Comb and conserves supply` in [protocol_invariants.feature](../../../features/protocol_invariants.feature#L26-L31)
