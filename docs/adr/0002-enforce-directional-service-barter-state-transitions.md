---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Protocol & Contracts Architecture
---

# Enforce Directional Service Barter State Transitions

## Context and Problem Statement

Standard ERC-20-style blind token transfers allow students and Sybil rings to move currency without verified educational work, breaking closed-loop velocity telemetry and enabling unbacked voucher extraction.

## Considered Options

* **Account model with partitioned token states (`RAW_POLLEN`, `LIQUID_NECTR`, `ROYAL_COMB_RESERVE`) and mandatory `DirectionalServiceBarterContract` handshakes**
* **Unrestricted ERC-20 account transfers with off-chain honor logs**
* **Cardano-style eUTXO colored-coin scripts**

## Decision Outcome

Chosen option: "Account model with partitioned token states and mandatory `DirectionalServiceBarterContract` handshakes", because it eliminates blind transfers on-chain while avoiding eUTXO dust fragmentation and shared Comb vault contention. Every transfer must record `Tutor -> Learner`, `Subject`, `Duration`, and co-signed `Attestation` (or `0-nectR` reciprocal skill barter), or execute an explicit `Comb`/bridge contract call.

### Consequences

* Good, because every token movement produces a verifiable directed edge on the Hive knowledge graph while strictly conserving closed-loop supply.
* Bad, because casual transfers without a service handshake or `Comb` contract transition are intentionally impossible.
