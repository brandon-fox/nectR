---
name: persona-simulation
description: Configures, runs, and analyzes the 6 Behavioral Persona Sub-Agents (Freshman Forager, Certified Senior Worker, Finals Week Panicker, Sybil Roommate Ring, Drifting Pollinator, Queen Facilitator) transacting on the private nectR blockchain.
---

# Behavioral Persona Sub-Agent Simulation Skill

Use this skill when designing, calibrating, or executing agent-based behavioral simulations in `src/nectr/personas/` and `experiments/`.

## 1. The 6 Persona Sub-Agent Archetypes

1. `FreshmanForagerPersona`: Starts with restricted `RAW_POLLEN` drawn from the Seed Comb; seeks tutoring in gateway courses from Certified Workers; later tutors peers in secondary skills.
2. `CertifiedSeniorWorkerPersona`: Queen-certified tutor; high tutoring supply; tests graduation sinks, demurrage/hoarding dynamics, and Swarm Queen eligibility.
3. `FinalsWeekPanickerPersona`: Hoards liquidity until Midterm/Finals epochs, then creates sudden 10x demand spikes to stress-test Waggle Dance surge bounties.
4. `SybilRoommateRingPersona`: Adversarial colluders executing reciprocal `A <-> B` tutoring loops to test pairwise collusion decay ($W = \frac{1}{1 + \alpha N_{A \leftrightarrow B}}$) and Worker Policing.
5. `DriftingPollinatorPersona`: Migrates from `HIVE_A` to `HIVE_B` with locked `nectR-HIVE_A`; must complete verified local tutoring in `HIVE_B` to pass the Guard Bee Accepted Status threshold.
6. `QueenFacilitatorPersona`: Non-tutoring administrator (Teacher-Queen or promoted Veteran Bee); certifies workers, resolves disputes, and manages Comb bounties to maximize the Hive Velocity & Diversity Index.

## 2. Closed-Loop Telemetry Metrics to Emit Every Epoch
- **Monetary Velocity ($V$)** and **Liquidity Distribution (Gini Coefficient)**
- **Comb Treasury Ratio** ($\text{Comb Reserve} / \text{Circulating Liquid nectR}$)
- **Collusion Attenuation Efficiency** (Effective Reputation gained by `SybilRoommateRingPersona` vs. Honest Bees)
- **Downstream Lineage Depth** ("Learn-then-Teach" multi-hop chains)
