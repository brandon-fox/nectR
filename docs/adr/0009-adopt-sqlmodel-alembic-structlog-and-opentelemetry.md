# Adopt SQLModel Alembic Structlog and OpenTelemetry

* Status: accepted
* Deciders: nectR Service Layer Architecture
* Date: 2026-11-21

## Context and Problem Statement

`HiveServiceLayer` in `src/nectr/services/hive_service.py` is currently in-memory only, lacking durable persistence, schema migrations, and structured telemetry.

## Considered Options

* **`sqlmodel` (MIT) + `alembic` (MIT) + `structlog` (MIT/Apache-2.0) + `opentelemetry-sdk` (Apache-2.0) behind hexagonal ports**
* **Raw `sqlalchemy` Core/ORM without Pydantic-unified models**
* **Custom SQLite wrapper and stdlib `logging`**

## Decision Outcome

Chosen option: "`sqlmodel` + `alembic` + `structlog` + `opentelemetry-sdk` behind hexagonal ports", because `sqlmodel` unifies Pydantic v2 validation with SQLAlchemy persistence, `alembic` manages deterministic migrations, and `structlog` + `opentelemetry-sdk` provide structured observability without leaking into `src/nectr/contracts/`.

### Consequences

* Good, because `HiveContractEngine` stays pure and deterministic while `HiveServiceLayer` gains durable storage and production tracing.
* Bad, because repository adapters must map between SQLModel table rows and domain entities.
