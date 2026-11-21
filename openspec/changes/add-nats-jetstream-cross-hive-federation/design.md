# Design: NATS Leaf Node JetStream Federation & CQRS Event Bus (`add-nats-jetstream-cross-hive-federation`)

## DDD Ports, Adapters & Domain Events
- **`CrossHiveBridgePort` (Hexagonal Outbound Port):** Abstract protocol in `src/nectr/services/ports.py` for publishing `AcceptedStatusGranted` and `CrossHiveBridgeInitiated` events and verifying inbound mirrored proof envelopes.
- **`NatsJetStreamBridgeAdapter` (Driven Adapter):** Native `asyncio` adapter using `nats-py` connected to a local `nats-server` Leaf Node (outbound TLS port `7422`) with Hive-scoped JetStream domains (`js_domain=f"nectr-{hive_id.lower()}"`).
- **`CQRSKnowledgeGraphProjector` (Read-Model Consumer):** Subscribes to post-commit block events (`SessionSettled`, `WorkerCertified`, `DisputeResolvedToComb`, `AcceptedStatusGranted`) to materialize `networkx` / `NetworKit` / `rustworkx` centrality and Fiedler-vector cluster views completely off-chain, keeping block validation 100% free of floating-point graph solver drift (`ADR-0014`).

## Invariants
1. **Asynchronous Proof Finality:** Cross-Hive bridging never holds a synchronous cross-campus DB lock; `HIVE_B` settles a bridge credit only after verifying `HIVE_A`'s Ed25519-signed block header, Merkle inclusion proof, and `AcceptedStatusGranted` state root.
2. **Idempotent Sequence Deduplication:** Re-delivered JetStream messages carrying an already-settled `(source_hive, bridge_nonce)` are ignored without mutating `HiveContractEngine` state.
3. **Export Quota & Backing-Ratio FX Guard:** Monthly outbound volume cannot exceed `monthly_export_quota`, and epoch FX is clamped to `[0.5x, 2.0x]` (`ADR-0005`, `DEC-004`).
