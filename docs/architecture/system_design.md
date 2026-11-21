# Flagship System Design: Private PoUW-PoW Blockchain and Hive Service Layer

This architecture defines **nectR**'s closed-loop, peer-to-peer campus tutoring platform, separating cryptographic consensus (`src/nectr/chain/`), deterministic smart contract state machines (`src/nectr/contracts/`), and the hexagonal application layer (`src/nectr/services/`). Domain acronyms (`MV = PQ`, `PoUW-PoW` = Proof-of-Useful-Work plus Proof-of-Work, `FX`, `QMP`) and ubiquitous language terms are defined in the [Domain Glossary](../glossary.md) per `DEC-008`.

Throughout this specification, **Implemented Baseline** denotes code currently present in `src/nectr/`, **Wave 1 Target Interfaces** denotes contracts/adapters specified in amended [ADR-0008](../adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md) and [ADR-0009](../adr/0009-adopt-sqlmodel-alembic-structlog-and-opentelemetry.md), and **Locked Protocol Specifications** denotes economic rules in `DEC-001`–`DEC-004` and `ADR-0003`–`ADR-0007` scheduled across implementation waves.

## Architectural Principles

1. **No Blind Token Transfers ([ADR-0002](../adr/0002-enforce-directional-service-barter-state-transitions.md)):** Every peer transfer executes through `DirectionalServiceBarterContract` (`Tutor -> Learner`, `Subject`, `Duration`, co-signed `Attestation`, or `0-nectR` reciprocal skill barter) or an explicit `ROYAL_COMB_RESERVE` (`Comb`) / cross-Hive bridge call.
2. **Zero-Fee P2P Barter & Comb Fee Routing ([ADR-0004](../adr/0004-route-governance-fees-to-comb-with-phase-split-royal-jelly.md)):** Peer-to-peer tutoring settlements charge `0%` fee, while `100%` of governance fees route into `Comb`.
3. **Strict Queen Separation of Powers ([ADR-0003](../adr/0003-enforce-multi-tier-beekeeper-and-queen-governance.md)):** `QUEEN` accounts cannot act as tutors, receive `RAW_POLLEN`, or bridge `LIQUID_NECTR`; institutional `Beekeeper` authorities retain transparent override and bond-slashing powers.
4. **Capped Comb Compute Jar ([ADR-0007](../adr/0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md)):** Open campus laptop mining couples SHA-256 Proof-of-Work (`PoW`) with `UsefulComputeProof` verification (`PoUW`), paid strictly from a capped Comb sub-pool with zero inflationary coinbase minting.
5. **Cryptographic & Merkle Integrity ([ADR-0008](../adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md)):** Wave 1 upgrades ad-hoc JSON hashing to `canonicaljson`, Ed25519 signatures via `cryptography`, and SSZ Merkle inclusion proofs via `remerkleable` (`MIT`).
6. **Hexagonal Purity ([ADR-0009](../adr/0009-adopt-sqlmodel-alembic-structlog-and-opentelemetry.md)):** Persistence (`SQLModel` + `Alembic`), HTTP (`FastAPI`), and telemetry (`structlog` + `opentelemetry-sdk`) attach through ports in `src/nectr/services/` while `src/nectr/contracts/` remains pure Python.

## C4 Level 1: System Context

```mermaid
flowchart TB
    subgraph Actors["Campus Participants & Governance Actors"]
        Learner["Learner Bee<br/>(Freshman Forager / Panicker)"]
        Worker["Certified Worker Bee<br/>(Accredited Student Tutor)"]
        Pollinator["Pollinator Visitor<br/>(Cross-Hive Migrant)"]
        Queen["Queen Steward<br/>(Phase 1 Faculty / Phase 2 Student)"]
        Beekeeper["Beekeeper<br/>(Institutional Override & Auditor)"]
        Sponsor["Campus Sponsor<br/>(Seed Comb Funder)"]
        Miners["Open Campus Laptop Nodes<br/>(PoUW-PoW Validators)"]
    end

    subgraph Platform["nectR Multi-Hive Platform"]
        HiveA["nectR Home Hive (H_A)<br/>Closed-Loop Tutoring Ledger & Contracts"]
        HiveB["nectR Target / Daughter Hive (H_B)<br/>Autonomous Swarming & Guard Bee Bridge"]
    end

    Sponsor -->|"Injects Seed Comb (Phase 1)"| HiveA
    Learner -->|"Spends RAW_POLLEN / LIQUID_NECTR"| HiveA
    Worker -->|"Refines RAW_POLLEN via Tutoring"| HiveA
    Queen -->|"Certifies Workers & Arbitrates Disputes"| HiveA
    Beekeeper -->|"Logged Emergency Override & Bond Slashing"| HiveA
    Miners -->|"Verifies UsefulComputeProof & Mines Blocks"| HiveA
    Pollinator -->|"Tutors K>=3 Local Peers for Accepted Status"| HiveB
    HiveA <-->|"Comb-to-Comb Bridge (Epoch FX + 5% Toll)"| HiveB
```

## C4 Level 2: Container Architecture

```mermaid
flowchart TB
    subgraph Clients["Driving Clients & Simulation Containers"]
        UI["Read-Only Telemetry UI<br/>src/nectr/ui/ (Streamlit + NetworkX, ADR-0011)"]
        Personas["6-Persona ABM Swarm<br/>src/nectr/personas/simulator.py (Mesa/Hypothesis target, ADR-0010)"]
        CampusHTTP["Campus HTTP Clients"]
    end

    subgraph ServiceBoundary["Hive Service Layer (src/nectr/services/)"]
        FastAPI["FastAPIHiveRouter (Wave 1 ADR-0009)<br/>src/nectr/services/api.py"]
        ServiceCore["HiveServiceLayer<br/>src/nectr/services/hive_service.py"]
        Telemetry["TelemetryAdapter (Wave 1 ADR-0009)<br/>src/nectr/services/telemetry.py (structlog + OpenTelemetry)"]
        RepoPort["HiveRepositoryPort & TelemetryPort<br/>src/nectr/services/ports.py"]
        SQLRepo["SQLModelHiveRepository & Alembic<br/>persistence.py + src/nectr/services/migrations/"]
    end

    subgraph DomainLedger["Deterministic Domain & Consensus Containers"]
        Contracts["HiveContractEngine (Pure Python)<br/>src/nectr/contracts/engine.py"]
        Chain["HiveBlockchain (PoUW-PoW Ledger)<br/>src/nectr/chain/ledger.py"]
        DB[("SQLite / SQL Database<br/>Alembic-Managed State")]
    end

    UI -->|"Read-only telemetry queries"| FastAPI
    CampusHTTP -->|"HTTPS / JSON commands"| FastAPI
    Personas -->|"Orchestrated simulation calls"| ServiceCore
    FastAPI --> ServiceCore
    ServiceCore --> Telemetry
    ServiceCore --> RepoPort
    RepoPort -.->|"implements"| SQLRepo
    SQLRepo --> DB
    ServiceCore -->|"Executes deterministic transitions"| Contracts
    ServiceCore -->|"Submits txs & mines epoch blocks"| Chain
```

## C4 Level 3: Component and Strict DDD Layering

Every Bounded Context defined in `openspec/project.md` enforces unidirectional inward/downward dependencies verified automatically by `.agents/skills/blockchain-architect/scripts/verify_architecture_gate.py`.

```mermaid
flowchart LR
    subgraph Driving["External & Simulation Layer"]
        UIMod["ui/__init__.py (Stub)"]
        SimMod["personas/simulator.py"]
        APIRouter["services/api.py (FastAPIHiveRouter)"]
    end

    subgraph AppLayer["Application & Ports Layer (src/nectr/services/)"]
        SvcLayer["HiveServiceLayer<br/>bootstrap_sponsored_hive<br/>execute_tutoring_handshake<br/>compute_useful_work_proof<br/>mine_epoch_block"]
        Ports["ports.py<br/>HiveRepositoryPort<br/>TelemetryPort"]
        Adapters["Adapters (ADR-0009)<br/>SQLModelHiveRepository<br/>TelemetryAdapter<br/>migrations/"]
    end

    subgraph ContractsCtx["Smart Contracts Context (src/nectr/contracts/)"]
        Engine["HiveContractEngine<br/>BeeAccount, ServiceBarterSession<br/>TokenState, BeeRole, SessionStatus<br/>assert_supply_conservation()"]
    end

    subgraph ChainCtx["Consensus & Ledger Context (src/nectr/chain/)"]
        Baseline["ledger.py (Baseline)<br/>HiveBlockchain, Block, BlockHeader<br/>UsefulComputeProof, compute_sha256"]
        Crypto["Wave 1 Crypto (ADR-0008)<br/>Ed25519Signer / Ed25519Verifier<br/>CanonicalPayload, SignedTransaction<br/>MerkleInclusionProof (remerkleable)"]
    end

    UIMod -.->|"Target read-only path"| APIRouter
    APIRouter --> SvcLayer
    SimMod --> SvcLayer
    SimMod -.->|"Transitional direct calls (bridge/pollen/verify)"| Engine
    SimMod -.->|"Transitional direct calls (submit_tx/verify_chain)"| Baseline
    SvcLayer --> Ports
    Ports -.-> Adapters
    SvcLayer --> Engine
    SvcLayer --> Baseline
    Baseline --> Crypto
```

### Bounded Context Dependency Matrix

| Bounded Context (`src/nectr/`) | Allowed Imports | Forbidden Imports | Transitional Codebase Note |
|---|---|---|---|
| `src/nectr/chain/` | Python stdlib, `pydantic`, plus Wave 1 `cryptography`, `canonicaljson`, `remerkleable` | `nectr.contracts`, `nectr.services`, `nectr.personas`, ORM/HTTP libs | Enforced via AST check in `verify_architecture_gate.py` |
| `src/nectr/contracts/` | Python stdlib ONLY (`__future__`, `dataclasses`, `enum.StrEnum`, `typing`) | `sqlmodel`, `alembic`, `fastapi`, `structlog`, `opentelemetry`, `pydantic`, `nectr.*` | Pure deterministic state machine (`HiveContractEngine`) |
| `src/nectr/services/` | `nectr.contracts`, `nectr.chain`, `sqlmodel`, `alembic`, `fastapi`, `structlog`, `opentelemetry-sdk` | `nectr.personas`, `nectr.ui` | Exposes ports in `ports.py`; keeps `contracts/` pure |
| `src/nectr/personas/` & `src/nectr/ui/` | `nectr.services` (and read-only contract enums/types) | Direct DB mutations bypassing `HiveServiceLayer` | `personas/simulator.py` currently invokes `hive.contracts.{register_bee, allocate_raw_pollen_to_learner, bridge_nectr_to_target_hive}` and `hive.blockchain.{submit_transaction, verify_chain}` directly alongside `HiveServiceLayer`; Wave 1 target routes all commands through `HiveServiceLayer` |

## PoUW-PoW Open Campus Mining and Capped Comb Compute Jar

Under [ADR-0007](../adr/0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md), **nectR** couples lightweight cryptographic hashing (`PoW`) with deterministic Knowledge Graph verification (`PoUW`) so student laptop nodes secure ledger immutability without inflationary block rewards.

### Consensus Commitment Model

In `src/nectr/chain/ledger.py`, every mined `Block` binds two commitments inside a frozen `BlockHeader`:

- **`UsefulComputeProof` Fields (`ConfigDict(frozen=True, extra="forbid")`):**
  - `epoch: int` — Monotonic epoch counter managed by `HiveServiceLayer`.
  - `active_bees: int` — Registered account count in the Hive (`len(contracts.accounts)`).
  - `total_directional_edges: int` — Settled transaction edge count (`len(contracts.settled_tx_log)`).
  - `collusion_discounted_velocity: float` — Sum of `amount * effective_weight` across settled transactions.
  - `gini_coefficient: float` — Inequality index in `[0.0, 1.0]` computed by `compute_gini_coefficient()` over non-`QUEEN` `liquid_nectr_balance + raw_pollen_balance`.
  - `graph_state_hash: str` — SHA-256 digest of sorted `tutor_effectiveness` and `comb_reserve` snapshot.
- **`BlockHeader` Fields:** `hive_id: str`, `height: int`, `prev_hash: str`, `merkle_root: str`, `knowledge_graph_root: str`, `difficulty: int` (default `2`), `nonce: int`, `timestamp: float`.
- **Dual Binding:** `HiveBlockchain.mine_block()` sets `knowledge_graph_root = useful_compute_proof.to_commitment_hash()` and increments `nonce` until `BlockHeader.block_hash()` begins with `"0" * self.difficulty`. `HiveBlockchain.verify_chain()` recomputes PoW prefix, `merkle_root`, `knowledge_graph_root`, and `prev_hash` links across all blocks (genesis `height=0`, `prev_hash="0" * 64`, `timestamp=1700000000.0`).

### Capped Comb Compute Jar Orchestration (`ADR-0007`)

To preserve strict closed-loop supply conservation (`MV = PQ`) while rewarding student laptop verifiers:

1. **Strict DDD Placement:** Compute rebate payouts are orchestrated exclusively inside `HiveServiceLayer` (application layer), NEVER inside `src/nectr/chain/`, so `chain/` contains zero tokenomics or balance state.
2. **Non-Inflationary Funding:** The Comb Compute Jar is a bounded sub-allocation of `ROYAL_COMB_RESERVE` fed solely by governance fees (`certify_worker_bee`, `resolve_disputed_session`), `DEC-001` idle-balance demurrage, and `5%` cross-Hive bridge tolls (`ADR-0005`). Zero coinbase tokens are minted on block creation.
3. **Automatic Pause on Reserve Lag:** Before disbursing a mining rebate from the jar, `HiveServiceLayer` checks available jar balance. If governance/demurrage inflows lag compute demand and the jar drops below its floor, coin payouts automatically pause while `PoUW-PoW` block verification continues, ensuring `total_minted_supply` remains strictly conserved.

## Wave 1 Consensus and Cryptographic Ledger Specification (`ADR-0008`)

[ADR-0008](../adr/0008-adopt-ed25519-canonicaljson-and-merklelib.md) (as amended in PR #19) replaces ad-hoc hashing in `src/nectr/chain/ledger.py` with audited, `MIT`-compatible cryptography while preserving backward compatibility for existing dict-based callers.

### Implemented Baseline vs. Wave 1 Crypto Components

| Component | Status | Library & License | Responsibility & Typing Constraints |
|---|---|---|---|
| `compute_sha256`, `compute_merkle_root`, `UsefulComputeProof`, `BlockHeader`, `Block`, `HiveBlockchain` | **Implemented Baseline** | Python stdlib `hashlib`/`json` + `pydantic` | SHA-256 hex digests, sorted compact JSON serialization, odd-leaf duplication Merkle root (`"EMPTY_BLOCK"` when empty), PoW nonce search, and chain verification |
| `CanonicalPayload` | **Wave 1 Target (`ADR-0008`)** | `canonicaljson` (`Apache-2.0`) | Encodes dicts/models via `canonicaljson.encode_canonical_json` (RFC 7159 deterministic byte layout) prior to SHA-256 hashing across Python versions and OSes |
| `Ed25519Signer`, `Ed25519Verifier`, `SignedTransaction` | **Wave 1 Target (`ADR-0008`)** | `cryptography` (`Apache-2.0 / BSD-3-Clause`) | Deterministic Ed25519 signing/verification via `cryptography.hazmat.primitives.asymmetric.ed25519`; zero raw private-key logging; `HiveBlockchain` validates `SignedTransaction` signatures while keeping dict compatibility |
| `MerkleInclusionProof` | **Wave 1 Target (`ADR-0008`)** | `remerkleable` (`MIT`, zero runtime deps) | Typed adapter wrapping `remerkleable.tree` (`subtree_fill_to_contents`, `RootNode`, `to_gindex`, `merkle_hash`) with `0x00`-prefixed leaf hashing for transaction inclusion proofs in `BlockHeader.merkle_root` |

### Library Selection & Typing Rules (`ADR-0008`)

- **Why `remerkleable` (`MIT`) Was Adopted:** `remerkleable` is `MIT`-licensed, carries zero runtime transitive dependencies, passes all Python 3.11–3.13 matrices, and produces deterministic SSZ binary Merkle inclusion proofs.
- **Explicitly Rejected Libraries:**
  - `pymerkle` — **Rejected** due to `GPLv3+` copyleft licensing, which violates nectR's `MIT`-compatible transitive license policy (`DEC-007`).
  - `merklelib` (`1.0`, 2018 release) — **Rejected** after runtime verification proved it crashes on Python 3.10+/3.12 with `AttributeError: module 'collections' has no attribute 'Iterable'`.
- **Strict `mypy` Compliance:** Because `remerkleable` ships without `py.typed` and `pyproject.toml` forbids `[[tool.mypy.overrides]]` (enforced by hygiene tests), the thin adapter inside `src/nectr/chain/` isolates its `remerkleable.tree` import with `# type: ignore[import-untyped]` and narrows all return values explicitly under `mypy --strict`.

## Wave 1 Hexagonal Persistence, API, and Observability (`ADR-0009`)

Currently, `HiveServiceLayer` (`src/nectr/services/hive_service.py`) maintains state strictly in memory (`bootstrap_sponsored_hive`, `execute_tutoring_handshake`, `compute_useful_work_proof`, `mine_epoch_block`). [ADR-0009](../adr/0009-adopt-sqlmodel-alembic-structlog-and-opentelemetry.md) and `openspec/changes/add-sqlmodel-persistence-and-api/design.md` introduce durable persistence, HTTP routing, and structured telemetry behind hexagonal ports without modifying `src/nectr/contracts/`.

### Hexagonal Ports and Adapters (`src/nectr/services/`)

| Module / Symbol | Role | Stack & License | Contract & Isolation Guarantees |
|---|---|---|---|
| `HiveRepositoryPort`, `TelemetryPort` (`src/nectr/services/ports.py`) | Driven Port Protocols | Python `typing.Protocol` | Abstract interfaces for loading/persisting `BeeAccount`, `ServiceBarterSession`, and `HiveState`, and emitting structured audit/trace events |
| `SQLModelHiveRepository` (`src/nectr/services/persistence.py`) | Persistence Adapter | `sqlmodel` (`MIT`) | Implements `HiveRepositoryPort` using `sqlmodel.Session`, mapping domain dataclasses to relational rows without introducing ORM classes into `contracts/` |
| Programmatic Migrations (`src/nectr/services/migrations/`) | Schema Lifecycle | `alembic` (`MIT`) | Deterministic forward/rollback database migrations invoked programmatically for test/runtime environments |
| `FastAPIHiveRouter` (`src/nectr/services/api.py`) | Driving HTTP Adapter | `fastapi` (`MIT`) | Translates validated HTTP payloads into `HiveServiceLayer` commands and returns deterministic JSON responses (exact route URI schemas remain governed by the `add-sqlmodel-persistence-and-api` implementation) |
| `TelemetryAdapter` (`src/nectr/services/telemetry.py`) | Observability Adapter | `structlog` (`MIT/Apache-2.0`) + `opentelemetry-sdk` (`Apache-2.0`) | Binds `hive_id`, `epoch`, and `tx_id` context onto logs and spans with zero secrets, private keys, or student PII |

### Backward Compatibility and Atomic Rollback Invariant

1. **Optional Port Defaults:** `HiveServiceLayer.__init__(hive_id, difficulty=2, accepted_status_peer_threshold=3, repository=None, telemetry=None)` preserves `repository=None` (in-memory) and `telemetry=None` defaults so existing simulation and BDD invariant suites run unchanged.
2. **Atomic Rollback on `ContractViolationError`:** Whenever `HiveContractEngine` raises `ContractViolationError`, `HiveServiceLayer` aborts the active `SQLModelHiveRepository` unit of work and rolls back the database transaction before commit, ensuring ledger, contract state, and SQL storage never diverge.

## Comb-to-Comb Cross-Hive Bridge Sequence Flow (`ADR-0005`, `DEC-003`, `DEC-004`)

Cross-Hive liquidity migration prevents Sybil drains and Bancor Maximal Extractable Value (MEV) attacks by gating transfers behind Guard Bee `Accepted Status` (`K = 3` distinct peers per `DEC-003`) and epoch health-ratio FX (`[0.5x, 2.0x]` + `5%` Comb toll per `DEC-004`).

```mermaid
sequenceDiagram
    actor Pollinator as "Pollinator Visitor (Home: HIVE_A)"
    participant ServiceA as "HiveServiceLayer (HIVE_A)"
    participant BridgeA as "GuardBeeCrossHiveBridge (HIVE_A)"
    participant BridgeB as "GuardBeeCrossHiveBridge (HIVE_B)"
    participant Chain as "HiveBlockchain (HIVE_A & HIVE_B)"

    Note over Pollinator,BridgeB: Phase 1 — Earn Accepted Status in Destination Hive
    Pollinator->>BridgeB: register_bee(bee_id, home_hive_id="HIVE_A")
    loop Tutor K = 3 distinct peers in HIVE_B (prior_pair_txs == 0, score >= 0.6)
        Pollinator->>BridgeB: settle_co_signed_session(session_id, score >= 0.6, comp_hash)
        BridgeB-->>BridgeB: Add learner_id to distinct_peers_tutored_in_hive
    end
    BridgeB-->>Pollinator: len(distinct_peers) >= 3 -> Add "HIVE_B" to accepted_in_hives

    Note over Pollinator,Chain: Phase 2 — Guarded Comb-to-Comb Bridge Transfer
    Pollinator->>ServiceA: Request bridge(bee_id, target_hive="HIVE_B", amount)
    ServiceA->>BridgeA: bridge_nectr_to_target_hive(bee_id, target_hive, amount, bridge_toll_rate=0.05)
    BridgeA->>BridgeA: Verify role != QUEEN and 0 < amount <= liquid_nectr_balance
    BridgeA->>BridgeB: Verify "HIVE_B" in target_acct.accepted_in_hives
    BridgeA->>BridgeA: Compute health ratios & clamp FX in [0.5, 2.0]
    BridgeA->>BridgeA: source_toll = round(amount * 0.05, 6) -> HIVE_A.comb_reserve
    BridgeA->>BridgeA: net_out = amount - source_toll; burn net_out from HIVE_A.total_minted_supply
    BridgeA->>BridgeA: HIVE_A.assert_supply_conservation()
    BridgeA->>BridgeB: Mint minted_in_target = round(net_out * exchange_rate, 6)
    BridgeB->>BridgeB: Credit target_acct.liquid_nectr_balance & HIVE_B.total_minted_supply
    BridgeB->>BridgeB: HIVE_B.assert_supply_conservation()
    BridgeA-->>ServiceA: Return CROSS_HIVE_BRIDGE tx record
    ServiceA->>Chain: submit_transaction(bridge_tx) & mine_epoch_block()
```

See [Smart Contracts Specification](smart_contracts.md) for full state machine diagrams, mathematical invariants, and the reconciliation mapping of all five logical service interfaces.
