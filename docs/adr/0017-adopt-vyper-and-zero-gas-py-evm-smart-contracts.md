---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Smart Contracts, Consensus & Security Architecture
---

# Adopt Vyper and Zero-Gas py-evm Smart Contracts

## Context and Problem Statement

`src/nectr/contracts/engine.py` uses custom Python state-machine code and IEEE-754 floats, violating our Open-Source-First mandate and risking float drift. Live PyPI license audits show `solc` (`GPL-3.0`), `snekmate` (`AGPL-3.0-only`), `bitcoinlib` (`GPLv3+`), and `python-bitcoinlib`/`python-bitcointx` (`LGPLv3+`) carry copyleft licenses. Which permissive open-source smart contract VM and language should execute nectR's 5 Hive contracts?

## Considered Options

* **Pythonic Ethereum EVM: `vyper` (`Apache-2.0`) `.vy` contracts on zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`) anchored into `HiveBlockchain` `PoUW-PoW` headers**
* **Solidity (`solc` `GPL-3.0`) or `snekmate` (`AGPL-3.0`) contract stack**
* **Bitcoin/Litecoin UTXO Script (`bitcoinlib` `GPLv3+` / `embit` `MIT`) or custom Python FSM**

## Decision Outcome

Chosen option: "Pythonic Ethereum EVM: `vyper` (`Apache-2.0`) `.vy` contracts on zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`) anchored into `HiveBlockchain` `PoUW-PoW` headers", because `vyper`, `py-evm`, `eth-tester`, `web3.py`, and `eth-account` have a 100% permissive (`MIT`/`Apache-2.0`/`BSD`) transitive tree, enforce native `uint256` `micro_nectr` integer math and `gas_limit` loop safety at `gas_price = 0` (`0%` P2P fee), authenticate Bees/Queens via `eth-account` (`secp256k1` EIP-712 `msg.sender`), and seal `evm_state_root` + `kg_root` inside `PoUW-PoW` blocks.

### Consequences

* Good, because custom FSM boilerplate and float rounding are replaced by real EVM bytecode in two sub-waves (`Wave 2B-1` core `.vy` + `Wave 2B-2` colony lifecycle `.vy`).
* Good, because `SQLModel` (`ADR-0009`) replays immutable blocks into `py-evm` deterministically on startup.
* Bad, because contributors author contract rules in strict `.vy` (`uint256` `micro_nectr` and `bps`) rather than dynamically typed Python dicts.
