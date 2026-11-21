Feature: Chain Cryptographic Ledger (Ed25519, CanonicalJSON, and Merkle Proofs)
  As a nectR consensus node operator
  I want blocks and transactions signed with Ed25519, serialized deterministically with canonicaljson, and committed with merklelib inclusion proofs
  So that PoUW-PoW block verification is deterministic and tamper-evident

  @red
  Scenario: Ed25519-signed canonical transaction produces verifiable Merkle inclusion proof
    Given an Ed25519 keypair for Bee "worker_1" and a canonicalized barter payload
    When the transaction is committed into a BlockHeader via merklelib
    Then the Ed25519 signature and Merkle inclusion proof verify deterministically
