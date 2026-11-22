# Design: Authority Hardening, Micro-Unit Accounting, and Escrow/Bridge Guards

## Bounded Context Impact

- **Smart Contracts Context (`src/nectr/contracts/engine.py`):**
  - Replace internal floating-point arithmetic with exact integer fixed-point micro-units (`1 nectR = 1_000_000` micro-units) and exact `==` conservation in `assert_supply_conservation()`.
  - Add explicit dispute state (`dispute_session`) prior to `resolve_disputed_session`, cap `service_fee_rate < 1.0`, and add `cancel_expired_escrow` returning 100% of `escrowed_amount` in original `token_state` after expiry.
  - Require explicit `home_hive_id` (or non-accepting visitor registration) so foreign Bees cannot obtain host-Hive `Accepted Status` without meeting `accepted_status_peer_threshold`.
- **Hive Service & Persistence Context (`src/nectr/services/`):**
  - Schema migration `0002` for integer micro-unit columns and `bee_keys` key-registry persistence.
  - Enforce `SignedTransaction` verification (Ed25519 signature, registered key, `hive_id`, monotonic `nonce`), bootstrap-only `QUEEN` role assignment, dual-signed settlement, and signed cross-hive bridging.
  - Expose `dispute_session` and `cancel_expired_escrow` service and FastAPI endpoints.
  - Compute collusion-discounted velocity per epoch (rather than cumulatively across all history) when accruing `royal_jelly_earned`.
- **Consensus & Ledger Context (`src/nectr/chain/`):**
  - Restrict `HiveBlockchain.submit_transaction()` to verified `SignedTransaction` instances.
  - Persist `hive_blocks` append-only with `block_hash`, run `verify_chain()` on load raising `ChainIntegrityError` naming the corrupted height, and default `difficulty=0`.

## Key Architectural Decisions & Known Limits

1. **Integer Micro-Unit Conservation (`D3=yes`):** All balances, reserves, escrows, fees, and bridge tolls use exact integer micro-units so `comb_reserve + sum(pollen) + sum(liquid) + sum(escrow) == total_minted_supply` holds with `==` and zero tolerance across arbitrary iterations.
2. **Bootstrap-Only Queen Appointment (`D1=yes`):** In `v0.1`, `BeeRole.QUEEN` accounts are provisioned exclusively during `bootstrap_sponsored_hive`; self-signed `register_bee` commands can only register `BeeRole.LEARNER_BEE`.
3. **Append-Only Blocks with `difficulty=0` Default (`D2=A`):** `hive_blocks` are stored append-only and verified on repository load via `verify_chain()`, retaining the `difficulty` parameter name with default `0`.
4. **Cross-Hive Bridge Supply Boundary (`D4=C`):** Guard Bee foreign registration never auto-grants host acceptance. Known limit: target-hive `LIQUID_NECTR` minted by a bridge is backed by cross-hive supply accounting and has no direct Comb backing in the target Hive.
