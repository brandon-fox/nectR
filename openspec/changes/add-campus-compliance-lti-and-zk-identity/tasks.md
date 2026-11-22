# Tasks: `add-campus-compliance-lti-and-zk-identity`

> **DEFERRED:** This change proposal is out of scope for current work under the Plan to B+ and is deferred until after the v0.1.0 release.

- [ ] 1. **Compliance & Schema Gate:** Define `CampusIdentityPort`, `ZeroPiiCommitmentGuard`, and `TitleIvComplianceFirewall` protocols in `src/nectr/services/`; verify zero copyleft dependencies.
- [ ] 2. **Phase 1 — RED:** Add zero-PII FERPA/GDPR erasure, LTI 1.3 roster mapping, and Title IV firewall scenarios to `features/hive_persistence_api.feature` and `features/steps/hive_persistence_api_steps.py`; add `@pytest.mark.xfail(strict=True)` tests in `tests/test_hive_persistence_api.py`; commit `test(services): add RED tests for FERPA zero-PII guard and Title IV compliance firewall`.
- [ ] 3. **Phase 2 — GREEN:** Implement `ZeroPiiCommitmentGuard`, `CampusIdentityPort`, `TitleIvComplianceFirewall`, and HECVAT 4.1.6 / DCO 1.1 documentation templates in `src/nectr/services/` and `business/`; observe `XPASS(strict)`, remove `xfail` and `@red`, verify `pytest` and `behave` exit `0`; commit `feat(services): implement zero-PII FERPA/GDPR guard, LTI 1.3 port, and Title IV firewall`.
- [ ] 4. **Phase 3 — REFACTOR & Archive:** Verify `mypy --strict`, merge delta spec into `openspec/specs/`, and archive change.
