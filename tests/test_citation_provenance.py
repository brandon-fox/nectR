"""Strict TDD tests for citation validation and provenance chain-of-custody."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_citations_and_provenance_pass_all_gates() -> None:
    """Repo paper/references.yaml, lineage.yaml, and provenance_lineage.md pass quality gates."""
    from nectr.devtools.citations import check_all_citations

    summary = check_all_citations(REPO_ROOT)
    assert summary["external_reference_count"] >= 14
    assert summary["peer_reviewed_ratio"] >= 0.70
    assert summary["quarantined_count"] == 0
    assert summary["report_in_sync"] is True


def test_citation_validator_blocks_banned_domains_low_ratio_and_missing_doi() -> None:
    """Quality floor rejects banned URLs, <70% peer-reviewed ratio, and missing DOI/URL."""
    from nectr.devtools.citations import (
        CitationGovernanceError,
        ReferenceEntry,
        ReferenceRegistry,
        validate_references,
    )

    bad_domain = ReferenceRegistry(
        references=[
            ReferenceEntry(
                id="bad_1",
                title="Wiki Claim",
                authors=["Anon"],
                year=2025,
                source_type="secondary-web",
                url="https://en.wikipedia.org/wiki/Tokenomics",
                custody_agent="sci-research-agent",
            )
        ]
    )
    with pytest.raises(CitationGovernanceError, match="banned domain"):
        validate_references(bad_domain)

    low_ratio = ReferenceRegistry(
        references=[
            ReferenceEntry(
                id="pr_1",
                title="Journal Paper",
                authors=["Smith, A."],
                year=2020,
                source_type="peer-reviewed-journal",
                doi="10.1000/test1",
                url="https://pubmed.ncbi.nlm.nih.gov/12345/",
                custody_agent="sci-research-agent",
            ),
            ReferenceEntry(
                id="ind_1",
                title="Spec 1",
                authors=["Org A"],
                year=2021,
                source_type="technical-spec",
                url="https://entethalliance.org/spec1",
                custody_agent="sci-research-agent",
            ),
            ReferenceEntry(
                id="ind_2",
                title="Spec 2",
                authors=["Org B"],
                year=2022,
                source_type="technical-spec",
                url="https://datatracker.ietf.org/doc/draft-test",
                custody_agent="sci-research-agent",
            ),
        ]
    )
    with pytest.raises(CitationGovernanceError, match="peer-reviewed ratio"):
        validate_references(low_ratio)


def test_lineage_graph_propagates_quarantine_blast_radius(tmp_path: Path) -> None:
    """Flawed upstream source marks all transitive downstream artifacts for rebuild."""
    from nectr.devtools.citations import (
        CitationGovernanceError,
        LineageEdge,
        LineageGraph,
        LineageNode,
        ReferenceEntry,
        ReferenceRegistry,
        compute_impacted_downstream,
        render_provenance_report,
    )

    (tmp_path / "docs" / "theory").mkdir(parents=True)
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "src" / "nectr").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "docs" / "theory" / "t.md").write_text("# T\n", encoding="utf-8")
    (tmp_path / "docs" / "adr" / "0001-a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "src" / "nectr" / "m.py").write_text("", encoding="utf-8")
    (tmp_path / "tests" / "test_m.py").write_text("", encoding="utf-8")

    refs = ReferenceRegistry(
        references=[
            ReferenceEntry(
                id="s_bad",
                title="Retracted Paper",
                authors=["Doe, J."],
                year=2019,
                source_type="peer-reviewed-journal",
                doi="10.1000/retracted",
                url="https://arxiv.org/abs/1901.00001",
                custody_agent="sci-research-agent",
                plagiarism_screen="flagged",
                status="quarantined",
            )
        ]
    )
    lineage = LineageGraph(
        nodes=[
            LineageNode(
                id="source:s_bad", kind="source", label="Retracted", path="paper/references.yaml"
            ),
            LineageNode(id="theory:eq1", kind="theory", label="Eq 1", path="docs/theory/t.md"),
            LineageNode(
                id="decision:ADR-0001", kind="decision", label="ADR 1", path="docs/adr/0001-a.md"
            ),
            LineageNode(
                id="code:m",
                kind="code",
                label="Module M",
                path="src/nectr/m.py",
                test_path="tests/test_m.py",
            ),
        ],
        edges=[
            LineageEdge(source="source:s_bad", target="theory:eq1", intent="justifies"),
            LineageEdge(source="theory:eq1", target="decision:ADR-0001", intent="drives"),
            LineageEdge(source="decision:ADR-0001", target="code:m", intent="implements"),
        ],
    )
    impacted = compute_impacted_downstream(lineage, "s_bad")
    assert impacted == ["code:m", "decision:ADR-0001", "theory:eq1"]

    with pytest.raises(CitationGovernanceError, match="quarantined"):
        render_provenance_report(refs, lineage, tmp_path, allow_quarantined=False)

    rebuilt = render_provenance_report(refs, lineage, tmp_path, allow_quarantined=True)
    assert "REBUILD REQUIRED" in rebuilt
    assert "code:m" in rebuilt
