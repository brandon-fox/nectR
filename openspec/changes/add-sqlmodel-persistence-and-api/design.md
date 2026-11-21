# Design: Hive Persistence & API (`hive-persistence-api`)

## DDD Ports & Adapters
- **`HiveRepositoryPort` (Hexagonal Port):** Abstract protocol in `src/nectr/services/ports.py` for loading/saving `BeeAccount`, `ServiceBarterSession`, and `HiveState`.
- **`SQLModelHiveRepository` (Adapter):** Implements `HiveRepositoryPort` using `sqlmodel.Session` and `alembic`-managed tables.
- **`FastAPIHiveRouter` (Driving Adapter):** Maps HTTP requests to `HiveServiceLayer` commands, returning deterministic JSON responses.
- **`TelemetryAdapter` (`structlog` + `opentelemetry-sdk`):** Binds `hive_id`, `epoch`, and `tx_id` context without logging secrets or private keys.

## Invariants
1. **Purity of Contracts:** `src/nectr/contracts/` MUST NOT import `sqlmodel`, `fastapi`, `structlog`, or `opentelemetry`.
2. **Transactional Atomicity:** State transitions in `HiveContractEngine` commit atomically to SQLModel storage; failed invariant checks roll back the DB transaction.
