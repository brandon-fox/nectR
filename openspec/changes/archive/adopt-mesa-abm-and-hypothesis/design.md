# Design: Mesa ABM Simulation, 15-Week Semester Volatility, Adaptive ML/RL & Hypothesis Fuzzing (`persona-abm-simulation`)

## DDD Entities, Ports & Agents
- **`HiveMesaModel(mesa.Model)`:** Orchestrates multi-hive 15-week semester epochs (0.3x baseline demand in Weeks 1–4, 3.0x–4.0x in Midterm Weeks 5–6 & 9–10, 10.0x in Finals Weeks 14–15) with a deterministic `seed` and `mesa.DataCollector` capturing Gini index, velocity ($MV=PQ$), collusion attenuation ratio, downstream Learn-then-Teach lineage depth, and Comb reserves.
- **`PersonaBeeAgent(mesa.Agent)`:** Base agent wrapping the 6 Behavioral Persona Sub-Agents (`FreshmanForagerPersona`, `CertifiedSeniorWorkerPersona`, `FinalsWeekPanickerPersona`, `SybilRoommateRingPersona`, `DriftingPollinatorPersona`, `QueenFacilitatorPersona`) and executing real Ed25519-signed transactions via `HiveServiceLayer`.
- **`AdaptiveBanditPolicy` (ML/RL Exploration Track):** Optional contextual multi-armed bandit / Q-learning policy pluggable into `SybilRoommateRingPersona` (adaptive evasion of pairwise decay and COCM clustering), `CertifiedSeniorWorkerPersona` (dynamic reservation pricing during Finals), and `QueenFacilitatorPersona` (`EXP-001` Honest vs. Nepotistic receiver-only praise).
- **`GraphTelemetryPort` (Hexagonal Analytics Port):** Abstracts graph centrality (EigenTrust, Personalized PageRank, Circle Anduin max-flow, and COCM Fiedler-vector spectral clustering) across `networkx` (default), `NetworKit` (`MIT`, C++/OpenMP for Python 3.11+), and `rustworkx` (`Apache-2.0`, Rust/rayon) while respecting `Mesa 3.x` / `nx-parallel` Python `>=3.12` floor constraints (`permissive_tooling_survey_for_nectR.md`).
- **`ContractStateMachine(hypothesis.stateful.RuleBasedStateMachine)`:** Generates arbitrary valid/invalid escrow, settlement, demurrage, dispute, and bridge sequences against `HiveContractEngine` decorated with `icontract` invariants.

## Invariants
1. **Bit-Level Reproducibility:** Identical `(seed, epochs, persona_mix, policy_mode)` inputs MUST produce bit-identical `DataCollector` time series and CSV/Parquet experiment artifacts.
2. **Real Contract Execution:** Persona agents MUST transact exclusively through `HiveServiceLayer` / `HiveContractEngine` rather than mutating balances directly.
