---
name: persona-simulation
description: >-
  Configures, runs, and analyzes the 6 Behavioral Persona Sub-Agents transacting
  on the private nectR blockchain. Use when designing, calibrating, or executing
  agent-based behavioral simulations in src/nectr/personas/ and experiments/.
---

# Behavioral Persona Sub-Agent Simulation

Follow this workflow when building or evaluating nectR's 6 behavioral persona simulations.

## Steps

1. **Align Archetypes & Epoch Metrics:** Review [persona_archetypes_and_metrics.md](./references/persona_archetypes_and_metrics.md) for the 6 persona behaviors and the 5 required epoch telemetry metrics.
2. **Execute / Update Simulations:** Implement or calibrate persona actors in `src/nectr/personas/` and simulation runners in `experiments/` using real signed contract transactions.
3. **Verify Telemetry & Tests:** Run [verify_persona_telemetry.py](./scripts/verify_persona_telemetry.py):
   ```bash
   uv run python .agents/skills/persona-simulation/scripts/verify_persona_telemetry.py
   ```

## Validation

- Confirm `verify_persona_telemetry.py` exits `0` (validates `experiments/` JSON/CSV telemetry outputs if present and runs persona/invariant tests).
