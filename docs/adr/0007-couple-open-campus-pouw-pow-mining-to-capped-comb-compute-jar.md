---
status: superseded by ADR-0019
date: 2026-11-21
decision-makers:
  - nectR Consensus & System Design Architecture
---

# Couple Open Campus PoUW-PoW Mining to Capped Comb Compute Jar

## Context and Problem Statement

The ledger must commit verifiable anti-collusion knowledge-graph state roots and stay open to student laptop nodes without printing inflationary block rewards or leaking infrastructure concerns into smart contracts.

## Considered Options

* **Open campus `PoUW-PoW` mining paid strictly from a capped Comb Compute Jar, orchestrated through the hexagonal `HiveServiceLayer`**
* **Open PoW mining with uncapped inflationary coinbase minting**
* **Closed institutional-only validator nodes with zero student node participation**

## Decision Outcome

Chosen option: "Open campus `PoUW-PoW` mining paid strictly from a capped Comb Compute Jar, orchestrated through the hexagonal `HiveServiceLayer`", because any student laptop can verify the epoch's Knowledge Graph, Gini, and collusion-decay proof (`UsefulComputeProof`) and earn capped Comb compute payouts—pausing automatically if the jar runs low so total Hive supply remains strictly conserved.

### Consequences

* Good, because consensus (`src/nectr/chain/`), deterministic contracts (`src/nectr/contracts/`), and service orchestration (`src/nectr/services/`) maintain clean DDD boundaries with zero systemic inflation.
* Bad, because miner coin payouts temporarily pause whenever Comb fee/demurrage inflows lag compute demand.
