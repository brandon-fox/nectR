# Specification Delta: Vyper `py-evm`, PactFlow Contract Governance & `/grill-me` Decisions (`decision-governance`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: ADDED — Open-Source Vyper `py-evm` Chain Contracts & PactFlow API/Event Governance (`ADR-0017`, `ADR-0018`, `DEC-017`–`DEC-020`)
The decision governance registry (`docs/planning/decisions.yaml`), MADR 4.0 records (`ADR-0017`, `ADR-0018`), OpenSpec proposals (`adopt-vyper-and-zero-gas-pyevm`, `add-pactflow-api-and-message-contracts`), and roadmap SHALL lock: (1) `vyper` (`Apache-2.0`) `.vy` smart contracts on zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`) anchored into `HiveBlockchain` `PoUW-PoW` headers (`ADR-0017`), (2) `pact-python` v4 (`MIT`) + PactFlow bi-directional HTTP and NATS JetStream async message contract governance (`ADR-0018`), (3) `uint256` `micro_nectr` and `0..10,000 bps` direct on-chain learner attestation scores (`DEC-017`, `DEC-018`), (4) layered `eth-account` `secp256k1` + `Ed25519` signing (`DEC-019`), and (5) JASSS/JEBO (`ODD+D`) + NSF DRMS/RSF primary framing (`DEC-020`).
- **Linked Scenario:** `Vyper py-evm chain contracts, PactFlow API contracts, micro_nectr math, and JASSS ODD+D framing are locked` in [decision_governance.feature](../../../../../features/decision_governance.feature#L33-L38)
