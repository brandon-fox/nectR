# Architecture Decision Records (MADR)

Architectural decisions in **nectR** use MADR 4.0 YAML front matter validated, formatted, and immutability-locked by [`adrlint`](https://github.com/polylint/adrlint) (`adrlint.lock`), with project-specific verbosity caps enforced by `nectr-decisions`.

## Decision Index

<!-- BEGIN AUTO-ADR-INDEX -->
| ADR | Title | Status |
| :--- | :--- | :--- |
| `ADR-0000` | [Use Markdown Architectural Decision Records](0000-use-markdown-architectural-decision-records.md) | `superseded by ADR-0012` |
| `ADR-0001` | [Use Commitizen for Automated Changelogs and Releases](0001-use-commitizen-for-automated-changelogs-and-releases.md) | `accepted` |
| `ADR-0002` | [Enforce Directional Service Barter State Transitions](0002-enforce-directional-service-barter-state-transitions.md) | `accepted` |
| `ADR-0003` | [Enforce Multi-Tier Beekeeper and Queen Governance](0003-enforce-multi-tier-beekeeper-and-queen-governance.md) | `accepted` |
| `ADR-0004` | [Route Governance Fees to Comb with Phase-Split Royal Jelly](0004-route-governance-fees-to-comb-with-phase-split-royal-jelly.md) | `accepted` |
| `ADR-0005` | [Gate Cross-Hive Bridges with Guard Bee Status and Epoch FX](0005-gate-cross-hive-bridges-with-guard-bee-status-and-epoch-fx.md) | `accepted` |
| `ADR-0006` | [Adopt Two-Phase Hive Genesis and Autonomous Swarming](0006-adopt-two-phase-hive-genesis-and-autonomous-swarming.md) | `accepted` |
| `ADR-0007` | [Couple Open Campus PoUW-PoW Mining to Capped Comb Compute Jar](0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md) | `accepted` |
| `ADR-0008` | [Adopt Ed25519 CanonicalJSON and Merklelib](0008-adopt-ed25519-canonicaljson-and-merklelib.md) | `accepted` |
| `ADR-0009` | [Adopt SQLModel Alembic Structlog and OpenTelemetry](0009-adopt-sqlmodel-alembic-structlog-and-opentelemetry.md) | `accepted` |
| `ADR-0010` | [Adopt Mesa ABM and Hypothesis Invariant Testing](0010-adopt-mesa-abm-and-hypothesis-invariant-testing.md) | `accepted` |
| `ADR-0011` | [Adopt Streamlit and NetworkX for Telemetry UI](0011-adopt-streamlit-and-networkx-for-telemetry-ui.md) | `accepted` |
| `ADR-0012` | [Adopt adrlint for MADR Linting and Immutability](0012-adopt-adrlint-for-madr-linting-and-immutability.md) | `accepted` |
| `ADR-0013` | [Restrict CrewAI to Isolated Off-Chain Peripherals](0013-restrict-crewai-to-isolated-off-chain-peripherals.md) | `accepted` |
| `ADR-0014` | [Adopt NATS Leaf Nodes JetStream and CQRS Graph Isolation](0014-adopt-nats-leaf-nodes-jetstream-and-cqrs-graph-isolation.md) | `accepted` |
| `ADR-0015` | [Enforce Zero-PII FERPA GDPR and Title IV Campus Compliance](0015-enforce-zero-pii-ferpa-gdpr-and-title-iv-campus-compliance.md) | `accepted` |
| `ADR-0016` | [Scope External Workflow Automation Off-Chain](0016-scope-external-workflow-automation-off-chain.md) | `accepted` |
| `ADR-0017` | [Isolate Concurrent Work in Ephemeral Worktrunk Git Worktrees](0017-isolate-concurrent-work-in-ephemeral-worktrunk-git-worktrees.md) | `accepted` |
| `ADR-0018` | [Enforce Incremental Mutation Testing with Poodle Ratchet Floors](0018-enforce-incremental-mutation-testing-with-poodle-ratchet-floors.md) | `accepted` |
<!-- END AUTO-ADR-INDEX -->

## `adrlint` Workflow & Configuration

Repository configuration lives in [`.adrlint.toml`](https://github.com/brandon-fox/nectR/blob/main/.adrlint.toml) (`dir = "docs/adr"`, `start = 0`, `path = "adrlint.lock"`).

* **Draft a proposal on a feature branch:** Run `uv run adrlint new "<Short Title>"` to create the next sequential `NNNN-<slug>.md` with `status: proposed` in YAML front matter.
* **Branch checks (`proposed` allowed pre-merge):** Run `uv run adrlint lint`, `uv run adrlint format --check`, and `uv run nectr-decisions check --allow-proposed`. Strict `nectr-decisions check` (used on `main`) rejects unaccepted `proposed` records.
* **Finalize & lock (`accepted` / `rejected` / `superseded` / `deprecated`):** Update `status:` in YAML front matter, run `uv run adrlint lint`, `uv run adrlint format`, `uv run adrlint lock`, and `uv run nectr-docs sync` to update this index and `mkdocs.yml`.
* **Verbosity limits (`nectr-decisions`):** Every ADR must remain concise: `<= 70` lines, `<= 380` words, H1 title `<= 70` chars, and `<= 6` bullets per section.
