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
2. **Isolate Worktrees & Assign Strict File Ownership:** Consult [domain_agents_matrix.md](./references/domain_agents_matrix.md) and isolate each concurrent builder in its own Worktrunk worktree (`.worktrees/<branch-slug>/` via `git-wt`) or `workspace: "share"` harness worktree (`ADR-0017`) with per-worktree `uv sync --frozen --extra dev` and explicit owned paths.
3. **Run Pre-Merge & Post-Stage Verification Gates:** Execute [verify_orchestration_gate.py](./scripts/verify_orchestration_gate.py) and `mutation_gate diff --base main` (`ADR-0018`, `DEC-017`), mirroring `.config/wt.toml` `[[pre-merge]]`, before landing via `git-wt merge main --no-squash`:

   ```bash
   uv run python -m nectr.devtools.mutation_gate diff --base main
   uv run python .agents/skills/orchestrate-nectr/scripts/verify_orchestration_gate.py
   ```

## Validation

- Confirm `verify_orchestration_gate.py` and `nectr.devtools.mutation_gate diff --base main` exit `0` (`mypy`, `pytest`, `behave`, `mkdocs build --strict`, tiered mutation targets, and git hygiene all pass with zero leftover `.poodle-temp` artifacts).
