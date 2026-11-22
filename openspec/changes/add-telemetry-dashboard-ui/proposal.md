# Proposal: Add Read-Only Telemetry Dashboard UI (`add-telemetry-dashboard-ui`)

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

## Why
`src/nectr/ui/__init__.py` is currently a placeholder. Researchers and campus administrators need an interactive, read-only dashboard to inspect the Knowledge Graph, Collusion Matrix, Gini index, and Comb reserves without coupling UI rendering to write-side smart contract execution.

## Affected Bounded Contexts
- **Telemetry UI (`src/nectr/ui/`)** — primary target (read-only presentation layer).
- **Architectural Decision:** [ADR-0011](../../../docs/adr/0011-adopt-streamlit-and-networkx-for-telemetry-ui.md).

## OSS License & CVE Audit
| Package | License | Status | Notes |
| --- | --- | --- | --- |
| `streamlit` | `Apache-2.0` | **Approved** | Python-native dashboard UI; verify `pip-audit` clean |
| `networkx` | `BSD-3-Clause` | **Approved** | Already in `pyproject.toml`; Knowledge Graph & collusion metrics |

## Acceptance Criteria
1. `src/nectr/ui/` renders Knowledge Graph, Collusion Matrix, Gini time series, and Comb reserves from read-only telemetry snapshots or `HiveServiceLayer` query endpoints.
2. `src/nectr/ui/` performs zero state-mutating calls to `HiveContractEngine`.
3. `streamlit` and all transitive dependencies pass `pip-licenses` and `pip-audit`.
