"""Cross-platform post-stage verification gate for multi-agent orchestration."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common


def main() -> int:
  """Run git hygiene, mypy, pytest, behave, and mkdocs gates.

  Returns:
    0 if all gates pass, otherwise the first non-zero exit code.
  """
  repo_root = skill_common.find_repo_root()
  mypy_targets = [
      "src",
      ".agents/lib",
      ".agents/skills",
      "tests/test_skills_spec.py",
  ]
  steps: list[tuple[str, Callable[[], int]]] = [
      ("git hygiene", lambda: skill_common.check_git_hygiene(repo_root)),
      ("mypy", lambda: skill_common.run_mypy(mypy_targets, repo_root)),
      ("pytest", lambda: skill_common.run_pytest(None, repo_root)),
      ("behave", lambda: skill_common.run_behave(None, repo_root)),
      ("mkdocs", lambda: skill_common.run_mkdocs_strict(repo_root)),
  ]
  return skill_common.run_steps(steps)


if __name__ == "__main__":
  raise SystemExit(main())
