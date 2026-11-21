"""Living documentation generator and drift checker for README spaces, tree, and mkdocs nav."""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from typing import Any

import yaml

BEGIN_SPACES_MARKER = "<!-- BEGIN AUTO-WORKSPACE-SPACES -->"
END_SPACES_MARKER = "<!-- END AUTO-WORKSPACE-SPACES -->"

EXCLUDED_TREE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "site",
        "node_modules",
    }
)

SPACE_DESCRIPTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "`paper/`",
        "Academic whitepaper, verified bibliography (`references.yaml`), & `lineage.yaml`",
        "`sci-research-agent`",
    ),
    (
        "`docs/`",
        "MkDocs portfolio site: `theory/`, `architecture/`, `business/`, `planning/`, `adr/`, `glossary.md`",
        "`sci-research-agent` / `system-arch-agent`",
    ),
    (
        "`business/`",
        "University Seed Comb sponsorship ROI models & multi-campus playbooks",
        "`business-proposal-agent`",
    ),
    (
        "`experiments/`",
        "Multi-semester Monte Carlo & adversarial simulation outputs",
        "`ux-behavior-agent`",
    ),
    (
        "`src/nectr/chain/`",
        "Hybrid `PoUW-PoW` ledger, Ed25519 signing, and Merkle state commitments",
        "`pow-compute-agent`",
    ),
    (
        "`src/nectr/contracts/`",
        "The 5 deterministic Hive smart contracts & supply-conservation FSMs",
        "`contracts-service-agent`",
    ),
    (
        "`src/nectr/services/`",
        "Hexagonal Hive Service Layer (Escrow, Knowledge Graph, Arbitration, Bridge)",
        "`contracts-service-agent`",
    ),
    (
        "`src/nectr/personas/`",
        "6 Behavioral Persona Sub-Agents executing signed transactions",
        "`ux-behavior-agent`",
    ),
    (
        "`src/nectr/ui/`",
        "Read-only Hive Explorer, Knowledge Graph & Comb reserve telemetry UI",
        "`design-ui-agent`",
    ),
    (
        "`src/nectr/devtools/`",
        "Zero-CVE `pyadr` MADR engine, decision registry, citation custody & docs sync",
        "`meta-orchestrator`",
    ),
    (
        "`openspec/` & `features/`",
        "OpenSpec requirement specs linked 1-to-1 to Behave Gherkin scenarios",
        "All agents",
    ),
    (
        "`tests/`",
        "Strict TDD (`xfail_strict`) unit, invariant, and governance test suites",
        "Domain owners",
    ),
)


class DocsSyncError(ValueError):
    """Raised when README spaces, IDE agnosticism, mkdocs nav, or orphan checks fail."""


class _MkDocsYamlLoader(yaml.SafeLoader):
    """SafeLoader subclass that ignores MkDocs Python-name tags cleanly."""


def _ignore_python_tag(loader: yaml.Loader, tag_suffix: str, node: yaml.Node) -> str:
    _ = loader, node
    return f"tag:{tag_suffix}"


_MkDocsYamlLoader.add_multi_constructor("tag:yaml.org,2002:python/", _ignore_python_tag)


def generate_tree(repo_root: Path, max_depth: int = 3) -> str:
    """Dynamically render the live monorepo directory tree from disk."""
    lines = [f"{repo_root.name}/"]

    def _walk(current: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        children = sorted(
            (
                p
                for p in current.iterdir()
                if p.name not in EXCLUDED_TREE_DIRS and not p.name.endswith(".egg-info")
            ),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
        for idx, child in enumerate(children):
            is_last = idx == len(children) - 1
            connector = "`-- " if is_last else "|-- "
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{prefix}{connector}{child.name}{suffix}")
            if child.is_dir():
                extension = "    " if is_last else "|   "
                _walk(child, prefix + extension, depth + 1)

    _walk(repo_root, "", 1)
    return "\n".join(lines)


def render_workspace_spaces_block(repo_root: Path) -> str:
    """Render bounded-context directory spaces after verifying top-level dirs exist."""
    rows = [
        BEGIN_SPACES_MARKER,
        "| Workspace Space | Purpose | Owning Agent |",
        "| :--- | :--- | :--- |",
    ]
    for space, desc, owner in SPACE_DESCRIPTIONS:
        first_dir = space.split("&", 1)[0].strip().strip("`").rstrip("/").split("/")[0]
        if not (repo_root / first_dir).exists():
            raise DocsSyncError(f"Expected workspace space '{first_dir}' missing on disk.")
        rows.append(f"| {space} | {desc} | {owner} |")
    rows.append(END_SPACES_MARKER)
    return "\n".join(rows)


def _read_adr_h1(adr_path: Path) -> str:
    for line in adr_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return adr_path.stem


def _build_expected_adr_nav_lines(repo_root: Path) -> list[str]:
    adr_dir = repo_root / "docs" / "adr"
    lines = [
        "      - Architecture Decision Records (MADR):",
        "          - ADR Index: adr/index.md",
        "          - ADR Lifecycle Guide: adr/lifecycle_guide.md",
    ]
    for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        adr_id = adr_file.stem.split("-", 1)[0]
        h1 = _read_adr_h1(adr_file)
        short = h1[:38].rstrip() + ("..." if len(h1) > 38 else "")
        lines.append(f'          - "{adr_id}: {short}": adr/{adr_file.name}')
    return lines


def render_synced_mkdocs(repo_root: Path) -> str:
    """Return mkdocs.yml text with Architecture Decision Records nav synced from docs/adr/."""
    mkdocs_path = repo_root / "mkdocs.yml"
    raw = mkdocs_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = raw.splitlines()
    start_idx: int | None = None
    end_idx: int | None = None
    for idx, ln in enumerate(lines):
        if ln.strip() == "- Architecture Decision Records (MADR):":
            start_idx = idx
            continue
        if start_idx is not None and not ln.startswith("          "):
            end_idx = idx
            break
    if start_idx is None:
        raise DocsSyncError("mkdocs.yml missing '- Architecture Decision Records (MADR):' section.")
    if end_idx is None:
        end_idx = len(lines)

    new_block = _build_expected_adr_nav_lines(repo_root)
    merged = lines[:start_idx] + new_block + lines[end_idx:]
    return "\n".join(merged) + "\n"


def _collect_nav_paths(node: Any) -> list[str]:
    collected: list[str] = []
    if isinstance(node, str):
        collected.append(node)
    elif isinstance(node, list):
        for item in node:
            collected.extend(_collect_nav_paths(item))
    elif isinstance(node, dict):
        for val in node.values():
            collected.extend(_collect_nav_paths(val))
    return collected


def sync_docs(repo_root: Path) -> None:
    """Update README.md workspace spaces block and mkdocs.yml ADR navigation."""
    readme_path = repo_root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    pattern = re.compile(
        re.escape(BEGIN_SPACES_MARKER) + r".*?" + re.escape(END_SPACES_MARKER),
        re.DOTALL,
    )
    spaces_block = render_workspace_spaces_block(repo_root)
    if not pattern.search(readme_text):
        raise DocsSyncError("README.md missing AUTO-WORKSPACE-SPACES markers.")
    updated_readme = pattern.sub(spaces_block, readme_text)
    readme_path.write_text(updated_readme, encoding="utf-8", newline="\n")

    mkdocs_path = repo_root / "mkdocs.yml"
    mkdocs_path.write_text(render_synced_mkdocs(repo_root), encoding="utf-8", newline="\n")


def check_docs_sync(repo_root: Path) -> dict[str, Any]:
    """Verify README spaces, IDE/skill agnosticism, mkdocs ADR nav sync, and zero orphan pages."""
    glossary_path = repo_root / "docs" / "glossary.md"
    if not glossary_path.exists():
        raise DocsSyncError("Missing docs/glossary.md.")

    readme_path = repo_root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if "Open as Active Workspace in Antigravity" in readme_text:
        raise DocsSyncError(
            "README.md must remain IDE-agnostic (remove Antigravity workspace lock-in)."
        )
    if "├──" in readme_text or "└──" in readme_text:
        raise DocsSyncError("README.md must not hardcode static ASCII directory trees.")
    if "docs/glossary.md" not in readme_text:
        raise DocsSyncError("README.md must link to docs/glossary.md.")

    expected_spaces = render_workspace_spaces_block(repo_root)
    readme_in_sync = expected_spaces in readme_text
    if not readme_in_sync:
        raise DocsSyncError(
            "README.md workspace spaces block is out of sync (run `nectr-docs sync`)."
        )

    mkdocs_path = repo_root / "mkdocs.yml"
    actual_mkdocs = mkdocs_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    expected_mkdocs = render_synced_mkdocs(repo_root)
    if actual_mkdocs != expected_mkdocs:
        raise DocsSyncError("mkdocs.yml ADR nav is out of sync (run `nectr-docs sync`).")

    parsed_mkdocs = yaml.load(actual_mkdocs, Loader=_MkDocsYamlLoader) or {}
    nav_files = set(_collect_nav_paths(parsed_mkdocs.get("nav", [])))
    exclude_raw = str(parsed_mkdocs.get("exclude_docs", ""))
    exclude_patterns = [ln.strip() for ln in exclude_raw.splitlines() if ln.strip()]

    docs_dir = repo_root / "docs"
    for nav_rel in sorted(nav_files):
        if not (docs_dir / nav_rel).exists():
            raise DocsSyncError(f"mkdocs.yml nav references missing file 'docs/{nav_rel}'.")

    orphan_pages: list[str] = []
    for md_file in sorted(docs_dir.rglob("*.md")):
        rel = md_file.relative_to(docs_dir).as_posix()
        if any(fnmatch.fnmatch(rel, pat) for pat in exclude_patterns):
            continue
        if rel not in nav_files:
            orphan_pages.append(rel)

    if orphan_pages:
        raise DocsSyncError(f"Orphaned docs pages missing from mkdocs.yml nav: {orphan_pages}")

    adr_nav_count = len(list((docs_dir / "adr").glob("[0-9][0-9][0-9][0-9]-*.md")))
    return {
        "orphan_pages": orphan_pages,
        "readme_in_sync": True,
        "mkdocs_adr_nav_in_sync": True,
        "adr_nav_count": adr_nav_count,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-docs",
        description="Generate live directory trees and verify README / mkdocs.yml synchronization.",
    )
    parser.add_argument("--root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Check README spaces, IDE agnosticism, and mkdocs nav sync.")
    sub.add_parser("sync", help="Sync README spaces and mkdocs.yml ADR nav entries.")
    tree_cmd = sub.add_parser("tree", help="Print the live monorepo directory tree.")
    tree_cmd.add_argument("--depth", type=int, default=3, help="Maximum directory depth.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "tree":
            print(generate_tree(root, max_depth=args.depth))
            return 0
        if args.command == "sync":
            sync_docs(root)
            print("Synced README.md spaces and mkdocs.yml ADR navigation.")
            return 0
        if args.command == "check":
            summary = check_docs_sync(root)
            print(f"Docs & Nav Sync OK (0 orphan pages, {summary['adr_nav_count']} ADRs synced).")
            return 0
    except (DocsSyncError, OSError, yaml.YAMLError) as exc:
        print(f"Docs sync error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
