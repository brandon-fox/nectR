# Design: Vyper `py-evm`, PactFlow Contracts, Integer `micro_nectr`, and JASSS `ODD+D` Alignment

## 1. Architectural Decisions (`ADR-0017` & `ADR-0018`)
- **`ADR-0017` (Vyper `.vy` + Zero-Gas `py-evm` Smart Contracts):**
  - Audited PyPI transitive tree: `vyper` (`Apache-2.0`), `eth-tester` (`MIT`), `py-evm` (`MIT`), `web3.py` (`MIT`), `eth-account` (`MIT`), `eth-abi` (`MIT`), `pycryptodome` (`BSD-2-Clause AND Unlicense AND MIT`), `cbor2` (`MIT`), `py-ecc` (`MIT`), `trie` (`MIT`), `ckzg` (`Apache-2.0`).
  - Explicitly rejects copyleft alternatives: `solc` (`GPL-3.0`), `snekmate` (`AGPL-3.0-only`), `bitcoinlib` (`GPLv3+`), `python-bitcoinlib` (`LGPLv3+`), and `python-bitcointx` (`LGPLv3+`).
  - Splits Swarm Wave 2 contract implementation into **Wave 2B-1** (`adopt-vyper-and-zero-gas-pyevm`: 5 core `.vy` contracts `D-01`–`D-05`, `uint256` `micro_nectr`, `0..10,000 bps` direct learner attestations, Demurrage, Waggle `60%` Co-Pay, 3-Door Senior Sinks) and **Wave 2B-2** (`add-biomimetic-lifecycle-and-swarming-contracts`: QMP Supersedure/24h Election, Khoury EO Circuit Breaker, Oophagy Fraud Proofs, and 15-Scout Swarming `.vy` modules).
- **`ADR-0018` (`pact-python` v4 + PactFlow Bi-Directional & Async Message Contracts):**
  - Audited PyPI transitive tree: `pact-python>=4.2.0` (`MIT`) + `pact-python-ffi` (`MIT`).
  - Covers HTTP consumer-driven pacts (`Streamlit` UI, `PersonaBeeAgent`, `LTI 1.3` $\to$ `FastAPIHiveRouter`), Async Message pacts (`NATS JetStream` `AcceptedStatusGranted` & CQRS `SessionSettled`), offline `pacts/*.json` verification on local hooks/fork PRs, and PactFlow Broker OpenAPI 3.1 bi-directional verification + `can-i-deploy` release gates.

## 2. Invariants
- All MADR 4.0 ADRs remain `<= 70` lines, `<= 380` words, H1 `<= 70` chars, and `<= 6` bullets/section, locked via `adrlint lock`.
- `decisions.yaml` (`DEC-001`–`DEC-020`, `EXP-001`–`EXP-006`) validates against `docs/planning/decisions.schema.json` and renders deterministically to `docs/planning/decision_log.md`.
- All OpenSpec `spec.md` files link directly to executable `.feature` and `_steps.py` files with zero hardcoded scenarios.
