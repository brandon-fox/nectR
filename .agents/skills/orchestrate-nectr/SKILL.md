---
name: orchestrate-nectr
description: Orchestrates the 8 specialized Domain Builder Agents (Scientific, Business, Product, Architecture, Software/Contracts, Hardware/PoW, Design, UX) and the 6 Behavioral Persona Sub-Agents for autonomous development in the nectR monorepo.
---

# nectR Multi-Agent Orchestration Skill

Use this skill whenever the user asks to run a multi-agent build phase, coordinate domain agents, or execute the phased autonomous development pipeline for **nectR**.

## 1. The 8 Domain Builder Agents & File Ownership Boundaries

To guarantee zero git cross-contamination (Rule #6), each Domain Builder Agent owns distinct paths in the monorepo:

1. **Scientific Research & Game Theory Agent (`sci-research-agent`)**
   - **Owned Paths:** `paper/`, `docs/theory/`
   - **Focus:** Honeybee biomimicry equations, closed-loop monetary velocity ($MV=PQ$), pairwise collusion decay math, Queen payoff mechanism design, and analyzing empirical outputs from `experiments/`.
2. **Business & Institutional Proposal Agent (`business-proposal-agent`)**
   - **Owned Paths:** `business/`, `docs/business/`
   - **Focus:** University Seed Comb sponsorship ROI models, retention economics, FERPA/campus compliance, and cross-campus Swarming playbooks.
3. **Product & Biomimetic Lifecycle Agent (`product-lifecycle-agent`)**
   - **Owned Paths:** `docs/planning/roadmap.md`, `docs/planning/decision_log.md`
   - **Focus:** Phase 1 Institutional Seeding (`Raw Pollen` $\rightarrow$ `Liquid nectR`) to Phase 2 Autonomous Swarming product specifications and acceptance criteria.
4. **System Architecture & Protocol Agent (`system-arch-agent`)**
   - **Owned Paths:** `docs/architecture/system_design.md`, `docs/architecture/smart_contracts.md`
   - **Focus:** Portfolio flagship C4 system architecture, Comb-to-Comb AMM bridge specifications, and protocol threat modeling.
5. **Software, Smart Contracts & Service Layer Agent (`contracts-service-agent`)**
   - **Owned Paths:** `src/nectr/contracts/`, `src/nectr/services/`, `tests/test_contracts.py`, `tests/test_services.py`
   - **Focus:** Implementing the 5 deterministic smart contracts and the Hive Service Layer API.
6. **Hardware, Distributed Compute & PoW Agent (`pow-compute-agent`)**
   - **Owned Paths:** `src/nectr/chain/`, `tests/test_chain.py`
   - **Focus:** Hybrid Proof-of-Useful-Work (`PoUW-PoW`) consensus engine, distributed compute payload verification (Knowledge Flow Matrix + Collusion Decay state roots), and campus node topology.
7. **Design System & Visual Tokenomics Agent (`design-ui-agent`)**
   - **Owned Paths:** `src/nectr/ui/`
   - **Focus:** Biomimetic Hive explorer, live Comb reserve gauges, and interactive knowledge graph visualizations.
8. **UX & Behavioral Feedback Agent (`ux-behavior-agent`)**
   - **Owned Paths:** `src/nectr/personas/`, `experiments/`, `docs/architecture/persona_swarm_spec.md`
   - **Focus:** Running the 6 Behavioral Persona Sub-Agents (`Freshman_Forager`, `Certified_Senior_Worker`, `Finals_Week_Panicker`, `Sybil_Roommate_Ring`, `Drifting_Pollinator`, `Queen_Facilitator`) against the blockchain and feeding behavioral anomalies back to the Scientific Agent.

## 2. How to Launch Coordinated Work

- **For Design Clarification:** Run an interactive `/grill-me` session using `docs/planning/decision_log.md` and record every finalized parameter.
- **For Multi-Agent Parallel Execution:** Use `define_subagent` / `invoke_subagent` (or `swarm` / `run_workflow`) assigning each agent its strict file ownership boundary above.
- **Post-Stage Verification Gate:**
  1. `uv run pytest` (All blockchain, contract, and game-theory invariant tests pass)
  2. `uv run mkdocs build --strict` (All documentation and portfolio links build cleanly)
