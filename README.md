# nectR — Federated Biomimetic Campus Tutoring Blockchain & Closed-Economy Ecosystem

**nectR** is a research-driven monorepo for a private, closed-loop Proof-of-Work & Proof-of-Useful-Compute (`PoUW-PoW`) blockchain and multi-agent behavioral economy modeled after real honeybee (*Apis mellifera*) colony dynamics.

---

## Priority Hierarchy of Deliverables

1. **Published Academic Paper & Economic/Biomimetic Theory** (`paper/`, `docs/theory/`)
   - Formal game theory, honeybee biomimicry, closed-loop monetary velocity ($MV=PQ$), graph-theoretic anti-collusion decay, and empirical agent-based computational economics (ACE) validation.
2. **Prototype & Behavioral Experimentation** (`src/nectr/personas/`, `experiments/`)
   - Autonomous student, colluder, pollinator, and Queen persona sub-agents transacting on the live private blockchain to generate observable emergent behavior data.
3. **Institutional Business & Campus Sponsorship Proposals** (`business/`, `docs/business/`)
   - University sponsorship ROI models (Seed Comb injection vs. static tutoring budgets), retention economics, and multi-campus autonomous Swarming playbooks.
4. **Flagship System Design Portfolio: Private Blockchain, Smart Contracts & Service Layer** (`src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, `docs/architecture/`)
   - Hybrid `PoUW-PoW` distributed compute consensus, the 5 deterministic smart contracts, and the hexagonal Hive Service Layer.

---

## Monorepo Directory Layout

```text
nectR/
├── AGENTS.md                        # Root Antigravity instructions & multi-agent orchestration rules
├── .agents/                         # Antigravity workspace customizations
│   ├── rules/                       # Hierarchical domain rules (chain, theory, git hygiene)
│   └── skills/                      # Specialized skills for the 8 Builder Agents & Persona Swarm
│       ├── orchestrate-nectr/       # Meta-orchestration & multi-agent workflow skill
│       ├── scientific-paper/        # Academic theory, math proofs & empirical charting skill
│       ├── persona-simulation/      # Tier-2 Behavioral Persona Sub-Agent swarm runner skill
│       └── blockchain-architect/    # Smart contracts, PoUW-PoW & Service Layer design skill
├── docs/                            # MkDocs documentation & System Design Portfolio site
│   ├── index.md
│   ├── theory/                      # Tokenomics, Game Theory & Honeybee Biomimicry specs
│   ├── architecture/                # Portfolio System Design, Smart Contracts & Service Layer
│   ├── business/                    # University Sponsorship & Swarming Business Proposals
│   └── planning/                    # Roadmap, Milestones, and /grill-me Decision Logs
├── paper/                           # Deliverable #1: Academic Whitepaper & LaTeX / Markdown manuscripts
├── business/                        # Deliverable #3: Sponsor ROI models & University Pitch materials
├── experiments/                     # Deliverable #2: Behavioral simulation configs & output telemetry
├── src/
│   └── nectr/
│       ├── chain/                   # Private PoW + Distributed Compute (PoUW) Blockchain Core
│       ├── contracts/               # 5 Core On-Chain Smart Contracts (State Machines)
│       ├── services/                # Hive Service Layer (Graph Indexer, Escrow, Arbitrator, Bridge)
│       ├── personas/                # 6 Behavioral Persona Sub-Agents (Learners, Workers, Sybils, Queens)
│       └── ui/                      # Block Explorer, Knowledge Flow Graph & Comb Dashboard
└── tests/                           # Unit, Smart Contract, Game-Theory Invariant & Simulation tests
```

---

## Quick Start

1. **Open as Active Workspace in Antigravity:**
   Set `<repo-root>` as your active workspace.
2. **Environment Setup (`uv`):**
   ```powershell
   uv sync
   uv run pytest
   ```
3. **Documentation Preview (`mkdocs`):**
   ```powershell
   uv run mkdocs build --strict
   uv run mkdocs serve
   ```
4. **Autonomous Agent Commands:**
   - Run `/grill-me` to resolve open design parameters recorded in `docs/planning/decision_log.md`.
   - Run `/teamwork` or invoke the workspace skills in `.agents/skills/` to coordinate the 8 Domain Builder Agents and 6 Persona Sub-Agents.
