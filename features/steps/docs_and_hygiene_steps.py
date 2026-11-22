"""Step definitions for Living Documentation, Glossary, Persona Extras, and Repo Hygiene BDD feature."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]


@given("the repository documentation root")
def step_given_docs_root(context) -> None:
    context.repo_root = REPO_ROOT
    context.docs_summary = None
    context.docs_error = None


@when("the onboarding and glossary validator inspects README and glossary")
def step_when_inspect_glossary(context) -> None:
    glossary_path = context.repo_root / "docs" / "glossary.md"
    readme_path = context.repo_root / "README.md"
    context.glossary_text = (
        glossary_path.read_text(encoding="utf-8") if glossary_path.exists() else ""
    )
    context.readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""


@then("docs/glossary.md defines MV=PQ and PoUW-PoW and README contains no IDE lock-in")
def step_then_glossary_and_readme_ok(context) -> None:
    assert "MV=PQ" in context.glossary_text or "MV = PQ" in context.glossary_text
    assert "PoUW-PoW" in context.glossary_text
    assert "Open as Active Workspace in Antigravity" not in context.readme_text
    assert "docs/glossary.md" in context.readme_text


@when("the docs synchronization validator checks README and mkdocs.yml")
def step_when_docs_sync_check(context) -> None:
    from nectr.devtools.docs_sync import DocsSyncError, check_docs_sync

    try:
        context.docs_summary = check_docs_sync(context.repo_root)
    except DocsSyncError as exc:
        context.docs_error = exc


@then("docs validation succeeds with zero orphaned pages and synced ADR navigation")
def step_then_docs_sync_ok(context) -> None:
    assert context.docs_error is None, f"Docs sync failed: {context.docs_error}"
    assert context.docs_summary is not None
    assert context.docs_summary["orphan_pages"] == []
    assert context.docs_summary["readme_in_sync"] is True
    assert context.docs_summary["mkdocs_adr_nav_in_sync"] is True


@given("the repository root configuration")
def step_given_repo_cfg(context) -> None:
    context.repo_root = REPO_ROOT


@when("git tracking, .gitattributes, and pyproject.toml extras are inspected")
def step_when_inspect_hygiene(context) -> None:
    res = subprocess.run(
        ["git", "ls-files", "HANDOFF.md"],
        cwd=context.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    context.tracked_handoff = res.stdout.strip()
    gitattr = context.repo_root / ".gitattributes"
    context.gitattributes_text = gitattr.read_text(encoding="utf-8") if gitattr.exists() else ""
    pyproject_data = tomllib.loads(
        (context.repo_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    context.optional_deps = pyproject_data.get("project", {}).get("optional-dependencies", {})


@then("HANDOFF.md is untracked, LF normalization is configured, and persona extras exist")
def step_then_hygiene_ok(context) -> None:
    assert context.tracked_handoff == "", f"HANDOFF.md is still tracked: {context.tracked_handoff}"
    assert "eol=lf" in context.gitattributes_text
    for persona in ("test", "lint", "security", "docs", "research", "dev"):
        assert persona in context.optional_deps, f"Missing persona extra '{persona}'"
    assert any("adrlint" in item for item in context.optional_deps.get("lint", []))
    assert "pyadr" not in str(context.optional_deps.get("dev", []))


@when("the documentation freeze validator inspects AGENTS.md and agent_orchestration.md")
def step_when_inspect_freeze(context) -> None:
    agents_path = context.repo_root / "AGENTS.md"
    orch_path = context.repo_root / "docs" / "planning" / "agent_orchestration.md"
    context.agents_text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    context.orch_text = orch_path.read_text(encoding="utf-8") if orch_path.exists() else ""


@then(
    "AGENTS.md enforces the structure freeze and agent_orchestration.md displays the superseded banner"
)
def step_then_freeze_ok(context) -> None:
    assert (
        "Structure Freeze Until v0.1.0" in context.agents_text
        or "Freeze Until v0.1.0" in context.agents_text
    )
    assert (
        "no new ADRs, change proposals, skills, workflows or gates outside the Plan to B+ until v0.1.0"
        in context.agents_text
    )
    assert "superseded for current work by the Plan to B+" in context.orch_text
    assert "Waves 3 to 5 are out of scope until after v0.1.0" in context.orch_text


@when("the README transparency validator inspects README and LICENSE")
def step_when_inspect_readme_transparency(context) -> None:
    readme_path = context.repo_root / "README.md"
    context.readme_lines = (
        readme_path.read_text(encoding="utf-8").splitlines() if readme_path.exists() else []
    )
    context.readme_text = "\n".join(context.readme_lines)
    context.has_license = (context.repo_root / "LICENSE").exists()


@then("README has a status line within ten lines and an Independence section and license link")
def step_then_readme_transparency_ok(context) -> None:
    assert context.readme_lines and context.readme_lines[0].startswith("# ")
    status_lines = [ln for ln in context.readme_lines[:10] if ln.startswith("> **Status:**")]
    assert len(status_lines) == 1, "Expected > **Status:** within first 10 lines of README.md"
    assert "research prototype" in status_lines[0]
    assert "## Independence" in context.readme_text
    assert "This is a personal project by Brandon Fox" in context.readme_text
    assert "First-ADE/PRINCIPLES.md" in context.readme_text
    if context.has_license:
        assert "## License" in context.readme_text or "[LICENSE](LICENSE)" in context.readme_text
        assert "MIT" in context.readme_text


@when("the OpenSpec lifecycle validator inspects active, archived, and deferred proposals")
def step_when_inspect_openspec_lifecycle(context) -> None:
    context.archive_dir = context.repo_root / "openspec" / "changes" / "archive"
    context.changes_dir = context.repo_root / "openspec" / "changes"
    context.openspec_readme = (
        (context.changes_dir / "README.md").read_text(encoding="utf-8")
        if (context.changes_dir / "README.md").exists()
        else ""
    )


@then("merged proposals are archived and out-of-scope proposals carry a deferral notice")
def step_then_openspec_lifecycle_ok(context) -> None:
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
        assert (context.archive_dir / merged_change).is_dir(), (
            f"Expected {merged_change} in archive"
        )

    for deferred_change in (
        "add-biomimetic-lifecycle-and-swarming-contracts",
        "add-campus-compliance-lti-and-zk-identity",
        "add-nats-jetstream-cross-hive-federation",
        "add-pactflow-api-and-message-contracts",
        "add-telemetry-dashboard-ui",
        "adopt-vyper-and-zero-gas-pyevm",
    ):
        proposal_file = context.changes_dir / deferred_change / "proposal.md"
        assert proposal_file.exists(), f"Expected {proposal_file} to exist"
        proposal_text = proposal_file.read_text(encoding="utf-8")
        assert "DEFERRED" in proposal_text

    assert "Active Changes" in context.openspec_readme
    assert "Deferred Changes" in context.openspec_readme
    assert "Archived Changes" in context.openspec_readme


@when(
    "the ADR and audit log wording validator inspects ADR records, README, architecture, theory, and glossary"
)
def step_when_inspect_audit_log_wording(context) -> None:
    context.adr_19_path = (
        context.repo_root
        / "docs"
        / "adr"
        / "0019-treat-the-hive-chain-as-a-signed-hash-chained-audit-log.md"
    )
    context.adr_7_path = (
        context.repo_root
        / "docs"
        / "adr"
        / "0007-couple-open-campus-pouw-pow-mining-to-capped-comb-compute-jar.md"
    )
    context.lock_path = context.repo_root / "adrlint.lock"
    context.sys_design_path = context.repo_root / "docs" / "architecture" / "system_design.md"
    context.readme_path = context.repo_root / "README.md"


@then(
    "ADR-0019 is accepted superseding ADR-0007 and consensus wording describes the signed audit log"
)
def step_then_audit_log_wording_ok(context) -> None:
    assert context.adr_19_path.exists(), "Expected ADR-0019 to exist"
    adr_19_text = context.adr_19_path.read_text(encoding="utf-8")
    assert "status: accepted" in adr_19_text
    assert "Treat the hive chain as a signed, hash-chained audit log" in adr_19_text
    assert "supersedes `ADR-0007`" in adr_19_text or "supersedes ADR-0007" in adr_19_text

    adr_7_text = context.adr_7_path.read_text(encoding="utf-8")
    assert "status: superseded by ADR-0019" in adr_7_text

    lock_text = context.lock_path.read_text(encoding="utf-8")
    assert "0019-treat-the-hive-chain-as-a-signed-hash-chained-audit-log.md" in lock_text

    readme_text = context.readme_path.read_text(encoding="utf-8")
    assert "Hybrid `PoUW-PoW` distributed compute consensus" not in readme_text
    assert "audit log" in readme_text

    sys_design_text = context.sys_design_path.read_text(encoding="utf-8")
    assert "Private PoUW-PoW Blockchain" not in sys_design_text
    assert "Signed Audit Log" in sys_design_text or "signed audit log" in sys_design_text


@when(
    "the assumption and smoke scenario validator inspects institutional proposal and tokenomics game theory"
)
def step_when_inspect_assumptions_and_smoke_scenario(context) -> None:
    context.proposal_text = (
        context.repo_root / "docs" / "business" / "institutional_proposal.md"
    ).read_text(encoding="utf-8")
    context.game_theory_text = (
        context.repo_root / "docs" / "theory" / "tokenomics_game_theory.md"
    ).read_text(encoding="utf-8")


@then(
    "institutional proposal labels fill rates and ROI inputs as assumptions and tokenomics game theory retitles smoke scenario output"
)
def step_then_assumptions_and_smoke_scenario_ok(context) -> None:
    assert "38.0%" in context.proposal_text and "67.4%" in context.proposal_text
    assert "assumption" in context.proposal_text.lower()
    assert (
        "planning assumption" in context.proposal_text.lower()
        or "modeled assumption" in context.proposal_text.lower()
    )
    assert "Scripted smoke-scenario output (not an experiment)" in context.game_theory_text


@when(
    "the AI research and metaphor validator inspects research reports, README, biomimicry model, and tokenomics"
)
def step_when_inspect_ai_research_and_metaphor(context) -> None:
    context.research_dir = context.repo_root / "docs" / "theory" / "research"
    context.readme_text = (context.repo_root / "README.md").read_text(encoding="utf-8")
    context.biomimicry_text = (
        context.repo_root / "docs" / "theory" / "biomimicry_model.md"
    ).read_text(encoding="utf-8")
    context.game_theory_text = (
        context.repo_root / "docs" / "theory" / "tokenomics_game_theory.md"
    ).read_text(encoding="utf-8")


@then(
    "all deep research reports carry an AI-generated notice and bee terminology is labeled as a design metaphor"
)
def step_then_ai_research_and_metaphor_ok(context) -> None:
    for report_name in (
        "biomimetic_hive_economics.md",
        "federated_barter_tokenomics.md",
        "federated_PoUW-PoW_blockchain_infrastructure.md",
        "nectR_funding_and_pilot_strategy.md",
        "permissive_tooling_survey_for_nectR.md",
        "student_tutoring_mechanism_design.md",
    ):
        report_text = (context.research_dir / report_name).read_text(encoding="utf-8")
        assert "AI-generated" in report_text or "Gemini Deep Research" in report_text, (
            f"Missing notice in {report_name}"
        )

    assert "metaphor" in context.readme_text.lower()
    assert "metaphor" in context.biomimicry_text.lower()
    assert "| :--- | :---: | :--- |\n| :--- | :---: | :--- |" not in context.game_theory_text


@when("the roadmap and vision validator inspects roadmap.md, vision.md, and mkdocs.yml")
def step_when_inspect_roadmap_and_vision(context) -> None:
    context.vision_path = context.repo_root / "docs" / "planning" / "vision.md"
    context.roadmap_path = context.repo_root / "docs" / "planning" / "roadmap.md"
    context.mkdocs_path = context.repo_root / "mkdocs.yml"
    context.roadmap_text = (
        context.roadmap_path.read_text(encoding="utf-8") if context.roadmap_path.exists() else ""
    )
    context.vision_text = (
        context.vision_path.read_text(encoding="utf-8") if context.vision_path.exists() else ""
    )


@then("vision.md documents the three-horizon product vision and roadmap.md details the Plan to B+")
def step_then_roadmap_and_vision_ok(context) -> None:
    assert context.vision_path.exists(), "Expected docs/planning/vision.md to exist"
    assert (
        "Three-Horizon Product Vision" in context.vision_text
        or "Three-Horizon" in context.vision_text
    )
    assert "Horizon 1" in context.vision_text and "Horizon 3" in context.vision_text
    assert "Plan to B+" in context.roadmap_text
    assert "Track CA" in context.roadmap_text or "Core Contracts" in context.roadmap_text
    assert "Track CB" in context.roadmap_text or "Service Layer" in context.roadmap_text
    assert "Track DC" in context.roadmap_text or "Documentation" in context.roadmap_text


@then(
    "roadmap.md accurately details all Plan to B+ workstream deliverables and unmerged hold statuses"
)
def step_then_roadmap_accurately_details_plan_to_b_plus(context) -> None:
    text = context.roadmap_text
    assert "[ ] **CA3:**" in text
    assert "[ ] **CB1:**" in text
    assert "dispute and escrow-cancel" in text.lower()
    assert "append-only" in text and "verify_chain()" in text
    assert "velocity" in text and "royal jelly" in text.lower()
    assert "--check-stale" in text
    assert "license" in text.lower() and "author" in text.lower()
    assert ("numpy" in text.lower() or "runtime" in text.lower()) and "TL4" in text
    assert "**TL6:**" in text
    assert "**TL7:**" in text
