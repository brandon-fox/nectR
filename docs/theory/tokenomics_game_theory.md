# Tokenomics & Game Theory Specification

This specification establishes the formal macroeconomic conservation laws, anti-collusion graph proofs, principal–agent governance equilibria, cross-Hive bridge pricing rules, and duplex `PoUW-PoW` security bounds for **nectR**. Every model parameter and institutional safeguard aligns with the locked protocol decisions (`DEC-001` through `DEC-015`, `EXP-001` through `EXP-003`) in the [Fast Decision Log](../planning/decision_log.md), the [Domain Glossary](../glossary.md), and the canonical bibliography in `paper/references.yaml` (audited via [Provenance & Lineage](provenance_lineage.md)).

## 1. Motivation: Illiquidity Recessions & Oracle Collusion

Closed peer-to-peer (P2P) campus tutoring economies face two intertwined market failures:

1. **Liquidity Freezes & Seasonal Demand Clustering (`sweeney_1977`, `mattsson_2023`):** As demonstrated in the Capitol Hill Babysitting Co-op (`sweeney_1977`), fixed-supply coupon economies suffer severe recessions whenever participants simultaneously hoard precautionary balances ahead of anticipated demand spikes. University semesters amplify this pathology: baseline demand near `0.3x` in Weeks 1–4 spikes to `3.0x–4.0x` during Midterms (Weeks 5–6, 9–10) and `10.0x` during Finals (Weeks 14–15), while overlapping-generations (OLG) graduation creates structural spring deflation when Seniors exit with unspent balances (`ADR-0006`).
2. **Oracle & Sybil Wash-Trading (`filippas_2020`, `iosifidis_2018`):** When zero-fee P2P transfers carry reputation or voucher-unlocking weight, pairs of colluding roommates ($A \leftrightarrow B$) can execute zero-cost phantom tutoring sessions to mint unbacked reputation, unlock restricted vouchers, or pass cross-Hive admission gates, while public star ratings collapse under retaliatory reputation inflation (`filippas_2020`).

## 2. Closed-Loop Supply Conservation, Fisher Velocity ($MV = PQ$) & Macro Stabilization

### 2.1 Closed-Loop Supply Conservation (`ADR-0002`, `D-03`, `D-05`, `HiveContractEngine`)

Within any single Hive $H_i$ at block height $t$, total minted supply $M_{H_i}(t)$ is strictly partitioned across four non-overlapping on-chain buckets (`src/nectr/contracts/engine.py`, `HiveContractEngine.assert_supply_conservation()`, invariant `D-03`):

$$M_{H_i}(t) = S_{\text{comb}}(t) + \sum_{u \in V} B_{\text{pollen}}(u, t) + \sum_{u \in V} B_{\text{nectR}}(u, t) + E_{\text{locked}}(t)$$

where:

- $S_{\text{comb}}(t)$ is the Hive's `ROYAL_COMB_RESERVE` (`comb_reserve`), holding institutional Seed Comb injections, governance fees, certification stakes, bridge tolls, and demurrage inflows (`ADR-0004`).
- $B_{\text{pollen}}(u, t)$ is Bee $u$'s restricted `RAW_POLLEN` balance (`raw_pollen_balance`), spendable exclusively with a `CERTIFIED_WORKER_BEE` accredited in the session's `subject_id` (`D-05`).
- $B_{\text{nectR}}(u, t)$ is Bee $u$'s unrestricted `LIQUID_NECTR` balance (`liquid_nectr_balance`), refined only via verified tutoring settlement.
- $E_{\text{locked}}(t) = \sum_{s \in \mathcal{S}_{\text{escrow}}(t)} a_s$ is total value locked in `ServiceBarterSession` escrows in `SessionStatus.INTENT_ESCROWED` (`escrowed_amount`).

All intra-Hive transitions—`allocate_raw_pollen_to_learner`, `certify_worker_bee`, `create_service_barter_escrow`, `settle_co_signed_session` (at `0%` P2P protocol fee), and `resolve_disputed_session` (routing `100%` of `fee_to_comb` to `comb_reserve`)—satisfy exact supply conservation ($\Delta M_{H_i} = 0$), verified after every mutation by `assert_supply_conservation()`. Cross-Hive bridges execute atomic burn-in-source and mint-in-target transitions with a `5%` source Comb toll (`ADR-0005`).

### 2.2 Fisher Equation of Exchange, Stock-Flow Differential & Burn-Mint Equilibrium (`BME`)

Active circulating supply outside the Comb and active escrows is:

$$M(t) = \sum_{u \in V} \big(B_{\text{pollen}}(u, t) + B_{\text{nectR}}(u, t)\big) = M_{H_i}(t) - S_{\text{comb}}(t) - E_{\text{locked}}(t)$$

Closed-economy price stability follows Fisher's Equation of Exchange (`sweeney_1977`, `mattsson_2023`):

$$M(e) \cdot V(e) = P(e) \cdot Q(e), \qquad V(e) = \frac{1}{M(e)} \sum_{\text{tx} \in e} a_{\text{tx}}$$

where $V(e)$ is epoch monetary turnover (and `HiveServiceLayer.compute_useful_work_proof()` computes the collusion-discounted network velocity $V_{\text{graph}}(e) = \sum_{\text{tx}} a_{\text{tx}} \cdot W_{\text{eff}}(\text{tx})$), $P(e)$ is the session price index (pegged conceptually to one structured campus tutoring hour, minimum `25 minutes` per `DEC-011`), and $Q(e) \equiv Y(e)$ is real verified tutoring hours delivered. Note that per `gneezy_rustichini_2000` ("Pay Enough or Don't Pay at All") and `DEC-011`, trivial micro-payments crowd out intrinsic prosocial help, so `LIQUID_NECTR` settlements enforce structured blocks (`>= 25 minutes`) rather than casual Q&A.

Across epoch $e$, circulating supply evolves via the stock-flow differential between **Faucets** $F(e)$ (Comb `RAW_POLLEN` unlocks, Waggle surge co-pays, and `PoUW-PoW` Compute Jar rebates) and **Sinks** $S(e)$ (certification/dispute/bridge fees, lazy demurrage, and Senior graduation sinks):

$$\Delta M(e) = F(e) - S(e)$$

Taking discrete log-differences of $M V = P Y$ gives $g_M + g_V = \pi_{\text{target}} + g_Y$, where $g_M = \Delta M / M$, $g_V = \Delta V / V$, $\pi_{\text{target}} = \Delta P / P$, and $g_Y = \Delta Y / Y$. At steady velocity ($g_V = 0$), optimal net monetary expansion is $\Delta M^*(e) = M(e)\,(g_Y + \pi_{\text{target}})$, yielding the exact Faucet-to-Sink and Sink-to-Source equilibrium ratios:

$$\frac{F(e)}{S(e)} = 1 + \frac{M(e)}{S(e)}(g_Y + \pi_{\text{target}}), \qquad \text{SSR}(e) = \frac{S(e)}{F(e)} = 1 - \frac{M(e)}{F(e)}(g_Y + \pi_{\text{target}})$$

Under unit-normalized epoch turnover ($S(e) \approx M(e)$), Faucet-to-Sink expansion scales as $1 + g_Y + \pi_{\text{target}}$; in stationary semesters ($g_Y = 0, \pi_{\text{target}} = 0$), steady-state Sink-to-Source equilibrium requires $\text{SSR}(e) = S(e) / F(e) = 1.00$. Solvency is safeguarded by the Burn-Mint Equilibrium (`BME`) Collateralization Ratio:

$$CR(t) = \frac{S_{\text{comb}}(t)}{L_{\text{outstanding}}(t)} \ge 1.0$$

where $L_{\text{outstanding}}(t)$ denotes outstanding Comb redemption and surge obligations.

### 2.3 Lazy Demurrage (`DEC-001`, `ADR-0003`, `mattsson_2023`, `EXP-002`)

To prevent Weeks 1–4 precautionary hoarding without $O(\lvert V \rvert)$ per-block ledger loops (`ADR-0002`, `mattsson_2023`), `DEC-001` specifies **lazy on-read / on-transfer demurrage** evaluated from `lastActive[u]` **exclusively** on `LIQUID_NECTR` above a protected student safety buffer $B_{\text{safe}}$ during Weeks 1–13, and **paused during Finals (Weeks 14–15)** (`RAW_POLLEN` and `ROYAL_COMB_RESERVE` are exempt):

$$\Delta B_{\text{demurrage}}(u, \Delta t_m) = \mathbb{I}[\text{week} \le 13] \cdot \max\!\left(0, \; B_{\text{nectR}}(u) - B_{\text{safe}}\right) \cdot \left(1 - (1 - d)^{\Delta t_m}\right), \qquad d \approx 0.02\text{ month}^{-1}$$

where $\Delta t_m$ is elapsed months since `lastActive[u]` (yielding $1 - 0.98^{12} = 21.53\%/\text{yr}$ on continuously idle surplus above $B_{\text{safe}}$, matching Sarafu's empirical $2\%/\text{month}$ holding decay in `mattsson_2023`). Tunable per Hive by Queens/`BEEKEEPER`, $100\%$ of $\Delta B_{\text{demurrage}}$ routes to $S_{\text{comb}}$ (tested jointly with `DEC-002` under `EXP-002`). *(Implementation boundary: `DemurrageAccumulator` is a planned Wave 2B contract extension in [Project Roadmap](../planning/roadmap.md) and is not yet active in `HiveContractEngine`.)*

### 2.4 Waggle Surge Co-Pay (`DEC-002`, `ADR-0004`, `EXP-002`)

During Midterms (Weeks 5–6, 9–10; `3.0x–4.0x` demand) and Finals (Weeks 14–15; `10.0x` demand), charging learners peak market-clearing prices out of pocket excludes liquidity-constrained students when course risk is highest. Under `DEC-002`, the Comb decouples tutor compensation $P_{\text{tutor}}(t)$ from learner out-of-pocket price $P_{\text{learner}}(t)$ via a Waggle surge multiplier $m_t \in [1.0, 2.2]$ and Comb co-pay target $\kappa_{\text{copay}} \approx 0.60$:

$$P_{\text{tutor}}(t) = m_t P_{\text{base}}, \qquad P_{\text{learner}}(t) = \text{clip}\!\left((1 - \kappa_{\text{copay}})\, m_t P_{\text{base}}, \; 1.0\, P_{\text{base}}, \; 1.3\, P_{\text{base}}\right), \qquad \Delta S_{\text{waggle}}(t) = P_{\text{tutor}}(t) - P_{\text{learner}}(t)$$

At peak surge ($m_t = 2.2$), tutors earn `~2.2x` $P_{\text{base}}$ while the Comb co-pays `~60%` of the peak payout (bounded so learners pay `~1.0x–1.3x` $P_{\text{base}}$, i.e., Comb covers $0.9 P_{\text{base}}$ to $1.2 P_{\text{base}}$ depending on Hive reserves and tier). *(Implementation boundary: `WaggleTrembleController` is scheduled for Wave 2B.)*

### 2.5 Senior 40/35/25 Exit Sinks & Dormant Alumni Sweep (`DEC-004`, `ADR-0006`)

To eliminate OLG graduation currency drain when net-supplier upperclassmen depart each spring, `DEC-004` and [ADR-0006](../adr/0006-adopt-two-phase-hive-genesis-and-autonomous-swarming.md) partition graduating balances $B_{\text{exit}}(u)$ across three sinks alongside a dormant alumni Comb sweep $B_{\text{dormant}}(u)$ after inactivity threshold $\tau_{\text{alum}}$:

$$S_{\text{grad\_sinks}}(u) = 0.40\, B_{\text{exit}}(u) + 0.35\, B_{\text{exit}}(u) + 0.25\, B_{\text{exit}}(u)$$

Here, `40%` locks or converts into verified honors credentials and Daughter-Hive Queen Swarming stakes, `35%` redeems low-marginal-cost campus perks (retiring supply), and `25%` feeds the Freshman Bounty Pool (alongside dormant alumni sweeps $B_{\text{dormant}}$) to replenish $S_{\text{comb}}$ for incoming freshman `RAW_POLLEN` vouchers and Finals Waggle subsidies. *(Implementation boundary: the 3-door Senior exit sink contract is scheduled for Wave 2B.)*

## 3. Pairwise Anti-Collusion Decay, Downstream Lineage & Saturation Proof (`DEC-003`)

### 3.1 Exact `HiveContractEngine` Weight & Gate Equations

In `src/nectr/contracts/engine.py` (`HiveContractEngine.settle_co_signed_session()`), let session $(u \leftarrow v, s)$ connect tutor $u$ and learner $v$ in subject $s$ with `learner_attestation_score` $a \in [0, 1]$ and prior undirected pair transaction count $n = N_{u \leftrightarrow v} \in \{0, 1, 2, \dots\}$ (`pairwise_counts[frozenset({u, v})]`). Using locked `DEC-003` defaults $\alpha = 1.5$ (`collusion_alpha`) and $\gamma = 0.5$ (`lineage_gamma`), the contract computes:

$$W(u, v, s, n) = \frac{a}{1 + \alpha n} \cdot \left(1 + \gamma \cdot \mathbb{I}\!\left[\mathcal{U}(u, s) \neq \emptyset\right]\right)$$

where $\mathcal{U}(u, s) = \text{subject\_lineage}[(u, s)]$ is the list of upstream tutors who previously taught $u$ subject $s$. Crucially, `HiveContractEngine` enforces a strict **attestation and peer-uniqueness gate**: if and only if **`prior_pair_txs == 0`** ($n = 0$) **and** **`a >= 0.6`**:

1. $u$ is appended to $\mathcal{U}(v, s)$ (`subject_lineage[(v, s)]`);
2. $v$ is added to $u$'s `distinct_peers_tutored_in_hive` (advancing Guard Bee `Accepted Status` toward $K = 3$);
3. Each upstream tutor $u' \in \mathcal{U}(u, s)$ receives **`+0.25 * W(u, v, s, 0)`** in `tutor_effectiveness` (**Learn-then-Teach** cascade, empirically grounded in `leung_2019` and `nickow_2024`).

### 3.2 Asymptotic Wash-Trading Saturation Proof (`buterin_2019`, `iosifidis_2018`, `weyl_2022`, `kamvar_2003`, `EXP-003`)

**Theorem 1 (Sublinear Collusion Decay & Bounded Bilateral Extraction).** *Under `HiveContractEngine` coupled with Pairwise Discoordination (`buterin_2019`) and cyclic motif filtering (`iosifidis_2018`), a bilateral wash-trading pair $(A \leftrightarrow B)$ executing $N$ repeated loops achieves:*

1. *Logarithmic cumulative contract effectiveness $\Theta(\frac{1}{\alpha}\ln N)$ with **identically zero** marginal Guard-Bee peer count and **identically zero** marginal upstream lineage credit for every repeat transaction $n \ge 1$; and*
2. *A strict finite upper bound $k < \infty$ (and $\le \binom{m}{2}k$ for an $m$-node Sybil ring) under graph-level Pairwise Discoordination.*

**Proof.**

- **1. Contract-Layer Attenuation (`engine.py`):** On loop index $n \in \{0, 1, \dots, N-1\}$, marginal decay $\frac{1}{1 + 1.5n}$ drops by $60\%$ at $n=1$ ($0.40$), $75\%$ at $n=2$ ($0.25$), and $>90\%$ for $n \ge 6$ ($\le 0.10$). Summing over $N$ loops yields:

$$\sum_{n=0}^{N-1} W(A, B, s, n) \le \sum_{n=0}^{N-1} \frac{1 + \gamma}{1 + \alpha n} \le (1 + \gamma)\left(1 + \frac{\ln(1 + \alpha(N-1))}{\alpha}\right) = \Theta\!\left(\frac{\ln N}{\alpha}\right)$$

Meanwhile, the uniqueness condition `prior_pair_txs == 0` evaluates to `False` for all $n \ge 1$, so $\Delta \lvert \text{distinct\_peers\_tutored\_in\_hive} \rvert = 0$ and $\Delta W_{\text{upstream}} = 0$ regardless of $N$.

- **2. Graph-Layer Pairwise Discoordination & COCM Dorm-Cluster Discounting (`buterin_2019`, `EXP-003`):** Over unordered peer pairs $\{i, j\}$ with shared-counterparty overlap $C_{i,j}$ and discoordination factor $k_{i,j} = \frac{k}{k + C_{i,j}}$, bilateral wash volume $W_{\text{wash}}$ between $A$ and $B$ satisfies $C_{A,B} \ge W_{\text{wash}}$, giving:

$$R_{\text{pair}}(A, B) = \frac{k}{k + W_{\text{wash}}} \sqrt{W_{\text{wash}} \cdot W_{\text{wash}}} = \frac{k\, W_{\text{wash}}}{k + W_{\text{wash}}} < k \qquad \text{with} \quad \lim_{W_{\text{wash}} \to \infty} R_{\text{pair}}(A, B) = k < \infty$$

Summing across all $\binom{m}{2}$ pairs in an $m$-node Sybil ring yields the finite cap $R_{\text{ring}} \le \binom{m}{2}k$, whereas $m$ honest peers serving unclustered classmates ($C_{i,j} = 0 \implies k_{i,j} = 1$) scale quadratically as $\binom{m}{2}w$. Simultaneously, Sardex $k$-cycle motif filtering (`iosifidis_2018`) assigns zero cyclic diversity weight to $k = 2$ bilateral reciprocity, while **Connection-Oriented Cluster Matching (`COCM`)** Fiedler-vector spectral clustering ($v_2$, second smallest eigenvalue of the user-SBT graph Laplacian, `weyl_2022`) and **EigenTrust** campus department/faculty Queen anchors (`kamvar_2003`) suppress coordinated dorm or fraternity cliques lacking external academic overlap (`EXP-003`). $\blacksquare$

### 3.3 Spence Single-Crossing Separation ($s^* = 6$) & Peer Collusion Game (`spence_1973`, `filippas_2020`, `EXP-001`)

Public two-sided star ratings collapse via reflected social retaliation (`filippas_2020`). Grounded in Spence's (1973) Signalling Theory (`spence_1973`), **nectR** suppresses public 5-star ratings (`EXP-001`) and `HiveContractEngine` gates elite tiers and Waggle surge access on verifiable downstream outcomes (`learner_attestation_score >= 0.6` plus `+0.25 * W` Learn-then-Teach lineage propagation). Let high-ability pedagogical tutors have type $\theta_H = 2$, answer-dumping tutors have type $\theta_L = 1$, signalling cost $c(s, \theta) = s / \theta$, and elite tier premium $\Delta W = 6$:

- **Single-Crossing Condition:** $\frac{\partial^2 c}{\partial s \partial \theta} = -\frac{1}{\theta^2} < 0$. Answer-dumpers cannot cheaply induce tutees to pass subsequent mastery checks and teach new peers.
- **Riley Least-Cost Separating Equilibrium:** Low-type non-mimicry ($\Delta W - s / \theta_L \le 0 \implies s \ge 6$) and high-type participation ($\Delta W - s / \theta_H \ge 0 \implies s \le 12$) pin the unique Cho–Kreps Intuitive Criterion threshold at **$s^* = 6$** downstream mastery points (net payoff $+3$ for $\theta_H$, $0$ for $\theta_L$).

| Peer A \ Peer B | Honest Session & Truthful Private Signal | Collude (Phantom Check-In / Reciprocal Rating) | Frame / Report Collusion Attempt |
| :--- | :--- | :--- | :--- |
| **Honest Session & Truthful Signal** | **(+10, +10)** — Valid edge, full weight | **(+10, +2)** — Phantom claim fails co-signing | **(+10, +10)** — No side-deal to report |
| **Collude (Phantom Check-In)** | **(+2, +10)** — Unilateral claim rejected | **(-6, -6)** under audit / decay (vs. +15 if unmonitored) | **(-12, +16)** — Defector claims framing bounty |
| **Frame / Report Collusion** | **(+10, +10)** — Baseless claim forfeits bond | **(+16, -12)** — Whistleblower claims bounty | **(-8, -8)** — Mutual reporting forfeits both bonds |

*(Biological parallel: selective worker policing / oophagy in `ratnieks_1988` and `wenseleers_ratnieks_2006`; see [Biomimetic Hive Mechanics](biomimicry_model.md).)*

## 4. Non-Tutoring Queen Payoff & Kofman–Lawarrée Nash Equilibrium (`ADR-0003`, `ADR-0004`, `tirole_1986`, `kofman_lawarree_1993`, `EXP-001`)

### 4.1 Strict Separation of Powers & Phase-Split Royal Jelly (`ADR-0003`, `ADR-0004`, `D-02`)

Under Tirole (`tirole_1986`) and Kofman & Lawarrée (`kofman_lawarree_1993`), delegating local certification and arbitration to Hive Queens introduces shirking and side-contract bribery risks unless strict Separation of Powers (`D-02`, `ADR-0003`) is paired with random `BEEKEEPER` / Meta-Court audits at probability $p$ and bond slashing $\lambda B_Q$. `BeeRole.QUEEN` accounts are cryptographically barred from acting as `tutor_id` in `create_service_barter_escrow`, as `worker_id` in `certify_worker_bee`, as `learner_id` in `allocate_raw_pollen_to_learner`, or from cross-Hive bridging (`src/nectr/contracts/engine.py`). Normal P2P settlements charge `0%` fee, while `100%` of governance fees ($F_{\text{cert}}, F_{\text{dispute}}, F_{\text{bridge}}$) flow into $S_{\text{comb}}$. Under [ADR-0004](../adr/0004-route-governance-fees-to-comb-with-phase-split-royal-jelly.md), Queen **Royal Jelly** compensation splits by deployment phase:

- **Phase 1 (Founding Teacher-Queen / Faculty Steward):** Earns non-monetary academic impact credits $I_Q(e) = R_Q(e)$ (zero `LIQUID_NECTR` disbursements, preserving student liquidity and avoiding institutional payroll conflicts).
- **Phase 2 (Veteran Student-Queen):** Posts staked collateral bond $B_Q$ (slashable by `BEEKEEPER` / Meta-Court audit) and earns bond-backed `LIQUID_NECTR` dividends tied to healthy Comb growth, collusion-discounted velocity $V_{\text{graph}}(e)$, and low wealth inequality:

$$R_Q(e) = \beta \cdot \Delta S_{\text{comb}}^+(e) \cdot V_{\text{graph}}(e) \cdot (1 - \text{Gini}(e))$$

### 4.2 Kofman–Lawarrée Auditing & Exact Nash Equilibrium Payoff Matrix (`kofman_lawarree_1993`)

Following delegated hierarchical auditing (`kofman_lawarree_1993`), a Meta-Court / `BEEKEEPER` audits Queen certifications and dispute rulings with unannounced probability $p \in [0, 1]$ and slashes fraction $\lambda \in (0, 1]$ of bond $B_Q$ upon detecting bribery ($B_{\text{bribe}}$) or frivolous dispute farming ($F_d$). Let $\gamma_Q \Delta M$ denote the delayed downstream-mastery vesting bonus, $c_{\text{verify}}$ verification cost, and $\delta_Q(D - D^*)$ the excess-dispute penalty:

$$E[U_{\text{honest}}] = R_Q(e) + \gamma_Q \Delta M - c_{\text{verify}}$$

$$E[U_{\text{bribe}}(p)] = (1 - p)\big(R_Q(e) + B_{\text{bribe}}\big) - p\,\lambda B_Q$$

$$E[U_{\text{fake\_dispute}}(p)] = (1 - p)\big(R_Q(e) + F_d - \delta_Q(D - D^*)\big) - p\,\lambda B_Q$$

Honest governance strictly dominates bribery ($E[U_{\text{honest}}] > E[U_{\text{bribe}}(p)]$) whenever:

$$p > p^* = \frac{B_{\text{bribe}} + c_{\text{verify}} - \gamma_Q \Delta M}{B_{\text{bribe}} + \lambda B_Q + R_Q(e)}$$

Using calibrated parameters $R_Q = 45.0$, $\gamma_Q \Delta M = 20.0$, $c_{\text{verify}} = 5.0$, $B_Q = 100.0$, $\lambda = 1.0$, $B_{\text{bribe}} = 12.0$, $F_d = 10.0$, and $\delta_Q(D - D^*) = 20.0$:

- $E[U_{\text{honest}}] = 45.0 + 20.0 - 5.0 = \mathbf{60.0}$ (independent of $p$).
- At $p = 0.15$: $E[U_{\text{bribe}}] = 0.85(45.0 + 12.0) - 0.15(100.0) = 48.45 - 15.00 = \mathbf{33.45}$; $E[U_{\text{fake\_dispute}}] = 0.85(45.0 + 10.0 - 20.0) - 0.15(100.0) = 29.75 - 15.00 = \mathbf{14.75}$.
- At $p = 0.00$: $E[U_{\text{bribe}}] = 1.00(57.0) - 0 = \mathbf{57.0}$; $E[U_{\text{fake\_dispute}}] = 1.00(35.0) - 0 = \mathbf{35.0}$.
- Even in the conservative boundary $\gamma_Q \Delta M = 0$ (before downstream mastery vests), $p^* = \frac{12 + 5}{12 + 100 + 45} = \frac{17}{157} \approx \mathbf{0.1083} < 0.15$, confirming $p = 0.15$ enforces honesty as the unique subgame-perfect Nash equilibrium.

| Queen Strategy \ Hive & Meta-Court State | Honest Peer Majority & Active Auditing ($p = 0.15$) | Lax Oversight / Unaudited Node ($p = 0.00$) |
| :--- | :--- | :--- |
| **Honest Certification & Impartial Arbitration** | **(60.0, +85)** — Unique Nash equilibrium; maximizes velocity and trust | **(60.0, +85)** — Still dominates ($60.0 > 57.0$) via delayed $\gamma_Q \Delta M$ |
| **Rubber-Stamp Tutor (Accept Bribe $B_{\text{bribe}} = 12$)** | **(33.45, -30)** — Audit probability $p=0.15$ slashes bond $\lambda B_Q$ ($33.45 < 60.0$) | **(57.0, -45)** — Inferior to Honest ($57.0 < 60.0$); fragile if $\gamma_Q \Delta M \to 0$ |
| **Manufacture Fake Dispute (Fee $F_d = 10$)** | **(14.75, -40)** — Excess dispute penalty + audit slash destroy surplus ($14.75 < 60.0$) | **(35.0, -40)** — Excess dispute penalty keeps payoff below Honest ($35.0 < 60.0$) |

### 4.3 Code Reconciliation (`HiveServiceLayer.mine_epoch_block()`) & `EXP-001` Caveat

In the current Wave 1 implementation (`src/nectr/services/hive_service.py`), `HiveServiceLayer.mine_epoch_block(queen_dividend_beta=0.05)` implements the Phase 1 non-monetary governance score:

```python
acct.royal_jelly_earned = round(
    queen_dividend_beta * proof.collusion_discounted_velocity * (1.0 - proof.gini_coefficient),
    4,
)
```

This score omits $\Delta S_{\text{comb}}^+(e)$, the delayed $\gamma_Q \Delta M$ vesting term, and the excess-dispute penalty $\delta_Q(D - D^*)$, which are deferred to Phase 2 Student-Queen bond-staking contracts. Additionally, per **`EXP-001`** in [Fast Decision Log](../planning/decision_log.md) (`status: open-simulation`), Queen receiver-only praise weights (allowing Queens to praise learner outcomes tracing backward to tutors) remain **unlocked** until validated across Honest vs. Biased nepotism simulation arms.

## 5. Guard Bee `Accepted Status`, Epoch Cross-Hive FX & `PoUW-PoW` Security

### 5.1 Guard Bee `Accepted Status`, FX Corridor & Bancor ABC Exclusion (`DEC-003`, `DEC-004`, `ADR-0005`, `downs_ratnieks_2000`)

Cross-Hive capital mobility is gated by **Guard Bee Cuticular Recognition** (`downs_ratnieks_2000`). A visiting `POLLINATOR_VISITOR` $u$ migrating from $H_A$ to $H_B$ earns `Accepted Status` (`u.accepted_in_hives.add(H_B)`) in `HiveContractEngine` if and only if $u$ tutors at least $K = 3$ (`accepted_status_peer_threshold = 3`, `DEC-003`) distinct host-Hive peers with `learner_attestation_score >= 0.6` on first-time pairs ($N_{u \leftrightarrow v} = 0$):

$$\mathrm{Accepted}(u, H_B) = \mathbb{I}\!\left(\left\lvert\left\{v \in V_{H_B} : \text{Attestation}(v \to u) \ge 0.6 \land N_{u \leftrightarrow v} = 0\right\}\right\rvert \ge K\right), \qquad K = 3$$

`BeeRole.QUEEN` accounts are unconditionally prohibited from bridging (`engine.py`). Once accepted, bridging amount $a$ from $H_A$ to $H_B$ (`bridge_nectr_to_target_hive`) computes each Hive's effective Comb-per-active-Bee backing ratio and clamps the epoch exchange rate to `[0.5x, 2.0x]` (`DEC-004`, `ADR-0005`) with a `5%` source Comb toll ($\tau_{\text{bridge}} = 0.05$):

$$R_{\text{eff}}(H, e) = \max\!\left(\frac{S_{\text{comb}}(H, e)}{\max(\lvert V_H \rvert, 1)}, \; 1.0\right), \qquad \text{FX}(H_A \to H_B, e) = \min\!\left(2.0, \; \max\!\left(0.5, \; \frac{R_{\text{eff}}(H_A, e)}{R_{\text{eff}}(H_B, e)}\right)\right)$$

$$F_{\text{bridge}} = 0.05 \cdot a \longrightarrow S_{\text{comb}}(H_A), \qquad \Delta M_{H_A} = -(a - F_{\text{bridge}}), \qquad \Delta M_{H_B} = +(a - F_{\text{bridge}}) \cdot \text{FX}(H_A \to H_B, e)$$

Supply conservation (`assert_supply_conservation()`) is verified on both Hives atomically.

**Exclusion of Continuous Bancor Augmented Bonding Curves (`ADR-0005`):** Continuous Bancor Augmented Bonding Curves (`ABC`s, $R = \rho \cdot S \cdot P$) are explicitly excluded per [ADR-0005](../adr/0005-gate-cross-hive-bridges-with-guard-bee-status-and-epoch-fx.md). As documented in the Sarafu post-mortem (`mattsson_2023`), Grassroots Economics dropped continuous Bancor curves in favor of single-token simplicity because per-trade curves introduce extreme reserve-ratio sensitivity, student UX confusion, and Maximal Extractable Value (MEV) sandwich arbitrage. Epoch-level Comb-per-active-Bee FX snapshots plus `K=3` Guard Bee acceptance eliminate sandwich attacks completely.

### 5.2 Open Campus & Transcript-Oracle `PoUW-PoW` Duplex Security (`ADR-0007`, `ball_2018`)

Per [ADR-0007](../adr/0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md), block mining in `src/nectr/chain/ledger.py` couples SHA-256 Proof-of-Work (`BlockHeader`) with a deterministic `UsefulComputeProof` committing `epoch`, `active_bees`, `total_directional_edges`, `collusion_discounted_velocity`, `gini_coefficient`, and `graph_state_hash`. Under fine-grained Proof-of-Useful-Work (`ball_2018`) and transcript-oracle difficulty coupling ([Federated PoUW-PoW Infrastructure](research/federated_PoUW-PoW_blockchain_infrastructure.md)), a campus node evaluates a bounded useful transcript $\pi_{\text{pouw}}$ over the epoch's Knowledge Graph and Pairwise Decay matrix from a deterministic header seed $\sigma_t$:

$$H(\sigma_t \parallel \text{kg\_root} \parallel \pi_{\text{pouw}} \parallel \text{nonce}) < 2^{\ell} \cdot p$$

When proving overhead is bounded and task instances are bucketed into uniform difficulty bands, the duplex security surplus above wasted work remains strictly positive ($\Delta_{\text{sec}} > 0$). Meanwhile, miner payouts derive strictly from a capped **Comb Compute Jar** with zero inflationary coinbase minting, pausing payouts whenever the jar depletes so $M_{H_i}(t)$ remains strictly conserved.

## 6. Empirical ACE Telemetry (`src/nectr/personas/simulator.py`, `nectr_sim_baseline_2026`)

Executing `run_multi_hive_persona_simulation()` (`src/nectr/personas/simulator.py`, cited as `nectr_sim_baseline_2026` in `paper/references.yaml`) runs all 6 Behavioral Persona Sub-Agents (`docs/experiments/persona_swarm_spec.md` / [Persona Swarm Spec](../experiments/persona_swarm_spec.md)) across `HIVE_ALPHA` and `HIVE_BETA` on the live `PoUW-PoW` chain (`tests/test_invariants.py`). *(Note: `simulator.py` sets `accepted_status_peer_threshold=2` for compact 3-epoch smoke validation versus the locked `DEC-003` production default `K=3`; `experiments/` currently holds `experiments/README.md` only, with full `mesa` Monte Carlo sweeps per `ADR-0010` / `DEC-009` scheduled for Milestone 3.)*

| Telemetry Metric (`SimulationTelemetry`) | Observed Baseline (`nectr_sim_baseline_2026`) | Theoretical Invariant Validated |
| :--- | :---: | :--- |
| `hive_a_blocks_mined` / `hive_a_chain_valid` | `5` / `True` | `PoUW-PoW` Merkle + `UsefulComputeProof` chain integrity |
| `hive_a_comb_reserve` | `905.5` | `1000.0` Seed Comb $-$ `95.0` `RAW_POLLEN` $+$ `0.5` `5%` bridge toll |
| `honest_worker_effectiveness` | `3.2062` | `>= 0.6` attestation + `0.25 * W` Learn-then-Teach cascade |
| `sybil_colluder_effectiveness` | `1.3232` | $\frac{1}{1 + 1.5n}$ decay across 6 `A <-> B` wash loops |
| `collusion_attenuation_ratio` | `2.4231x` | Honest vs. Sybil effectiveness separation |
| `pollinator_accepted_in_hive_b` | `True` | Guard Bee `Accepted Status` (testbench `K=2`, prod `K=3`) |
| `exchange_rate` / `pollinator_bridged_nectr` | `0.707` / `6.716797` | Clamped `[0.5x, 2.0x]` FX on `9.5` net `LIQUID_NECTR` (`10.0 - 0.5` toll) |
| `queen_royal_jelly_score` | `2.009` | Phase 1 `HiveServiceLayer.mine_epoch_block()` (`beta = 0.05`) |

## 7. Provenance Lineage Mapping (`paper/lineage.yaml`)

This specification maps directly to four canonical theory nodes in `paper/lineage.yaml` (rendered in [Provenance & Lineage](provenance_lineage.md)):

- `theory:supply_conservation`: driven by `source:sweeney_1977` and `source:mattsson_2023`, governing `decision:ADR-0002` and `decision:ADR-0006` (`code:contracts_engine`).
- `theory:pairwise_decay`: driven by `source:iosifidis_2018`, `source:buterin_2019`, `source:spence_1973`, `source:kazil_2020`, and `source:nectr_sim_baseline_2026`, governing `decision:ADR-0010` (`code:persona_simulator`).
- `theory:queen_payoff`: driven by `source:tirole_1986` and `source:kofman_lawarree_1993`, governing `decision:ADR-0003` and `decision:ADR-0004` (`code:contracts_engine`, `code:hive_service`).
- `theory:duplex_pouw_security`: driven by `source:ball_2018` and `source:treinish_2022`, governing `decision:ADR-0007`, `decision:ADR-0008`, and `decision:ADR-0014` (`code:chain_ledger`, `code:hive_service`).
