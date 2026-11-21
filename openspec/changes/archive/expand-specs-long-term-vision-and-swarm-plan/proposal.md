# Proposal: Synthesize 6 Deep Research Tracks, Expand Specs, and Plan Long-Term Vision & Swarm Roadmap (`expand-specs-long-term-vision-and-swarm-plan`)

## Why
Three new foundational Deep Research reports have been added to `docs/theory/research/`:
1. `permissive_tooling_survey_for_nectR.md` (Prompt 4: Permissively Licensed Cryptographic, Formal Verification, ABM/Graph & Supply-Chain Tooling)
2. `federated_PoUW-PoW_blockchain_infrastructure.md` (Prompt 5: Federated NATS Leaf Node Proof Relay, Deterministic Storage, CQRS Graph Isolation, Transcript-Oracle PoUW-PoW & Kurtosis/Pumba Chaos Testbeds)
3. `nectR_funding_and_pilot_strategy.md` (Prompt 6: Non-Dilutive Academic/DPG Grant Strategy, FERPA/GDPR Zero-PII Hybrid Architecture, IRS/Title IV Service-Credit Firewall, LTI 1.3/Shibboleth/HECVAT 4.1.6 & Apereo Foundation Incubation)

To translate all 6 Deep Research reports into actionable engineering and research specifications while keeping all repository governance gates green, we need to:
- Register all 6 Deep Research reports in `mkdocs.yml`, `docs/planning/deep_research_prompts.md`, `docs/index.md`, and `paper/README.md` (resolving orphan page drift).
- Expand `paper/references.yaml` and `paper/lineage.yaml` with primary peer-reviewed citations across all 6 research tracks and regenerate `docs/theory/provenance_lineage.md`.
- Record structural architectural decisions (`ADR-0014`, `ADR-0015`) via `adrlint` and operational/experimental rules (`DEC-011`–`DEC-015`, `EXP-002`–`EXP-005`) via `nectr-decisions`.
- Expand the core theory, architecture, business, experiment, and canonical OpenSpec specifications (`docs/theory/*`, `docs/architecture/*`, `docs/business/*`, `docs/experiments/*`, `openspec/specs/*`, `openspec/changes/*`).
- Author future OpenSpec change proposals (`add-biomimetic-lifecycle-and-swarming-contracts`, `add-nats-jetstream-cross-hive-federation`, `add-campus-compliance-lti-and-zk-identity`) and define the 3-Horizon Long-Term Roadmap and 5-Wave Multi-Agent Swarm & `/teamwork` Build Plan in `docs/planning/roadmap.md` and `docs/planning/agent_orchestration.md`.

## Bounded Contexts & Paths Affected
- `docs/planning/` (`roadmap.md`, `agent_orchestration.md`, `deep_research_prompts.md`, `decisions.yaml`, `decision_log.md`)
- `docs/adr/` (`0014-adopt-nats-leaf-nodes-jetstream-and-cqrs-graph-isolation.md`, `0015-enforce-zero-pii-ferpa-gdpr-and-title-iv-campus-compliance.md`, `index.md`, `adrlint.lock`)
- `docs/theory/` (`biomimicry_model.md`, `tokenomics_game_theory.md`, `whitepaper_outline.md`, `provenance_lineage.md`)
- `docs/architecture/` (`system_design.md`, `smart_contracts.md`)
- `docs/business/institutional_proposal.md`, `docs/experiments/persona_swarm_spec.md`, `docs/glossary.md`, `docs/index.md`
- `paper/` (`README.md`, `references.yaml`, `lineage.yaml`), `mkdocs.yml`
- `openspec/specs/` and `openspec/changes/`
- `features/` and `tests/`
