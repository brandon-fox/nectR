"""Behave step definitions for custom agent skills conformance."""

from __future__ import annotations

from pathlib import Path
import sys

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / ".agents" / "lib"))

import skill_common  # noqa: E402


@given("the repository custom skills workspace")
def step_given_skills_workspace(context) -> None:
  context.repo_root = REPO_ROOT
  context.skill_errors = []
  context.local_path_rc = 0


@when('the skill conformance validator runs on "{rel_dir}"')
def step_when_validator_runs(context, rel_dir: str) -> None:
  skills_dir = context.repo_root / rel_dir
  context.skill_dirs = [p for p in skills_dir.iterdir() if p.is_dir()]
  context.skill_errors = skill_common.validate_all_skills(skills_dir)
  context.local_path_rc = skill_common.check_no_local_paths(
      [context.repo_root / ".agents" / "lib", skills_dir],
      context.repo_root,
  )


@then("all 7 custom skills pass validation with zero local paths")
def step_then_all_skills_pass(context) -> None:
  assert len(context.skill_dirs) == 7, f"Expected 7 skills, found {len(context.skill_dirs)}"
  assert context.skill_errors == [], f"Skill spec violations: {context.skill_errors}"
  assert context.local_path_rc == 0, "Hardcoded local paths detected in .agents/"
