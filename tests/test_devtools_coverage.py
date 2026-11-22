"""Comprehensive edge-case and CLI tests for nectR devtools governance & sync modules."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import pytest

from nectr.devtools import citations, decisions, docs_sync, spec_links
from nectr.devtools.ci_parity import check_no_red_scenarios, check_workflow_action_hygiene

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_docs_sync_tree_sync_cli_and_error_guards(tmp_path: Path) -> None:
    tree_str = docs_sync.generate_tree(REPO_ROOT, max_depth=2)
    assert "src/" in tree_str
    assert docs_sync.main(["--root", str(REPO_ROOT), "tree", "--depth", "1"]) == 0
    assert docs_sync.main(["--root", str(REPO_ROOT), "check"]) == 0

    # Missing glossary error
    assert docs_sync.main(["--root", str(tmp_path), "check"]) == 1

    # Build a minimal valid synthetic workspace to test sync_docs() and drift checks
    for top in (
        "paper",
        "docs/adr",
        "business",
        "experiments",
        "src",
        "openspec",
        "tests",
    ):
        (tmp_path / top).mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "glossary.md").write_text("# Glossary\n", encoding="utf-8")
    (tmp_path / "docs" / "index.md").write_text("# Home\n", encoding="utf-8")
    (tmp_path / "docs" / "adr" / "0001-sample.md").write_text(
        "---\nstatus: accepted\n---\n# Sample Decision Title\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "adr" / "index.md").write_text(
        f"# ADRs\n{docs_sync.BEGIN_ADR_INDEX_MARKER}\nold\n{docs_sync.END_ADR_INDEX_MARKER}\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        f"# nectR\nSee [glossary](docs/glossary.md).\n"
        f"{docs_sync.BEGIN_SPACES_MARKER}\nold\n{docs_sync.END_SPACES_MARKER}\n",
        encoding="utf-8",
    )
    (tmp_path / "mkdocs.yml").write_text(
        "nav:\n"
        "  - Home: index.md\n"
        "  - Glossary: glossary.md\n"
        "  - Planning:\n"
        "      - Architecture Decision Records (MADR):\n"
        "          - ADR Index: adr/index.md\n",
        encoding="utf-8",
    )

    assert docs_sync.main(["--root", str(tmp_path), "sync"]) == 0
    assert docs_sync.main(["--root", str(tmp_path), "check"]) == 0

    # Orphan doc detection
    (tmp_path / "docs" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
    with pytest.raises(docs_sync.DocsSyncError, match="Orphaned docs pages"):
        docs_sync.check_docs_sync(tmp_path)
    (tmp_path / "docs" / "orphan.md").unlink()

    # IDE lock-in & static tree rejection
    (tmp_path / "README.md").write_text(
        "Open as Active Workspace in Antigravity\n", encoding="utf-8"
    )
    with pytest.raises(docs_sync.DocsSyncError, match="IDE-agnostic"):
        docs_sync.check_docs_sync(tmp_path)


def test_spec_links_cli_and_error_paths(tmp_path: Path) -> None:
    assert spec_links.main([str(REPO_ROOT)]) == 0
    assert spec_links.main([str(tmp_path)]) == 1

    spec_dir = tmp_path / "openspec" / "specs" / "demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Demo\nSee [ext](https://example.com) and [broken](../../../features/missing.feature).\n",
        encoding="utf-8",
    )
    assert spec_links.main([str(tmp_path)]) == 1


def test_citations_cli_quarantine_render_and_validation_guards(tmp_path: Path) -> None:
    assert citations.main(["--root", str(REPO_ROOT), "check"]) == 0
    assert citations.main(["--root", str(REPO_ROOT), "impact", "unknown_ref_id"]) == 0
    assert citations.main(["--root", str(tmp_path), "check"]) == 1

    # Duplicate ID & empty registry guards
    with pytest.raises(ValueError, match="Duplicate reference ID"):
        citations.ReferenceRegistry(
            references=[
                citations.ReferenceEntry(
                    id="dup_1",
                    title="First Paper Title",
                    authors=["A"],
                    year=2020,
                    source_type=citations.SourceType.PEER_REVIEWED_JOURNAL,
                    doi="10.1000/1",
                    custody_agent="sci-research-agent",
                ),
                citations.ReferenceEntry(
                    id="dup_1",
                    title="Second Paper Title",
                    authors=["B"],
                    year=2021,
                    source_type=citations.SourceType.PEER_REVIEWED_JOURNAL,
                    doi="10.1000/2",
                    custody_agent="sci-research-agent",
                ),
            ]
        )

    with pytest.raises(citations.CitationGovernanceError, match="cannot be empty"):
        citations.validate_references(citations.ReferenceRegistry(references=[]))

    # Missing DOI/URL on external ref
    no_doi_reg = citations.ReferenceRegistry(
        references=[
            citations.ReferenceEntry(
                id="ext_1",
                title="Missing Identifier Paper",
                authors=["Author"],
                year=2022,
                source_type=citations.SourceType.PEER_REVIEWED_JOURNAL,
                custody_agent="sci-research-agent",
            )
        ]
    )
    with pytest.raises(
        citations.CitationGovernanceError, match="must provide a DOI or archival URL"
    ):
        citations.validate_references(no_doi_reg)

    # Render with --allow-quarantined on a copy of paper/ + docs/theory/
    (tmp_path / "paper").mkdir(parents=True)
    (tmp_path / "docs" / "theory").mkdir(parents=True)
    (tmp_path / "paper" / "references.yaml").write_text(
        "schema_version: 1\n"
        "references:\n"
        "  - id: clean_ref\n"
        "    title: Clean Primary Journal Study\n"
        "    authors: ['Seeley, T. D.']\n"
        "    year: 2010\n"
        "    source_type: peer-reviewed-journal\n"
        "    doi: 10.1000/clean\n"
        "    custody_agent: sci-research-agent\n"
        "  - id: tainted_ref\n"
        "    title: Flagged Preprint Source\n"
        "    authors: ['Anon']\n"
        "    year: 2023\n"
        "    source_type: peer-reviewed-journal\n"
        "    doi: 10.1000/tainted\n"
        "    custody_agent: sci-research-agent\n"
        "    plagiarism_screen: flagged\n"
        "    status: quarantined\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "theory" / "doc.md").write_text("# Doc\n", encoding="utf-8")
    (tmp_path / "paper" / "lineage.yaml").write_text(
        "schema_version: 1\n"
        "nodes:\n"
        "  - id: source:tainted_ref\n"
        "    kind: source\n"
        "    label: Tainted\n"
        "    path: paper/references.yaml\n"
        "  - id: theory:doc\n"
        "    kind: theory\n"
        "    label: Theory Doc\n"
        "    path: docs/theory/doc.md\n"
        "edges:\n"
        "  - source: source:tainted_ref\n"
        "    target: theory:doc\n"
        "    intent: Supports model\n",
        encoding="utf-8",
    )
    assert citations.main(["--root", str(tmp_path), "render"]) == 1
    assert citations.main(["--root", str(tmp_path), "render", "--allow-quarantined"]) == 0
    assert citations.main(["--root", str(tmp_path), "impact", "tainted_ref"]) == 0


def test_decisions_cli_and_frontmatter_guards(tmp_path: Path) -> None:
    assert decisions.main(["--root", str(REPO_ROOT), "check"]) == 0
    assert decisions.main(["--root", str(REPO_ROOT), "check-adrs"]) == 0
    assert decisions.main(["--root", str(tmp_path), "check"]) == 1

    # Unterminated / non-mapping front matter & verbosity checks
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    bad_adr = adr_dir / "0001-bad.md"
    bad_adr.write_text("---\nunterminated\n", encoding="utf-8")
    with pytest.raises(decisions.DecisionGovernanceError, match="Unterminated YAML front matter"):
        decisions.validate_adr_verbosity(adr_dir)

    bad_adr.write_text("---\n- list_not_dict\n---\n# Title\n", encoding="utf-8")
    with pytest.raises(decisions.DecisionGovernanceError, match="must be a mapping"):
        decisions.validate_adr_verbosity(adr_dir)

    bad_adr.write_text("---\nstatus: accepted\n---\nNo H1 here\n", encoding="utf-8")
    with pytest.raises(decisions.DecisionGovernanceError, match="Missing H1"):
        decisions.validate_adr_verbosity(adr_dir)

    # Exercise render & add-decision in isolated copy
    (tmp_path / "docs" / "planning").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / "docs" / "planning" / "decisions.yaml",
        tmp_path / "docs" / "planning" / "decisions.yaml",
    )
    # Copy referenced files so validate_registry_links succeeds on tmp_path
    reg = decisions.load_registry(tmp_path / "docs" / "planning" / "decisions.yaml")
    for item in [*reg.decisions, *reg.experiments]:
        for rel in (
            getattr(item, "related_adr", None),
            getattr(item, "openspec_ref", None),
            getattr(item, "protocol_path", None),
        ):
            if rel:
                src = REPO_ROOT / rel
                dst = tmp_path / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_file():
                    shutil.copy2(src, dst)
                elif src.is_dir():
                    dst.mkdir(parents=True, exist_ok=True)

    assert decisions.main(["--root", str(tmp_path), "render"]) == 0
    assert (
        decisions.main(
            [
                "--root",
                str(tmp_path),
                "add-decision",
                "--id",
                "DEC-099",
                "--category",
                "workflow-policy",
                "--title",
                "Enforce PR rebase queue and 90% branch coverage",
                "--decision",
                "Require rebase-linear PR branches, Commitizen titles, and 90% branch coverage.",
                "--owner",
                "meta-orchestrator",
            ]
        )
        == 0
    )


def test_ci_parity_edge_cases(tmp_path: Path) -> None:
    assert check_workflow_action_hygiene(tmp_path) == ["Missing .github/workflows directory."]
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    assert check_workflow_action_hygiene(tmp_path) == [
        "No GitHub Actions workflow YAML files found under .github/workflows."
    ]
    (wf_dir / "bad.yml").write_text("- not_a_mapping\n", encoding="utf-8")
    assert "must be a YAML mapping" in check_workflow_action_hygiene(tmp_path)[0]

    feat = tmp_path / "sample.feature"
    feat.write_text("Feature: X\n  @red\n  Scenario: S\n    Given a\n", encoding="utf-8")
    assert check_no_red_scenarios(tmp_path, feature_files=[feat]) == ["sample.feature:2"]


def test_pyproject_license_and_author_metadata() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    assert project.get("license") == "MIT"
    assert project.get("license-files") == ["LICENSE"]
    assert (REPO_ROOT / "LICENSE").is_file()
    authors = project.get("authors", [])
    assert any(
        isinstance(author, dict)
        and author.get("name") == "Brandon Fox"
        and author.get("email") == "32090240+brandon-fox@users.noreply.github.com"
        for author in authors
    )


@pytest.mark.xfail(
    strict=True,
    reason="RED: TL4 runtime dependencies not yet trimmed",
)
def test_pyproject_runtime_deps_trimmed() -> None:
    import re

    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    runtime_names = {
        re.split(r"[<>=!~;\[\s]", dep, maxsplit=1)[0].lower()
        for dep in project.get("dependencies", [])
    }
    for dropped_or_moved in ("numpy", "rich", "httpx", "uvicorn"):
        assert dropped_or_moved not in runtime_names

    opt_deps = project["optional-dependencies"]
    test_names = {
        re.split(r"[<>=!~;\[\s]", dep, maxsplit=1)[0].lower() for dep in opt_deps.get("test", [])
    }
    api_names = {
        re.split(r"[<>=!~;\[\s]", dep, maxsplit=1)[0].lower() for dep in opt_deps.get("api", [])
    }
    assert "httpx" in test_names
    assert "uvicorn" in api_names
    assert any("api" in item for item in opt_deps.get("dev", []))
