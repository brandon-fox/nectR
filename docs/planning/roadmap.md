# Project Roadmap & Autonomous Development Milestones

## Milestone 0: Open-Source Hygiene, Governance & Automated Remediation
- [x] **Security, Secret & Local-Path Hygiene:** Configured `detect-secrets` (`.secrets.baseline`), `pygrep`/hook local-path guards, `.githooks/` (`pre-commit`, `commit-msg`, `pre-push`), and `.pre-commit-config.yaml`.
- [x] **Open-Source-First & Transitive License Audit:** Enforced permissive-license-only rule and scheduled `pip-licenses` + `pip-audit` + CycloneDX SBOM (`.github/workflows/license-and-security-scan.yml`) + Dependabot (`.github/dependabot.yml`).
- [x] **OpenSpec + Behave BDD + Strict TDD (`xfail_strict`) + `pyadr` Governance:** Enforced `nectr.devtools.decisions check` (`pyadr` MADR + `decisions.yaml`), `nectr.devtools.spec_links` (no hardcoded scenarios in `spec.md`), `commitizen` (`cz check` / `cz changelog`), and `.github/workflows/roadmap-and-changelog.yml`.
- [ ] **Phase 2 (Automated Issue Creation on License Drift/Flag):** Open/deduplicate labeled GitHub Issues (`license-violation`, `cve-alert`) via `actions/github-script` when scheduled scans fail.
- [ ] **Phase 3 (Downstream Agent Auto-Remediation):** Trigger downstream agent PR workflow on `license-violation` issues under strict OpenSpec → BDD → TDD gates.
- [ ] **Repo Normalization & `.gitattributes` ([#8](https://github.com/brandon-fox/nectR/issues/8)):** Enforce LF line endings, `ruff format --check`, and Markdown linting (`pymarkdownlnt`/`mdformat`) in pre-commit & CI before legacy diffs accumulate.
- [ ] **`pyadr` Fork/Remediation & Persona Dependency Split ([#6](https://github.com/brandon-fox/nectR/issues/6), [#10](https://github.com/brandon-fox/nectR/issues/10)):** Fork/replace `pyadr` to drop `cleo 0.8.1` (`PYSEC-2022-43178`) and `text-unidecode`, and split `pyproject.toml` `dev` extras by user persona (`test`, `lint`, `docs`, `research`, `ui`).
- [ ] **Git Tracking & `pyadr` Workflow Polish ([#5](https://github.com/brandon-fox/nectR/issues/5), [#11](https://github.com/brandon-fox/nectR/issues/11)):** Untrack `HANDOFF.md` (`git rm --cached`) so `.gitignore` applies, support `--allow-proposed` ADR checks on branches, and document `.adr` config & `proposed` status buckets.

## Milestone 1: Theoretical Foundation & `/grill-me` Specification
- [x] Run the 3 Gemini Deep Research prompts (`docs/planning/deep_research_prompts.md`) and archive the reports in [`docs/theory/research/`](../theory/research/federated_barter_tokenomics.md).
- [x] Complete the interactive `/grill-me` session to lock down open equations in `docs/planning/decision_log.md` and `docs/adr/`.
- [ ] **Citation Validation & Provenance Chain-of-Custody ([#7](https://github.com/brandon-fox/nectR/issues/7)):** Build `paper/references.yaml` + automated link/DOI/source-tier floor checks (banning AI-wikis, Reddit, SEO blogs, plagiarism archives) and lineage tracking (Sources → Equations → ADRs → Code) with automated downstream regeneration.
- [ ] Finalize the mathematical model in `docs/theory/tokenomics_game_theory.md` and `docs/theory/biomimicry_model.md`.

## Milestone 2: Private `PoUW-PoW` Blockchain, Smart Contracts & Service Layer
- [ ] Implement the `PoUW-PoW` consensus and block verification engine in `src/nectr/chain/`.
- [ ] Implement the 5 deterministic smart contracts in `src/nectr/contracts/`.
- [ ] Build the Hive Service Layer (Escrow, Graph Indexer, Queen Arbitration, Cross-Hive Bridge) in `src/nectr/services/`.
- [ ] Pass 100% of unit and economic invariant tests in `tests/`.

## Milestone 3: Behavioral Persona Swarm & Closed-Loop Experimentation
- [ ] Implement the 6 Persona Sub-Agents in `src/nectr/personas/` using `mesa` ABM ([ADR-0010](../adr/0010-adopt-mesa-abm-and-hypothesis-invariant-testing.md)) rather than LLM-agent frameworks (CrewAI/k8n).
- [ ] **Adaptive ML / RL Behavioral Persona Track:** Explore reinforcement learning & multi-armed bandits for adaptive Sybil evasion, tutor pricing, and `EXP-001` nepotism stress-testing in `src/nectr/personas/` and `experiments/`.
- [ ] Execute multi-semester Monte Carlo and adversarial collusion simulations in `experiments/`.
- [ ] Generate empirical telemetry datasets (velocity, Gini coefficient, collusion attenuation, Comb reserves).

## Milestone 4: Academic Paper, Business Proposals & Flagship Portfolio
- [ ] Compile the publication-ready manuscript in `paper/nectR_whitepaper.md`.
- [ ] Finalize the University Sponsorship & Swarming Business Proposal in `business/university_sponsorship_proposal.md`.
- [ ] **Living Docs, Glossary & IDE-Agnostic Onboarding ([#9](https://github.com/brandon-fox/nectR/issues/9), [#12](https://github.com/brandon-fox/nectR/issues/12)):** Add `docs/glossary.md` defining `MV=PQ` & `PoUW-PoW`, make `README.md` IDE/skill-agnostic, and automate `README.md` tree & `mkdocs.yml` `nav:` generation/drift checks.
- [ ] Publish the System Design Portfolio architecture site via `uv run mkdocs build --strict`.
