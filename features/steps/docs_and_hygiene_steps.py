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
