---
trigger: always_on
---

# nectR Workspace Rules & Multi-Agent Operating Charter

You are operating inside the **nectR** monorepo (repository root).

## 1. Deliverable Priority Order (Never Violate)

1. **Priority 1 — Published Academic Paper & Theory** (`paper/`, `docs/theory/`): Every mechanism in code must map directly to a formal mathematical equation or honeybee (*Apis mellifera*) biomimetic dynamic documented in `docs/theory/` and `paper/`.
2. **Priority 2 — Prototype & Behavioral Experimentation** (`src/nectr/personas/`, `experiments/`): The 6 Persona Sub-Agents must execute real signed transactions against the private blockchain to produce empirical telemetry (velocity, Gini index, collusion decay, Comb reserves).
3. **Priority 3 — Institutional Business Proposals** (`business/`, `docs/business/`): Translate simulation telemetry into university sponsorship ROI, retention impact, and multi-campus swarming business cases.
4. **Priority 4 — System Design Portfolio Highlight** (`src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, `docs/architecture/`): The private `PoUW-PoW` blockchain, the 5 deterministic smart contracts, and the Hive Service Layer must exemplify clean, modular, production-grade systems engineering.

## 2. Core Protocol Invariants (Enforced in Code & Theory)

- **No Blind Token Transfers:** `nectR` can NEVER be transferred without a `DirectionalServiceBarter` state transition (`Tutor -> Learner`, `Subject`, `Duration`, `Attestation`) or an explicit `Comb` treasury/bridge contract call.
- **Zero-Fee P2P Barter:** Direct peer-to-peer tutoring settlement charges `0%` protocol fee.
- **Strict Queen Separation of Powers:** Wallets holding `QUEEN_ROLE` are cryptographically prohibited from acting as `Tutor` to generate `nectR`. Queens only manage (certify Worker Bees, resolve disputes, manage Comb bounties, approve cross-hive bridges).
- **Fee-to-Comb Rule:** Fees are only levied when Queen/Hive services are invoked, and 100% of service fees flow into the Hive's **Comb (Treasury)**. Queens receive a performance-tied **Royal Jelly Dividend** based on Hive Velocity & Diversity Index.
- **Cross-Hive Capital Control ("Accepted Status"):** `nectR` is scoped to its home Hive (`nectR-HIVE_A`). A migrating Bee cannot bridge funds into `HIVE_B` until they earn on-chain **Accepted Status** (Guard Bee recognition via verified tutoring contribution in `HIVE_B`).
- **Two-Phase Hive Genesis:**
  - *Phase 1 (Sponsored Injection):* School injects a Seed Comb; Founding Teacher-Queens certify seed Worker Bees; Learners spend restricted `RAW_POLLEN` with Certified Workers, converting it into `LIQUID_NECTR`.
  - *Phase 2 (Autonomous Swarming):* Veteran Certified Bees with high downstream effectiveness swarm to found new daughter Hives as Queens, seeded by a Swarm Grant from mature Combs.

## 3. Multi-Agent Concurrency & Git Isolation

- **Ephemeral Worktree Isolation (`ADR-0017`):** Keep the primary checkout clean on `main`. Run concurrent tasks inside isolated Worktrunk worktrees (`.worktrees/<branch-slug>/` via `git-wt`) or agent harness shared-repo worktrees; `.config/wt.toml` provisions per-worktree `.venv` (`uv sync --frozen --extra dev`), enforces `[[pre-merge]]` gates, and lands via `git-wt merge main --no-squash` to preserve atomic SSH-signed commits.
- **Atomic File Ownership:** When running as a specialized domain agent or subagent, only stage (`git add <explicit-file>`) the exact files within your domain scope. Never run `git add .` or `git commit -a`.
- **Documentation Verification:** Whenever updating or moving files in `docs/` or `mkdocs.yml`, run `uv run mkdocs build --strict`.
- **Testing & Mutation Verification (`ADR-0018`, `DEC-017`):** Keep `pythonpath = ["src"]` in `pyproject.toml` and verify contract invariants with `uv run pytest`. Never add inline mutation suppression pragmas in `src/` (`mutation_gate check-pragmas`), and pass changed-line mutation checks (`uv run python -m nectr.devtools.mutation_gate diff`) during `REFACTOR`, `[[pre-merge]]`, and `pre-push` (`>= 85%` Tier 1 `contracts/`/`chain/`, `>= 75%` Tier 2 `services/`/`devtools/`; upward-only baseline floors on `main`).

## 4. Open-Source Security, OpenSpec, BDD, Strict TDD & DDD (No Exceptions)

- **Open-Source-First & Transitive License Audit:** Never rebuild or write custom code when a secure, well-respected, permissively licensed OSS solution exists. Before adding any dependency, research existing OSS libraries/services and scan all direct and chained sub-dependencies for free, MIT-compatible licenses (`MIT`, `Apache-2.0`, `BSD-*`, `ISC`, `PSF-2.0`).
- **Pre-Read / Pre-Commit / Pre-Push Security Gate:** Run `detect-secrets-hook --baseline .secrets.baseline <file>` (or `detect-secrets scan`) before reading new files. Never commit secrets, private references, or local hardcoded paths. Git hooks in `.githooks/` (`core.hooksPath = .githooks`) and `.pre-commit-config.yaml` (`detect-secrets`, `commitizen`, `pygrep`) enforce this automatically; `--no-verify` is strictly forbidden.
- **OpenSpec (`openspec/`):** Every behavioral change requires an OpenSpec spec/change proposal (`openspec/changes/<change-id>/`) before implementation.
- **BDD (`features/`):** Every OpenSpec scenario must be defined in Gherkin (`features/*.feature`) and verified with `python -m behave`.
- **Strict TDD (Red-Green-Refactor) & DDD:** Follow Red-Green-Refactor (`python -m pytest`) and respect DDD Bounded Contexts defined in `openspec/project.md` before, during, and after every action.
