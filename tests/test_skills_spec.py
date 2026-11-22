"""Tests enforcing Antigravity skill structure, typing, and commit-hook gates."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".agents" / "lib"))

import skill_common


def test_all_custom_skills_conform_to_spec() -> None:
    """Verify every skill in .agents/skills/ meets structure and spec rules."""
    skills_dir = REPO_ROOT / ".agents" / "skills"
    assert skills_dir.is_dir(), "Expected .agents/skills directory to exist"
    skill_dirs = [p for p in skills_dir.iterdir() if p.is_dir()]
    assert len(skill_dirs) == 7, f"Expected 7 custom skills, found {len(skill_dirs)}"

    errors = skill_common.validate_all_skills(skills_dir)
    assert errors == [], "Skill spec violations:\n" + "\n".join(errors)


def test_agent_files_have_no_local_paths() -> None:
    """Verify .agents/lib and .agents/skills contain no hardcoded user paths."""
    rc = skill_common.check_no_local_paths(
        [REPO_ROOT / ".agents" / "lib", REPO_ROOT / ".agents" / "skills"],
        REPO_ROOT,
    )
    assert rc == 0, "Hardcoded local user paths detected in .agents/"


def test_mypy_is_enforced_in_commit_hooks() -> None:
    """Verify mypy is configured in both .pre-commit-config.yaml and .githooks/pre-push."""
    pre_commit_cfg = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    git_hook = (REPO_ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    assert "mypy" in pre_commit_cfg, "mypy hook missing from .pre-commit-config.yaml"
    assert "mypy" in git_hook, "mypy check missing from .githooks/pre-push"
