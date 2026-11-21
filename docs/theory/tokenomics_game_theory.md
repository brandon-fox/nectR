# Tokenomics & Game Theory Specification

## 1. Conservation of Closed-Loop Supply
Within any single Hive $H_i$ at block height $t$:

$$M_{H_i}(t) = S_{\text{comb}}(t) + \sum_{u \in V} B_{\text{pollen}}(u, t) + \sum_{u \in V} B_{\text{nectR}}(u, t) + E_{\text{locked}}(t)$$

Normal peer-to-peer tutoring sessions are strictly zero-sum transfers of $B_{\text{nectR}}$ with zero protocol fee, preventing inflationary minting via collusion.

## 2. Pairwise Anti-Collusion Effectiveness Decay
When Tutor $u$ and Learner $v$ co-sign a `DirectionalServiceBarterTx` in subject $s$, the effective reputation and lineage weight $W(u, v, s)$ decays exponentially with the count of reciprocal or repeated closed-loop exchanges $N_{u \leftrightarrow v}$ within trailing window $\tau$:

$$W(u, v, s) = \frac{\text{Attestation}(v \to u)}{1 + \alpha \cdot N_{u \leftrightarrow v}(\tau)} \cdot \left(1 + \gamma \cdot L_{\text{downstream}}(v, s)\right)$$

where $L_{\text{downstream}}(v, s)$ measures whether Learner $v$ subsequently succeeds in tutoring downstream peers in subject $s$ (**Learn-then-Teach Lineage**).

## 3. Non-Tutoring Queen Payoff Function
Queens collect $0\%$ directly from fees. All Queen service fees ($F_{\text{cert}}, F_{\text{dispute}}, F_{\text{bridge}}$) flow into the Comb $S_{\text{comb}}$. At each epoch $e$, the Queen's Royal Jelly dividend $R_Q(e)$ is:

$$R_Q(e) = \beta \cdot \Delta S_{\text{comb}}^+(e) \cdot \mathcal{V}_{\text{graph}}(e) \cdot (1 - \text{Gini}(e))$$

where $\mathcal{V}_{\text{graph}}(e)$ is the collusion-discounted transaction velocity across distinct network components.
