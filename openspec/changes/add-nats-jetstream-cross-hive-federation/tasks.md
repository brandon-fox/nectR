# Tasks: `add-nats-jetstream-cross-hive-federation`

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

- [ ] 1. **Dependencies & License Gate:** Add `nats-py` to `pyproject.toml` (optional `federation` extra); verify `pip-licenses` and `pip-audit`.
- [ ] 2. **Phase 1 — RED:** Add cross-Hive NATS JetStream relay and CQRS graph projection scenarios to `features/hive_persistence_api.feature` and `features/steps/hive_persistence_api_steps.py`; add `@pytest.mark.xfail(strict=True)` tests in `tests/test_hive_persistence_api.py`; commit `test(services): add RED tests for NATS JetStream federation and CQRS projector`.
- [ ] 3. **Phase 2 — GREEN:** Implement `CrossHiveBridgePort`, `NatsJetStreamBridgeAdapter`, `CQRSKnowledgeGraphProjector`, and Kurtosis/Toxiproxy `EXP-005` harness; observe `XPASS(strict)`, remove `xfail` and `@red`, verify `pytest` and `behave` exit `0`; commit `feat(services): implement NATS JetStream cross-Hive federation and CQRS graph read model`.
- [ ] 4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge delta spec into `openspec/specs/`, and archive change.
