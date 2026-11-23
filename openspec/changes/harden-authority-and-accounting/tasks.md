# Tasks: Harden Authority, Cryptographic Signing, and Deterministic Accounting

- [x] CA1: Author `openspec/changes/harden-authority-and-accounting/` and add 5 strict `xfail` tests for review findings 1, 3, 4, 5a, and 5b (`tests/test_services.py`, `tests/test_contracts.py`).
- [x] CA2: Migrate `HiveContractEngine` and persistence schema (`0002`) to exact integer micro-unit accounting (`10^-6` micro-nectR) with zero-tolerance `==` supply conservation (fixes Finding 3).
- [x] CA3: Enforce explicit dispute transitions, `service_fee_rate < 1.0`, and epoch-expiry learner escrow cancellation returning original `TokenState` (fixes Findings 5a & 5b).
- [ ] CA4: Harden Guard Bee cross-hive registration so foreign Bees cannot obtain host-Hive `Accepted Status` without tutoring peers (fixes Finding 4; documents bridge target Comb-backing limit).
- [ ] CA5: Complete protocol invariant tests, Hypothesis stateful checks, telemetry checks, and Behave BDD scenarios for hardened authority and accounting.
- [ ] CB1: Add `bee_keys` registry, `SignedTransaction` verification across `HiveServiceLayer`/`HiveBlockchain`/FastAPI, bootstrap-only `QUEEN` role binding, dual-signed settlement, signed bridge, and deterministic simulator signing (fixes Finding 1).
- [ ] CB2: Expose `dispute_session` and `cancel_expired_escrow` commands in `HiveServiceLayer` and FastAPI endpoints (depends on CA3 & CB1).
- [ ] CB3: Make `hive_blocks` append-only with persisted `block_hash`, `verify_chain()` on load raising `ChainIntegrityError` on bad height, and default `difficulty=0` (depends on CB2).
- [ ] CB4: Compute collusion-discounted velocity per epoch and accrue Queen Royal Jelly accurately (depends on CB3 & CA4).
