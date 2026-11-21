"""Cross-platform OpenSpec + Behave BDD + Strict TDD gate runner."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OpenSpec/BDD/TDD verification gate.")
    parser.add_argument(
        "--phase",
        choices=("red", "green", "refactor", "all"),
        default="all",
        help="Lifecycle phase to verify.",
    )
    args = parser.parse_args()

    repo_root = skill_common.find_repo_root()
    rc = skill_common.run_detect_secrets([], repo_root)
    if rc != 0:
        return rc

    sys.path.insert(0, str(repo_root / "src"))
    from nectr.devtools.spec_links import SpecLinkError, validate_spec_links

    try:
        validate_spec_links(repo_root)
    except SpecLinkError as exc:
        print(f"SPEC LINK GATE FAILED: {exc}", file=sys.stderr)
        return 1

    rc = skill_common.run_pytest(None, repo_root)
    if rc != 0:
        return rc

    if args.phase == "red":
        return skill_common.run_behave(["~@red"], repo_root)
    return skill_common.run_behave(None, repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
