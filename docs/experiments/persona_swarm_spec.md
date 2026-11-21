# Behavioral Persona Swarm & Agent-Based Computational Economics (ACE) Specification

To validate **nectR**'s mechanism design empirically prior to human-subjects IRB trials, `src/nectr/personas/` and `experiments/` implement a deterministic **Agent-Based Computational Economics (`ACE`)** testbed where **6 Behavioral Persona Sub-Agents** execute real Ed25519-signed transactions against `HiveContractEngine` and `HiveBlockchain`.

---

## 1. The 6 Behavioral Persona Archetypes (`Tier-2 Sub-Agents`)

| Persona Archetype | Biological Analog (*Apis mellifera*) | Behavioral Policy & ML/RL Adaptive Track | Primary Invariants & Equations Stress-Tested |
| :--- | :--- | :--- | :--- |
| **1. `FreshmanForagerPersona`** | Newly eclosed **Cell Cleaner $\rightarrow$ Nurse Bee** consuming brood food (`leoncini_2004`). | Draws initial restricted `RAW_POLLEN` from the school Seed Comb; books gateway STEM sessions (`CALC-101`, `CS-101`, `>= 25 min` per `DEC-011`) with Certified Workers; unlocks **Learn-then-Teach** peer tutoring in secondary skills once mastery lineage crosses threshold. | Restricted `RAW_POLLEN` refinement (`D-05`), early-semester commitment deposits, and cross-disciplinary skill swaps (`leung_2019`). |
| **2. `CertifiedSeniorWorkerPersona`** | **Nurse Bee $\rightarrow$ Middle-Aged Receiver / Swarm Candidate** (`khoury_2011`). | Accredited by a Founding Queen; supplies high tutoring bandwidth; tests reservation-price elasticity during Finals, 3-door Senior graduation sinks (`DEC-004`), and `SWARM_PREP` Honey Engorgement (`DEC-012`). | OLG currency drain mitigation (`40%` Credentials/Swarming, `35%` Perks, `25%` Freshman Bounties) and Khoury Precocious Promotion Circuit Breaker (`D-07`). |
| **3. `FinalsWeekPanickerPersona`** | Seasonal **Forage Dearth / Colony Congestion Shock** (`sweeney_1977`). | Attempts to hoard liquidity during Weeks 1–4 and Weeks 11–13 before generating `3.0x–4.0x` Midterm (Epochs 5–6, 9–10) and `10.0x` Finals (Epochs 14–15) demand spikes. | Lazy demurrage (`~2%/mo` above safety buffer, paused in Finals, `DEC-001`) + `60%` Comb Waggle surge co-pay on `2.2x` peak tutor payouts (`DEC-002`, `EXP-002`). |
| **4. `SybilRoommateRingPersona`** | **Rogue Egg-Laying Worker / Robber Bee Clique** (`ratnieks_1988`). | Executes reciprocal $A \leftrightarrow B$ and $m$-node ring wash-trading loops (plus contextual multi-armed bandit evasion policies) to farm reputation, Waggle subsidies, or Accepted Status. | Pairwise Discoordination ($\alpha = 1.5$, $\le \binom{m}{2}k$ ceiling, `buterin_2019`), EigenTrust anchors (`kamvar_2003`), `COCM` Fiedler-vector dorm-SBT clustering (`EXP-003`), and Oophagy / Escrow-DKG framing bounties. |
| **5. `DriftingPollinatorPersona`** | **Nectar-Laden Drifting Forager / Nest-Site Scout** (`downs_ratnieks_2000`, `seeley_visscher_2004`). | Migrates from `HIVE_ALPHA` to `HIVE_BETA` with locked `nectR-HIVE_ALPHA`; tutors $K = 3$ distinct local peers in `HIVE_BETA` to earn **Accepted Status** and triggers NATS JetStream Comb-to-Comb bridging (`ADR-0005`, `ADR-0014`). | Reserve-coupled Guard Bee acceptance threshold, clamped `[0.5x, 2.0x]` Effective Backing Ratio FX (`D-04`), monthly export quotas, and 15-Scout Swarm Quorum Sensing (`D-08`). |
| **6. `QueenFacilitatorPersona`** | **Queen & QMP Pheromonal Steward** (`tirole_1986`, `kofman_lawarree_1993`). | Certifies Workers, resolves disputed escrows (`100%` fee to Comb), tunes Waggle/Tremble parameters, and tests Honest vs. Nepotistic receiver-only praise arms under $p = 0.15$ Beekeeper meta-audits. | Queen Separation of Powers (`D-02`), Fee-to-Comb conservation (`D-03`), phase-split Royal Jelly payoff $R_Q(e)$, and `EXP-001` nepotism resistance. |

---

## 2. 15-Week Semester Calibration & Five Core Telemetry Series

Every seeded `HiveMesaModel` simulation (`ADR-0010`, `DEC-009`) runs over 15-epoch semesters (`Weeks 1–15`) across multiple academic cohorts and collects five canonical time series via `mesa.DataCollector` and `GraphTelemetryPort` (`networkx` / `NetworKit` / `rustworkx`):

1. **Monetary Velocity ($V_e$) & Semester Fill Rate:** Collusion-discounted turnover $V_e = \frac{1}{M_e} \sum_{\text{tx} \in e} \text{amount}_{\text{tx}} \cdot W(u,v,s)$ and fraction of student tutoring requests cleared during Low Season (`0.3x`), Midterms (`3.0x–4.0x`), and Finals (`10.0x`).
2. **Wealth & Effectiveness Gini Coefficient ($\text{Gini}_e \in [0, 1]$):** Inequality index across non-Queen accounts (alert threshold: $\text{Gini}_e < 0.60$).
3. **Comb Treasury & Collateralization Ratio ($CR_e$):** Ratio of `comb_reserve` to circulating `LIQUID_NECTR` and outstanding `RAW_POLLEN` liabilities, plus Sink-to-Source Ratio ($\text{SSR}_e \to 1.00$).
4. **Collusion Attenuation Efficiency ($\text{CAE}_e$):** Ratio of cumulative effective reputation earned by honest `CertifiedSeniorWorkerPersona` tutors versus `SybilRoommateRingPersona` wash-traders per unit of token volume.
5. **Downstream Lineage Depth & QMP Coverage:** Mean multi-hop chain length of **Learn-then-Teach** cascades (`Freshman_1` $\rightarrow$ `Freshman_2` $\rightarrow$ `Freshman_3`) and peripheral graph-hop QMP health $\mathbf{Q}(v)$.

---

## 3. Experimental Hypothesis Matrix (`EXP-001` through `EXP-005`)

| Experiment ID | Hypothesis & Simulation Arms | Target Metric & Pass Criterion | Owning Agents |
| :--- | :--- | :--- | :--- |
| **`EXP-001`** | **Queen Receiver-Only Praise vs. Nepotism Stress-Test:** Compare Honest Queen praise against Biased/Nepotistic Queen praise (`20%` favored clique) under private ratings and $p = 0.15$ Beekeeper audits. | Biased Queen loses expected utility ($E[U_{\text{bribe}}] < E[U_{\text{honest}}]$) and favored low-ability tutors fail Spence threshold $s^* = 6$. | `ux-behavior-agent`, `sci-research-agent` |
| **`EXP-002`** | **15-Week Finals Crunch & Waggle `60%` Co-Pay Fill Rate:** Compare Capitol Hill fixed-price scrip ($d = 0$, no surge co-pay) against `nectR` (`2%/mo` Weeks 1–13 demurrage + `60%` Comb Waggle co-pay on `2.2x` peak tutor payouts). | Full-semester tutoring fill rate increases from `~38.0%` (fixed scrip) to **`>= 65.0%`** (`~67.4%` calibrated benchmark) while $CR \ge 1.0$. | `ux-behavior-agent`, `product-lifecycle-agent` |
| **`EXP-003`** | **Pairwise Discoordination + `COCM` Dorm-Cluster Sybil Bound:** Pit adaptive bandit `SybilRoommateRingPersona` cliques ($m \in \{2, 5, 10\}$ sharing dorm SBTs) against Pairwise Decay ($\alpha = 1.5$) + `COCM` Fiedler-vector clustering. | Total Sybil ring reputation extraction saturates strictly below $\binom{m}{2}k$ (`>95%` wash volume neutralized at $W = 5,000$). | `sci-research-agent`, `contracts-service-agent` |
| **`EXP-004`** | **Khoury Mortality Bifurcation & Ethyl Oleate Circuit Breaker:** Inject a `50%` external Scout attrition shock ($\mu_{\text{churn}} > \mu_{\text{crit}}$) with vs. without the Precocious Promotion Circuit Breaker (`D-07`). | Circuit breaker prevents Nurse-Tutor depletion and preserves **`>= 85%`** gateway freshman tutoring completion (vs. colony collapse when unguarded). | `sci-research-agent`, `ux-behavior-agent` |
| **`EXP-005`** | **Asymmetric Campus NAT Partition & NATS JetStream Recovery:** Inject `30-minute` WAN partitions and `15%` packet loss via **Kurtosis + Pumba/Toxiproxy** across outbound NATS Leaf Node (`port 7422`) links between `HIVE_ALPHA` and `HIVE_BETA`. | `100%` of `AcceptedStatusGranted` and bridge settlements converge deterministically post-healing with zero double-minting or supply conservation drift. | `system-arch-agent`, `contracts-service-agent` |
