"""Strict TDD tests for adrlint MADR 4.0 records, verbosity limits, and the fast YAML registry."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_adrs_and_fast_decision_log_pass_all_controls() -> None:
    """Repo docs/adr/ (adrlint) and docs/planning/decisions.yaml + decision_log.md must pass all gates."""
    from nectr.devtools.decisions import check_all_governance

    summary = check_all_governance(REPO_ROOT)
    assert summary["accepted_adr_count"] >= 15
    assert summary["adrlint_ok"] is True
    assert summary["toc_in_sync"] is True
    assert summary["decision_count"] >= 15
    assert summary["experiment_count"] >= 5
    assert summary["decision_log_in_sync"] is True


def test_adr_verbosity_limits_reject_excessive_lines_words_titles_and_bullets(
    tmp_path: Path,
) -> None:
    """MADR verbosity gate enforces line, word, title-length, and per-section bullet caps."""
    from nectr.devtools.decisions import DecisionGovernanceError, validate_adr_verbosity

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    # 1. Title > 70 chars rejected
    long_title = (
        "Establish Overly Verbose Architectural Decision Title Exceeding Seventy Characters Easily"
    )
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


def test_oss_adrlint_replaces_bespoke_adr_module_and_locks_decisions(tmp_path: Path) -> None:
    """Custom adr.py must not exist; OSS adrlint handles init, new, lint, format, and lock."""
    import shutil
    import subprocess
    import sys

    from nectr.devtools.decisions import DecisionGovernanceError, validate_adrlint_repo

    assert not (REPO_ROOT / "src" / "nectr" / "devtools" / "adr.py").exists()
    assert (REPO_ROOT / ".adrlint.toml").exists()
    assert (REPO_ROOT / "adrlint.lock").exists()

    adrlint_bin = shutil.which("adrlint") or str(
        Path(sys.executable).resolve().parent
        / ("adrlint.exe" if sys.platform == "win32" else "adrlint")
    )
    subprocess.run(
        [adrlint_bin, "init", "--dir", "docs/adr", "--start", "0", "--force"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run([adrlint_bin, "lock"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        [adrlint_bin, "new", "Evaluate Cache Adapter"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    with pytest.raises(DecisionGovernanceError, match="proposed"):
        validate_adrlint_repo(tmp_path, allow_proposed=False)

    assert validate_adrlint_repo(tmp_path, allow_proposed=True) == 1

    proposed_file = tmp_path / "docs" / "adr" / "0001-evaluate-cache-adapter.md"
    proposed_file.write_text(
        proposed_file.read_text(encoding="utf-8").replace(
            "status: proposed", "status: accepted", 1
        ),
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run([adrlint_bin, "lock"], cwd=tmp_path, check=True, capture_output=True, text=True)
    assert validate_adrlint_repo(tmp_path, allow_proposed=False) == 2


def test_n8n_workflow_decisions_adr_and_roadmap_options() -> None:
    """DEC-009 clarifies CrewAI/n8n while DEC-016, EXP-006, ADR-0016, and roadmap govern Milestone 3 options."""
    from nectr.devtools.decisions import (
        DecisionStatus,
        ExperimentStatus,
        check_all_governance,
        load_registry,
    )

    summary = check_all_governance(REPO_ROOT)
    assert summary["adrlint_ok"] is True
    assert summary["decision_log_in_sync"] is True

    registry = load_registry(REPO_ROOT / "docs" / "planning" / "decisions.yaml")
    decisions = {d.id: d for d in registry.decisions}
    experiments = {e.id: e for e in registry.experiments}

    dec009 = decisions["DEC-009"]
    assert dec009.status == DecisionStatus.LOCKED
    assert "CrewAI/n8n" in dec009.title
    assert "CrewAI/n8n" in dec009.decision
    assert "Mesa ABM" in dec009.decision

    assert "DEC-016" in decisions
    dec016 = decisions["DEC-016"]
    assert dec016.status == DecisionStatus.LOCKED
    assert "n8n" in dec016.decision
    assert "HiveServiceLayer" in dec016.decision
    assert dec016.related_adr == "docs/adr/0016-scope-external-workflow-automation-off-chain.md"

    assert "EXP-006" in experiments
    exp006 = experiments["EXP-006"]
    assert exp006.status == ExperimentStatus.OPEN_SIMULATION
    assert "n8n" in exp006.hypothesis
    assert exp006.related_adr == "docs/adr/0016-scope-external-workflow-automation-off-chain.md"

    adr_path = REPO_ROOT / "docs" / "adr" / "0016-scope-external-workflow-automation-off-chain.md"
    assert adr_path.exists()
    adr_text = adr_path.read_text(encoding="utf-8")
    assert "status: accepted" in adr_text
    assert "Sustainable Use License" in adr_text

    roadmap_path = REPO_ROOT / "docs" / "planning" / "roadmap.md"
    vision_path = REPO_ROOT / "docs" / "planning" / "vision.md"
    roadmap_text = (
        roadmap_path.read_text(encoding="utf-8")
        + "\n"
        + (vision_path.read_text(encoding="utf-8") if vision_path.exists() else "")
    )
    assert "CrewAI/n8n" in roadmap_text
    for option_tool in ("Activepieces", "Kestra", "Prefect", "Temporal", "EXP-006"):
        assert option_tool in roadmap_text


def test_vyper_pyevm_pactflow_and_jasss_grill_me_decisions_locked() -> None:
    """Verify ADR-0017, ADR-0018, DEC-017..020, Vyper/PactFlow OpenSpec proposals, and ODD+D framing."""
    from nectr.devtools.decisions import DecisionStatus, check_all_governance, load_registry

    summary = check_all_governance(REPO_ROOT)
    assert summary["accepted_adr_count"] >= 18
    assert summary["decision_count"] >= 20
    assert summary["adrlint_ok"] is True
    assert summary["decision_log_in_sync"] is True

    adr0017 = REPO_ROOT / "docs" / "adr" / "0017-adopt-vyper-and-zero-gas-py-evm-smart-contracts.md"
    adr0018 = (
        REPO_ROOT / "docs" / "adr" / "0018-enforce-pact-v4-and-pactflow-bi-directional-contracts.md"
    )
    assert adr0017.exists()
    assert adr0018.exists()
    assert "vyper" in adr0017.read_text(encoding="utf-8").lower()
    assert "py-evm" in adr0017.read_text(encoding="utf-8").lower()
    assert "pact-python" in adr0018.read_text(encoding="utf-8").lower()
    assert "pactflow" in adr0018.read_text(encoding="utf-8").lower()

    registry = load_registry(REPO_ROOT / "docs" / "planning" / "decisions.yaml")
    decisions = {d.id: d for d in registry.decisions}
    for dec_id in ("DEC-017", "DEC-018", "DEC-019", "DEC-020"):
        assert dec_id in decisions
        assert decisions[dec_id].status == DecisionStatus.LOCKED
    assert "micro_nectr" in decisions["DEC-017"].decision
    assert "10,000 bps" in decisions["DEC-018"].decision
    assert "secp256k1" in decisions["DEC-019"].decision
    assert "JASSS" in decisions["DEC-020"].decision
    assert "ODD+D" in decisions["DEC-020"].decision

    assert (
        REPO_ROOT / "openspec" / "changes" / "adopt-vyper-and-zero-gas-pyevm" / "proposal.md"
    ).exists()
    assert (
        REPO_ROOT
        / "openspec"
        / "changes"
        / "add-pactflow-api-and-message-contracts"
        / "proposal.md"
    ).exists()

    whitepaper_outline = (REPO_ROOT / "docs" / "theory" / "whitepaper_outline.md").read_text(
        encoding="utf-8"
    )
    assert "ODD+D" in whitepaper_outline
    assert "JASSS" in whitepaper_outline
