# Specification Delta: Vyper `.vy` Smart Contracts on Zero-Gas `py-evm` (`protocol-invariants`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/protocol_invariants.feature](../../../../../features/protocol_invariants.feature)
- **Step Definitions:** [features/steps/protocol_invariants_steps.py](../../../../../features/steps/protocol_invariants_steps.py)

## Requirements

### Requirement: ADDED — Permissive Vyper `.vy` Smart Contracts & Exact `uint256` `micro_nectr` Execution (`ADR-0017`, `DEC-017`–`DEC-019`)
All five core Hive smart contracts SHALL be implemented in `vyper` (`Apache-2.0`) and executed on a zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`) backend using exact `uint256` `micro_nectr` (`10^6`) balances, `0..10,000 bps` direct learner attestation scores, and `eth-account` (`secp256k1`) `msg.sender` authentication, sealing `evm_state_root` into `HiveBlockchain` `PoUW-PoW` block headers.
- **Linked Scenario:** `RAW_POLLEN refines into LIQUID_NECTR when settled with a Certified Worker Bee` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L19-L24)
