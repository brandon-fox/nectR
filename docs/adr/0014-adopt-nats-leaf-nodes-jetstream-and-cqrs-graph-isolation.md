---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Consensus, Service Layer & Federation Architecture
---

# Adopt NATS Leaf Nodes JetStream and CQRS Graph Isolation

## Context and Problem Statement

Campus IT firewalls block arbitrary inbound P2P ports, `py-libp2p` v0.8.0 dropped `asyncio` for `trio` (preventing in-process embedding in `FastAPI`/`uvicorn`), and executing floating-point `networkx` centrality math inside block validation risks non-deterministic consensus forks across heterogeneous university VMs.

## Considered Options

* **Outbound NATS Leaf Nodes (`nats-py`, port 7422) + per-Hive JetStream Domains + off-chain CQRS Knowledge Graph projector**
* **In-process `py-libp2p` (`trio`) inside `HiveServiceLayer` workers**
* **Synchronous on-chain `networkx` centrality execution during block validation**

## Decision Outcome

Chosen option: "Outbound NATS Leaf Nodes (`nats-py`, port 7422) + per-Hive JetStream Domains + off-chain CQRS Knowledge Graph projector", because Apache-2.0 `nats-server` and native-`asyncio` `nats-py` traverse campus NATs via outbound TLS Leaf Node links while durably mirroring `AcceptedStatusGranted` proofs across WAN partitions, and committing only a 32-byte `knowledge_graph_root` (`kg_root`) on-chain isolates `networkx`/`NetworKit`/`rustworkx` graph analytics in an asynchronous post-commit CQRS read model.

### Consequences

* Good, because campus Hives federate without inbound firewall rules or `trio`/`asyncio` event-loop deadlocks.
* Good, because block validation stays bit-for-bit deterministic across OSes and Python versions.
* Bad, because each federated Hive must configure a unique JetStream domain name and idempotent nonce deduplication.
