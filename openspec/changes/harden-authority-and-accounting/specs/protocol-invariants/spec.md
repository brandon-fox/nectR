# Delta Specification: Harden Authority, Escrow Lifecycle, Guard Bee Registration & Micro-Unit Accounting (`protocol-invariants`)

## Linked Behavior & Executable Steps

- **Feature File:** [features/protocol_invariants.feature](../../../../../features/protocol_invariants.feature)
- **Step Definitions:** [features/steps/protocol_invariants_steps.py](../../../../../features/steps/protocol_invariants_steps.py)

> User stories and Given/When/Then scenarios are maintained exclusively in the linked `.feature` file above (never hardcoded in `spec.md`).

## Requirements

### Requirement: MODIFIED — Authenticated Command Authority & Bootstrap-Only Queen Role (D-02)
`HiveServiceLayer` SHALL require verified `SignedTransaction` commands (valid Ed25519 signature, registered key, matching `hive_id`, monotonic nonce) for all state-changing operations and SHALL reject attempts to self-register `BeeRole.QUEEN` outside Hive bootstrap.

- **Linked Scenario:** `Queen Separation of Powers blocks Queen from tutoring` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L6-L10)

### Requirement: MODIFIED — Exact Integer Micro-Unit Supply Conservation (D-03)
`HiveContractEngine` SHALL execute all token allocations, escrows, settlements, dispute payouts, fees, and bridges in exact integer micro-units (`10^-6` micro-nectR) such that `comb_reserve + sum(raw_pollen) + sum(liquid_nectr) + sum(escrowed) == total_minted_supply` holds strictly with zero tolerance.

- **Linked Scenario:** `Queen dispute resolution routes 100% of fees to Comb and conserves supply` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L26-L31)

### Requirement: ADDED — Explicit Dispute State, Bounded Arbitration Fee, and Escrow Expiry Cancellation (D-03)
A `QUEEN` SHALL only arbitrate sessions explicitly transitioned to a disputed state (`dispute_session`) and with `service_fee_rate < 1.0`. Once an `INTENT_ESCROWED` session passes its expiry epoch, the `learner_id` SHALL be able to cancel the escrow (`cancel_expired_escrow`) and recover 100% of `escrowed_amount` in the original `TokenState`.

- **Linked Scenarios:**
  - `Queen cannot arbitrate undisputed escrow or charge 100 percent fee` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature)
  - `Learner cancels expired escrow and recovers full original token state` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature)

### Requirement: MODIFIED — Guard Bee Foreign Registration & Accepted Status Isolation (D-04)
Registering an external Bee in a target Hive without prior host-Hive tutoring SHALL NOT grant `Accepted Status` in the target Hive, regardless of whether `home_hive_id` is supplied; cross-hive bridging SHALL raise `ContractViolationError` matching `"Guard Bee Rejection"` until `accepted_status_peer_threshold` distinct host-Hive peers are tutored.

- **Linked Scenario:** `Guard Bee blocks unaccepted Pollinator bridge and permits Accepted Status bridge with Comb toll` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L40-L45)
