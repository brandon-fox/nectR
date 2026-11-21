# Adopt Ed25519 CanonicalJSON and Merklelib

* Status: accepted
* Deciders: nectR Consensus & Security Architecture
* Date: 2026-11-21

## Context and Problem Statement

`src/nectr/chain/ledger.py` currently uses ad-hoc JSON serialization and custom Merkle hashing without cryptographic Ed25519 signatures. We need battle-tested, MIT-compatible OSS libraries for deterministic canonicalization, Ed25519 signing, and Merkle inclusion proofs.

## Considered Options

* **`cryptography` (Apache-2.0/BSD-3-Clause) + `canonicaljson` (Apache-2.0) + `merklelib` (MIT)**
* **`cryptography` + `canonicaljson` + `pymerkle` (GPLv3+)**
* **Continue maintaining custom ad-hoc hashing and Merkle code**

## Decision Outcome

Chosen option: "`cryptography` + `canonicaljson` + `merklelib`", because `pymerkle` is GPLv3+ (prohibited under nectR's MIT transitive license policy), whereas `merklelib` (MIT), `canonicaljson` (Apache-2.0), and `cryptography` (Apache-2.0/BSD-3-Clause) are permissive and deterministic.

### Consequences

* Good, because `BlockHeader` and `UsefulComputeProof` gain RFC 7159 canonical hashing, Ed25519 signatures, and Merkle inclusion proofs with MIT-compatible licensing.
* Bad, because `merklelib` requires a thin typed adapter in `src/nectr/chain/` to preserve `mypy --strict` compliance.
