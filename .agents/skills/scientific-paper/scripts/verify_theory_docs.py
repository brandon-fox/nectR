"""Cross-platform documentation, secret-scan, and local-path verifier for scientific-paper."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common


def main() -> int:
    repo_root = skill_common.find_repo_root()
    target_dirs = [p for p in (repo_root / "paper", repo_root / "docs" / "theory") if p.exists()]
    target_files = [
        str(f.relative_to(repo_root))
        for d in target_dirs
        for f in d.rglob("*.md")
        if f.is_file()
    ]

    if target_files:
        rc = skill_common.run_detect_secrets(target_files, repo_root)
        if rc != 0:
            return rc
        rc = skill_common.check_no_local_paths(target_dirs, repo_root)
        if rc != 0:
            return rc

    return skill_common.run_mkdocs_strict(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
