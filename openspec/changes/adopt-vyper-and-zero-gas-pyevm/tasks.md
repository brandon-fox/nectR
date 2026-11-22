# Tasks: `adopt-vyper-and-zero-gas-pyevm`

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

- [ ] 1. **Dependencies & License Audit:** Add `vyper`, `eth-tester`, `py-evm`, `web3`, and `eth-account` to `pyproject.toml`; run `pip-licenses` and `pip-audit` to confirm 100% MIT/Apache/BSD compliance.
- [ ] 2. **Phase 1 — RED:** Add Vyper `py-evm` `micro_nectr` conservation, EIP-712 co-signing, and `evm_state_root` commitment scenarios to `features/protocol_invariants.feature` and `@pytest.mark.xfail(strict=True)` tests in `tests/test_vyper_contracts.py`; commit `test(contracts): ...`.
- [ ] 3. **Phase 2 — GREEN:** Author the 5 `.vy` contracts (`TokenStateAndComb.vy`, `DirectionalServiceBarter.vy`, `QueenGovernance.vy`, `KnowledgeGraphAndPolicing.vy`, `GuardBeeCrossHiveBridge.vy`) and zero-gas `py-evm` adapter in `src/nectr/contracts/`; observe `XPASS(strict)`, remove `xfail` and `@red`, verify `pytest` and `behave` exit `0`; commit `feat(contracts): ...`.
- [ ] 4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict` and changed-line mutation score (`>= 85%`), promote spec delta into `openspec/specs/protocol-invariants/spec.md`, and archive change.
