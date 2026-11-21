"""Strict TDD tests for glossary, living docs sync, git hygiene, and persona extras."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.xfail(strict=True, reason="RED: remediate-review-issues-and-provenance")
def test_handoff_untracked_gitattributes_and_zero_cve_persona_extras() -> None:
    """Verify HANDOFF.md is untracked, LF normalization exists, and dev extras have no pyadr."""
    ls_handoff = subprocess.run(
        ["git", "ls-files", "HANDOFF.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert ls_handoff.stdout.strip() == ""

    gitattr = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in gitattr

    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    opt_deps = pyproject["project"]["optional-dependencies"]
    for group in ("test", "lint", "security", "docs", "research", "dev"):
        assert group in opt_deps
    assert not any("pyadr" in item for item in opt_deps["dev"])
    assert pyproject["tool"]["mypy"].get("overrides") is None


@pytest.mark.xfail(strict=True, reason="RED: remediate-review-issues-and-provenance")
def test_glossary_and_ide_agnostic_readme() -> None:
    """Verify docs/glossary.md defines core acronyms and README has no IDE lock-in or static tree."""
    glossary = (REPO_ROOT / "docs" / "glossary.md").read_text(encoding="utf-8")
    for term in ("MV = PQ", "PoUW-PoW", "RAW_POLLEN", "LIQUID_NECTR", "Beekeeper"):
        assert term in glossary

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Open as Active Workspace in Antigravity" not in readme
    assert "├──" not in readme
    assert "docs/glossary.md" in readme
    assert "Fisher" in readme


@pytest.mark.xfail(strict=True, reason="RED: remediate-review-issues-and-provenance")
def test_docs_sync_passes_with_zero_orphan_pages_and_synced_nav() -> None:
    """Verify nectr.devtools.docs_sync confirms zero orphan docs pages and synced mkdocs nav."""
    from nectr.devtools.docs_sync import check_docs_sync

    summary = check_docs_sync(REPO_ROOT)
    assert summary["orphan_pages"] == []
    assert summary["readme_in_sync"] is True
    assert summary["mkdocs_adr_nav_in_sync"] is True
    assert summary["adr_nav_count"] >= 12
