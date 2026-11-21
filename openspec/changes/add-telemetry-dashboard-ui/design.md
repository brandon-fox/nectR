# Design: Read-Only Telemetry Dashboard UI (`telemetry-ui`)

## DDD Presentation Layer
- **`TelemetrySnapshotLoader` (Query Adapter):** Reads exported JSON/CSV simulation artifacts or `FastAPI` read endpoints into immutable Pydantic view models.
- **`KnowledgeGraphPanel` / `CollusionMatrixPanel` / `MacroMetricsPanel`:** Pure presentation functions consuming `networkx.DiGraph` and epoch telemetry series for `streamlit` rendering.

## Invariants
1. **Strict Read-Only Boundary:** `src/nectr/ui/` MUST NOT import `HiveContractEngine` directly or invoke state-mutating service commands.
2. **Deterministic View Models:** Panel data-preparation functions are pure and unit-testable without launching a live Streamlit server.
