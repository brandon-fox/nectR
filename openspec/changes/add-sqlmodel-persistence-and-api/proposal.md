# Proposal: Add SQLModel Persistence, FastAPI Endpoints, and Structured Observability (`add-sqlmodel-persistence-and-api`)

## Why
`HiveServiceLayer` (`src/nectr/services/hive_service.py`) currently stores state only in memory. Durable persistence, schema migrations, HTTP API endpoints, and structured observability are needed behind hexagonal ports/adapters without leaking infrastructure into `src/nectr/contracts/`.

## Affected Bounded Contexts
- **Hive Service Layer (`src/nectr/services/`)** — primary target.
- **Architectural Decision:** [ADR-0009](../../../docs/adr/0009-adopt-sqlmodel-alembic-structlog-and-opentelemetry.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `sqlmodel` | `MIT` | **Approved** | Pydantic v2 + SQLAlchemy ORM (`MIT`); verify `pip-audit` clean |
| `alembic` | `MIT` | **Approved** | Deterministic schema migrations |
| `fastapi` | `MIT` | **Approved** | Already in `pyproject.toml`; REST endpoints for `HiveServiceLayer` |
| `structlog` | `MIT OR Apache-2.0` | **Approved** | Structured JSON logging |
| `opentelemetry-sdk` | `Apache-2.0` | **Approved** | Distributed tracing & span export |

## Acceptance Criteria
1. `HiveServiceLayer` persists Bee accounts, escrow barters, and Comb reserves via a `sqlmodel` repository port + `alembic` migrations.
2. `fastapi` endpoints expose barter, dispute, and telemetry queries while delegating all domain rules to `HiveContractEngine`.
3. `structlog` + `opentelemetry-sdk` emit structured logs and spans with zero secrets or PII.
