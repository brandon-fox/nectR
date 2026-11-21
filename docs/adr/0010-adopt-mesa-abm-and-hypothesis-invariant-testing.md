---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Behavioral Economy & Verification Architecture
---

# Adopt Mesa ABM and Hypothesis Invariant Testing

## Context and Problem Statement

`src/nectr/personas/simulator.py` uses a custom epoch loop for the 6 Behavioral Persona Sub-Agents, and contract invariants are tested only on fixed examples.

## Considered Options

* **`mesa` (Apache-2.0) for ABM scheduling/telemetry + `hypothesis` (MPL-2.0) for property-based contract invariant testing**
* **Custom Python `for`-loop simulator with hand-written CSV/JSONL collectors**

## Decision Outcome

Chosen option: "`mesa` + `hypothesis`", because `mesa` provides standard agent scheduling, `DataCollector` telemetry, and reproducible RNG seeding, while `hypothesis` fuzzes `HiveContractEngine` invariants (supply conservation, Queen separation, Accepted Status) across arbitrary transaction sequences.

### Consequences

* Good, because ACE simulations align with academic ABM standards and `hypothesis` catches edge-case invariant violations automatically.
* Bad, because `mesa` introduces a framework dependency in `src/nectr/personas/`.
