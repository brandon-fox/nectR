#!/usr/bin/env python3
"""Conventional Commits validator for nectR git commit-msg hook.

Enforces: <type>(<optional-scope>)<!>: <description>
Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CONVENTIONAL_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9][a-z0-9._/-]*\))?"
    r"(!)?:\s+.+$"
)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: validate_commit_msg.py <commit-msg-file>", file=sys.stderr)
        return 1

    msg_path = Path(args[0])
    lines = [
        line
        for line in msg_path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    if not lines or not lines[0].strip():
        print("COMMIT REJECTED: Empty commit message.", file=sys.stderr)
        return 1

    subject = lines[0].strip()
    if subject.startswith(("Merge ", "Revert ")):
        return 0

    if not CONVENTIONAL_PATTERN.match(subject):
        print(
            "COMMIT REJECTED: Commit subject must follow Conventional Commits:\n"
            "  <type>(<optional-scope>): <description>\n"
            "  Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert\n"
            f"  Got: {subject!r}",
            file=sys.stderr,
        )
        return 1

    if len(subject) > 100:
        print(
            f"COMMIT REJECTED: Commit subject exceeds 100 chars ({len(subject)}).",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
