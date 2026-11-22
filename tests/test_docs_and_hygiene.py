"""Strict TDD tests for glossary, living docs sync, git hygiene, and persona extras."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_handoff_untracked_gitattributes_and_zero_cve_persona_extras() -> None:
    """Verify HANDOFF.md is untracked, LF normalization exists, and dev uses MIT adrlint."""
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
    assert any("adrlint" in item for item in opt_deps["lint"])
    assert not any("pyadr" in item for item in opt_deps["dev"])
    assert pyproject["tool"]["mypy"].get("overrides") is None


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


def test_docs_sync_passes_with_zero_orphan_pages_and_synced_nav() -> None:
    """Verify nectr.devtools.docs_sync confirms zero orphan docs pages and synced mkdocs nav."""
    from nectr.devtools.docs_sync import check_docs_sync

    summary = check_docs_sync(REPO_ROOT)
    assert summary["orphan_pages"] == []
    assert summary["readme_in_sync"] is True
    assert summary["mkdocs_adr_nav_in_sync"] is True
    assert summary["adr_nav_count"] >= 15


def test_six_deep_research_tracks_and_five_wave_swarm_plan_documented() -> None:
    """Verify all 6 deep research tracks, 5 roadmap milestones, and 5 swarm waves are documented."""
    prompts = (REPO_ROOT / "docs" / "planning" / "deep_research_prompts.md").read_text(
        encoding="utf-8"
    )
    for report in (
        "federated_barter_tokenomics.md",
        "student_tutoring_mechanism_design.md",
        "biomimetic_hive_economics.md",
        "permissive_tooling_survey_for_nectR.md",
        "federated_PoUW-PoW_blockchain_infrastructure.md",
        "nectR_funding_and_pilot_strategy.md",
    ):
        assert report in prompts

    roadmap = (REPO_ROOT / "docs" / "planning" / "roadmap.md").read_text(encoding="utf-8")
    vision = (REPO_ROOT / "docs" / "planning" / "vision.md").read_text(encoding="utf-8")
    assert "Milestone 5:" in roadmap or "Milestone 5:" in vision
    assert "Apereo Foundation" in roadmap or "Apereo Foundation" in vision

    orchestration = (REPO_ROOT / "docs" / "planning" / "agent_orchestration.md").read_text(
        encoding="utf-8"
    )
    assert "Swarm Wave 1" in orchestration
    assert "Swarm Wave 5" in orchestration


def test_structure_freeze_until_v010() -> None:
    """Verify AGENTS.md has structure freeze section and agent_orchestration.md has superseded banner."""
    agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Structure Freeze Until v0.1.0" in agents_md or "Freeze Until v0.1.0" in agents_md
    assert (
        "no new ADRs, change proposals, skills, workflows or gates outside the Plan to B+ until v0.1.0"
        in agents_md
    )

    orchestration = (REPO_ROOT / "docs" / "planning" / "agent_orchestration.md").read_text(
        encoding="utf-8"
    )
    assert "superseded for current work by the Plan to B+" in orchestration
    assert "Waves 3 to 5 are out of scope until after v0.1.0" in orchestration


def test_readme_plain_language_status_independence_and_license() -> None:
    """Verify README has status line within 10 lines, Independence section, and license link."""
    readme_lines = (REPO_ROOT / "README.md").read_text(encoding="utf-8").splitlines()

    assert readme_lines[0].startswith("# ")

    status_lines = [line for line in readme_lines[:10] if line.startswith("> **Status:**")]
    assert len(status_lines) == 1
    assert "research prototype" in status_lines[0]

    readme = "\n".join(readme_lines)
    assert "## Independence" in readme
    assert "This is a personal project by Brandon Fox" in readme
    assert "First-ADE/PRINCIPLES.md" in readme

    license_path = REPO_ROOT / "LICENSE"
    if license_path.exists():
        assert "## License" in readme or "[LICENSE](LICENSE)" in readme
        assert "MIT" in readme


def test_openspec_archiving_and_deferrals() -> None:
    """Verify merged changes are archived and out-of-scope proposals carry deferral notices."""
    archive_dir = REPO_ROOT / "openspec" / "changes" / "archive"
    for merged_change in (
        "add-github-actions-and-schema-hooks",
        "add-sqlmodel-persistence-and-api",
        "adopt-ed25519-and-pymerkle",
        "adopt-mesa-abm-and-hypothesis",
        "automate-pr-lifecycle-and-merge-safety",
        "enforce-spec-feature-links",
        "harden-ci-action-runtimes-and-review",
        "standardize-custom-skills",
    ):
        assert (archive_dir / merged_change).is_dir(), f"Expected {merged_change} in archive"

    changes_dir = REPO_ROOT / "openspec" / "changes"
    for deferred_change in (
        "add-biomimetic-lifecycle-and-swarming-contracts",
        "add-campus-compliance-lti-and-zk-identity",
        "add-nats-jetstream-cross-hive-federation",
        "add-pactflow-api-and-message-contracts",
        "add-telemetry-dashboard-ui",
        "adopt-vyper-and-zero-gas-pyevm",
    ):
        proposal_file = changes_dir / deferred_change / "proposal.md"
        assert proposal_file.exists(), f"Expected {proposal_file} to exist"
        proposal_text = proposal_file.read_text(encoding="utf-8")
        assert "DEFERRED" in proposal_text

    readme_text = (changes_dir / "README.md").read_text(encoding="utf-8")
    assert "Active Changes" in readme_text
    assert "Deferred Changes" in readme_text
    assert "Archived Changes" in readme_text


def test_chain_audit_log_adr_and_wording_supersession() -> None:
    """Verify ADR-0019 supersedes ADR-0007 and doc wording describes the signed audit log."""
    adr_19 = (
        REPO_ROOT
        / "docs"
        / "adr"
        / "0019-treat-the-hive-chain-as-a-signed-hash-chained-audit-log.md"
    )
    assert adr_19.exists(), "Expected ADR-0019 to exist"
    adr_19_text = adr_19.read_text(encoding="utf-8")
    assert "status: accepted" in adr_19_text
    assert "Treat the hive chain as a signed, hash-chained audit log" in adr_19_text
    assert "supersedes `ADR-0007`" in adr_19_text or "supersedes ADR-0007" in adr_19_text

    adr_7 = (
        REPO_ROOT
        / "docs"
        / "adr"
        / "0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md"
    )
    adr_7_text = adr_7.read_text(encoding="utf-8")
    assert "status: superseded by ADR-0019" in adr_7_text

    lock_text = (REPO_ROOT / "adrlint.lock").read_text(encoding="utf-8")
    assert "0019-treat-the-hive-chain-as-a-signed-hash-chained-audit-log.md" in lock_text

    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Hybrid `PoUW-PoW` distributed compute consensus" not in readme_text
    assert "audit log" in readme_text

    sys_design_text = (REPO_ROOT / "docs" / "architecture" / "system_design.md").read_text(
        encoding="utf-8"
    )
    assert "Private PoUW-PoW Blockchain" not in sys_design_text
    assert "Signed Audit Log" in sys_design_text or "signed audit log" in sys_design_text


def test_unsourced_figures_labeled_as_assumptions_and_smoke_scenario_retitle() -> None:
    """Verify fill rates and ROI inputs are labeled assumptions and smoke scenario retitled."""
    proposal = (REPO_ROOT / "docs" / "business" / "institutional_proposal.md").read_text(
        encoding="utf-8"
    )
    assert "38.0%" in proposal and "67.4%" in proposal
    assert "assumption" in proposal.lower()
    assert "planning assumption" in proposal.lower() or "modeled assumption" in proposal.lower()

    game_theory = (REPO_ROOT / "docs" / "theory" / "tokenomics_game_theory.md").read_text(
        encoding="utf-8"
    )
    assert "Scripted smoke-scenario output (not an experiment)" in game_theory


def test_ai_generated_research_and_bee_metaphor_labeled() -> None:
    """Verify research reports carry AI-generated notices and bee metaphor is explicitly labeled."""
    research_dir = REPO_ROOT / "docs" / "theory" / "research"
    for report_name in (
        "biomimetic_hive_economics.md",
        "federated_barter_tokenomics.md",
        "federated_PoUW-PoW_blockchain_infrastructure.md",
        "nectR_funding_and_pilot_strategy.md",
        "permissive_tooling_survey_for_nectR.md",
        "student_tutoring_mechanism_design.md",
    ):
        report_text = (research_dir / report_name).read_text(encoding="utf-8")
        assert "AI-generated" in report_text or "Gemini Deep Research" in report_text

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "metaphor" in readme.lower()

    biomimicry = (REPO_ROOT / "docs" / "theory" / "biomimicry_model.md").read_text(encoding="utf-8")
    assert "metaphor" in biomimicry.lower()

    game_theory = (REPO_ROOT / "docs" / "theory" / "tokenomics_game_theory.md").read_text(
        encoding="utf-8"
    )
    assert "| :--- | :---: | :--- |\n| :--- | :---: | :--- |" not in game_theory


def test_roadmap_plan_to_b_plus_and_vision_document() -> None:
    """Verify roadmap.md focuses on Plan to B+ and vision.md captures 3-horizon vision."""
    vision_path = REPO_ROOT / "docs" / "planning" / "vision.md"
    assert vision_path.exists(), "Expected docs/planning/vision.md to exist"
    vision_text = vision_path.read_text(encoding="utf-8")
    assert "Three-Horizon Product Vision" in vision_text or "Three-Horizon" in vision_text
    assert "Horizon 1" in vision_text and "Horizon 3" in vision_text

    roadmap_text = (REPO_ROOT / "docs" / "planning" / "roadmap.md").read_text(encoding="utf-8")
    assert "Plan to B+" in roadmap_text
    assert "Track CA" in roadmap_text or "Core Contracts" in roadmap_text
    assert "Track CB" in roadmap_text or "Service Layer" in roadmap_text
    assert "Track DC" in roadmap_text or "Documentation" in roadmap_text

    from nectr.devtools.docs_sync import check_docs_sync

    summary = check_docs_sync(REPO_ROOT)
    assert "planning/vision.md" not in summary["orphan_pages"]
    assert summary["orphan_pages"] == []
