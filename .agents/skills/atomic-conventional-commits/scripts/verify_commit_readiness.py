"""Cross-platform commit readiness, mypy, and Conventional Commits verifier."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common

MYPY_TARGETS: Final[tuple[str, ...]] = (
    "src",
    ".agents/lib",
    ".agents/skills",
    "tests/test_skills_spec.py",
)


def main() -> int:
  """Verify git hooks, SSH signing, mypy strict typing, and commit message.

  Returns:
    Exit code (0 on success).
  """
  parser = argparse.ArgumentParser(
      description="Verify git hooks, SSH signing, mypy, and commit message."
  )
  parser.add_argument(
      "--message",
      help="Optional commit message string to validate with commitizen.",
  )
  parser.add_argument(
      "--skip-mypy",
      action="store_true",
      help="Skip running mypy --strict.",
  )
  args = parser.parse_args()

  repo_root = skill_common.find_repo_root()
  rc = skill_common.check_git_hygiene(repo_root, require_ssh_signing=True)
  if rc != 0:
    return rc

  if not args.skip_mypy:
    rc = skill_common.run_mypy(MYPY_TARGETS, repo_root)
    if rc != 0:
      return rc

  if args.message:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".txt", delete=False
    ) as tmp:
      tmp.write(args.message)
      tmp_path = Path(tmp.name)
    try:
      cmd = [
          *skill_common.resolve_tool_cmd("cz", "commitizen"),
          "check",
          "--commit-msg-file",
          str(tmp_path),
      ]
      return skill_common.run_step("commitizen check", cmd, repo_root)
    finally:
      tmp_path.unlink(missing_ok=True)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
