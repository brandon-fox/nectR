# Tasks: `expand-specs-long-term-vision-and-swarm-plan`

- [ ] 1. **OpenSpec Blueprint & Future Change Specs:**
  - [ ] Author `openspec/changes/expand-specs-long-term-vision-and-swarm-plan/` (`proposal.md`, `design.md`, `tasks.md`, and delta specs).
  - [ ] Expand active OpenSpec proposals (`adopt-ed25519-and-pymerkle`, `add-sqlmodel-persistence-and-api`, `adopt-mesa-abm-and-hypothesis`, `add-telemetry-dashboard-ui`).
  - [ ] Author new future OpenSpec proposals (`add-biomimetic-lifecycle-and-swarming-contracts`, `add-nats-jetstream-cross-hive-federation`, `add-campus-compliance-lti-and-zk-identity`) linked to Behave features.
- [ ] 2. **Phase 1 — RED (BDD + Strict TDD):**
  - [ ] Add Gherkin acceptance scenarios in `features/protocol_invariants.feature`, `features/docs_and_hygiene.feature`, `features/decision_governance.feature`, and `features/citation_provenance.feature`.
  - [ ] Add `@pytest.mark.xfail(strict=True)` tests in `tests/` verifying 6-report research integration, expanded protocol invariant BDD coverage (`D-01`–`D-05`), `ADR-0014`/`ADR-0015`, `DEC-011`–`DEC-015`, `EXP-002`–`EXP-005`, and expanded citation lineage.
- [ ] 3. **Phase 2 — GREEN (Research Synthesis, ADRs, Decisions, Docs & Roadmap):**
  - [ ] Create and lock `ADR-0014` and `ADR-0015` via `adrlint`, add `DEC-011`–`DEC-015` and `EXP-002`–`EXP-005` to `docs/planning/decisions.yaml`, and render `docs/planning/decision_log.md`.
  - [ ] Expand `paper/references.yaml` and `paper/lineage.yaml` with primary sources from all 6 Deep Research tracks and render `docs/theory/provenance_lineage.md`.
  - [ ] Expand `docs/theory/biomimicry_model.md`, `docs/theory/tokenomics_game_theory.md`, `docs/theory/whitepaper_outline.md`, `docs/architecture/system_design.md`, `docs/architecture/smart_contracts.md`, `docs/business/institutional_proposal.md`, `docs/experiments/persona_swarm_spec.md`, `docs/glossary.md`, `docs/planning/deep_research_prompts.md`, `docs/planning/roadmap.md`, and `docs/planning/agent_orchestration.md`.
  - [ ] Sync `mkdocs.yml`, `README.md`, and `docs/adr/index.md` via `nectr-docs sync`.
  - [ ] Observe `XPASS(strict)` on `pytest`, remove `@pytest.mark.xfail`, and verify `pytest`, `behave`, `adrlint`, `nectr-decisions`, `nectr-citations`, `nectr-docs`, `spec_links`, `pymarkdown`, `mypy --strict`, and `mkdocs build --strict` all exit `0`.
- [ ] 4. **Phase 3 — REFACTOR & Promote Canonical Specs:**
  - [ ] Promote canonical spec expansions into `openspec/specs/` and verify all quality gates pass 100%.
