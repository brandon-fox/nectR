# Design: Read-Only Telemetry Dashboard UI & Apache-2.0 Perses/Prometheus Observability (`telemetry-ui`)

## DDD Presentation & Observability Layer
- **`TelemetrySnapshotLoader` (Query Adapter):** Reads exported JSON/CSV/Parquet simulation artifacts or `FastAPI` CQRS read endpoints into immutable Pydantic view models.
- **`KnowledgeGraphPanel` / `CollusionMatrixPanel` / `MacroMetricsPanel` / `SwarmReadinessPanel`:** Pure presentation functions consuming `networkx.DiGraph` and epoch telemetry series (`MV=PQ` velocity, Gini index, Comb Collateralization Ratio $CR$, QMP health vector, and Waggle/Tremble latency gauges) for `streamlit` rendering (`ADR-0011`).
- **`OtlpPersesDashboardExporter` (Observability Adapter):** Exports OpenTelemetry metrics to `Prometheus` (`--web.enable-otlp-receiver` with `30m` out-of-order window for partitioned Hives) and generates declarative dashboard definitions for **Perses (`Apache-2.0`)**—explicitly replacing Grafana to maintain 100% permissive license compliance (`DEC-014`, `federated_PoUW-PoW_blockchain_infrastructure.md`).

## Invariants
1. **Strict Read-Only Boundary:** `src/nectr/ui/` MUST NOT import `HiveContractEngine` directly or invoke state-mutating service commands.
2. **Deterministic View Models:** Panel data-preparation and Perses JSON spec generators are pure and unit-testable without launching a live Streamlit or Prometheus server.
