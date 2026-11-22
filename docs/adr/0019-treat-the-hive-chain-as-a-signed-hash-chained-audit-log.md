---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Consensus Team
---

# Treat the hive chain as a signed, hash-chained audit log

## Context and Problem Statement

`ADR-0007` originally framed the ledger as open campus `PoUW-PoW` mining coupled to a capped Comb Compute Jar. However, nectR operates within campus administrative boundaries where energy-wasting proof-of-work puzzles and uncoordinated competitive mining introduce unnecessary complexity, friction, and security risks. How should the transaction ledger and state root verification be structured for closed-loop campus tutoring economies?

## Considered Options

* **Signed, hash-chained cryptographic audit log with Ed25519 signatures and Merkle state roots (supersedes `ADR-0007`)**
* **Open campus `PoUW-PoW` mining with difficulty target puzzles (`ADR-0007`)**
* **Decentralized Byzantine Fault Tolerant (BFT) multi-node consensus with voting rounds**

## Decision Outcome

Chosen option: "Signed, hash-chained cryptographic audit log with Ed25519 signatures and Merkle state roots", because treating the chain as a verifiable append-only audit log preserves cryptographic tamper-evidence (Ed25519 signatures, SHA-256 block hash chaining, and remerkleable inclusion proofs) while eliminating proof-of-work mining overhead, puzzle difficulty loops, and mining races. This record supersedes `ADR-0007`.

### Consequences

* Good, because block generation becomes deterministic, reproducible, and lightweight without artificial hash grind or energy waste.
* Good, because student and Queen nodes verify ledger integrity directly through signed command chains and Merkle proofs rather than competitive mining.
* Bad, because multi-party censorship resistance relies on Queen and Guard Bee authority signatures rather than permissionless proof-of-work mining weight.
