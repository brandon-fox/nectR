---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Consensus & Security Architecture
---

# Adopt Ed25519 CanonicalJSON and Merklelib

## Context and Problem Statement

`src/nectr/chain/ledger.py` currently uses ad-hoc JSON serialization and custom Merkle hashing without cryptographic Ed25519 signatures. We need battle-tested, MIT-compatible, Python 3.11+ OSS libraries for deterministic canonicalization, Ed25519 signing, and Merkle inclusion proofs. (Amended in M0 after runtime probes showed `merklelib 1.0` crashes on Python 3.10+ due to removed `collections.Iterable`.)

## Considered Options

* **`cryptography` (Apache-2.0/BSD-3-Clause) + `canonicaljson` (Apache-2.0) + `remerkleable` (MIT)**
* **`cryptography` + `canonicaljson` + `merklelib` (MIT, 2018 release; crashes on Python 3.11+)**
* **`cryptography` + `canonicaljson` + `pymerkle` (GPLv3+)**
* **Continue maintaining custom ad-hoc hashing and Merkle code**

## Decision Outcome

Chosen option: "`cryptography` + `canonicaljson` + `remerkleable`", because `pymerkle` is GPLv3+ (prohibited under nectR's MIT transitive license policy) and `merklelib 1.0` crashes on Python 3.11+ (`AttributeError: module 'collections' has no attribute 'Iterable'`), whereas `remerkleable` (`MIT`, zero runtime deps), `canonicaljson` (`Apache-2.0`), and `cryptography` (`Apache-2.0/BSD-3-Clause`) are permissive, deterministic, and Python 3.11+ compatible.

### Consequences

* Good, because `BlockHeader` and `UsefulComputeProof` gain RFC 7159 canonical hashing, Ed25519 signatures, and SSZ binary Merkle inclusion proofs with MIT-compatible licensing and zero extra transitive dependencies.
* Bad, because `remerkleable` lacks `py.typed` and requires a thin typed adapter in `src/nectr/chain/` (with `# type: ignore[import-untyped]` on the adapter import) for `mypy --strict` compliance.
