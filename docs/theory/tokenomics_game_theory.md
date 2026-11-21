# Tokenomics & Game Theory Specification

This specification defines the closed-loop monetary equilibrium, graph-theoretic anti-collusion bounds, Principal-Agent governance matrices, Spence downstream mastery signalling, and Proof-of-Useful-Work (`PoUW-PoW`) duplex security proofs for **nectR**.

---

## 1. Closed-Loop Supply Conservation & Stock-Flow Equilibrium ($MV = PQ$)

Within any single campus Hive $H_i$ at block height $t$, total token supply $M_{H_i}(t)$ is strictly conserved across four partitioned states (`ADR-0002`, `D-03`):

$$M_{H_i}(t) = S_{\text{comb}}(t) + \sum_{u \in V} B_{\text{pollen}}(u, t) + \sum_{u \in V} B_{\text{nectR}}(u, t) + E_{\text{locked}}(t)$$

Direct peer-to-peer tutoring settlements transfer $B_{\text{nectR}}$ (or refine restricted $B_{\text{pollen}} \to B_{\text{nectR}}$ when paired with a `CERTIFIED_WORKER_BEE`, `D-05`) at a **`0%` protocol fee**, preventing inflationary self-minting. Aggregate monetary circulation obeys Fisher's Equation of Exchange:

$$M \cdot V = P \cdot Q$$

where $M$ is circulating supply, $V$ is epoch turnover velocity, $P$ is the session price index (pegged conceptually to one structured campus tutoring hour, minimum `25 minutes` per `DEC-011`), and $Q$ is real verified tutoring hours delivered.

### 1.1 Lazy Demurrage, Waggle Co-Pay & Sink-to-Source Balance

To prevent the **Capitol Hill Babysitting Co-op liquidity trap** (`sweeney_1977`) across a 15-week semester—where demand surges from `0.3x` in Weeks 1–4 to `3.0x–4.0x` during Midterms (Weeks 5–6, 9–10) and `10.0x` during Finals (Weeks 14–15)—`TokenStateAndCombContract` applies a lazy monthly demurrage rate $d \approx 2\%/\text{month}$ (`mattsson_2023`, `DEC-001`) solely on idle `LIQUID_NECTR` balances above a protected student safety cushion $B_{\text{safe}}$ during Weeks 1–13 (pausing during Finals Weeks 14–15):

$$\Delta B_{\text{demurrage}}(u, \Delta e) = \max\!\left(0, \; B_{\text{nectR}}(u) - B_{\text{safe}}\right) \cdot \left(1 - (1 - d)^{\Delta e}\right)$$

100% of demurrage inflows, certification fees ($F_{\text{cert}}$), dispute arbitration fees ($F_{\text{dispute}}$), and cross-Hive bridge tolls ($F_{\text{bridge}}$) flow into the **Comb** ($S_{\text{comb}}$) to fund the **Waggle Surge Bounty Pool** (`DEC-002`), which co-pays `60%` of `2.2x` peak Midterm/Finals tutor payouts so learners pay only `1.0x–1.3x`. In steady-state equilibrium ($\Delta P = 0$), the **Sink-to-Source Ratio** satisfies:

$$\text{SSR}(e) = \frac{\Sigma_{\text{sinks}}(e)}{\Sigma_{\text{sources}}(e)} = \frac{F_{\text{cert}} + F_{\text{dispute}} + F_{\text{bridge}} + \Delta B_{\text{demurrage}} + S_{\text{grad\_sinks}}}{\text{PollenRefined} + \text{WaggleCoPay} + \text{ComputeJarRebates}} = 1.00$$

guarded by an Akash-inspired **Burn-Mint Equilibrium (`BME`) Collateralization Ratio** $CR = S_{\text{comb}} / L_{\text{outstanding}} \ge 1.0$.

---

## 2. Graph-Theoretic Anti-Collusion Defense Stack

### 2.1 Pairwise Discoordination & Learn-then-Teach Lineage (`DEC-003`)

When Tutor $u$ and Learner $v$ co-sign a `DirectionalServiceBarterTx` in subject $s$, the effective reputation and lineage weight $W(u, v, s)$ decays hyperbolically with the count of reciprocal or repeated exchanges $N_{u \leftrightarrow v}(\tau)$ within trailing window $\tau$:

$$W(u, v, s) = \frac{\text{Attestation}(v \to u)}{1 + \alpha \cdot N_{u \leftrightarrow v}(\tau)} \cdot \left(1 + \gamma \cdot L_{\text{downstream}}(v, s)\right)$$

with baseline defaults $\alpha = 1.5$ and $\gamma = 0.5$ (`DEC-003`), where $L_{\text{downstream}}(v, s)$ credits upstream tutors when Learner $v$ subsequently teaches peers in the **Learn-then-Teach** cascade (`leung_2019`).

### 2.2 Buterin Pairwise Coordination Bound & COCM Dorm-Cluster Discounting

Adapting Vitalik Buterin's **Pairwise Coordination Subsidies** (`buterin_2019`) and Sardex $k$-cycle motif centrality (`iosifidis_2018`), aggregate reputation/subsidy weight across unordered learner pairs $\{i, j\}$ is bounded by the pairwise discoordination coefficient $k_{i,j} = \frac{k}{k + C_{i,j}}$:

$$R_{\text{pairwise}}(u) = \sum_{i < j} k_{i,j} \sqrt{w_{i \to u} \cdot w_{j \to u}} \le \binom{m}{2} k$$

Even if $m$ colluding roommates wash infinite volume $W \to \infty$, total extractable reputation is strictly upper-bounded by $\binom{m}{2}k$. To defeat coordinated dorm or fraternity cliques that do not share on-chain transfer edges, **Connection-Oriented Cluster Matching (`COCM`)** and spectral clustering via the **Fiedler vector** ($v_2$, second smallest eigenvalue of the user-SBT graph Laplacian, `weyl_2022`) discount intra-cluster endorsements while **EigenTrust** (`kamvar_2003`) anchors global trust restarts to verified campus departments and faculty Queens (`EXP-003`).

---

## 3. Principal-Agent Game Theory for Non-Tutoring Queens

Under Tirole (`tirole_1986`) and Kofman & Lawarrée (`kofman_lawarree_1993`), delegating local certification and arbitration to Hive Queens introduces shirking and side-contract bribery risks unless Separation of Powers (`D-02`, `ADR-0003`) is paired with random `BEEKEEPER` / Meta-Court audits at probability $p$ and bond slashing $\phi S_Q$.

### 3.1 Queen Expected Utility & Royal Jelly Payoff (`ADR-0004`)

Queens collect `0%` directly from transaction fees. At epoch $e$, a Queen's Royal Jelly dividend $R_Q(e)$ is:

$$R_Q(e) = \beta \cdot \Delta S_{\text{comb}}^+(e) \cdot \mathcal{V}_{\text{graph}}(e) \cdot (1 - \text{Gini}(e))$$

Adding a downstream-vested certification bonus $\gamma_Q \Delta M$ and an excess-dispute penalty $\delta_Q \max(0, D - D^*)$, the Queen's expected per-epoch utilities under Honest Stewardship versus Bribery ($B$) or Dispute-Farming ($F_d$) are:

$$E[U_{\text{honest}}] = R_Q(e) + \gamma_Q \Delta M - c_{\text{verify}}$$

$$E[U_{\text{bribe}}] = (1 - p)\!\left(R_Q(e) + B\right) - p \cdot \phi S_Q, \qquad E[U_{\text{fake\_dispute}}] = (1 - p)\!\left(R_Q(e) + F_d - \delta_Q(D - D^*)\right) - p \cdot \phi S_Q$$

Incentive compatibility ($E[U_{\text{honest}}] > E[U_{\text{bribe}}]$) holds strictly whenever:

$$p > \frac{B + c_{\text{verify}} - \gamma_Q \Delta M}{B + \phi S_Q + R_Q(e)}$$

#### Payoff Matrix 1: Queen vs. Hive Governance & Auditing Game

Calibrated at $R_Q = 45$, $\gamma_Q \Delta M = 20$, $c_{\text{verify}} = 5$, $S_Q = 100$, $\phi = 1.0$, $p = 0.15$, $B = 12$, $F_d = 10$, $\delta_Q(D - D^*) = 20$:

| Queen Strategy \ Oversight State | Active Beekeeper / Meta-Court Auditing ($p = 0.15$) | Unaudited Node ($p = 0.00$) |
| :--- | :--- | :--- |
| **Honest Certification & Impartial Arbitration** | **`(60.0, +85.0)`** — Unique incentive-compatible Nash equilibrium. | **`(60.0, +85.0)`** — Honest Queen captures full downstream mastery bonus $\gamma_Q \Delta M$. |
| **Rubber-Stamp Unqualified Tutor (Bribe $B = 12$)** | **`(31.0, -30.0)`** — Audit slashes bond $S_Q$ and revokes $\gamma_Q \Delta M$ (`31.0 < 60.0`). | **`(52.0, -45.0)`** — Strictly dominated (`52.0 < 60.0`) because lost $\gamma_Q \Delta M > B - c_{\text{verify}}$. |
| **Manufacture Frivolous Dispute (Fee $F_d = 10$)** | **`(20.0, -40.0)`** — Excess-dispute penalty $\delta_Q$ + bond slash destroys Queen utility. | **`(35.0, -40.0)`** — Dominated (`35.0 < 60.0`) due to Comb fee routing and $\delta_Q$ penalty. |

---

## 4. Spence Signalling & Whistleblower Prisoner's Dilemma

To eliminate public 5-star reputation inflation (`filippas_2020`), **nectR** suppresses public star ratings (`EXP-001`) and gates elite tutor tiers and Waggle surge access on **verifiable downstream outcomes** (tutee gateway exam pass rates and Learn-then-Teach conversions). Under Michael Spence's (`spence_1973`) signalling model with signaling cost $c(s, \theta) = s / \theta$ for high-ability pedagogical tutors ($\theta_H = 2$) versus low-ability answer-dumpers ($\theta_L = 1$) and tier premium $\Delta W = 6$, the unique Riley least-cost separating equilibrium (surviving the Cho-Kreps Intuitive Criterion) pins the minimum downstream mastery threshold $s^*$:

$$\frac{s^*}{\theta_L} = \Delta W \implies s^* = 6 \text{ verified downstream mastery units}$$

At $s^* = 6$, an answer-dumper gains $\Delta W - s^*/\theta_L = 0$ (no incentive to mimic), whereas a pedagogical tutor earns positive net surplus $\Delta W - s^*/\theta_H = +3$. Pairing dual-signed session proofs with **Escrow-DKG Whistleblower Framing Bounties** traps colluding peers in a strict Prisoner's Dilemma:

#### Payoff Matrix 2: Peer A vs. Peer B Collusion & Whistleblower Framing Game

| Peer A \ Peer B | Honest Session & Private Diagnostic Signal | Collude (Phantom Check-In / Wash Loop) | Frame / Report Collusion Solicitation |
| :--- | :--- | :--- | :--- |
| **Honest Session & Private Signal** | **`(+10, +10)`** — Verified mastery & lineage growth. | **`(+10, +2)`** — Unilateral phantom claim fails dual-signature check. | **`(+10, +10)`** — Baseless challenge forfeits challenger bond. |
| **Collude (Phantom Wash Loop)** | **`(+2, +10)`** — Unilateral claim rejected. | **`(-6, -6)`** — Pairwise decay + zero downstream conversion triggers Oophagy slash. | **`(-12, +16)`** — Peer B defects, submits signed solicitation proof, and captures framing bounty. |
| **Frame / Report Collusion** | **`(+10, +10)`** — No illicit side-deal exists. | **`(+16, -12)`** — Peer A defects and claims framing bounty from B's slashed deposit. | **`(-8, -8)`** — Mutual simultaneous reporting forfeits both deposits. |

---

## 5. Cross-Hive Epoch FX & Duplex `PoUW-PoW` Security Equilibrium

### 5.1 Effective Backing Ratio Cross-Hive Exchange Rate (`ADR-0005`, `DEC-004`)

Once a migrating Pollinator earns **Accepted Status** in target Hive $H_B$, the once-per-epoch Comb-to-Comb exchange rate $\text{FX}_{A \to B}(e)$ is computed from each Hive's Effective Backing Ratio $R_{\text{eff}}(H_i) = \frac{S_{\text{comb}}(H_i)}{N_{\text{active}}(H_i) \cdot \widetilde{B}_{\text{active}}(H_i)} \cdot h_{\text{sardex}}(H_i)$ and clamped to `[0.5x, 2.0x]` with a `5%` source Comb toll:

$$\text{FX}_{A \to B}(e) = \min\!\left(2.0, \; \max\!\left(0.5, \; \left(\frac{R_{\text{eff}}(H_A, e)}{R_{\text{eff}}(H_B, e)}\right)^{\eta}\right)\right)$$

### 5.2 Transcript-Oracle `PoUW-PoW` Duplex Security Surplus (`ADR-0007`, `ball_2018`)

Under fine-grained Proof-of-Useful-Work (`ball_2018`) and transcript-oracle difficulty coupling (`federated_PoUW-PoW_blockchain_infrastructure.md`), a campus node evaluates a bounded useful transcript $\pi_{\text{pouw}}$ over the epoch's Knowledge Graph and Pairwise Decay matrix from deterministic seed $\sigma_t = H(\text{prev\_hash} \parallel \text{kg\_root})$:

$$H(\sigma_t \parallel \text{kg\_root} \parallel \pi_{\text{pouw}} \parallel \text{nonce}) < 2^{\ell} \cdot p$$

Let $W_{\text{pure}}$ denote pure hashing work, $U_{\text{off}}$ pure off-chain graph computation, and $D_{\text{duplex}}$ joint `PoUW-PoW` work with proving overhead $\epsilon_{\text{pouw}} \ll 1$. The duplex security surplus $\Delta_{\text{sec}} = S_{\text{total}} - W_{\text{wasted}}$ remains strictly positive ($\Delta_{\text{sec}} > 0$) whenever $\epsilon_{\text{pouw}}$ is bounded and task instances are bucketed into uniform difficulty bands, while compute rewards draw strictly from the capped **Comb Compute Jar** (`ADR-0007`) so consensus security never inflates `nectR` supply.
