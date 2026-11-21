---
name: blockchain-architect
description: Guides implementation and verification of the private nectR PoUW-PoW blockchain, the 5 deterministic smart contracts, and the Hive Service Layer for the flagship System Design Portfolio.
---

# nectR Blockchain, Smart Contracts & Service Layer Skill

Use this skill when building or reviewing `src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, or `docs/architecture/`.

## 1. The 5 Core Deterministic Smart Contracts
1. `TokenStateAndCombContract`: Enforces `RAW_POLLEN` $\rightarrow$ `LIQUID_NECTR` $\rightarrow$ `ROYAL_COMB_RESERVE` transitions.
2. `DirectionalServiceBarterContract`: Enforces the 3-step tutoring handshake (`INTENT_ESCROWED` $\rightarrow$ `SESSION_CO_SIGNED` $\rightarrow$ `SETTLED` or `DISPUTED_TO_QUEEN`) and 0-nectR direct skill barter.
3. `QueenGovernanceContract`: Cryptographically blocks `QUEEN_ROLE` wallets from tutoring for `nectR`; routes 100% of service fees to the Comb; distributes epoch Royal Jelly dividends.
4. `KnowledgeGraphAndPolicingContract`: Updates directional subject edges $(u \xrightarrow{\text{topic}} v)$, downstream lineage weights, and pairwise wash-trading decay.
5. `GuardBeeCrossHiveBridgeContract`: Verifies `Accepted Status` in the host Hive and executes Comb-to-Comb AMM cross-hive swaps.

## 2. Service Layer Portfolio Requirements
- Provide clean domain service interfaces (`HiveNodeService`, `BarterEscrowService`, `GraphTelemetryService`, `QueenArbitrationService`, `CrossHiveBridgeService`) decouplable from the transport layer.
- Include deterministic unit and property tests in `tests/`.
