# Proposal: Expand 5 Deterministic Smart Contracts with Phase 2 Biomimetic Lifecycle & Swarming (`add-biomimetic-lifecycle-and-swarming-contracts`)

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

## Why
Following **Swarm Wave 2B-1 (`adopt-vyper-and-zero-gas-pyevm`, `ADR-0017`)** — which migrates baseline `D-01`–`D-06` state transitions (`uint256` `micro_nectr`, `0..10,000 bps` direct learner attestations, lazy demurrage `DEC-001`, Waggle `60%` co-pay `DEC-002`, `25-minute` minimum block `DEC-011`, and 3-door Senior sinks `DEC-004`) onto 5 `vyper` (`Apache-2.0`) `.vy` smart contracts running on zero-gas-price `eth-tester[py-evm]` + `web3.py` (`MIT`) — **Swarm Wave 2B-2 (`add-biomimetic-lifecycle-and-swarming-contracts`)** extends those `.vy` contracts to encode the full colony lifecycle established in `biomimetic_hive_economics.md`, `federated_barter_tokenomics.md`, and `student_tutoring_mechanism_design.md`:
1. **Lazy Demurrage & Student Safety Cushion (`DEC-001`):** ~2%/month lazy decay on idle `LIQUID_NECTR` above a protected buffer during Weeks 1–13, paused during Finals (Weeks 14–15), routed 100% into the Comb.
2. **Waggle Surge Co-Pay (`DEC-002`), Tremble Latency Ramp & Stop-Signals (`DEC-013`):** 60% Comb co-pay of 2.2x peak Midterm/Finals tutor payouts, linear Tremble fee reallocation as validation queue latency climbs from $\tau_{\text{low}}=20\text{s}$ to $\tau_{\text{high}}=80\text{s}$, and cross-inhibitory Stop-Signals ($\sigma_{j \to i}$).
3. **Polyandrous Oophagy Fraud Proofs & Escrow-DKG Whistleblower Framing Bounties:** Permissionless challenge/slashing of unverified claims and framing bounties that destabilize Queen-tutor bribery and roommate phantom rings.
4. **Network-Decayed QMP Health Index, Epigenetic Royal Jelly Bitmask & Supersedure vs. 24h Emergency Election:** Graph-hop decayed QMP gated by Brood Synergy (active freshman onboarding), DNMT3/HDAC3/UHRF1 permission bitmask, Graceful Supersedure dual-coexistence epoch, and 24-hour Emergency Succession favoring `<24h larval window` high-velocity contributors.
5. **Temporal Polyethism, Ethyl Oleate (EO) Inhibition & Khoury Precocious Promotion Circuit Breaker (`DEC-013`):** Learner $\to$ Certified Worker Tutor $\to$ Comb Validator/Guard $\to$ Scout lifecycle regulated by EO social inhibition and a circuit breaker clamping Tutor-to-Scout promotion when churn approaches critical mortality $\mu_{\text{crit}}$.
6. **3-Door Senior Graduation Sinks (`DEC-004`) & Reproductive Swarming Bivouac Escrow (`DEC-012`):** 40% Credentials/Swarming, 35% Campus Perks, 25% Freshman Pay-It-Forward + dormant alumni Comb sweeps; composite `SWARM_PREP` trigger ($\ge 90\%$ Comb congestion + QMP attenuation + tutor surplus), 6.25x–8.0x Honey-to-Wax deployment burn, Reina et al. contra stop-signals, and 15-Scout (30%) Quorum Sensing with 1-hour Worker Piping Timelock.

## Affected Bounded Contexts
- **Smart Contracts Context (`src/nectr/contracts/`)** — primary target (`vyper` `.vy` modules + typed Python adapter over zero-gas `py-evm`).
- **Architectural Decisions:** [ADR-0002](../../../docs/adr/0002-enforce-directional-service-barter-state-transitions.md), [ADR-0003](../../../docs/adr/0003-enforce-multi-tier-beekeeper-and-queen-governance.md), [ADR-0004](../../../docs/adr/0004-route-governance-fees-to-comb-with-phase-split-royal-jelly.md), [ADR-0005](../../../docs/adr/0005-gate-cross-hive-bridges-with-guard-bee-status-and-epoch-fx.md), [ADR-0006](../../../docs/adr/0006-adopt-two-phase-hive-genesis-and-autonomous-swarming.md), [ADR-0017](../../../docs/adr/0017-adopt-vyper-and-zero-gas-py-evm-smart-contracts.md).

## OSS License & CVE Audit
| Package / Tool | License | Status | Notes |
| --- | --- | --- | --- |
| `vyper` + `eth-tester[py-evm]` + `web3` | `Apache-2.0` / `MIT` | **Approved** | Zero-gas-price Pythonic Ethereum EVM execution (`ADR-0017`, `uint256` `micro_nectr` `DEC-017`) |
| `icontract` | `MIT` | **Approved** | Design-by-Contract (`@require`, `@ensure`, `@invariant`) decorators on typed Python boundary |
| `hypothesis` | `MPL-2.0` | **Approved** | Stateful property-based invariant fuzzing (`RuleBasedStateMachine`) |
| `quint` (Informal Systems) | `Apache-2.0` | **Approved** | External TLA+ / Apalache formal verification CLI (`specs/quint/`) |

## Acceptance Criteria
1. All contract state transitions remain pure, deterministic functions of `(current_state, signed_tx, block_context)` with zero external oracle or wall-clock calls.
2. `icontract` class invariants and `assert_supply_conservation()` enforce strict closed-loop token accounting across `RAW_POLLEN`, `LIQUID_NECTR`, `ROYAL_COMB_RESERVE`, `EscrowLocked`, and `BivouacStaged`.
3. Every session enforces a minimum duration of 25 minutes (`DEC-011`) to prevent Gneezy-Rustichini micro-payment crowding out.
