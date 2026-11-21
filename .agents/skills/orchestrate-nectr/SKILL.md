---
name: orchestrate-nectr
description: >-
  Orchestrates the 8 specialized Domain Builder Agents and 6 Behavioral Persona
  Sub-Agents with strict file ownership boundaries. Use when coordinating
  multi-agent build phases, assigning domain ownership, or running parallel
  subagents or swarms in the nectR monorepo.
---

# nectR Multi-Agent Orchestration

Coordinate parallel domain agents while enforcing zero git cross-contamination.

## Steps

1. **Clarify Design Parameters (If Ambiguous):** Run an interactive `/grill-me` session against `docs/planning/decision_log.md` and record finalized parameters.
2. **Assign Strict File Ownership:** Consult [domain_agents_matrix.md](./references/domain_agents_matrix.md) and assign each subagent (`define_subagent` / `invoke_subagent` / `swarm` / `run_workflow`) only its owned paths.
3. **Run Post-Stage Verification Gate:** Execute [verify_orchestration_gate.py](./scripts/verify_orchestration_gate.py):
   ```bash
   uv run python .agents/skills/orchestrate-nectr/scripts/verify_orchestration_gate.py
   ```

## Validation

- Confirm `verify_orchestration_gate.py` exits `0` (`mypy`, `pytest`, `behave`, `mkdocs build --strict`, and git hygiene all pass).
