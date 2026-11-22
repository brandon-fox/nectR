---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Behavioral Economy
---

# Scope External Workflow Automation Off-Chain

## Context and Problem Statement

`DEC-009` and [ADR-0010](0010-adopt-mesa-abm-and-hypothesis-invariant-testing.md) select `mesa` ABM and RL/bandits over LLM/workflow orchestration (`"CrewAI/k8n"`). Historical `"k8n"` references mean **`n8n`** (node-based workflow/webhook automation), which uses the source-available **Sustainable Use License (SUL)** incompatible with `DEC-007` packaging rules. How should `n8n` and permissive-OSS workflow tools fit into Milestone 3?

## Considered Options

* **Isolate `n8n` and OSS workflow orchestrators behind off-chain `HiveServiceLayer` webhooks**
* **Bundle `n8n` or external orchestrators inside `pyproject.toml` and `src/nectr/personas/`**
* **Prohibit all external workflow orchestration across Milestone 3 experiments**

## Decision Outcome

Chosen option: "Isolate `n8n` and OSS workflow orchestrators behind off-chain `HiveServiceLayer` webhooks", because `n8n`'s Sustainable Use License violates `DEC-007` (`MIT`/`Apache-2.0`/`BSD`/`MPL` packaging) and external triggers introduce non-determinism. Canonical Monte Carlo sweeps remain seeded `mesa` ABM + ML/RL (`ADR-0010`), while `n8n` MAY act strictly as an out-of-process sidecar calling `HiveServiceLayer` endpoints with logged replayable inputs (`EXP-006`). For packaged or in-repo automation, `DEC-007`-compliant permissive tools (`Activepieces` MIT, `Kestra`/`Prefect` Apache-2.0, `Temporal` MIT) are preferred.

### Consequences

* Good, because `pyproject.toml`, `uv.lock`, and core `mesa` ACE baselines remain permissive-OSS compliant (`DEC-007`) and bit-reproducible.
* Good, because Milestone 3 (`EXP-006`) can evaluate webhook-triggered campus surge/adversary experiments without bypassing smart contract checks.
* Bad, because self-hosted `n8n` deployments remain external to Python packaging and require explicit replay logs for scientific reproducibility.
