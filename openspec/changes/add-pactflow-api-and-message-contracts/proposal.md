# Proposal: Enforce Pact v4 & PactFlow Bi-Directional HTTP and Async Message Contracts (`add-pactflow-api-and-message-contracts`)

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

## Why
As `HiveServiceLayer` (`FastAPI`) connects to multiple independent consumers (`Streamlit` Telemetry UI, `Mesa` Persona HTTP runners, Campus `LTI 1.3` adapters, and cross-Hive `NATS JetStream` subscribers), ad-hoc mocked unit tests risk silent payload drift across parallel multi-agent worktrees. Per [ADR-0018](../../../docs/adr/0018-enforce-pact-v4-and-pactflow-bi-directional-contracts.md), we adopt **`pact-python` v4.2+ (`MIT`) and PactFlow** for end-to-end API and event contract governance:
1. **HTTP REST Consumer-Driven Pacts:** Verify request/response contracts between `TelemetrySnapshotLoader` / `LTI 1.3` / Persona HTTP clients and `FastAPIHiveRouter`.
2. **Asynchronous Message Pacts (`NATS JetStream` & CQRS):** Use Pact v4 `MessageConsumer` / `MessageProvider` to verify `AcceptedStatusGranted`, `CrossHiveBridgeInitiated`, and `SessionSettled` event schemas across `HIVE_ALPHA` and `HIVE_BETA`.
3. **Offline Fork Safety + PactFlow Bi-Directional CI (`can-i-deploy`):** Verify generated `pacts/*.json` artifacts and FastAPI's OpenAPI 3.1 schema 100% offline during local TDD hooks and untrusted fork PRs (zero secrets required), while publishing Consumer Pacts + OpenAPI 3.1 provider verification to **PactFlow** (`PACT_BROKER_BASE_URL`, `PACT_BROKER_TOKEN`) with `can-i-deploy` gating on `main` and `release.yml`.

## Affected Bounded Contexts
- **Hive Service Layer (`src/nectr/services/`)** — `FastAPI` OpenAPI 3.1 provider & `NATS JetStream` message provider verification.
- **Telemetry UI & Personas (`src/nectr/ui/`, `src/nectr/personas/`)** — Pact v4 HTTP & message consumers generating `pacts/*.json`.
- **CI & Release Workflows (`.github/workflows/`)** — PactFlow publish & `can-i-deploy` steps gated on broker secret presence.
- **Architectural Decision:** [ADR-0018](../../../docs/adr/0018-enforce-pact-v4-and-pactflow-bi-directional-contracts.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `pact-python` (`>=4.2.0`) | `MIT` | **Approved** | Official Pact v4 Python SDK (`requires-python >=3.11`) |
| `pact-python-ffi` (`>=0.5.12`) | `MIT` | **Approved** | Rust FFI Pact v4 core (`MIT` SPDX, prebuilt Linux/macOS/Windows wheels) |

## Acceptance Criteria
1. Consumer Pact v4 tests generate deterministic `pacts/*.json` contracts for `FastAPIHiveRouter` HTTP routes and `NATS JetStream` domain events, verified against `HiveServiceLayer` in `pytest` and `behave` with zero external network or secret requirement.
2. `FastAPIHiveRouter` exports a deterministic OpenAPI 3.1 JSON schema validated alongside consumer pacts for PactFlow Bi-Directional Contract Testing.
3. CI/release workflows publish pacts/schemas to PactFlow and run `can-i-deploy` whenever `PACT_BROKER_BASE_URL` and `PACT_BROKER_TOKEN` are configured in GitHub Secrets (`detect-secrets` clean).
