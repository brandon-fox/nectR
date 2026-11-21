# Flagship System Design: Private PoUW-PoW Blockchain & Hive Service Layer

This architecture serves as the **System Design Portfolio Highlight** for **nectR**, separating the distributed consensus layer, the deterministic smart contract state machine, and the hexagonal Hive Service Layer.

```mermaid
flowchart TB
    subgraph Clients["Campus Clients & Persona Swarm"]
        WebUI["Hive Explorer & Dashboard"]
        Personas["6 Behavioral Persona Sub-Agents"]
    end

    subgraph ServiceLayer["Hive Service Layer (src/nectr/services/)"]
        EscrowSvc["Barter Escrow & Session Handshake Service"]
        GraphSvc["Directional Knowledge Graph & Telemetry Service"]
        QueenSvc["Queen Governance, Certification & Arbitration Service"]
        BridgeSvc["Guard Bee Cross-Hive Bridge Service"]
    end

    subgraph Contracts["Deterministic Smart Contracts (src/nectr/contracts/)"]
        C1["1. TokenStateAndCombContract"]
        C2["2. DirectionalServiceBarterContract"]
        C3["3. QueenGovernanceContract"]
        C4["4. KnowledgeGraphAndPolicingContract"]
        C5["5. GuardBeeCrossHiveBridgeContract"]
    end

    subgraph Chain["Private PoUW-PoW Blockchain Core (src/nectr/chain/)"]
        Mempool["Signed Tx Mempool"]
        PoUW["Hybrid PoW + Useful Compute (EigenTrust/Decay Matrix) Miner"]
        Ledger["Immutable Block Ledger & Merkle State Tree"]
    end

    Clients <--> ServiceLayer
    ServiceLayer <--> Contracts
    Contracts <--> Chain
```

## Key System Design Highlights

1. **Hybrid Proof-of-Useful-Work (`PoUW-PoW`):** Mining nodes secure block immutability via cryptographic hashing *and* compute the trailing epoch's directional knowledge flow matrix and pairwise collusion decay root.
2. **Hexagonal Service Layer:** Decouples fast off-chain session matching and telemetry queries from on-chain state settlement.
3. **Deterministic State Machine Contracts:** Zero external oracle dependency; every state transition is verifiable from signed directional session handshakes.
