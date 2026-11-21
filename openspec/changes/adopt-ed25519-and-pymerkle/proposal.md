# Proposal: Adopt Ed25519, CanonicalJSON, Remerkleable & Transcript-Oracle PoUW (`adopt-ed25519-and-pymerkle`)

## Why
`src/nectr/chain/ledger.py` currently uses ad-hoc JSON serialization and custom Merkle hashing without cryptographic Ed25519 signatures or domain-separated leaf/node prefixes. Synthesizing [ADR-0007](../../../docs/adr/0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md), [ADR-0008](../../../docs/adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md), `permissive_tooling_survey_for_nectR.md`, and `federated_PoUW-PoW_blockchain_infrastructure.md`, we harden `src/nectr/chain/` behind swappable hexagonal ports:
1. **Ed25519 Signing (`SignerPort`):** Use `cryptography` (`Apache-2.0 OR BSD-3-Clause`) and/or `PyNaCl` (`Apache-2.0`, libsodium 1.0.20-stable with BLAKE2b and deterministic RNG) for transaction and block authentication.
2. **Canonical Serialization (`CanonicalCodecPort`):** Use `canonicaljson` (`Apache-2.0`, RFC 7159) or `rfc8785` (`Apache-2.0`, Trail of Bits RFC 8785 JCS) with integer/fixed-point consensus fields to guarantee bit-identical digests across platforms.
3. **Permissive Merkle & Sparse Commitments (`MerkleAccumulatorPort`):** Use `remerkleable` (`MIT`, Ethereum SSZ binary Merkle trees + `hash_tree_root`, 0 runtime deps) with explicit `0x00` leaf and `0x01` internal-node domain separation (preventing CVE-2012-2459 odd-leaf duplication), superseding unmaintained `merklelib` (which crashes on Python 3.10+ due to removed `collections.Iterable`) and blocking copyleft `pymerkle` (`GPLv3+`).
4. **Transcript-Oracle `PoUW-PoW` & Capped Comb Compute Jar (`ADR-0007`):** Couple block mining difficulty to a compact transcript proof of the trailing epoch's Knowledge Graph & Collusion Decay matrix (BRSV '18 / transcript-oracle PoUW ensuring duplex security surplus $\Delta_{\text{sec}} > 0$), paid strictly from the capped Comb Compute Jar with zero systemic token inflation.

## Affected Bounded Contexts
- **Consensus & Ledger (`src/nectr/chain/`)** — primary target.
- **Architectural Decisions:** [ADR-0007](../../../docs/adr/0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md), [ADR-0008](../../../docs/adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `cryptography` / `PyNaCl` | `Apache-2.0 OR BSD-3-Clause` | **Approved** | Ed25519 keygen, signing, verification, BLAKE2b; `pip-audit` clean |
| `canonicaljson` / `rfc8785` | `Apache-2.0` | **Approved** | Deterministic canonical JSON encoding (RFC 7159 / RFC 8785 JCS) |
| `remerkleable` | `MIT` | **Approved** | Binary Merkle tree construction & inclusion proofs (0 runtime deps; supersedes `merklelib`) |
| `merklelib` | `MIT` | **REJECTED** | Unmaintained 2018 release; raises `AttributeError` (`collections.Iterable`) on Python 3.11+ |
| `pymerkle` | `GPLv3+` | **BLOCKED** | Rejected by `open-source-first-and-license-audit.md` (copyleft incompatible with MIT) |

## Acceptance Criteria
1. All `BlockHeader`, `SignedTransaction`, and `UsefulComputeProof` payloads serialize via `CanonicalCodecPort` (`canonicaljson` / `rfc8785`) and sign/verify via `SignerPort` (`cryptography` / `PyNaCl` Ed25519).
2. Merkle roots, transaction inclusion proofs, and account-state Sparse Merkle Trees use `MerkleAccumulatorPort` (`remerkleable`, `MIT`) with `0x00`/`0x01` domain separation in `src/nectr/chain/`.
3. Transcript-Oracle `PoUW-PoW` difficulty verification enforces $\Delta_{\text{sec}} > 0$ and halts coin payouts automatically when the Comb Compute Jar is depleted (`ADR-0007`).
4. `pip-licenses` and `pip-audit` pass with zero prohibited licenses or critical CVEs.
