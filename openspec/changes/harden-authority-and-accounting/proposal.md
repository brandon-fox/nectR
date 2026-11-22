# Proposal: Harden Authority, Cryptographic Signing, and Deterministic Accounting

## Problem Statement

An adversarial architecture and accounting review of the `nectR` smart contracts, service layer, persistence, and consensus ledger identified five high-severity soundness gaps:

1. **Unauthenticated Role & Write Commands (Finding 1):** `HiveServiceLayer.register_bee(..., role=BeeRole.QUEEN)` and mutating service/API/chain entry points accept unsigned actor IDs, permitting arbitrary self-promotion to `QUEEN` or forged tutoring/arbitration calls.
2. **Floating-Point Rounding Drift in Supply Conservation (Finding 3):** `HiveContractEngine` stores balances and executes `round(..., 6)` arithmetic on IEEE-754 `float` values with a `1e-4` tolerance in `assert_supply_conservation()`, allowing cumulative rounding drift across repeated `RAW_POLLEN` allocations and dispute settlements.
3. **Unintended Host-Hive Auto-Acceptance on Foreign Registration (Finding 4):** Registering a migrating Bee in a target Hive without an explicit `home_hive_id` defaults `origin` to the target Hive and immediately adds the target Hive to `accepted_in_hives`, bypassing the Guard Bee peer-tutoring threshold.
4. **Unilateral Queen Arbitrage & 100% Fee Extraction on Undisputed Escrow (Finding 5a):** `resolve_disputed_session()` allows a `QUEEN` to arbitrate any `INTENT_ESCROWED` session without a prior dispute transition and permits `service_fee_rate = 1.0`, draining 100% of escrowed learner/tutor funds into `comb_reserve`.
5. **Missing Escrow Expiry & Learner Cancellation Path (Finding 5b):** An `INTENT_ESCROWED` session has no expiration horizon or learner-initiated cancellation path, allowing locked funds to remain stranded indefinitely when a tutor disappears.

## Motivation & Goals

- Bind every Bee identity to an Ed25519 public key and monotonic nonce, restrict `QUEEN` appointment to Hive bootstrap, and enforce signed commands across `HiveServiceLayer`, FastAPI routes, and `HiveBlockchain`.
- Eliminate floating-point drift by migrating `HiveContractEngine` and persistence accounting to exact integer fixed-point micro-units (`10^-6` micro-nectR) with exact `==` supply conservation.
- Require an explicit dispute state before Queen arbitration, bound `service_fee_rate < 1.0`, and support deterministic epoch-based escrow expiry cancellation returning full funds in their original `TokenState`.
- Enforce strict Guard Bee `Accepted Status` gating so registering in a host Hive never auto-grants acceptance without verified peer tutoring.
- Make persisted `hive_blocks` append-only and verify chain integrity on repository load.

## Scope

- **OpenSpec & Strict-RED Baseline (`CA1`):** Author this OpenSpec change and add 5 strict `@pytest.mark.xfail(strict=True)` regression tests covering Findings 1, 3, 4, 5a, and 5b.
- **Contracts & Accounting Track (`CA2`–`CA5`):** Micro-unit fixed-point accounting + Alembic migration `0002`, dispute/expiry escrow FSM, Guard Bee foreign acceptance hardening, and end-to-end invariant/BDD verification.
- **Services, Signing & Chain Track (`CB1`–`CB4`):** Ed25519 key registry (`bee_keys`) + signed command enforcement, dispute/cancel service & API commands, append-only `hive_blocks` with `verify_chain()` on load, and per-epoch velocity/Royal Jelly accrual.
