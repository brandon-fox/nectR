# Design: Chain Cryptographic Ledger (`chain-crypto-ledger`)

## DDD Entities & Value Objects
- **`Ed25519Signer` / `Ed25519Verifier` (Value Object / Adapter):** Wraps `cryptography.hazmat.primitives.asymmetric.ed25519` for deterministic keypair handling without exposing raw private keys in logs.
- **`CanonicalPayload` (Value Object):** Encodes domain dicts/models via `canonicaljson.encode_canonical_json` before SHA-256 hashing.
- **`MerkleInclusionProof` (Value Object):** Typed wrapper around `remerkleable` (`subtree_fill_to_contents`, `RootNode`, `to_gindex`, `merkle_hash`) with `0x00`-prefixed leaf hashing for transaction inclusion in `BlockHeader.merkle_root`.

## Invariants
1. **Determinism:** Identical semantic payloads MUST produce byte-identical canonical JSON and identical SHA-256 digests across Python versions and OSes.
2. **Domain Isolation:** `src/nectr/chain/` contains zero tutoring or tokenomics business rules; it validates cryptographic signatures, Merkle proofs, and `UsefulComputeProof` hashes only.
3. **Strict Typing:** All adapters pass `mypy --strict` (using `# type: ignore[import-untyped]` on the single adapter import from untyped `remerkleable.tree`, as `pyproject.toml` forbids global mypy overrides).
