# Specification: Chain Cryptographic Ledger (`chain-crypto-ledger`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/chain_crypto_ledger.feature](../../../../../features/chain_crypto_ledger.feature)
- **Step Definitions:** [features/steps/chain_crypto_ledger_steps.py](../../../../../features/steps/chain_crypto_ledger_steps.py)

## Requirements

### Requirement: ADDED — Deterministic Canonical Serialization & Ed25519 Signatures
All ledger transactions, `BlockHeader` commitments, and `UsefulComputeProof` payloads SHALL serialize via `canonicaljson` and authenticate via `cryptography` Ed25519 signatures.
- **Linked Scenario:** `Ed25519-signed canonical transaction produces verifiable Merkle inclusion proof` in [chain_crypto_ledger.feature](../../../../../features/chain_crypto_ledger.feature#L6-L10)

### Requirement: ADDED — Permissive-License Merkle Inclusion Proofs
Block transaction commitments SHALL construct and verify Merkle roots and inclusion proofs using `merklelib` (`MIT`), prohibiting copyleft (`GPLv3+`) alternatives such as `pymerkle`.
- **Linked Scenario:** `Ed25519-signed canonical transaction produces verifiable Merkle inclusion proof` in [chain_crypto_ledger.feature](../../../../../features/chain_crypto_ledger.feature#L6-L10)
