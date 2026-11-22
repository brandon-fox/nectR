# Proposal: Migrate 5 Hive Smart Contracts to Vyper (`.vy`) on Zero-Gas `py-evm` (`adopt-vyper-and-zero-gas-pyevm`)

## Why
`src/nectr/contracts/engine.py` currently implements a bespoke Python state machine using IEEE-754 `float` balances. Per [ADR-0017](../../../docs/adr/0017-adopt-vyper-and-zero-gas-py-evm-smart-contracts.md) and our Open-Source-First mandate, **Swarm Wave 2B-1** migrates the 5 core deterministic smart contracts (`TokenStateAndComb.vy`, `DirectionalServiceBarter.vy`, `QueenGovernance.vy`, `KnowledgeGraphAndPolicing.vy`, `GuardBeeCrossHiveBridge.vy`) to **`vyper` (`Apache-2.0`)** executed on an embedded **zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`)** EVM backend:
1. **100% Permissive Transitive Stack:** Avoids copyleft traps (`solc` `GPL-3.0`, `snekmate` `AGPL-3.0-only`, `bitcoinlib` `GPLv3+`, `python-bitcoinlib` `LGPLv3+`).
2. **Exact Integer `micro_nectr` & `bps` Math (`DEC-017`, `DEC-018`):** All balances execute in `uint256` `micro_nectr` (`1 nectR = 1,000,000` units) and rates/attestation scores in `0..10,000 bps` (`DEC-018`), guaranteeing exact supply conservation (`accounted == expected`) with zero float drift.
3. **Layered `secp256k1` EVM + `Ed25519` Consensus Signing (`DEC-019`):** Bees and Queens sign `.vy` transactions and EIP-712 co-signed tutoring attestations via `eth-account` (`secp256k1`, `MIT`) so `py-evm` verifies `msg.sender` and `ecrecover` natively, while `HiveBlockchain` seals `evm_state_root` + `kg_root` inside `Ed25519` / `remerkleable` `PoUW-PoW` headers (`ADR-0007`, `ADR-0008`).
4. **Core Semester Economics Included in Wave 2B-1:** Implements `D-01`–`D-06`, Lazy Demurrage (`DEC-001`), Waggle `60%` Surge Co-Pay (`DEC-002`), Minimum `25-minute` block (`DEC-011`), and 3-Door Senior Graduation Sinks (`DEC-004`).

## Affected Bounded Contexts
- **Smart Contracts Context (`src/nectr/contracts/`)** — `.vy` sources + typed `web3.py` / `eth-tester` orchestrator.
- **Consensus & Ledger Context (`src/nectr/chain/`)** — `evm_state_root` field commitment in `BlockHeader`.
- **Architectural Decision:** [ADR-0017](../../../docs/adr/0017-adopt-vyper-and-zero-gas-py-evm-smart-contracts.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `vyper` | `Apache-2.0` | **Approved** | Pythonic EVM compiler; transitive deps (`cbor2`, `lark`, `asttokens`, `immutables`, `pycryptodome`) 100% MIT/Apache/BSD |
| `eth-tester` + `py-evm` | `MIT` | **Approved** | Embedded Python EVM execution engine (`gas_price = 0`, `gas_limit` enforced) |
| `web3` + `eth-account` | `MIT` | **Approved** | Typed contract ABI binding, `secp256k1` wallets, and EIP-712 co-signatures |
| `snekmate` / `solc` / `bitcoinlib` | `AGPL-3.0` / `GPL-3.0` | **BLOCKED** | Prohibited under `open-source-first-and-license-audit.md` |

## Acceptance Criteria
1. All 5 `.vy` contracts compile via `vyper` and execute on zero-gas-price `eth-tester[py-evm]` with exact `uint256` `micro_nectr` conservation (`D-01`–`D-06`).
2. `HiveContractEngine` exposes a clean, typed domain facade (`mypy --strict`) converting human decimals at the service boundary while delegating all state transitions to `py-evm`.
3. `pip-licenses` and `pip-audit` pass with zero copyleft packages or critical CVEs.
