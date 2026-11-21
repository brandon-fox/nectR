# Tasks: `adopt-ed25519-and-pymerkle`

1. **Dependencies & License Gate:** Add `cryptography`, `canonicaljson`, and `merklelib` to `pyproject.toml`; run `pip-licenses` and `pip-audit`.
2. **Phase 1 — RED:** Expand `features/chain_crypto_ledger.feature` and `features/steps/chain_crypto_ledger_steps.py`; add `xfail(strict=True)` unit tests in `tests/test_chain_crypto.py`; commit `test(chain): ...`.
3. **Phase 2 — GREEN:** Implement `canonicaljson`, Ed25519, and `merklelib` adapters in `src/nectr/chain/`; remove `@red` and `xfail`; verify `pytest` and `behave` pass; commit `feat(chain): ...`.
4. **Phase 3 — REFACTOR & Archive:** Refine types for `mypy --strict`, merge `specs/chain-crypto-ledger/spec.md` into `openspec/specs/`, and archive this change.
