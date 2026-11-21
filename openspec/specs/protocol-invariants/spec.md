# Specification: Core nectR Protocol Invariants

## Purpose
Define the non-negotiable economic, cryptographic, and biomimetic invariants enforced by the `nectR` Smart Contracts (`src/nectr/contracts/`) and Hive Service Layer (`src/nectr/services/`).

## Requirements

### Requirement: Queen Separation of Powers (D-02)
The `HiveContractEngine` SHALL prohibit any account holding `BeeRole.QUEEN` from acting as a `Tutor` in a `ServiceBarterSession` or receiving `CERTIFIED_WORKER_BEE` certification.

#### Scenario: Queen attempts to tutor a learner
- **GIVEN** a Hive with a registered `QUEEN` account and a registered `LEARNER_BEE` holding `RAW_POLLEN`
- **WHEN** the `QUEEN` attempts to create a `ServiceBarterSession` as `tutor_id`
- **THEN** the contract SHALL raise `ContractViolationError` with `"Queen Separation of Powers Violation"`
- **AND** no escrow or token balance SHALL change.

### Requirement: Restricted RAW_POLLEN Refinement (D-05)
The `HiveContractEngine` SHALL restrict `TokenState.RAW_POLLEN` spending exclusively to tutors holding `BeeRole.CERTIFIED_WORKER_BEE` certified for the session's `subject_id`, refining settled `RAW_POLLEN` into `TokenState.LIQUID_NECTR`.

#### Scenario: Learner attempts to spend RAW_POLLEN with an uncertified peer
- **GIVEN** a `LEARNER_BEE` holding `RAW_POLLEN` and an uncertified `LEARNER_BEE` peer
- **WHEN** the learner attempts to escrow `RAW_POLLEN` for tutoring with the uncertified peer
- **THEN** the contract SHALL raise `ContractViolationError`
- **AND** the learner's `RAW_POLLEN` balance SHALL remain unchanged.

#### Scenario: Learner settles RAW_POLLEN session with a Certified Worker Bee
- **GIVEN** a `LEARNER_BEE` holding `15.0` `RAW_POLLEN` and a `CERTIFIED_WORKER_BEE` certified in `"CALC-101"`
- **WHEN** they escrow and settle a `"CALC-101"` session for `10.0` `RAW_POLLEN`
- **THEN** the Certified Worker's `LIQUID_NECTR` balance SHALL increase by `10.0`
- **AND** the Learner's `RAW_POLLEN` balance SHALL decrease to `5.0`.

### Requirement: Fee-to-Comb Rule & Supply Conservation (D-03)
Direct P2P tutoring settlement SHALL charge `0%` protocol fee. Dispute resolution by a `QUEEN` SHALL route `100%` of the dispute service fee into `comb_reserve` while strictly conserving total Hive supply.

#### Scenario: Queen resolves a disputed session with a 10% service fee
- **GIVEN** a Hive with `180.0` in `comb_reserve` and a `20.0` `RAW_POLLEN` session in escrow
- **WHEN** a `QUEEN` resolves the dispute with `tutor_share_ratio=0.5` and `service_fee_rate=0.10`
- **THEN** `2.0` SHALL be routed into `comb_reserve` (raising it to `182.0`)
- **AND** the tutor SHALL receive `9.0` `LIQUID_NECTR` and the learner SHALL receive `9.0` `RAW_POLLEN`
- **AND** total Hive token supply SHALL remain conserved.
