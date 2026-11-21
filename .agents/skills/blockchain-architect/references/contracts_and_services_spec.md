# Smart Contracts & Hive Service Layer Specification

## 1. The 5 Core Deterministic Smart Contracts
1. `TokenStateAndCombContract`: Enforces `RAW_POLLEN` -> `LIQUID_NECTR` -> `ROYAL_COMB_RESERVE` transitions.
2. `DirectionalServiceBarterContract`: Enforces the 3-step tutoring handshake (`INTENT_ESCROWED` -> `SESSION_CO_SIGNED` -> `SETTLED` or `DISPUTED_TO_QUEEN`) and 0-nectR direct skill barter.
3. `QueenGovernanceContract`: Cryptographically blocks `QUEEN_ROLE` wallets from tutoring for `nectR`; routes 100% of service fees to the Comb; distributes epoch Royal Jelly dividends.
4. `KnowledgeGraphAndPolicingContract`: Updates directional subject edges `(u --topic--> v)`, downstream lineage weights, and pairwise wash-trading decay.
5. `GuardBeeCrossHiveBridgeContract`: Verifies `Accepted Status` in the host Hive and executes Comb-to-Comb AMM cross-hive swaps.

## 2. Hive Service Layer Interfaces
Provide clean domain service interfaces decouplable from transport:
- `HiveNodeService`
- `BarterEscrowService`
- `GraphTelemetryService`
- `QueenArbitrationService`
- `CrossHiveBridgeService`

## 3. DDD Layering Invariant
- `src/nectr/chain/` must remain independent of `nectr.contracts`, `nectr.services`, and `nectr.personas`.
- All contract transitions must have deterministic unit and property tests in `tests/`.
