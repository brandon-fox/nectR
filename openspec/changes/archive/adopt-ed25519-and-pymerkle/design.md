# Design: Chain Cryptographic Ledger & Transcript-Oracle PoUW-PoW (`chain-crypto-ledger`)

## DDD Ports, Entities & Value Objects
- **`SignerPort` / `Ed25519Signer` (Port & Value Object Adapter):** Wraps `cryptography.hazmat.primitives.asymmetric.ed25519` (or `PyNaCl` `nacl.signing`) for deterministic keypair generation, signing, and verification without leaking private keys in logs.
- **`CanonicalCodecPort` / `CanonicalPayload` (Port & Value Object):** Encodes domain dicts/models via `canonicaljson.encode_canonical_json` (or `rfc8785.dumps`) before SHA-256 / BLAKE2b hashing, rejecting unrounded floating-point drift.
- **`MerkleAccumulatorPort` / `MerkleInclusionProof` (Port & Value Object):** Typed wrapper around `remerkleable` (`subtree_fill_to_contents`, `RootNode`, `to_gindex`, `merkle_hash`) with explicit `0x00` leaf and `0x01` internal-node domain separation for transaction and `BeeAccount` inclusion/exclusion proofs in `BlockHeader.merkle_root`.
- **`TranscriptOraclePoUWVerifier` (Value Object):** Verifies the bounded intermediate transcript $\pi_{\text{pouw}}$ committing the epoch's Knowledge Flow Matrix and Pairwise Collusion Decay root $H(\text{seed} \parallel \text{kg\_root} \parallel \pi_{\text{pouw}}) < 2^{\ell} \cdot p$ with orthogonal task-dimension ($N$) and puzzle-probability ($p$) knobs for heterogeneous university VMs (`federated_PoUW-PoW_blockchain_infrastructure.md`).

## Invariants
1. **Determinism & Preimage Safety:** Identical semantic payloads MUST produce byte-identical canonical JSON and identical digests across Python 3.11–3.14 and OSes; leaf/node domain separation prevents second-preimage and odd-leaf duplication attacks.
2. **Domain Isolation:** `src/nectr/chain/` contains zero tutoring or tokenomics business rules; it validates cryptographic signatures, Merkle proofs, and `UsefulComputeProof` commitments only.
3. **Zero Systemic Inflation (`ADR-0007`):** Mining a valid `PoUW-PoW` block never mints new `nectR` supply; compute rebates draw strictly from the capped Comb Compute Jar.
4. **Strict Typing:** All ports and adapters pass `mypy --strict` (using `# type: ignore[import-untyped]` on the single adapter import from untyped `remerkleable.tree`, as `pyproject.toml` forbids global mypy overrides).
