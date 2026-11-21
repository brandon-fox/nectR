Feature: Hive Persistence, FastAPI Endpoints, and Structured Observability
  As a nectR Hive service operator
  I want HiveServiceLayer backed by SQLModel and Alembic with FastAPI endpoints and structlog/OpenTelemetry observability
  So that Hive state persists across restarts while preserving pure contract invariants

  @red
  Scenario: Settled tutoring session persists across HiveServiceLayer repository reload
    Given a SQLModel-backed HiveServiceLayer initialized via Alembic migrations
    When a Certified Worker Bee settles a tutoring barter via the FastAPI endpoint
    Then the updated balances persist across repository reload with structured trace logs

  @red
  Scenario: Failed contract invariant rolls back persistence and in-memory state atomically
    Given a SQLModel-backed HiveServiceLayer initialized via Alembic migrations
    When a tutoring handshake fails with an invalid attestation score via the FastAPI endpoint
    Then the HTTP request is rejected and learner balances remain unchanged across repository reload
