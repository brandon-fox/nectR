# Design: Pact v4 HTTP & Async Message Contracts + PactFlow CI Integration (`add-pactflow-api-and-message-contracts`)

## 1. Contract Boundaries & Artifacts
- **HTTP Consumer -> Provider (`pacts/nectr-ui-nectr-hive-api.json`):** `TelemetrySnapshotLoader` (`src/nectr/ui/`) and Campus HTTP clients define expected `GET /hives/{hive_id}/telemetry` and `POST /hives/{hive_id}/sessions` interactions using `pact.v3. Pact` (v4 spec), verified against `FastAPIHiveRouter`.
- **Async Message Producer -> Consumer (`pacts/nectr-bridge-consumer-nectr-hive-events.json`):** `NatsJetStreamBridgeAdapter` verifies `AcceptedStatusGranted` and `SessionSettled` JSON envelopes (`micro_nectr` `int` fields, Ed25519 proof hex, `kg_root`) via Pact v4 message interactions.
- **PactFlow Bi-Directional Gate:** Exports `openapi.json` from `FastAPIHiveRouter`; in CI (`if: env.PACT_BROKER_TOKEN != ''`), uploads both `pacts/*.json` and `openapi.json` to PactFlow and executes `can-i-deploy` prior to release tagging.

## 2. Invariants
- **Zero-Secret Local & Fork Execution:** Local `.githooks/pre-commit` and fork PRs never require `PACT_BROKER_TOKEN`; provider verification runs directly against local `pacts/*.json` fixtures.
- **Strict `micro_nectr` Schema Parity:** Pact matchers enforce integer `micro_nectr` and `bps` wire types (`DEC-017`) across HTTP and NATS boundaries.
