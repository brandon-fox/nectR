# Honeybee (*Apis mellifera*) Biomimetic Protocol Mapping & Mathematical Formalism

The **nectR** decentralized peer-to-peer (P2P) tutoring marketplace translates six superorganism mechanisms of the Western honeybee (*Apis mellifera*)—trophallactic nectar refinement, waggle/tremble surge signaling, Queen Mandibular Pheromone (`QMP`) non-tutoring governance, polyandrous worker policing, guard-bee adaptive acceptance, and ethyl oleate-regulated temporal polyethism with quorum-sensed reproductive swarming—into formal differential equations and deterministic smart-contract invariants in `src/nectr/contracts/` and `src/nectr/services/`. Every parameter and mechanism aligns with the [Domain Glossary](../glossary.md), the [Fast Decision Log](../planning/decision_log.md) (`DEC-001` through `DEC-015`, `EXP-001`, `EXP-004`), and verified primary literature in `paper/references.yaml` (tracked in [Provenance & Lineage](provenance_lineage.md)).

## 1. Problem Statement & Scope Boundaries

### 1.1 Dual Market Failures in Closed Campus Barter (`sweeney_1977`, `mattsson_2023`, `filippas_2020`, `iosifidis_2018`)

Closed student time-banking systems collapse from two structural failures:

1. **Seasonal Illiquidity & Overlapping-Generations (`OLG`) Drain (`sweeney_1977`, `mattsson_2023`):** Like the Capitol Hill Babysitting Co-op (`sweeney_1977`), fixed-supply scrip freezes when students hoard tokens ahead of predictable exam surges (`0.3x` demand in Weeks 1–4 jumping to `3.0x–4.0x` in Midterms and `10.0x` in Finals), compounded by spring deflation when Seniors graduate holding unspent credits (`ADR-0006`).
2. **Oracle & Sybil Rating Inflation (`filippas_2020`, `iosifidis_2018`):** Because P2P tutoring creates unobservable off-chain quality, public 5-star reviews inflate toward ceiling values (`filippas_2020`) while zero-fee reciprocal `A <-> B` loops allow roommate Sybil rings to mint fake reputation unless filtered by cyclic-motif and pairwise decay rules (`iosifidis_2018`, `buterin_2019`).

### 1.2 Evidentiary Caveats & Implementation Phase Boundaries

Four explicit scope boundaries govern this specification:

1. **Seeley & Tovey (`seeley_tovey_1994`) Interior Constants:** While the negative linear relationship $1 / T_{\text{wait}} = a - b \cdot \lambda_{\text{arrive}}$ is established in `seeley_tovey_1994`, exact physical definitions of the interior scaling constants $a$ and $b$ are not enumerated in the retrieved primary summary and are treated as empirically calibrated Hive telemetry parameters.
2. **Network-Relayed `QMP` + Brood Synergy Revision:** Rather than modeling `QMP` as a passive uniform diffusive cloud ("QMP dilution"), **nectR** models `QMP` relay across worker social-contact ("retinue") graph hops reinforced by an active Learner ("open brood") synergy factor $\Phi_{\text{brood}}$.
3. **Explicit Exclusion of Royalactin & Insulin/TOR Signaling:** Molecular caste commitment in **nectR** is modeled exclusively on **DNMT3** inhibition (DNA hypomethylation), **10HDA/HDAC3** inhibition (open chromatin `H3K27ac`), and **UHRF1** epigenetic integration. Pathways involving **royalactin** and **insulin/TOR signaling** are unsupported in the retrieved molecular sources and are explicitly **excluded** from **nectR**'s state-unlocking specification.
4. **Open Simulation & Wave 2B Boundaries:** Per **`EXP-001`** ([Fast Decision Log](../planning/decision_log.md)), Queen receiver-only praise weights remain `open-simulation` (unlocked) until tested across Honest vs. Biased nepotism arms. In `src/nectr/personas/simulator.py`, the compact 3-epoch smoke testbench sets `accepted_status_peer_threshold = 2` versus the locked `DEC-003` production default `K = 3` in `HiveContractEngine`. Controllers not yet implemented in `src/nectr/contracts/engine.py` are tagged **`[Planned Wave 2B]`** per the [Project Roadmap](../planning/roadmap.md).

## 2. Master Biological-to-Protocol Translation Matrix

| Biological Subsystem | Entomological Mechanism & Equations | nectR Protocol & Smart Contract Translation |
| :--- | :--- | :--- |
| **Trophallaxis & Nectar Refinement** (`seeley_tovey_1994`) | `57%–81%` pre-concentration; `25%–60%` in-nest tax; wait-time cue $1/T_{\text{wait}} = a - b \lambda_{\text{arrive}}$; density-dependent storage vs. immediate consumption | Off-chain signed attendance/rubric pre-aggregation; `HiveContractEngine.create_service_barter_escrow()` & `settle_co_signed_session()` (`RAW_POLLEN` $\to$ `LIQUID_NECTR` at `0%` P2P fee; fees & demurrage $\to$ `ROYAL_COMB_RESERVE`, `ADR-0002`, `ADR-0006`) |
| **Waggle, Tremble & Stop-Signals** (`camazine_sneyd_1991`, `DEC-002`, `DEC-013`) | Recruitment ODEs ($dF_k/dt, dD_k/dt$); Profitability Index $p_k$; `20s–80s` Tremble linear ramp; `30s–180s` abandonment; cross-inhibitory $\sigma_{j \to k}$ | Midterm/Finals Waggle surge co-pay (`~60%` of `~2.2x` peak payout, learner pays `~1.0x–1.3x`); congestion fee reallocation & Stop-Signal queue throttling (`WaggleTrembleController` `[Planned Wave 2B]`) |
| **Queen & `QMP` Governance** (`ADR-0003`, `ADR-0004`, `kofman_lawarree_1993`) | `1 Qeq/day` beacon; network-relayed $\mathbf{Q}(v) \cdot \Phi_{\text{brood}}$; Graceful Supersedure (`1–3` slots) vs. `24h` Emergency Rearing (`up to 27`); `DNMT3`/`10HDA-HDAC3`/`UHRF1` epigenetics | `BeeRole.QUEEN` tutoring ban (`engine.py`); `100%` fees to `comb_reserve`; Phase 1 non-coin impact / Phase 2 bond-backed `Royal Jelly` $R_Q(e)$ (`HiveServiceLayer.mine_epoch_block()`); `QMPHealthAndSupersedureFSM` `[Planned Wave 2B]` |
| **Polyandrous Worker Policing** (`ratnieks_1988`, `wenseleers_ratnieks_2006`, `buterin_2019`, `DEC-003`) | Polyandry ($n_m > 2 \implies \Delta r < 0$); `99.88%` selective oophagy of rogue worker eggs; cyclic diversity | `HiveContractEngine` pairwise decay $\alpha = 1.5$, lineage bonus $\gamma = 0.5$, `>= 0.6` attestation gate, `prior_pair_txs == 0` uniqueness, `+0.25 * W` upstream credit; Pairwise Discoordination cap & Escrow-DKG whistleblower bounties |
| **Guard Bee Acceptance** (`downs_ratnieks_2000`, `ADR-0005`, `DEC-003`, `DEC-004`) | `10–15%` guard rotation (`9:1` scaling); swaying-flight interception; Reeve threshold $\tau_{\text{accept}}(t)$; laden-drifter acceptance | Layer-0 burst drop; `Accepted Status` after `K = 3` distinct host-Hive peers (`>= 0.6` attestation); `bridge_nectr_to_target_hive()` `[0.5x, 2.0x]` epoch FX + `5%` source Comb toll |
| **Temporal Polyethism & Swarming** (`leoncini_2004`, `khoury_2011`, `bonabeau_1996`, `seeley_visscher_2004`, `reina_2017`, `ADR-0006`, `DEC-001`, `DEC-004`, `DEC-012`, `DEC-013`) | `EO` maturation damper; Khoury $\mu_{\text{crit}}$ bifurcation; Hill task thresholds; `>= 15` (`30%`) scout quorum (`seeley_visscher_2004`, `reina_2017`); `1h` piping; `6.25–8.0:1` Honey-to-Wax burn | Campus Hive Member Lifecycle; `DEC-001` `~2%/mo` lazy demurrage (`DemurrageAccumulator`); `TemporalPolyethismGovernor` (Precocious Promotion Circuit Breaker) & `SwarmBivouacEscrow` `[Planned Wave 2B]`; Senior `40%/35%/25%` exit sinks + dormant sweep |

## 3. Formal Mathematical Subsystems

### 3.1 Trophallaxis, Nectar Dehydration & Comb Storage (`seeley_tovey_1994`, `ADR-0002`, `ADR-0006`)

**Biological Mechanism:** Honeybee foragers convert raw floral nectar (`20%–60%` sugar) into capped honey (`>80%` sugar). Because in-nest ripening consumes `25%–60%` of nectar sugars, foragers perform pre-concentration via tongue-lashing at the floral patch and in flight, removing `57%–81%` of water before reaching the nest. Returning foragers pass nectar via mouth-to-mouth **trophallaxis** to middle-aged receiver bees (`MAB`s), which allocate dilute forage (`~30%` sugar) to immediate colony consumption while ripening concentrated nectar into long-term **Comb** buffers. Every forager senses colony-wide receiver congestion directly through her mean unloading wait time $T_{\text{wait}}$ (`seeley_tovey_1994`):

$$\frac{1}{T_{\text{wait}}} = a - b \cdot \lambda_{\text{arrive}}$$

where $\lambda_{\text{arrive}}$ is the arrival rate of incoming nectar foragers (and, as noted in Section 1.2, exact physical definitions of interior constants $a$ and $b$ remain unenumerated in the available primary summary).

**Protocol Translation (`HiveContractEngine`):**

1. **Off-Chain Pre-Concentration:** Client applications bundle signed attendance intervals, quiz score deltas, and `tutor_comprehension_hash` commitments off-chain before calling `create_service_barter_escrow()` and `settle_co_signed_session()`, minimizing on-chain state bloat.
2. **Density-Dependent Consumption vs. Comb Storage:** Let $c_i$ denote a session's value-density score against threshold $c_{\text{thresh}}$. Routine P2P `LIQUID_NECTR` exchanges ($c_i < c_{\text{thresh}}$) settle directly to `tutor.liquid_nectr_balance` at **`0%` protocol fee** (`fee_charged = 0.0` in `engine.py`), mirroring immediate consumption of dilute nectar. Restricted institutional `RAW_POLLEN` vouchers can **only** be spent with a `BeeRole.CERTIFIED_WORKER_BEE` accredited in `session.subject_id` (`subject_id in tutor.certified_subjects`), refining `RAW_POLLEN` into `LIQUID_NECTR` upon verified settlement while `100%` of governance, dispute, and bridge fees flow into `ROYAL_COMB_RESERVE` (`comb_reserve`) to buffer seasonal academic shocks (`assert_supply_conservation()`).

### 3.2 Waggle Profitability, Tremble Latency Ramp & Stop-Signals (`camazine_sneyd_1991`, `DEC-002`, `DEC-013`)

**Biological Mechanism:** When unloading wait time $T_{\text{wait}}$ is low, foragers recruit followers to high-yield patches via the **waggle dance** (`camazine_sneyd_1991`). Across competing nectar sources $k$, Camazine and Sneyd (1991) model active foragers $F_k$, unloading bees $U_k$, dancers $D_k$, and idle/unmatched followers $F_0$ via coupled ordinary differential equations (`ODE`s):

$$\frac{dF_k}{dt} = p_k r_k F_0 - \frac{1}{\tau_{f,k}} F_k, \qquad \frac{dD_k}{dt} = \frac{q_k}{\tau_{u,k}} U_k - \frac{1}{\tau_{d,k}} D_k - \sum_{j \neq k} \sigma_{j \to k} D_j D_k$$

where $p_k$ is recruitment share, $r_k$ is follower encounter rate, $q_k$ is conditional dancing probability upon unloading, $\tau_{f,k}, \tau_{u,k}, \tau_{d,k}$ are mean foraging, unloading, and dancing durations, and $\sigma_{j \to k}$ is vibrational **Stop-Signal** cross-inhibition delivered onto dancers advertising congested or hazardous sources. When unloading delay exceeds ~1 minute, foragers shift to the **tremble dance**—ramping linearly across `20s–80s` to recruit additional receivers—while source abandonment ramps across `30s–180s`.

**Protocol Translation (`DEC-002`, `DEC-013`, `WaggleTrembleController` `[Planned Wave 2B]`):**

- **1. Waggle Profitability Index & `DEC-002` Surge Co-Pay:** Subject queues rank bounties by profitability $p_k$ above hive threshold $\theta_{\text{hive}}(t)$. During Midterm (`3.0x–4.0x`) and Finals (`10.0x`) demand peaks (`DEC-002`), the Comb co-pays `~60%` of `~2.2x` peak tutor payouts $P_{\text{tutor}}^{\text{peak}} = m_t P_{\text{base}}$ ($m_t \in [1.0, 2.2]$) so learners pay `~1.0x–1.3x` $P_{\text{base}}$ (see [Tokenomics & Game Theory](tokenomics_game_theory.md)):

$$p_k = \frac{\mathrm{NetReward}(k)}{\mathrm{EffortTime}(k)} \cdot \mathbb{I}\!\left(p_k > \theta_{\text{hive}}(t)\right), \qquad P_{\text{learner}}(t) = \text{clip}\!\left((1 - \kappa_{\text{copay}})\, m_t P_{\text{base}}, \; 1.0\, P_{\text{base}}, \; 1.3\, P_{\text{base}}\right), \qquad \kappa_{\text{copay}} \approx 0.60$$

- **2. Tremble Latency Ramp & Stop-Signal Throttling (`DEC-013`):** As validation queue wait time $T_{\text{wait}}$ climbs across $\tau_{\text{low}} = 20\text{s}$ toward $\tau_{\text{high}} = 80\text{s}$, the Tremble signal ramps linearly, reallocating validator Comb rebates to recruit mid-tier members while emitting cross-inhibitory Stop-Signals $\sigma_{j \to k}$ to dampen Waggle multipliers on saturated or disputed cohorts (with abandonment ramping across `30s–180s`):

$$P_{\text{tremble}}(T_{\text{wait}}) = \min\!\left(1, \; \max\!\left(0, \; \frac{T_{\text{wait}} - \tau_{\text{low}}}{\tau_{\text{high}} - \tau_{\text{low}}}\right)\right), \qquad \tau_{\text{low}} = 20\text{s}, \quad \tau_{\text{high}} = 80\text{s}$$

### 3.3 Queen Separation of Powers, `QMP` Network Relay & Epigenetic Caste Unlocking (`ADR-0003`, `ADR-0004`, `kofman_lawarree_1993`, `EXP-001`)

**Biological Mechanism:** A honeybee queen does not forage; she acts as reproductive anchor and emits roughly `1 Qeq/day` of **Queen Mandibular Pheromone (`QMP`)**, relayed through worker social-contact networks and stabilized by pheromones from open brood. When a queen fails, workers execute either **Graceful Supersedure** (`1–3` centrally provisioned queen cells with brief mother–daughter coexistence) or **Emergency Queen Rearing** (begun within `24 hours` across `up to 27` candidate cells, prioritizing `<24h` young larvae over `>3-day` entrenched larvae). Epigenetic differentiation into a Queen proceeds via **DNMT3** inhibition (DNA hypomethylation), **10HDA/HDAC3** inhibition (histone `H3K27ac` acetylation), and **UHRF1** chromatin integration—explicitly **excluding** royalactin and insulin/TOR pathways per Section 1.2.

**Protocol Translation (`ADR-0003`, `ADR-0004`, `HiveContractEngine`, `HiveServiceLayer`):**

- **1. Cryptographic Non-Tutoring Invariant (`engine.py`):** Accounts holding `BeeRole.QUEEN` are strictly barred from acting as `tutor_id` in `create_service_barter_escrow()`, as `worker_id` in `certify_worker_bee()`, as `learner_id` in `allocate_raw_pollen_to_learner()`, and from `bridge_nectr_to_target_hive()`. `100%` of certification and dispute arbitration fees (`service_fee_rate = 0.10` default) flow directly into `comb_reserve`.
- **2. Social-Network Relayed `QMP` & Epigenetic Bitmask (`QMPHealthAndSupersedureFSM` `[Planned Wave 2B]`):** Governance health propagates across retinue graph hop distance $d(Q, v)$ with decay $\lambda$ and open-brood onboarding synergy $\Phi_{\text{brood}}$:

$$\mathbf{Q}(v) = \mathbf{Q}(0)\,e^{-\lambda d(Q, v)} \cdot \Phi_{\text{brood}}$$

Graceful Supersedure opens `1–3` curated slots with 1-epoch coexistence when $\mathbf{Q}(v) < \theta_{\text{soft}}$ while Comb invariants hold; Emergency Succession triggers on sudden liveness failure ($\mathbf{Q} = 0$) as a `24-hour` election (`up to 27` candidates) weighting recently certified `<24h` agile contributors over entrenched `>3-day` positions, clearing `DNMT3`/`10HDA-HDAC3`/`UHRF1` permission bits without royalactin or insulin/TOR assumptions.

- **3. Phase-Split Royal Jelly, Auditing & Code Reconciliation (`kofman_lawarree_1993`, `EXP-001`):** Phase 1 Teacher-Queens earn non-monetary impact credits; Phase 2 Veteran Student-Queens post bond $B_Q$ and earn `LIQUID_NECTR` dividends under `BEEKEEPER` / Meta-Court audit probability $p = 0.15$ and bond slash $\lambda B_Q$ (`kofman_lawarree_1993`, full Nash payoff matrix in [Tokenomics & Game Theory](tokenomics_game_theory.md)):

$$R_Q(e) = \beta \cdot \Delta S_{\text{comb}}^+(e) \cdot \mathcal{V}_{\text{graph}}(e) \cdot (1 - \text{Gini}(e))$$

*Code Reconciliation:* Currently, `HiveServiceLayer.mine_epoch_block(queen_dividend_beta=0.05)` (`src/nectr/services/hive_service.py`) computes the Phase 1 non-monetary health score `round(queen_dividend_beta * proof.collusion_discounted_velocity * (1.0 - proof.gini_coefficient), 4)`, omitting $\Delta S_{\text{comb}}^+(e)$, $\gamma_Q \Delta M$, and $\delta_Q(D - D^*)$ until Phase 2 bond-staking contracts are deployed. Per **`EXP-001`**, Queen receiver-only praise weights remain unlocked until simulated across Honest vs. Biased nepotism arms.

### 3.4 Polyandrous Worker Policing & Guard Bee Acceptance (`ratnieks_1988`, `wenseleers_ratnieks_2006`, `downs_ratnieks_2000`, `DEC-003`, `DEC-004`, `ADR-0005`)

**Biological Mechanism:** Because honeybee queens mate with $n_m \in [10, 20]$ unrelated drones (**polyandry**), workers are mostly half-sisters (`ratnieks_1988`, `wenseleers_ratnieks_2006`). A worker's relatedness to the queen's sons is $r_Q = \frac{1}{4}$, whereas her mean relatedness to fellow workers' sons is $r_W(n_m)$:

$$r_Q = \frac{1}{4}, \qquad r_W(n_m) = \frac{1}{n_m}\!\left(\frac{3}{8}\right) + \left(1 - \frac{1}{n_m}\right)\!\left(\frac{1}{8}\right) = \frac{1}{8} + \frac{1}{4n_m}, \qquad \Delta r = r_W(n_m) - r_Q = \frac{1}{4n_m} - \frac{1}{8}$$

Whenever effective mating frequency $n_m > 2$ (yielding $r_W \in [0.1375, 0.15] < 0.25$ for $n_m \in [10, 20]$), $\Delta r < 0$, making mutual **worker policing** via selective **oophagy** (`99.88%` destruction of un-marked worker-laid eggs) evolutionarily dominant. At hive entrances, `10%–15%` of mid-tenure workers serve as **guard bees** scaling `9:1` with intruder pressure (`downs_ratnieks_2000`), intercepting swaying-flight robbers immediately and matching cuticular hydrocarbons (`CHC`s) against an adaptive **Reeve acceptance threshold** $\tau_{\text{accept}}(t)$—tightening during nectar dearth and relaxing during abundant flow so **nectar-laden drifters** earn **Accepted Status** via submissive trophallaxis.

**Protocol Translation (`HiveContractEngine`, `DEC-003`, `DEC-004`, `ADR-0005`):**

- **1. Oophagy Fraud Proofs & Pairwise Anti-Collusion Decay (`buterin_2019`, `iosifidis_2018`, `spence_1973`, `leung_2019`):** Unverified claims lacking co-signed provenance face permissionless fraud-proof rejection, while `HiveContractEngine.settle_co_signed_session()` enforces hyperbolic decay with $\alpha = 1.5$ (`collusion_alpha`) and $\gamma = 0.5$ (`lineage_gamma`):

$$W(u, v, s, n) = \frac{a}{1 + \alpha n} \cdot \left(1 + \gamma \cdot \mathbb{I}\!\left[\mathcal{U}(u, s) \neq \emptyset\right]\right)$$

Only when `prior_pair_txs == 0` ($n = 0$) and `learner_attestation_score >= 0.6` (`a >= 0.6`) does `engine.py` record `subject_lineage`, add $v$ to `u.distinct_peers_tutored_in_hive`, and award `+0.25 * W` to each upstream tutor in $\mathcal{U}(u, s)$ (implementing `spence_1973` single-crossing downstream mastery and `leung_2019` Learn-then-Teach gains while saturating `A <-> B` wash rings under `buterin_2019` and `iosifidis_2018`).

- **2. Adaptive Guard Threshold & `K = 3` Laden-Drifter Admission (`downs_ratnieks_2000`, `ADR-0005`):** Guards drop Layer-0 swaying-flight nonce/wash bursts and evaluate credential distance $d(u, H_B)$ minus submissive resource tribute $\Delta d_{\text{tribute}}$ against the Reeve reserve-coupled threshold $\tau_{\text{accept}}(t)$:

$$\tau_{\text{accept}}(t) = \tau_0 + \kappa \ln\!\left(\frac{R_{\text{comb}}(t)}{R^*}\right) - \eta I(t), \qquad d(u, H_B) - \Delta d_{\text{tribute}} \le \tau_{\text{accept}}(t)$$

where $R_{\text{comb}}(t)/R^*$ is normalized Comb reserve health and $I(t)$ is intrusion intensity. On-chain, a visiting `POLLINATOR_VISITOR` earns `Accepted Status` (`accepted_in_hives.add(H_B)`) after tutoring **`K = 3`** (`accepted_status_peer_threshold = 3`, `DEC-003`; overridden to `2` in `simulator.py` smoke tests) distinct host-Hive peers with `a >= 0.6`, unlocking `bridge_nectr_to_target_hive()` at epoch FX clamped to `[0.5x, 2.0x]` (`DEC-004`) with a `5%` source Comb toll (`F_bridge = 0.05 * A_bridge`).

### 3.5 Temporal Polyethism, Ethyl Oleate Circuit Breaker & Demurrage (`leoncini_2004`, `khoury_2011`, `bonabeau_1996`, `DEC-001`, `DEC-013`, `EXP-004`)

**Biological Mechanism:** Adult honeybees progress dynamically across concentric behavioral castes—**Cell Cleaners** (Days 1–4) $\to$ **Nurse Bees** (Days 4–12, high vitellogenin `Vg`, low juvenile hormone `JH`) $\to$ **Middle-Aged Bees (`MAB`s)** (Days 12–21, comb building & guarding) $\to$ **Foragers/Scouts** (Days 21+, high `JH`, emitting the primer pheromone **ethyl oleate (`EO`)**) (`leoncini_2004`). Khoury, Myerscough, and Barron (`khoury_2011`) model Hive Bees $H$ and Foragers $F$ under queen egg-laying rate $L_{\text{onboard}}$, eclosion $E(H, F) = L_{\text{onboard}} \frac{H + F}{w + H + F}$, baseline maturation $\alpha_{\text{mat}}$, `EO` social inhibition $\sigma_{\text{EO}}$, and external forager mortality $\mu_{\text{churn}}$:

$$\frac{dH}{dt} = E(H, F) - H \cdot R(H, F), \qquad \frac{dF}{dt} = H \cdot R(H, F) - \mu_{\text{churn}} F, \qquad R(H, F) = \alpha_{\text{mat}} - \sigma_{\text{EO}} \left(\frac{F}{H + F}\right)$$

Above a critical churn threshold $\mu_{\text{crit}}$, `EO` depletion causes runaway precocious foraging, stripping nurses from brood care and collapsing the colony (`khoury_2011`). Individual task specialization within castes follows the Bonabeau-Theraulaz (`bonabeau_1996`) **Reinforced Response Threshold** Hill model: inactive Bee $i$ responds to task stimulus $s$ with threshold $\theta_i$, updated by reinforcement learning $\xi$ and forgetting $\varphi$ across active indicator $I_i(t) \in \{0, 1\}$:

$$P(s, \theta_i) = \frac{s^2}{s^2 + \theta_i^2}, \qquad \theta_i(t + \Delta t) = \theta_i(t) - \xi \cdot I_i(t) \cdot \Delta t + \varphi \cdot \big(1 - I_i(t)\big) \cdot \Delta t$$

**Protocol Translation (`Campus Hive Member Lifecycle`, `DEC-001`, `DEC-013`, `EXP-004`, `[Planned Wave 2B]`):**

| Biological Caste | nectR Campus Role | Core Activities & Economic Analog |
| :--- | :--- | :--- |
| **Cell Cleaner** (Days 1–4) | `LEARNER_BEE` | Onboards with `RAW_POLLEN` vouchers; consumes tutoring, cleans study notes, builds mastery |
| **Nurse Bee** (Days 4–12) | `CERTIFIED_WORKER_BEE` (`Nurse-Tutor`) | Refines `RAW_POLLEN` $\to$ `LIQUID_NECTR` in certified subjects; protected from external market churn |
| **Middle-Aged Bee (`MAB`)** (Days 12–21) | Comb Validator & Guard Node | Curates structured Comb bounties, validates proofs, rotates onto Layer-0 Guard firewall (`10–15%`) |
| **Forager / Scout** (Days 21+) | `POLLINATOR_VISITOR` / Scout | Bridges cross-Hive liquidity (`Accepted Status` `K = 3`), scouts daughter Hives, emits `EO` pacing signal |
| **Queen** | `QUEEN` (`Hive Steward`) | Non-tutoring credential root (`BeeRole.QUEEN`); emits `QMP` telemetry and earns phase-split Royal Jelly |

When external Scout churn approaches $\mu_{\text{crit}}$, **`TemporalPolyethismGovernor` `[Planned Wave 2B]`** activates a **Precocious Promotion Circuit Breaker** (`D-07`, `DEC-013`, `EXP-004`), clamping `Nurse-Tutor` outbound maturation ($R(H, F) \ge 0$ bounded) and redirecting Comb reserves to internal learner retention bounties. Simultaneously, **`DemurrageAccumulator` `[Planned Wave 2B]`** enforces `DEC-001` lazy demurrage (`~2%/month` on `LIQUID_NECTR` above protected safety buffer $B_{\text{safe}}$ during Weeks 1–13, paused in Weeks 14–15, `RAW_POLLEN` and `ROYAL_COMB_RESERVE` exempt) so idle balances circulate without taxing active `Nurse-Tutors`.

### 3.6 Reproductive Swarming, Quorum Sensing & Senior Graduation Sinks (`seeley_visscher_2004`, `reina_2017`, `ADR-0006`, `DEC-004`, `DEC-012`)

**Biological Mechanism:** Mature colonies swarm when three composite triggers align: `~90%` comb carrying-capacity congestion, `QMP` network attenuation at colony margins, and nurse-to-brood demographic surplus. Workers rear `6–12` cancellable swarm queen cells; departing workers engorge `30–40 mg` honey (`50%–67%` of the workforce departs with the veteran queen, leaving `33%–50%` and `~5/6` of *Varroa* mites in the parent nest), and build new wax comb at a **`6.25–8.0:1` Honey-to-Wax** metabolic burn ratio. Hanging in a temporary bivouac (`95%` quiescent, `3%–5%` scouts), scouts evaluate candidate daughter sites via cross-inhibitory stop-signal competition (`reina_2017`):

$$\frac{dx_i}{dt} = q_i x_u - \alpha_i x_i + \rho_i x_i x_u - \sum_{j \neq i} \sigma_{\text{contra}} x_i x_j$$

where $x_i$ is the scout fraction committed to candidate site $i$, $x_u$ is uncommitted scouts, $q_i$ is discovery rate, $\alpha_i$ is spontaneous abandonment, $\rho_i$ is waggle recruitment, and $\sigma_{\text{contra}}$ is contra stop-signal cross-inhibition from rival scouts (noting that for $N \ge 3$ equal options, symmetric cross-inhibition requires an explicit tie-breaker per `reina_2017`). Following Seeley and Visscher (`seeley_visscher_2004`), deployment is governed by **Quorum Sensing** rather than full-population voting: once quorum reaches $Q_{\text{quorum}} \ge 15$ independent scouts (`~30%` of the active scout cohort), scouts trigger **worker piping** (`~1 hour` before liftoff) to launch the daughter colony.

**Protocol Translation (`ADR-0006`, `DEC-004`, `DEC-012`, `D-08`, `SwarmBivouacEscrow` `[Planned Wave 2B]`):**

1. **Autonomous Daughter-Hive Forking (`DEC-012`, `D-08`):** When a Hive enters `SWARM_PREP` (`>= 90%` Comb utilization, outer $\mathbf{Q}(v) < \theta_{\text{swarm}}$, and Certified Tutor surplus), `6–12` cancellable Swarm Queen slots open. Committed participants (`50%–67%`) lock `30–40` credit Honey Engorgement stakes inside `SwarmBivouacEscrow`. Once $Q_{\text{quorum}} \ge 15$ independent Scouts (`30%` quorum per `seeley_visscher_2004`) concurrently verify a target campus, a `1-hour` Worker Piping Timelock fires, burning the `6.25–8.0:1` Honey-to-Wax infrastructure seed ($C_{\text{burn}} \in [6.25, 8.0] \cdot W_{\text{daughter}}$) while isolating legacy parent disputes ("Varroa load") inside the parent ledger (`D-08`).
2. **Senior `40%/35%/25%` Exit Sinks & Dormant Alumni Sweep (`DEC-004`, `ADR-0006`):** To close the spring OLG currency drain cleanly, graduating Senior balances $B_{\text{exit}}(u)$ route across `40%` Credentials/Swarming stakes (funding Daughter-Hive Queen launches), `35%` low-marginal-cost Campus Perks (retired from circulation), and `25%` Pay-It-Forward Freshman Bounties—paired with dormant alumni Comb sweeps $B_{\text{dormant}}$ back into $S_{\text{comb}}$.

## 4. Empirical ACE Grounding & Useful Compute Audit Log Verification (`src/nectr/personas/simulator.py`)

Agent-Based Computational Economics (`ACE`) validation in `src/nectr/personas/simulator.py` (`nectr_sim_baseline_2026`, scheduled for full `mesa` Monte Carlo sweeps under `ADR-0010` / `DEC-009` in Milestone 3; `experiments/` currently contains `experiments/README.md`) executes all 6 Behavioral Persona Sub-Agents against `HiveServiceLayer` and the signed audit log (`ADR-0019`, superseding `ADR-0007`, `src/nectr/chain/ledger.py`, `UsefulComputeProof`). Verified baseline telemetry confirms:

- `hive_a_blocks_mined = 5` and `hive_a_chain_valid = True` (signed audit log Merkle + Knowledge Graph commitment integrity);
- `honest_worker_effectiveness = 3.2062` vs. `sybil_colluder_effectiveness = 1.3232` (`collusion_attenuation_ratio = 2.4231x` across 6 `A <-> B` wash loops);
- `pollinator_accepted_in_hive_b = True` (using smoke override `K = 2` vs. production `K = 3`), `pollinator_bridged_nectr = 6.716797` at clamped `exchange_rate = 0.707` and `5%` `source_comb_toll = 0.5` (`hive_a_comb_reserve = 905.5`);
- `queen_royal_jelly_score = 2.009` via `HiveServiceLayer.mine_epoch_block()`.

## 5. Code Symbol Mapping & `paper/lineage.yaml` Provenance Traceability

| Biomimetic Equation / Rule | Implementation Status | Exact Repository Module & Symbol |
| :--- | :--- | :--- |
| Token partitions (`RAW_POLLEN`, `LIQUID_NECTR`, `ROYAL_COMB_RESERVE`) & conservation | Implemented (Wave 0/1) | `src/nectr/contracts/engine.py`: `TokenState`, `HiveContractEngine.assert_supply_conservation()` |
| `QUEEN` non-tutoring separation & `100%` dispute fee to `comb_reserve` | Implemented (Wave 0/1) | `src/nectr/contracts/engine.py`: `BeeRole.QUEEN`, `create_service_barter_escrow()`, `resolve_disputed_session()` |
| Pairwise decay (`1.5`), lineage (`0.5`), `>= 0.6` gate, `0.25 * W` credit | Implemented (Wave 0/1) | `src/nectr/contracts/engine.py`: `HiveContractEngine.settle_co_signed_session()` |
| Guard Bee `Accepted Status` (`K = 3`), `[0.5x, 2.0x]` FX, `5%` bridge toll | Implemented (Wave 0/1) | `src/nectr/contracts/engine.py`: `HiveContractEngine.bridge_nectr_to_target_hive()` |
| Phase 1 Royal Jelly health score & useful compute verification (`UsefulComputeProof`) | Implemented (Wave 0/1) | `src/nectr/services/hive_service.py`: `HiveServiceLayer.mine_epoch_block()`, `compute_useful_work_proof()` |
| Multi-Hive 6-Persona ACE smoke simulation (`K = 2` testbench override) | Implemented (Wave 0/1) | `src/nectr/personas/simulator.py`: `SimulationTelemetry`, `run_multi_hive_persona_simulation()` |
| Lazy demurrage (`DEC-001`), Waggle surge (`DEC-002`, `DEC-013`), `QMP` FSM, `EO` Governor (`DEC-013`), Swarm Bivouac (`DEC-012`) & Senior sinks (`DEC-004`) | `[Planned Wave 2B]` | `DemurrageAccumulator`, `WaggleTrembleController`, `QMPHealthAndSupersedureFSM`, `TemporalPolyethismGovernor`, `SwarmBivouacEscrow` |

In `paper/lineage.yaml` (rendered in [Provenance & Lineage](provenance_lineage.md)), this document corresponds to **`theory:biomimetic_guards`**, tracing upstream primary citations `source:downs_ratnieks_2000`, `source:bonabeau_1996`, `source:seeley_visscher_2004`, and `source:reina_2017` (alongside `seeley_tovey_1994`, `camazine_sneyd_1991`, `ratnieks_1988`, `wenseleers_ratnieks_2006`, `leoncini_2004`, and `khoury_2011` in `paper/references.yaml`) into `decision:ADR-0005` (`code:contracts_engine`), complementing sibling theory nodes `theory:supply_conservation`, `theory:pairwise_decay`, `theory:queen_payoff`, and `theory:duplex_pouw_security` in [Tokenomics & Game Theory](tokenomics_game_theory.md).
