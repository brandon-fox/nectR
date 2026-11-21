# Project Roadmap & Autonomous Development Milestones

## Milestone 1: Theoretical Foundation & `/grill-me` Specification
- [x] Run the 3 Gemini Deep Research prompts (`docs/planning/deep_research_prompts.md`) and archive the reports in [`docs/theory/research/`](../theory/research/federated_barter_tokenomics.md).
- [ ] Complete the interactive `/grill-me` session to lock down open equations in `docs/planning/decision_log.md`.
- [ ] Finalize the mathematical model in `docs/theory/tokenomics_game_theory.md` and `docs/theory/biomimicry_model.md`.

## Milestone 2: Private `PoUW-PoW` Blockchain, Smart Contracts & Service Layer
- [ ] Implement the `PoUW-PoW` consensus and block verification engine in `src/nectr/chain/`.
- [ ] Implement the 5 deterministic smart contracts in `src/nectr/contracts/`.
- [ ] Build the Hive Service Layer (Escrow, Graph Indexer, Queen Arbitration, Cross-Hive Bridge) in `src/nectr/services/`.
- [ ] Pass 100% of unit and economic invariant tests in `tests/`.

## Milestone 3: Behavioral Persona Swarm & Closed-Loop Experimentation
- [ ] Implement the 6 Persona Sub-Agents in `src/nectr/personas/`.
- [ ] Execute multi-semester Monte Carlo and adversarial collusion simulations in `experiments/`.
- [ ] Generate empirical telemetry datasets (velocity, Gini coefficient, collusion attenuation, Comb reserves).

## Milestone 4: Academic Paper, Business Proposals & Flagship Portfolio
- [ ] Compile the publication-ready manuscript in `paper/nectR_whitepaper.md`.
- [ ] Finalize the University Sponsorship & Swarming Business Proposal in `business/university_sponsorship_proposal.md`.
- [ ] Publish the System Design Portfolio architecture site via `uv run mkdocs build --strict`.
