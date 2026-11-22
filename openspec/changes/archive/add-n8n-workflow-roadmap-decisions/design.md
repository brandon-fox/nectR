# Design: External Workflow & n8n ("k8n") Scope for Milestone 3 (`decision-governance`)

## Governance & Architectural Boundary

- **Core Simulation Determinism (`DEC-009` / `ADR-0010`):** Canonical Monte Carlo ACE runs in `src/nectr/personas/` remain deterministic seeded `mesa` ABM + ML/RL policies tested with `hypothesis`.
- **Out-of-Process Webhook Boundary (`DEC-016` / `ADR-0016`):** External workflow tools (including `n8n` under its Sustainable Use License) MUST NOT enter `pyproject.toml` or mutate `HiveContractEngine` state directly; any integration runs out-of-process via documented `HiveServiceLayer` REST/webhook ports with logged replayable inputs.
- **Permissive-OSS Preference (`DEC-007`):** When evaluating packaged or self-hosted workflow orchestration in Milestone 3, permissive OSS engines (`Activepieces` MIT, `Kestra` Apache-2.0, `Prefect` Apache-2.0, `Temporal` MIT) take precedence over fair-code `n8n`.
- **Benchmarking Hypothesis (`EXP-006`):** Compare pure seeded Mesa ABM + ML/RL against an external webhook-triggered hybrid arm on seed parity, latency, and collusion detection fidelity alongside `EXP-001`–`EXP-005`.

## Invariants

1. `DEC-009` stays `locked` (not superseded) and `decisions.yaml` <-> `decision_log.md` stays deterministically synchronized via `nectr-decisions render`.
2. `ADR-0016` satisfies `adrlint` (`lint`, `format --check`, `lock --check`) and `nectr-decisions` verbosity limits (`<= 70` lines, `<= 380` words, title `<= 70` chars, `<= 6` bullets per section).
