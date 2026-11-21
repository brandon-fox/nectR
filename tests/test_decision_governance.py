"""Strict TDD tests for pyadr MADR records, verbosity limits, and the fast YAML decision registry."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_adrs_and_fast_decision_log_pass_all_controls() -> None:
    """Repo docs/adr/ (pyadr) and docs/planning/decisions.yaml + decision_log.md must pass all gates."""
    from nectr.devtools.decisions import check_all_governance

    summary = check_all_governance(REPO_ROOT)
    assert summary["accepted_adr_count"] >= 8
    assert summary["toc_in_sync"] is True
    assert summary["decision_count"] >= 7
    assert summary["experiment_count"] >= 1
    assert summary["decision_log_in_sync"] is True


def test_adr_verbosity_limits_reject_excessive_lines_words_titles_and_bullets(tmp_path: Path) -> None:
    """MADR verbosity gate enforces line, word, title-length, and per-section bullet caps."""
    from nectr.devtools.decisions import DecisionGovernanceError, validate_adr_verbosity

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    # 1. Title > 70 chars rejected
    long_title = "Establish Overly Verbose Architectural Decision Title Exceeding Seventy Characters Easily"
    (adr_dir / "0002-long.md").write_text(
        f"# {long_title}\n\n* Status: accepted\n* Date: 2026-11-21\n\n"
        "## Context and Problem Statement\n\nShort.\n\n"
        "## Considered Options\n\n* A\n* B\n\n"
        '## Decision Outcome\n\nChosen option: "A", because concise.\n',
        encoding="utf-8",
    )
    with pytest.raises(DecisionGovernanceError, match="exceeds max title length"):
        validate_adr_verbosity(adr_dir)
    (adr_dir / "0002-long.md").unlink()

    # 2. > 6 bullets in a section rejected
    many_bullets = "\n".join(f"* Option {i}" for i in range(8))
    (adr_dir / "0002-bullets.md").write_text(
        "# Valid Title\n\n* Status: accepted\n* Date: 2026-11-21\n\n"
        "## Context and Problem Statement\n\nShort.\n\n"
        f"## Considered Options\n\n{many_bullets}\n\n"
        '## Decision Outcome\n\nChosen option: "Option 0", because concise.\n',
        encoding="utf-8",
    )
    with pytest.raises(DecisionGovernanceError, match="exceeds max bullets per section"):
        validate_adr_verbosity(adr_dir)
    (adr_dir / "0002-bullets.md").unlink()

    # 3. > 380 words in under 70 lines rejected
    wordy_paragraph = " ".join(["concise"] * 400)
    (adr_dir / "0002-words.md").write_text(
        "# Valid Title\n\n* Status: accepted\n* Date: 2026-11-21\n\n"
        f"## Context and Problem Statement\n\n{wordy_paragraph}\n\n"
        "## Considered Options\n\n* A\n* B\n\n"
        '## Decision Outcome\n\nChosen option: "A", because concise.\n',
        encoding="utf-8",
    )
    with pytest.raises(DecisionGovernanceError, match="exceeds max word limit"):
        validate_adr_verbosity(adr_dir)


def test_fast_decision_registry_rejects_verbose_entries_and_missing_links(tmp_path: Path) -> None:
    """Fast non-architectural decisions enforce concise 180-char summaries and verified file links."""
    from pydantic import ValidationError

    from nectr.devtools.decisions import (
        DecisionGovernanceError,
        DecisionRegistry,
        validate_registry_links,
    )

    with pytest.raises(ValidationError):
        DecisionRegistry.model_validate(
            {
                "schema_version": 1,
                "decisions": [
                    {
                        "id": "DEC-001",
                        "category": "parameter-default",
                        "status": "locked",
                        "title": "Short Parameter Title",
                        "decision": "x" * 200,  # Exceeds 180-char verbosity limit!
                        "owner_agent": "product-lifecycle-agent",
                    }
                ],
                "experiments": [],
            }
        )

    reg = DecisionRegistry.model_validate(
        {
            "schema_version": 1,
            "decisions": [
                {
                    "id": "DEC-001",
                    "category": "parameter-default",
                    "status": "locked",
                    "title": "Valid Concise Parameter Title",
                    "decision": "Apply 2%/month idle demurrage above safety buffer during Weeks 1-13.",
                    "owner_agent": "product-lifecycle-agent",
                    "related_adr": "docs/adr/9999-missing.md",
                }
            ],
            "experiments": [],
        }
    )
    with pytest.raises(DecisionGovernanceError, match="Missing related_adr file"):
        validate_registry_links(reg, tmp_path)


def test_cli_add_decision_updates_yaml_and_renders_markdown_in_sync(tmp_path: Path) -> None:
    """CLI `add` command appends a validated DEC entry and keeps decision_log.md in sync."""
    from nectr.devtools.decisions import DecisionRegistry, load_registry, main, render_decision_log

    planning = tmp_path / "docs" / "planning"
    adr_dir = tmp_path / "docs" / "adr"
    planning.mkdir(parents=True)
    adr_dir.mkdir(parents=True)
    (adr_dir / "index.md").write_text("# Architecture Decision Records\n", encoding="utf-8")

    seed_yaml = planning / "decisions.yaml"
    seed_yaml.write_text(
        "schema_version: 1\ndecisions: []\nexperiments: []\n",
        encoding="utf-8",
    )
    rc = main(
        [
            "--root",
            str(tmp_path),
            "add-decision",
            "--id",
            "DEC-001",
            "--category",
            "parameter-default",
            "--title",
            "Default Session Minimum Duration",
            "--decision",
            "Set structured tutoring minimum block to 25 minutes to prevent micro-payment crowding out.",
            "--owner",
            "ux-behavior-agent",
        ]
    )
    assert rc == 0
    reg: DecisionRegistry = load_registry(seed_yaml)
    assert len(reg.decisions) == 1
    rendered_file = (planning / "decision_log.md").read_text(encoding="utf-8")
    assert rendered_file == render_decision_log(reg, tmp_path)
    assert "DEC-001" in rendered_file


@pytest.mark.xfail(strict=True, reason="RED: remediate-review-issues-and-provenance")
def test_mit_adr_engine_supports_proposed_lifecycle_and_zero_external_pyadr(tmp_path: Path) -> None:
    """Zero-CVE nectr.devtools.adr replaces external pyadr and supports --allow-proposed."""
    from nectr.devtools.adr import AdrCore, AdrError, slugify_title
    from nectr.devtools.decisions import DecisionGovernanceError, main as decisions_main

    assert slugify_title("Adopt Ed25519 CanonicalJSON and Merklelib") == (
        "adopt-ed25519-canonicaljson-and-merklelib"
    )
    core = AdrCore(tmp_path)
    core.init_adr_repo()
    proposed = core.new_adr("Evaluate Cache Adapter")
    assert proposed.name == "XXXX-evaluate-cache-adapter.md"
    core.generate_toc()
    toc_text = (tmp_path / "docs" / "adr" / "index.md").read_text(encoding="utf-8")
    assert "Status `proposed`" in toc_text
    assert "XXXX - Evaluate Cache Adapter" in toc_text

    # Strict check fails on proposed ADR
    with pytest.raises(AdrError, match="proposed"):
        core.check_adr_repo(check_no_proposed=True)

    # --allow-proposed passes via CLI
    assert decisions_main(["--root", str(tmp_path), "check-adrs", "--allow-proposed"]) == 0

    # Accepting assigns 0002 and passes strict check
    accepted = core.accept_or_reject(proposed, "accepted", toc=True)
    assert accepted.name == "0002-evaluate-cache-adapter.md"
    core.check_adr_repo(check_no_proposed=True)

    # Docs README exists in repo docs/adr
    assert (REPO_ROOT / "docs" / "adr" / "README.md").exists()
    with pytest.raises(DecisionGovernanceError):
        raise DecisionGovernanceError("sanity check type")
