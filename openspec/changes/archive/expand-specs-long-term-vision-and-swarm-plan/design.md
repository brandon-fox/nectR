# Design: Research Synthesis, Expanded Specifications, Long-Term Vision & Swarm Build Architecture

## 1. Domain-Driven Design (DDD) Alignment Across 6 Architectural Planes
1. **Consensus & State Plane (`src/nectr/chain/`):**
   - Hexagonal ports (`SignerPort`, `CanonicalCodecPort`, `MerkleAccumulatorPort`) backed by `PyNaCl`/`cryptography` (Ed25519 + BLAKE2b), `rfc8785`/`canonicaljson` (banning floats in consensus payloads), and `remerkleable`/`merklelib` + 0x00/0x01 domain-separated Sparse Merkle Tree.
   - Transcript-Oracle `PoUW-PoW` duplex difficulty coupling ($\Delta_{\text{sec}} > 0$) funded strictly from the capped Comb Compute Jar (`ADR-0007`, `ADR-0008`).
2. **Deterministic Smart Contracts Plane (`src/nectr/contracts/`):**
   - Pure finite-state machines enforced by `icontract` Design-by-Contract (`@require`, `@ensure`, `@invariant`) and verified via Quint/TLA+ (`specs/quint/`) and `Hypothesis` stateful fuzzing.
   - Extended biomimetic mechanisms: Lazy Demurrage (`DEC-001`), Waggle 60% surge co-pay (`DEC-002`), Tremble/Stop-Signal latency routing (`DEC-013`), Oophagy fraud proofs & Escrow-DKG whistleblower framing bounties, network-decayed QMP + Royal Jelly permission bitmask (Graceful Supersedure vs. 24h Emergency Election), Khoury Precocious Promotion Circuit Breaker, 3-door Senior graduation sinks (`DEC-004`), and Reproductive Swarming Bivouac Escrow (`DEC-012`).
3. **Hexagonal Hive Service Layer (`src/nectr/services/`):**
   - `SQLModel` + `Alembic` persistence (or `RocksDict` / single-writer `aiosqlite` in strict WAL snapshot mode banning SQL wall-clock functions), `FastAPI` driving adapters, and `structlog` + `OpenTelemetry` observability (`ADR-0009`).
4. **Cross-Hive Federation Plane (`src/nectr/services/` adapters):**
   - Outbound **NATS Leaf Nodes (port 7422)** + per-Hive **JetStream Domains & Stream Mirrors** (`nats-py`, Apache-2.0) to relay `AcceptedStatusGranted` proofs across asymmetric university NATs (`ADR-0014`).
5. **Off-Chain CQRS Knowledge Graph Read Model (`src/nectr/services/`, `experiments/`):**
   - Asynchronous event-sourced consumer building `networkx` / `NetworKit` / `rustworkx` graphs behind `GraphTelemetryPort` from post-commit block events while storing only a 32-byte `kg_root` on-chain (`ADR-0014`).
6. **Campus Compliance, Chaos Testbed & Observability Plane (`src/nectr/ui/`, `business/`):**
   - Zero-PII FERPA/GDPR boundary (campus off-chain DB + on-chain salted commitments / BBS+ ZK proofs), IRS Pub 970 / Title IV non-monetary service-duration credit firewall, 1EdTech LTI 1.3 (NRPS) + InCommon Shibboleth SAML 2.0 SSO, HECVAT 4.1.6, MIT + DCO 1.1, and Apereo Foundation incubation path (`ADR-0015`, `DEC-015`).
   - Reproducible multi-Hive testbeds via post-June-2024 Apache-2.0 **Kurtosis** + **Pumba** / **Toxiproxy** and **Prometheus OTLP + Perses (Apache-2.0)** + read-only `Streamlit` explorer (`ADR-0011`, `DEC-014`).

## 2. Invariants
- Zero orphaned pages under `docs/` (`nectr-docs check` and `mkdocs build --strict` pass 100%).
- All `openspec/` `spec.md` files state formal requirements/invariants and link directly to executable `features/*.feature` and `features/steps/*_steps.py` without hardcoded scenarios (`nectr.devtools.spec_links` exits `0`).
- All MADR 4.0 ADRs obey verbosity limits (`<= 70` lines, `<= 380` words, H1 `<= 70` chars, `<= 6` bullets/section) and are locked in `adrlint.lock`.
