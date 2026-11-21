"""Tier-2 Behavioral Persona Sub-Agents for Closed-Loop Experimentation (Owned by ux-behavior-agent)."""

from enum import StrEnum

from nectr.personas.simulator import SimulationTelemetry, run_multi_hive_persona_simulation


class PersonaArchetype(StrEnum):
    """The 6 Behavioral Persona Sub-Agents modeling campus dynamics."""

    FRESHMAN_FORAGER = "FRESHMAN_FORAGER"
    CERTIFIED_SENIOR_WORKER = "CERTIFIED_SENIOR_WORKER"
    FINALS_WEEK_PANICKER = "FINALS_WEEK_PANICKER"
    SYBIL_ROOMMATE_RING = "SYBIL_ROOMMATE_RING"
    DRIFTING_POLLINATOR = "DRIFTING_POLLINATOR"
    QUEEN_FACILITATOR = "QUEEN_FACILITATOR"


__all__ = [
    "PersonaArchetype",
    "SimulationTelemetry",
    "run_multi_hive_persona_simulation",
]
