---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Behavioral Economy
---

# Restrict CrewAI to Isolated Off-Chain Peripherals

## Context and Problem Statement

`DEC-009` and [ADR-0010](0010-adopt-mesa-abm-and-hypothesis-invariant-testing.md) select `mesa` ABM and RL/bandits over LLM orchestration (`CrewAI`) for ACE simulations. Does `CrewAI` offer valid utility elsewhere in `nectR` without violating deterministic contracts, scientific reproducibility, or zero-CVE dependency hygiene (`DEC-007`)?

## Considered Options

* **Exclude `CrewAI` from core, ACE, and `dev` stacks; permit only isolated off-chain or CI peripherals**
* **Adopt `CrewAI` inside `src/nectr/personas/` or `src/nectr/services/`**
* **Ban `CrewAI` unconditionally across all future extensions and CI bots**

## Decision Outcome

Chosen option: "Exclude `CrewAI` from core, ACE, and `dev` stacks; permit only isolated off-chain or CI peripherals", because `PoUW-PoW` consensus, deterministic contracts, `HiveServiceLayer`, and seeded `mesa` ACE runs use structured handshakes, require bit-reproducibility with zero external oracle reliance, and avoid transitive LLM/vector-DB dependency bloat. `CrewAI` (MIT) MAY only be adopted outside core and `dev` dependencies for: external GitHub Actions CI remediation bots (Milestone 0 Phase 3), future off-chain free-text UX or Queen dispute-brief prep, or offline exploratory red-teaming re-encoded in `mesa`/`hypothesis`.

### Consequences

* Good, because core contracts, `HiveServiceLayer`, `dev` extras, and Monte Carlo ACE experiments remain deterministic, fast, and clean under `pip-licenses` and `pip-audit`.
* Good, because peripheral natural-language or CI workflows remain possible later without introducing on-chain oracle nondeterminism.
* Bad, because any future `CrewAI` integration must live in an isolated optional dependency group or external runner with its own OpenSpec review.
