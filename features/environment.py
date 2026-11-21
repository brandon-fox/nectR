"""Behave environment hooks for nectR BDD acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def before_scenario(context: object, scenario: object) -> None:
    """Skip @red scenarios awaiting Phase 1/2 BDD-TDD implementation."""
    tags = getattr(scenario, "tags", [])
    if "red" in tags:
        scenario.skip("Marked @red: awaiting Phase 1/2 BDD-TDD implementation")  # type: ignore[attr-defined]
