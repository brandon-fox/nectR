# nectR

> **Status:** research prototype — a campus peer-tutoring credit economy with deterministic smart contracts, agent simulation, and a signed audit log.

**nectR** is an open-source research prototype exploring how universities can organize peer tutoring as a closed-loop credit economy. Students earn tutoring credits (nectR) by teaching peers and spend them when receiving tutoring, backed by a campus treasury (the Comb). The protocol uses deterministic smart contracts, simulated economic agent personas, and a signed cryptographic audit log to study token velocity, anti-collusion incentives, and academic retention. All domain acronyms, equations, and roles are defined in the canonical [Domain Glossary](docs/glossary.md).

---

## Priority Hierarchy of Deliverables

1. **Published Academic Paper & Economic/Biomimetic Theory** (`paper/`, `docs/theory/`)
   - Formal game theory, honeybee biomimicry, closed-loop monetary velocity (**`MV = PQ`** — Fisher's Equation of Exchange balancing Money Supply × Velocity against Price Level × Real Tutoring Output), graph-theoretic anti-collusion decay, and empirical Agent-Based Computational Economics (ACE) validation with automated citation chain-of-custody.
2. **Prototype & Behavioral Experimentation** (`src/nectr/personas/`, `experiments/`)
   - Autonomous student, colluder, pollinator, and Queen persona sub-agents built with **Mesa ABM** (`ADR-0010`)—and an adaptive ML/RL exploration track—executing real signed transactions on the private blockchain.
3. **Institutional Business & Campus Sponsorship Proposals** (`business/`, `docs/business/`)
   - University sponsorship ROI models (Seed Comb injection vs. static tutoring budgets), retention economics, and multi-campus autonomous Swarming playbooks.
4. **Flagship System Design Portfolio: Private Blockchain, Smart Contracts & Service Layer** (`src/nectr/chain/`, `src/nectr/contracts/`, `src/nectr/services/`, `docs/architecture/`)
   - Hybrid `PoUW-PoW` distributed compute consensus (`ADR-0007`), the 5 deterministic smart contracts, and the hexagonal Hive Service Layer.

---

## Workspace Spaces (Auto-Synced Bounded Contexts)

Run `uv run nectr-docs tree` at any time to inspect the live directory tree directly from disk (avoiding stale hardcoded ASCII trees).

<!-- BEGIN AUTO-WORKSPACE-SPACES -->
| Workspace Space | Purpose | Owning Agent |
| :--- | :--- | :--- |
| `paper/` | Academic whitepaper, verified bibliography (`references.yaml`), & `lineage.yaml` | `sci-research-agent` |
| `docs/` | MkDocs portfolio site: `theory/`, `architecture/`, `business/`, `planning/`, `adr/`, `glossary.md` | `sci-research-agent` / `system-arch-agent` |
| `business/` | University Seed Comb sponsorship ROI models & multi-campus playbooks | `business-proposal-agent` |
| `experiments/` | Multi-semester Monte Carlo & adversarial simulation outputs | `ux-behavior-agent` |
| `src/nectr/chain/` | Hybrid `PoUW-PoW` ledger, Ed25519 signing, and Merkle state commitments | `pow-compute-agent` |
| `src/nectr/contracts/` | The 5 deterministic Hive smart contracts & supply-conservation FSMs | `contracts-service-agent` |
| `src/nectr/services/` | Hexagonal Hive Service Layer (Escrow, Knowledge Graph, Arbitration, Bridge) | `contracts-service-agent` |
| `src/nectr/personas/` | 6 Behavioral Persona Sub-Agents executing signed transactions | `ux-behavior-agent` |
| `src/nectr/ui/` | Read-only Hive Explorer, Knowledge Graph & Comb reserve telemetry UI | `design-ui-agent` |
| `src/nectr/devtools/` | Decision registry, citation custody & living docs sync (MADR linting via OSS `adrlint`) | `meta-orchestrator` |
| `openspec/` & `features/` | OpenSpec requirement specs linked 1-to-1 to Behave Gherkin scenarios | All agents |
| `tests/` | Strict TDD (`xfail_strict`) unit, invariant, and governance test suites | Domain owners |
<!-- END AUTO-WORKSPACE-SPACES -->

---

## Quick Start (IDE-Agnostic CLI)

1. **Clone & Enter the Repository:**

   ```powershell
   git clone https://github.com/brandon-fox/nectR.git
   cd nectR
   ```

2. **Install by Persona (`uv`):**
   - Core runtime only: `uv sync`
   - Full contributor stack (`test` + `lint` + `security` + `docs`): `uv sync --extra dev`
   - Targeted persona installs: `uv sync --extra test`, `uv sync --extra docs`, `uv sync --extra research`, `uv sync --extra lint`, `uv sync --extra security`
3. **Verify Tests, Governance & Documentation:**

   ```powershell
   uv run pytest
   uv run behave
   uv run adrlint lint
   uv run adrlint lock --check
   uv run nectr-decisions check
   uv run nectr-citations check
   uv run nectr-docs check
   uv run mkdocs build --strict
   ```

4. **Optional: Shipped Repository Agent Skills (`.agents/skills/`):**
   - The repository ships portable skills and rules under `.agents/skills/` and `.agents/rules/` (validated by `tests/test_skills_spec.py`) for AI coding assistants that support workspace skill loading, while every workflow remains 100% runnable via standard CLI commands above (`uv run adrlint`, `uv run nectr-decisions`, `uv run nectr-citations`, `uv run nectr-docs`, `uv run pytest`, `uv run behave`).

---

## Independence

This is a personal project by Brandon Fox, built on my own time and equipment. It is not affiliated with, endorsed by, or derived from the work of any employer, current or former, and does not represent their views, products or practices. Licensed under the MIT License; principles at [First-ADE/PRINCIPLES.md](https://github.com/First-ADE/.github/blob/main/PRINCIPLES.md).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.
