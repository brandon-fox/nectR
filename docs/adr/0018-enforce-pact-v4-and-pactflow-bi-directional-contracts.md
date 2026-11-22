---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Service Layer, Federation & CI Governance Architecture
---

# Enforce Pact v4 and PactFlow Bi-Directional Contracts

## Context and Problem Statement

`HiveServiceLayer` exposes `FastAPI` REST endpoints (for `Streamlit` UI, `Personas`, and Campus `LTI 1.3` clients) and asynchronous `NATS JetStream` domain events (`AcceptedStatusGranted`, `SessionSettled`). Ad-hoc integration tests risk silent schema drift across multi-agent worktrees and campus deployments. How should API and event contracts be governed without exposing secrets on fork PRs?

## Considered Options

* **`pact-python` v4.2+ (`MIT`) HTTP & Async Message Pacts + PactFlow Bi-Directional OpenAPI 3.1 verification and `can-i-deploy` release gates**
* **Provider-only OpenAPI schema snapshots without consumer-driven or async message pacts**
* **Ad-hoc mocked HTTP/NATS unit tests per consumer**

## Decision Outcome

Chosen option: "`pact-python` v4.2+ (`MIT`) HTTP & Async Message Pacts + PactFlow Bi-Directional OpenAPI 3.1 verification and `can-i-deploy` release gates", because `pact-python` and `pact-python-ffi` (`MIT`, Python `>=3.11`) verify both HTTP REST and NATS JetStream async message contracts deterministically offline via `pacts/*.json` on local hooks and fork PRs (zero secrets required), while authenticated CI/release workflows publish consumer pacts and FastAPI's OpenAPI 3.1 spec to PactFlow (`PACT_BROKER_BASE_URL` / `PACT_BROKER_TOKEN`) with `can-i-deploy` gating.

### Consequences

* Good, because breaking changes across `FastAPI` routes or cross-Hive `NATS JetStream` event payloads are caught before merge and deployment.
* Good, because local TDD and untrusted fork PRs run 100% offline with zero secret leakage (`detect-secrets` clean).
* Bad, because every new HTTP route or NATS domain event requires a corresponding Pact v4 consumer/message interaction test.
