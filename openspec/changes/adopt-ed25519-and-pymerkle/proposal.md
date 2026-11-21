# Proposal: Adopt Ed25519, CanonicalJSON, and Remerkleable (`adopt-ed25519-and-pymerkle`)

## Why
`src/nectr/chain/ledger.py` currently uses ad-hoc JSON serialization and custom Merkle hashing without cryptographic Ed25519 signatures. Adopting permissive, battle-tested, Python 3.11+ OSS libraries eliminates custom crypto/serialization maintenance while hardening `BlockHeader` and `UsefulComputeProof` verifiability.

## Affected Bounded Contexts
- **Consensus & Ledger (`src/nectr/chain/`)** — primary target.
- **Architectural Decision:** [ADR-0008](../../../docs/adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `cryptography` | `Apache-2.0 OR BSD-3-Clause` | **Approved** | Ed25519 keygen, signing, verification; verify `pip-audit` clean |
| `canonicaljson` | `Apache-2.0` | **Approved** | Deterministic RFC 7159 canonical JSON encoding |
| `remerkleable` | `MIT` | **Approved** | Binary Merkle tree construction & inclusion proofs (0 runtime deps; supersedes `merklelib`, which crashes on Python 3.10+ due to removed `collections.Iterable`) |
| `merklelib` | `MIT` | **REJECTED** | Unmaintained 2018 release; raises `AttributeError` (`collections.Iterable`) on Python 3.11+ |
| `pymerkle` | `GPLv3+` | **BLOCKED** | Rejected by `open-source-first-and-license-audit.md` (copyleft incompatible with MIT) |

## Acceptance Criteria
1. All `BlockHeader`, transaction, and `UsefulComputeProof` payloads serialize via `canonicaljson` and sign/verify via `cryptography` Ed25519.
2. Merkle roots and inclusion proofs use `remerkleable` (`MIT`) behind `MerkleInclusionProof` in `src/nectr/chain/`.
3. `pip-licenses` and `pip-audit` pass with zero prohibited licenses or critical CVEs.
