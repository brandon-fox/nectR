# Tasks: `lock-vyper-pactflow-and-grill-me-decisions`

- [x] 1. **Phase 1 — RED (OpenSpec + BDD + Strict TDD):**
  - [x] Author `openspec/changes/lock-vyper-pactflow-and-grill-me-decisions/` (`proposal.md`, `design.md`, `tasks.md`, `specs/decision-governance/spec.md`).
  - [x] Add `@red` Gherkin scenario in `features/decision_governance.feature` and step definitions in `features/steps/decision_governance_steps.py`.
  - [x] Add `@pytest.mark.xfail(strict=True)` test in `tests/test_decision_governance.py` asserting `ADR-0017`, `ADR-0018`, `DEC-017`–`DEC-020`, OpenSpec proposals (`adopt-vyper-and-zero-gas-pyevm`, `add-pactflow-api-and-message-contracts`), and JASSS `ODD+D` / NSF DRMS framing.
  - [x] Verify `pytest` exits `0` (`xfailed`) and `behave --tags=-red` passes; commit atomically (`test(governance): ...`).
- [x] 2. **Phase 2 — GREEN (ADRs, Decisions, OpenSpec Proposals & Docs):**
  - [x] Author and `adrlint`-lock `ADR-0017` and `ADR-0018`; add `DEC-017`–`DEC-020` to `docs/planning/decisions.yaml` and run `nectr-decisions render`.
  - [x] Author `openspec/changes/adopt-vyper-and-zero-gas-pyevm/` and `openspec/changes/add-pactflow-api-and-message-contracts/`, and update `add-biomimetic-lifecycle-and-swarming-contracts` and `add-sqlmodel-persistence-and-api`.
  - [x] Update `roadmap.md`, `agent_orchestration.md`, `smart_contracts.md`, `system_design.md`, `whitepaper_outline.md`, `persona_swarm_spec.md`, `institutional_proposal.md`, and `glossary.md`; run `nectr-docs sync`.
  - [x] Run `pytest` to confirm `XPASS(strict)` failure, remove `@pytest.mark.xfail` and `@red`, verify all gates exit `0`, and commit atomically (`feat(governance): ...`).
- [x] 3. **Phase 3 — Promote & Archive:**
  - [x] Promote delta requirements into `openspec/specs/decision-governance/spec.md`, archive this change under `openspec/changes/archive/`, re-verify all CI/parity gates, and commit atomically (`docs(spec): ...`).
