# Design: Mesa ABM Simulation & Hypothesis Invariant Fuzzing (`persona-abm-simulation`)

## DDD Entities & Agents
- **`HiveMesaModel(mesa.Model)`:** Orchestrates multi-hive epochs with a deterministic `seed` and `mesa.DataCollector` capturing Gini index, velocity, collusion decay, and Comb reserves.
- **`PersonaBeeAgent(mesa.Agent)`:** Base agent wrapping the 6 Behavioral Persona Sub-Agents (`AltruisticTutor`, `StrategicLearner`, `ColludingRing`, `FreeRider`, `BridgeMigrant`, `QueenGovernor`) and executing real signed transactions via `HiveServiceLayer`.
- **`ContractStateMachine(hypothesis.stateful.RuleBasedStateMachine)`:** Generates arbitrary valid/invalid escrow, settlement, dispute, and bridge sequences against `HiveContractEngine`.

## Invariants
1. **Reproducibility:** Identical `(seed, epochs, persona_mix)` inputs MUST produce bit-identical `DataCollector` time series.
2. **Real Contract Execution:** Persona agents MUST transact through `HiveServiceLayer` / `HiveContractEngine` rather than bypassing smart contract checks.
