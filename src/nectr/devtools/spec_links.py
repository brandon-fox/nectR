"""Validate that OpenSpec spec.md files link to Behave features instead of hardcoding scenarios."""

from __future__ import annotations

import re
import sys
from pathlib import Path

FORBIDDEN_SCENARIO_RE = re.compile(
    r"^\s*(?:####\s*Scenario:|[-*]\s*\*\*(?:GIVEN|WHEN|THEN|AND)\*\*)",
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#\s]+)(?:#[^)\s]+)?\)")


class SpecLinkError(ValueError):
    """Raised when an OpenSpec spec.md violates feature-linking or scenario rules."""


def _iter_spec_files(repo_root: Path) -> list[Path]:
    openspec_dir = repo_root / "openspec"
    if not openspec_dir.exists():
        return []
    specs: list[Path] = []
    for path in sorted(openspec_dir.rglob("spec.md")):
        rel_parts = path.relative_to(openspec_dir).parts
        if "archive" in rel_parts:
            continue
        specs.append(path)
    return specs


def validate_spec_links(repo_root: Path) -> list[Path]:
    """Ensure every OpenSpec spec.md links to existing .feature and _steps.py files."""
    spec_files = _iter_spec_files(repo_root)
    if not spec_files:
        raise SpecLinkError(f"No OpenSpec spec.md files found under {repo_root / 'openspec'}.")

    for spec_path in spec_files:
        rel_spec = spec_path.relative_to(repo_root).as_posix()
        content = spec_path.read_text(encoding="utf-8")

        for line_no, line in enumerate(content.splitlines(), start=1):
            if FORBIDDEN_SCENARIO_RE.match(line):
                raise SpecLinkError(
                    f"{rel_spec}:{line_no}: contains hardcoded scenario/Given-When-Then block; "
                    "move scenarios to features/*.feature and link them."
                )

        has_feature_link = False
        has_steps_link = False
        for raw_target in MARKDOWN_LINK_RE.findall(content):
            if raw_target.startswith(("http://", "https://")):
                continue
            resolved = (spec_path.parent / raw_target).resolve()
            if not resolved.exists():
                raise SpecLinkError(f"{rel_spec}: broken link target '{raw_target}'.")
            if resolved.suffix == ".feature" and "features" in resolved.parts:
                has_feature_link = True
            if resolved.name.endswith("_steps.py") and "steps" in resolved.parts:
                has_steps_link = True

        if not has_feature_link or not has_steps_link:
            raise SpecLinkError(
                f"{rel_spec}: missing linked features/*.feature and/or features/steps/*_steps.py."
            )

    return spec_files


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[3]
    try:
        specs = validate_spec_links(root)
    except SpecLinkError as exc:
        print(f"SPEC LINK GATE FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"OpenSpec feature-link check passed ({len(specs)} spec(s) verified).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
