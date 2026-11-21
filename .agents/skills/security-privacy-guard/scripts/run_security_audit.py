"""Cross-platform security, secrets, hooks, and dependency audit runner."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common


def main() -> int:
    parser = argparse.ArgumentParser(description="Run nectR security and privacy checks.")
    parser.add_argument(
        "--mode",
        choices=("pre-read", "pre-commit", "full"),
        default="pre-commit",
        help="Audit scope to execute.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="Relative file paths for pre-read secret scanning.",
    )
    args = parser.parse_args()

    repo_root = skill_common.find_repo_root()

    if args.mode == "pre-read":
        if not args.files:
            print("[FAIL] --mode pre-read requires --files <path...>", file=sys.stderr)
            return 2
        rc = skill_common.run_detect_secrets(args.files, repo_root)
        if rc != 0:
            return rc
        return skill_common.check_no_local_paths([Path(f) for f in args.files], repo_root)

    rc = skill_common.check_git_hygiene(repo_root)
    if rc != 0:
        return rc

    rc = skill_common.run_detect_secrets([], repo_root)
    if rc != 0:
        return rc

    if args.mode == "full":
        pre_commit_cmd = [*skill_common.resolve_tool_cmd("pre-commit", "pre_commit"), "run", "--all-files"]
        rc = skill_common.run_step("pre-commit run --all-files", pre_commit_cmd, repo_root)
        if rc != 0:
            return rc
        pip_lic_cmd = [*skill_common.resolve_tool_cmd("pip-licenses", "piplicenses")]
        rc = skill_common.run_step("pip-licenses", pip_lic_cmd, repo_root)
        if rc != 0:
            return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
