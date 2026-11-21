# Proposal: Add NATS Leaf Node JetStream Cross-Hive Federation & Kurtosis Chaos Testbed (`add-nats-jetstream-cross-hive-federation`)

## Why
University campus networks routinely block inbound P2P ports behind strict asymmetric NATs/firewalls, and `py-libp2p` v0.8.0 dropped `asyncio` support in favor of `trio` (preventing direct in-process embedding inside `FastAPI`/`uvicorn` workers). As synthesized in `federated_PoUW-PoW_blockchain_infrastructure.md`, **NATS Server (`nats-server`) + `nats-py` (Apache-2.0, confirmed by the May 2025 CNCF/Synadia agreement)** solves both constraints:
1. Each campus Hive opens strictly outbound TLS **NATS Leaf Node** connections on port `7422` to a DMZ relay hub without requiring inbound campus firewall holes.
2. Per-Hive **JetStream Domains & Stream Mirrors** durably replicate post-commit `AcceptedStatusGranted` and Comb-to-Comb bridge proof events across WAN outages.
3. Post-June-2024 Apache-2.0 **Kurtosis** paired with **Pumba** (`tc netem`) and **Toxiproxy** (userspace TCP fault proxy for locked-down campus VMs lacking `NET_ADMIN` or `sch_netem`) enables reproducible multi-Hive fault-injection experiments (`EXP-005`).

## Affected Bounded Contexts
- **Hive Service Layer (`src/nectr/services/`)** — outbound NATS JetStream federation adapter behind `CrossHiveBridgePort`.
- **Behavioral Experimentation (`experiments/`)** — Kurtosis + Pumba/Toxiproxy multi-Hive chaos topology (`EXP-005`).
- **Architectural Decisions:** [ADR-0005](../../../docs/adr/0005-gate-cross-hive-bridges-with-guard-bee-status-and-epoch-fx.md), [ADR-0014](../../../docs/adr/0014-adopt-nats-leaf-nodes-jetstream-and-cqrs-graph-isolation.md).

## OSS License & CVE Audit
| Package / Tool | License | Status | Notes |
| --- | --- | --- | --- |
| `nats-py` (`nats-io/nats.py`) | `Apache-2.0` | **Approved** | Native `asyncio` Python client for NATS Core & JetStream |
| `nats-server` | `Apache-2.0` | **Approved** | CNCF/Synadia May 2025 settlement guarantees Apache-2.0 |
| `kurtosis` (post-June 2024) | `Apache-2.0` | **Approved** | Pin post-June-2024 Apache-2.0 release (reject older BSL 1.11.1) |
| `pumba` / `toxiproxy` | `Apache-2.0` / `MIT` | **Approved** | Container/TCP chaos fault injection (`--duration`, `--label`) |

## Acceptance Criteria
1. `CrossHiveBridgePort` in `src/nectr/services/` publishes and consumes signed `AcceptedStatusProof` and `CombBridgeSettlement` envelopes over `nats-py` JetStream domains with idempotent replay deduplication.
2. Monthly Kolektivo/Sardex export quotas and Effective Backing Ratio FX clamping (`[0.5x, 2.0x]`, `DEC-004`) are enforced deterministically on every cross-Hive bridge settlement.
3. Multi-Hive partition tests (`EXP-005`) recover deterministically after 30-minute WAN disconnects with zero double-minting or supply drift.
