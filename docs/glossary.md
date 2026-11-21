# nectR Domain Glossary & Ubiquitous Language

Every term, economic equation, and honeybee (*Apis mellifera*) metaphor used across **nectR** code, specs, and academic manuscripts is defined below.

## Economic & Consensus Terms

- **`MV = PQ` (Fisher's Equation of Exchange):** Fundamental closed-economy balance where **M** is circulating token supply (`RAW_POLLEN` + `LIQUID_NECTR`), **V** is transaction velocity (turnovers per epoch), **P** is average session price, and **Q** is real tutoring hours delivered.
- **`PoUW-PoW` (Proof-of-Useful-Work + Proof-of-Work):** Hybrid consensus in `src/nectr/chain/` where campus nodes pair cryptographic SHA-256 block difficulty with a verifiable `UsefulComputeProof` committing the epoch's Knowledge Graph, Gini coefficient, and anti-collusion velocity matrix, paid strictly from a capped Comb Compute Jar (`ADR-0007`).
- **Demurrage:** A gentle, pre-programmed negative interest rate on stagnant idle balances above a protected student safety cushion during Weeks 1–13, routed back to the Hive **Comb** to deter early-semester hoarding and subsidize Finals Week tutoring (`DEC-001`).
- **Pairwise Discoordination:** Anti-collusion graph weighting (`1 / (1 + alpha * N_{u <-> v})`) that saturates repeated `A <-> B` roommate wash-trading while preserving full rewards for tutoring distinct classmates.
- **Spence Signalling (Downstream Mastery):** Replacing easily inflated public 5-star ratings with unforgeable downstream outcomes (whether a tutee subsequently passes mastery checks or teaches peers in the **Learn-then-Teach** cascade).

## Biomimetic Hive Entities & Token States

- **`RAW_POLLEN`:** Institutional seed voucher drawn from the **Comb**; restricted so it can ONLY be spent with a Queen-certified Worker Bee in a certified subject, converting into `LIQUID_NECTR` upon verified settlement (`ADR-0006`).
- **`LIQUID_NECTR`:** Unrestricted peer-to-peer currency created only when `RAW_POLLEN` is refined via verified tutoring, freely transferable through `DirectionalServiceBarterContract` handshakes (`ADR-0002`).
- **`ROYAL_COMB_RESERVE` (`Comb`):** Shared Hive treasury holding seed capital, 100% of Queen governance fees, certification stakes, bridge tolls, and demurrage inflows to fund surge bounties and compute rebates (`ADR-0004`).
- **`Beekeeper`:** Institutional/campus root authority holding transparent, on-chain logged emergency override ("God Mode") and bond-slashing powers over Hives (`ADR-0003`).
- **`Queen`:** Non-tutoring Hive administrator (Phase 1 Teacher-Queen or Phase 2 Veteran Student-Queen) who certifies Worker Bees, arbitrates disputes, tunes Hive defaults, and earns **Royal Jelly** incentives—cryptographically barred from tutoring for `nectR` (`ADR-0003`, `ADR-0004`).
- **`Certified Worker Bee`:** Student tutor accredited by a Queen in specific subjects; eligible to refine `RAW_POLLEN` into `LIQUID_NECTR`.
- **`Learner Bee`:** Student onboarding into the Hive with `RAW_POLLEN` vouchers who can progress into peer tutoring after verified mastery.
- **`Pollinator Visitor` & `Accepted Status`:** Visiting Bee migrating between Hives; locked home-Hive `nectR` cannot bridge until **Guard Bees** verify local tutoring contributions in the destination Hive (`ADR-0005`).
- **`Waggle` / `Tremble` Signals & `Swarming`:** Dynamic Comb surge co-pays during Finals demand spikes (`Waggle`), difficulty/fee throttling on congested cohorts (`Tremble`), and mature Hives spinning off daughter Hives (`Swarming`) (`DEC-002`, `ADR-0006`).
