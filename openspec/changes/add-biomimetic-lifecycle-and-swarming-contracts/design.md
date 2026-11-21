# Design: Biomimetic Lifecycle, Demurrage, Waggle/Tremble Routing & Reproductive Swarming (`add-biomimetic-lifecycle-and-swarming-contracts`)

## DDD Entities, Value Objects & State Machines
- **`DemurrageAccumulator` (Value Object):** Lazily computes idle-balance decay $B(t) = B(t_0) \cdot (1 - d)^{\Delta e}$ above `safety_cushion` during Weeks 1–13 (paused in Finals Weeks 14–15, `DEC-001`), crediting decayed units directly to `comb_reserve`.
- **`WaggleTrembleController` (Domain Service / FSM):**
  - *Waggle Surge:* Co-pays $60\%$ of the $2.2\times$ peak tutor payout from the Comb during Midterms (Weeks 5–6, 9–10) and Finals (Weeks 14–15) so learners pay $1.0\times\text{--}1.3\times$ (`DEC-002`).
  - *Tremble & Stop-Signals:* Computes $P_{\text{tremble}}(T_s) = \text{clip}((T_s - 20)/60, 0, 1)$ from rolling settlement queue wait time $T_s$ (Seeley & Tovey 1994) and applies cross-inhibitory stop-signals $\sigma_{j \to i}$ (`DEC-013`).
- **`QMPHealthAndSupersedureFSM` (Contract State Machine):**
  - Evaluates network-decayed QMP vector $\mathbf{Q}(v) = \mathbf{Q}_0 e^{-\lambda d(Q,v)} \cdot \Phi_{\text{brood}}$ and manages the epigenetic `RoyalJellyBitmask` (`DNMT3_CLEARED`, `HDAC3_CLEARED`, `UHRF1_LOCKED`) across Graceful Supersedure (1–3 slots, 1-epoch dual-coexistence) and 24-hour Emergency Succession (up to 27 candidate slots weighted toward recent high-velocity contributors).
- **`TemporalPolyethismGovernor` (Contract State Machine):**
  - Tracks progression across `LEARNER_BEE` $\to$ `CERTIFIED_WORKER_BEE` $\to$ `COMB_VALIDATOR_GUARD` $\to$ `SCOUT_POLLINATOR`, streaming Ethyl Oleate (`EO`) inhibition and activating the Khoury Precocious Promotion Circuit Breaker when Scout churn approaches $\mu_{\text{crit}}$ (Khoury et al. 2011).
- **`SwarmBivouacEscrow` (Aggregate Root):**
  - Activates `SWARM_PREP` when Comb congestion $\ge 90\%$, outer-cohort QMP $< \theta_{\text{swarm}}$, and tutor supply exceeds unmentored learner demand.
  - Locks 30–40 credit-unit Honey Engorgement stakes in Bivouac staging, evaluates Scout Waggle stakes and Reina et al. (2017) Contra Stop-Signals across candidate campuses, triggers a 1-hour Worker Piping Timelock upon reaching a 15-Scout (30%) quorum (Seeley & Visscher 2004), and burns a $6.25\times\text{--}8.0\times$ Honey-to-Wax infrastructure fee (`DEC-012`).

## Extended Protocol Invariants (`D-01` through `D-08`)
- **`D-01`–`D-05`:** Existing core invariants (No blind transfers, Queen separation of powers, Fee-to-Comb & supply conservation, Guard Bee Accepted Status + clamped epoch FX, Restricted `RAW_POLLEN` refinement).
- **`D-06` (Minimum Session Duration & Demurrage Safety Buffer):** No paid tutoring session $< 25$ minutes (`0.4167` hours, `DEC-011`); lazy demurrage never reduces a student's balance below `safety_cushion` and pauses during Finals epochs (`DEC-001`).
- **`D-07` (Khoury Collapse Protection):** When Scout attrition exceeds $\mu_{\text{crit}}$, `TemporalPolyethismGovernor` freezes Nurse-Tutor outbound promotion to preserve internal teaching capacity.
- **`D-08` (Swarm Quorum & Legacy Debt Isolation):** Daughter Hive genesis requires $\ge 15$ independent Scout attestations (or $30\%$ quorum) plus the $6.25\times\text{--}8.0\times$ Honey-to-Wax burn, while open disputes ("Varroa load") remain isolated in the Parent Hive.
