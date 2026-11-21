"""Cross-platform DDD boundary and contract/chain test gate."""

from __future__ import annotations

import ast
from pathlib import Path
import sys
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common

FORBIDDEN_CHAIN_IMPORTS: Final[tuple[str, ...]] = (
    "nectr.contracts",
    "nectr.services",
    "nectr.personas",
)
CANDIDATE_TEST_FILES: Final[tuple[str, ...]] = (
    "tests/test_invariants.py",
    "tests/test_contracts.py",
    "tests/test_chain.py",
    "tests/test_services.py",
)


def check_chain_ddd_boundaries(repo_root: Path) -> int:
  """Ensure ``src/nectr/chain/`` does not import higher-level domain layers.

  Args:
    repo_root: Repository root path.

  Returns:
    0 if no boundary violations are found, otherwise 1.
  """
  chain_dir = repo_root / "src" / "nectr" / "chain"
  if not chain_dir.is_dir():
    print(
        "[PASS] src/nectr/chain/ not yet created; skipping import boundary check"
    )
    return 0

  violations: list[str] = []
  for py_file in chain_dir.rglob("*.py"):
    tree = ast.parse(
        py_file.read_text(encoding="utf-8"), filename=str(py_file)
    )
    for node in ast.walk(tree):
      modules: list[str] = []
      lineno = 0
      if isinstance(node, ast.Import):
        modules = [alias.name for alias in node.names]
        lineno = node.lineno
      elif isinstance(node, ast.ImportFrom) and node.module:
        modules = [node.module]
        lineno = node.lineno
      for mod in modules:
        if any(
            mod == bad or mod.startswith(f"{bad}.")
            for bad in FORBIDDEN_CHAIN_IMPORTS
        ):
          rel = py_file.relative_to(repo_root)
          violations.append(f"{rel}:{lineno} imports '{mod}'")

  if violations:
    print(
        f"[FAIL] DDD boundary violations in chain/: {', '.join(violations)}",
        file=sys.stderr,
    )
    return 1
  print("[PASS] src/nectr/chain/ DDD import boundaries clean")
  return 0


def main() -> int:
  """Verify chain DDD boundaries and run architecture-relevant pytest suite.

  Returns:
    Exit code (0 on success).
  """
  repo_root = skill_common.find_repo_root()
  rc = check_chain_ddd_boundaries(repo_root)
  if rc != 0:
    return rc

  candidate_tests = [
      p for p in CANDIDATE_TEST_FILES if (repo_root / p).is_file()
  ]
  return skill_common.run_pytest(candidate_tests or None, repo_root)


if __name__ == "__main__":
  raise SystemExit(main())
