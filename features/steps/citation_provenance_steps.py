"""Step definitions for Citation Validation and Provenance Chain-of-Custody BDD feature."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]


@given("a temporary citation registry containing a banned wiki URL")
def step_given_banned_ref(context) -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_cit_bad_"))
    (tmp_dir / "paper").mkdir(parents=True)
    (tmp_dir / "paper" / "references.yaml").write_text(
        "schema_version: 1\n"
        "references:\n"
        "  - id: bad_wiki_1\n"
        "    title: Capitol Hill Wiki Summary\n"
        "    authors: ['Unknown']\n"
        "    year: 2026\n"
        "    source_type: secondary-web\n"
        "    url: https://en.wikipedia.org/wiki/Capitol_Hill_Babysitting_Co-op\n"
        "    custody_agent: sci-research-agent\n"
        "    plagiarism_screen: clean\n"
        "    status: verified\n",
        encoding="utf-8",
    )
    context.temp_dir = tmp_dir
    context.cit_error = None


@when("the citation quality validator checks the temporary registry")
def step_when_cit_check_temp(context) -> None:
    from nectr.devtools.citations import CitationGovernanceError, load_references, validate_references

    try:
        refs = load_references(context.temp_dir / "paper" / "references.yaml")
        validate_references(refs)
    except CitationGovernanceError as exc:
        context.cit_error = exc
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then('citation validation fails with "{expected_substring}"')
def step_then_cit_fails(context, expected_substring: str) -> None:
    assert context.cit_error is not None, "Expected CitationGovernanceError, but validation passed"
    assert expected_substring in str(context.cit_error).lower()


@given('a temporary lineage workspace where source "{bad_ref}" has failed plagiarism screening')
def step_given_tainted_lineage(context, bad_ref: str) -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_cit_taint_"))
    (tmp_dir / "paper").mkdir(parents=True)
    (tmp_dir / "docs" / "theory").mkdir(parents=True)
    (tmp_dir / "docs" / "adr").mkdir(parents=True)
    (tmp_dir / "src" / "nectr").mkdir(parents=True)
    (tmp_dir / "tests").mkdir(parents=True)

    (tmp_dir / "docs" / "theory" / "eq.md").write_text("# Eq\n", encoding="utf-8")
    (tmp_dir / "docs" / "adr" / "0002-test.md").write_text("# Test ADR\n", encoding="utf-8")
    (tmp_dir / "src" / "nectr" / "mod.py").write_text("# mod\n", encoding="utf-8")
    (tmp_dir / "tests" / "test_mod.py").write_text("# test\n", encoding="utf-8")

    (tmp_dir / "paper" / "references.yaml").write_text(
        "schema_version: 1\n"
        "references:\n"
        "  - id: good_journal_1\n"
        "    title: Monetary Theory Paper\n"
        "    authors: ['Sweeney, J.', 'Sweeney, R.']\n"
        "    year: 1977\n"
        "    source_type: peer-reviewed-journal\n"
        "    doi: 10.2307/1991998\n"
        "    url: https://www.jstor.org/stable/1991998\n"
        "    custody_agent: sci-research-agent\n"
        "    plagiarism_screen: clean\n"
        "    status: verified\n"
        f"  - id: {bad_ref}\n"
        "    title: Quarantined Source\n"
        "    authors: ['Flagged, A.']\n"
        "    year: 2020\n"
        "    source_type: peer-reviewed-journal\n"
        "    doi: 10.0000/flagged\n"
        "    url: https://arxiv.org/abs/0000.0000\n"
        "    custody_agent: sci-research-agent\n"
        "    plagiarism_screen: flagged\n"
        "    status: quarantined\n",
        encoding="utf-8",
    )
    (tmp_dir / "paper" / "lineage.yaml").write_text(
        "schema_version: 1\n"
        "nodes:\n"
        f"  - id: source:{bad_ref}\n"
        "    kind: source\n"
        "    label: Quarantined Source\n"
        "    path: paper/references.yaml\n"
        "  - id: theory:eq_quarantined\n"
        "    kind: theory\n"
        "    label: Derived Equation\n"
        "    path: docs/theory/eq.md\n"
        "  - id: decision:ADR-0002\n"
        "    kind: decision\n"
        "    label: Test ADR\n"
        "    path: docs/adr/0002-test.md\n"
        "  - id: code:mod\n"
        "    kind: code\n"
        "    label: Downstream Module\n"
        "    path: src/nectr/mod.py\n"
        "    test_path: tests/test_mod.py\n"
        "edges:\n"
        f"  - source: source:{bad_ref}\n"
        "    target: theory:eq_quarantined\n"
        "    intent: mathematically justifies\n"
        "  - source: theory:eq_quarantined\n"
        "    target: decision:ADR-0002\n"
        "    intent: drives architectural invariant\n"
        "  - source: decision:ADR-0002\n"
        "    target: code:mod\n"
        "    intent: enforced in implementation\n",
        encoding="utf-8",
    )
    context.temp_dir = tmp_dir
    context.rendered_provenance = ""


@when("the provenance renderer rebuilds the lineage report with allow-quarantined")
def step_when_render_quarantined(context) -> None:
    from nectr.devtools.citations import (
        load_lineage,
        load_references,
        render_provenance_report,
    )

    try:
        refs = load_references(context.temp_dir / "paper" / "references.yaml")
        lineage = load_lineage(context.temp_dir / "paper" / "lineage.yaml")
        context.rendered_provenance = render_provenance_report(
            refs, lineage, context.temp_dir, allow_quarantined=True
        )
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then("the rendered provenance report flags downstream theory, ADR, and code artifacts for rebuild")
def step_then_report_flags_rebuild(context) -> None:
    text = context.rendered_provenance
    assert "REBUILD REQUIRED" in text
    assert "theory:eq_quarantined" in text
    assert "decision:ADR-0002" in text
    assert "code:mod" in text


@given("the repository root citation and lineage workspace")
def step_given_repo_cit(context) -> None:
    context.repo_root = REPO_ROOT
    context.cit_summary = None
    context.cit_error = None


@when("the full citation and provenance check runs")
def step_when_repo_cit_check(context) -> None:
    from nectr.devtools.citations import CitationGovernanceError, check_all_citations

    try:
        context.cit_summary = check_all_citations(context.repo_root)
    except CitationGovernanceError as exc:
        context.cit_error = exc


@then("citation validation succeeds with peer-reviewed ratio at least {min_ratio:f} and report in sync")
def step_then_repo_cit_ok(context, min_ratio: float) -> None:
    assert context.cit_error is None, f"Unexpected error: {context.cit_error}"
    assert context.cit_summary is not None
    assert context.cit_summary["peer_reviewed_ratio"] >= min_ratio
    assert context.cit_summary["report_in_sync"] is True
