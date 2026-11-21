---
status: superseded by ADR-0012
date: 2026-11-21
decision-makers:
  - nectR Architecture & Meta-Orchestrator
---

# Use Markdown Architectural Decision Records

## Context and Problem Statement

Mixing cross-cutting blockchain and smart-contract invariants with tunable economic parameters in a single flat table caused drift and lacked lifecycle controls. How should structural architectural decisions be separated, validated, and kept concise?

## Considered Options

* **MADR managed by `pyadr` + code-enforced verbosity budgets (`<= 70` lines, `<= 380` words)**
* **Single hand-edited Markdown table for all decisions**
* **Unbounded free-form design documents without CLI validation**

## Decision Outcome

Chosen option: "MADR managed by `pyadr` + code-enforced verbosity budgets", because `pyadr` automates sequential numbering, slug verification, status lifecycle, and `docs/adr/index.md` generation while `nectr-decisions` prevents bloated ADRs and manages fast non-architectural presets separately in `docs/planning/decisions.yaml`.

### Consequences

* Good, because structural invariants (`docs/adr/`) and fast parameter/workflow rules (`docs/planning/decisions.yaml`) are separated and validated in pre-commit and CI.
* Bad, because contributors must run `pyadr toc` / `nectr-decisions render` rather than hand-editing generated index files.
