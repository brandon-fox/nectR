---
trigger: model_decision
description: Enforce blockchain, smart contract, and service layer architectural invariants when editing src/nectr/chain, src/nectr/contracts, or src/nectr/services.
---

# Blockchain, Smart Contracts & Service Layer Architecture Rules

When designing or modifying files under `src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, or `docs/architecture/`:

1. **Hexagonal Architecture Separation:**
   - `src/nectr/chain/`: Consensus (`PoUW-PoW`), block headers, Merkle state roots, cryptographic signatures, and mempool ordering. No business logic about tutoring subjects lives here.
   - `src/nectr/contracts/`: Deterministic finite-state machines (`TokenStateAndCombContract`, `DirectionalServiceBarterContract`, `QueenGovernanceContract`, `KnowledgeGraphAndPolicingContract`, `GuardBeeCrossHiveBridgeContract`). All state transitions must be pure, deterministic functions of `(current_state, signed_tx, block_context)`.
   - `src/nectr/services/`: The portfolio Service Layer (Transaction Relayer, Knowledge Graph Telemetry Engine, Escrow Coordinator, Persona Simulation Runner, FastAPI endpoints).

2. **Hybrid Proof-of-Useful-Work (`PoUW-PoW`):**
   - Every mined block header must contain both a cryptographic PoW nonce and a `useful_compute_root` committing to the trailing epoch's **Directional Knowledge Flow Matrix** and **Pairwise Collusion Decay Scores**.

3. **Explicit Invariant Checks:**
   - Every contract transition must assert conservation of token supply:
     $$\text{TotalSupply}(\text{Hive}) = \sum \text{RawPollen} + \sum \text{LiquidNectR} + \text{CombReserve} + \text{EscrowLocked}$$
