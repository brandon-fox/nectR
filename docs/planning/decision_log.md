# Design Decision Log (`/grill-me` Tracker)

This file tracks finalized architectural decisions and open questions to be resolved during `/grill-me` design sessions.

## Finalized Decisions

| ID | Domain | Decision Summary | Status |
| :--- | :--- | :--- | :--- |
| **D-01** | Core Primitive | **Directional Service-Barter Handshake:** No blind token transfers exist. Every transaction records `Tutor -> Learner`, `Subject`, `Duration`, and `Attestation`, or 0-nectR direct skill barter. | Locked |
| **D-02** | Governance | **Queen Separation of Powers:** Queens manage the Hive (certify Workers, resolve disputes, manage Comb bounties) and are cryptographically blocked from tutoring for `nectR`. | Locked |
| **D-03** | Fee Model | **Zero-Fee P2P / Fee-to-Comb Governance:** Normal P2P tutoring is free. Fees are only charged when Queen/Hive services are used, and 100% flow into the Comb. | Locked |
| **D-04** | Cross-Hive Mobility | **Accepted Status Capital Control:** `nectR` lives in its home Hive until a visiting Bee earns Accepted Status in the host Hive via verified tutoring contribution. | Locked |
| **D-05** | Two-Phase Genesis | **Sponsored Seeding $\rightarrow$ Organic Swarming:** Schools seed initial Combs with Teacher-Queens and Certified Workers (`RAW_POLLEN` $\rightarrow$ `LIQUID_NECTR`). Mature Hives spawn daughter Hives led by veteran Bees turned Queens. | Locked |

---

## Open Questions for Next `/grill-me` Session

1. **Q-01 (`PoUW-PoW` Mining Incentives):** Should student/dorm nodes that contribute distributed compute and PoW mining earn rewards from a dedicated Comb Compute Pool (or earn accelerated Accepted/Worker Status), or is block production restricted to Certified Worker & Queen nodes?
2. **Q-02 (Royal Jelly Queen Dividend Formula):** What exact formula governs the Queen's epoch payout from the Comb (e.g., $\text{Dividend} = \beta \cdot \Delta \text{Comb} \cdot \text{VelocityDiversityIndex}$), and how do Teacher-Queens in Phase 1 vs. Student-Turned-Queens in Phase 2 differ?
3. **Q-03 (Senior Graduation & Hoarding Sinks):** How do graduating seniors off-ramp or utilize accumulated `nectR` so upperclassmen stay motivated to tutor freshmen right up to graduation (e.g., staking `nectR` to swarm a new Hive, tuition/bookstore Comb buybacks, or on-chain honors credentials)?
4. **Q-04 (Comb-to-Comb Cross-Hive Exchange Rate):** Should cross-hive transfers use an Automated Market Maker (AMM) ratio based on each Hive's $\text{CombReserve} / \text{ActiveBees}$, or a parity peg weighted by Hive Effectiveness Scores?
