# Design: Hive Persistence, Deterministic WAL Snapshots, CQRS Graph Read Model & FastAPI (`hive-persistence-api`)

## DDD Ports & Adapters
- **`HiveRepositoryPort` (Hexagonal Port):** Abstract protocol in `src/nectr/services/ports.py` for loading/saving `BeeAccount`, `ServiceBarterSession`, `HiveState`, and sequential block logs.
- **`SQLModelHiveRepository` (Adapter):** Implements `HiveRepositoryPort` using `sqlmodel.Session` and `alembic`-managed tables (with single-writer SQLite WAL snapshot discipline or `RocksDict` KV backend, banning non-deterministic SQL functions such as `now()`, `CURRENT_TIMESTAMP`, and `random()`, deriving all timestamps strictly from verified `BlockHeader.timestamp`).
- **`PostCommitEventBus` & `CQRSGraphProjector` (Read-Model Adapter):** Emits immutable post-commit domain events (`PollenAllocated`, `WorkerCertified`, `BarterEscrowed`, `SessionSettled`, `DisputeResolvedToComb`, `AcceptedStatusGranted`) after block commit to update off-chain `networkx` / `NetworKit` / `rustworkx` views asynchronously while keeping on-chain consensus state restricted to the 32-byte `knowledge_graph_root` (`ADR-0014`).
- **`FastAPIHiveRouter` (Driving Adapter):** Maps HTTP requests to `HiveServiceLayer` commands and read-model queries, returning deterministic JSON responses.
- **`TelemetryAdapter` (`structlog` + `opentelemetry-sdk`):** Binds `hive_id`, `epoch`, and `tx_id` context and exports OTLP metrics (PoUW solve/verify latency, block interval, Comb ratio) with zero secrets or FERPA/GDPR PII (`ADR-0009`, `ADR-0015`).

## Invariants
1. **Purity of Contracts:** `src/nectr/contracts/` MUST NOT import `sqlmodel`, `fastapi`, `structlog`, `opentelemetry`, or `networkx`.
2. **Transactional Atomicity & Deterministic Replay:** State transitions in `HiveContractEngine` commit atomically to storage; replaying an ordered genesis + block log across any two university VMs produces bit-identical state roots.
