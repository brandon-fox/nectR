# Domain Builder Agents & File Ownership Matrix

To guarantee zero git cross-contamination, each Domain Builder Agent owns distinct paths:

| Agent | Owned Paths | Focus |
| :--- | :--- | :--- |
| `sci-research-agent` | `paper/`, `docs/theory/` | Biomimetic equations, $MV=PQ$ velocity, collusion decay, Queen payoff proofs |
| `business-proposal-agent` | `business/`, `docs/business/` | Seed Comb ROI, retention economics, FERPA/campus compliance, swarming playbooks |
| `product-lifecycle-agent` | `docs/planning/roadmap.md`, `docs/planning/decision_log.md` | Phase 1 Institutional Seeding to Phase 2 Autonomous Swarming specs |
| `system-arch-agent` | `docs/architecture/system_design.md`, `docs/architecture/smart_contracts.md` | C4 architecture, Comb-to-Comb AMM bridge specs, threat modeling |
| `contracts-service-agent` | `src/nectr/contracts/`, `src/nectr/services/`, `tests/test_contracts.py`, `tests/test_services.py` | 5 deterministic smart contracts and Hive Service Layer API |
| `pow-compute-agent` | `src/nectr/chain/`, `tests/test_chain.py` | Hybrid `PoUW-PoW` consensus, Knowledge Flow Matrix + Collusion Decay roots |
| `design-ui-agent` | `src/nectr/ui/` | Biomimetic Hive explorer, Comb reserve gauges, knowledge graph UI |
| `ux-behavior-agent` | `src/nectr/personas/`, `experiments/`, `docs/experiments/persona_swarm_spec.md` | 6 Behavioral Persona Sub-Agents & empirical anomaly feedback |

## Coordination Patterns
- **Interactive Design:** `/grill-me` with `docs/planning/decision_log.md`
- **Parallel Execution:** `define_subagent` / `invoke_subagent`, `swarm`, or `run_workflow` with explicit path ownership in every brief.
