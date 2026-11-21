"""Step definitions for Dual-Track Decision Governance BDD feature."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]


@given("the repository root decision governance workspace")
def step_given_repo_workspace(context) -> None:
    context.target_root = REPO_ROOT
    context.gov_error = None
    context.gov_summary = None


@when("the full decision and ADR governance check runs")
def step_when_full_check_runs(context) -> None:
    from nectr.devtools.decisions import DecisionGovernanceError, check_all_governance

    try:
        context.gov_summary = check_all_governance(context.target_root)
    except DecisionGovernanceError as exc:
        context.gov_error = exc


@then("validation succeeds with at least {min_adrs:d} accepted MADR records and an in-sync ADR index")
def step_then_validation_succeeds(context, min_adrs: int) -> None:
    assert context.gov_error is None, f"Unexpected governance error: {context.gov_error}"
    assert context.gov_summary is not None
    assert context.gov_summary["accepted_adr_count"] >= min_adrs
    assert context.gov_summary["toc_in_sync"] is True
    assert context.gov_summary["decision_log_in_sync"] is True


@given("a temporary ADR directory containing a verbose MADR record of {line_count:d} lines")
def step_given_verbose_temp_adr(context, line_count: int) -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_adr_bdd_"))
    adr_dir = tmp_dir / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    body_lines = [
        "# Verbose Architecture Record",
        "",
        "* Status: accepted",
        "* Date: 2026-11-21",
        "",
        "## Context and Problem Statement",
        "",
        "Context line.",
        "",
        "## Considered Options",
        "",
        "* Option A",
        "* Option B",
        "",
        "## Decision Outcome",
        "",
        'Chosen option: "Option A", because it is concise.',
    ]
    while len(body_lines) < line_count:
        body_lines.append(f"Extra filler line {len(body_lines)}")
    (adr_dir / "0001-verbose-architecture-record.md").write_text(
        "\n".join(body_lines) + "\n", encoding="utf-8"
    )
    context.temp_dir = tmp_dir
    context.temp_adr_dir = adr_dir
    context.gov_error = None


@when("the ADR verbosity validator inspects the temporary ADR directory")
def step_when_verbosity_validator_runs(context) -> None:
    from nectr.devtools.decisions import DecisionGovernanceError, validate_adr_verbosity

    try:
        validate_adr_verbosity(context.temp_adr_dir)
    except DecisionGovernanceError as exc:
        context.gov_error = exc
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@given("a temporary copy of the fast decision registry and rendered decision log")
def step_given_temp_registry_copy(context) -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_dec_bdd_"))
    (tmp_dir / "docs" / "planning").mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO_ROOT / "docs" / "adr", tmp_dir / "docs" / "adr")
    shutil.copytree(REPO_ROOT / "openspec", tmp_dir / "openspec")
    shutil.copy2(REPO_ROOT / ".adr", tmp_dir / ".adr")
    shutil.copy2(
        REPO_ROOT / "docs" / "planning" / "decisions.yaml",
        tmp_dir / "docs" / "planning" / "decisions.yaml",
    )
    shutil.copy2(
        REPO_ROOT / "docs" / "planning" / "decision_log.md",
        tmp_dir / "docs" / "planning" / "decision_log.md",
    )
    context.temp_dir = tmp_dir
    context.gov_error = None


@when("manual text drift is injected into the rendered decision_log.md")
def step_when_drift_injected(context) -> None:
    from nectr.devtools.decisions import DecisionGovernanceError, check_all_governance

    log_path = context.temp_dir / "docs" / "planning" / "decision_log.md"
    log_path.write_text(log_path.read_text(encoding="utf-8") + "\n<!-- unapproved manual edit -->\n", encoding="utf-8")
    try:
        check_all_governance(context.temp_dir)
    except DecisionGovernanceError as exc:
        context.gov_error = exc
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then('governance validation fails with "{expected_substring}"')
def step_then_governance_fails(context, expected_substring: str) -> None:
    assert context.gov_error is not None, "Expected DecisionGovernanceError, but validation succeeded"
    assert expected_substring in str(context.gov_error), (
        f"Expected '{expected_substring}' in '{context.gov_error}'"
    )


@given("a temporary copy of the repository ADR workspace with a proposed ADR")
def step_given_temp_proposed_adr(context) -> None:
    from nectr.devtools.adr import AdrCore

    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_prop_adr_"))
    shutil.copytree(REPO_ROOT / "docs" / "adr", tmp_dir / "docs" / "adr")
    shutil.copy2(REPO_ROOT / ".adr", tmp_dir / ".adr")
    core = AdrCore(tmp_dir)
    core.new_adr("Evaluate Optional Caching Adapter")
    context.temp_dir = tmp_dir
    context.strict_error = None
    context.allow_proposed_ok = False


@when("the ADR validator inspects the workspace with allow-proposed disabled and enabled")
def step_when_inspect_proposed(context) -> None:
    from nectr.devtools.decisions import DecisionGovernanceError, validate_pyadr_repo_and_toc

    try:
        validate_pyadr_repo_and_toc(context.temp_dir, allow_proposed=False)
    except DecisionGovernanceError as exc:
        context.strict_error = exc

    try:
        from nectr.devtools.adr import AdrCore

        AdrCore(context.temp_dir).generate_toc()
        _, ok = validate_pyadr_repo_and_toc(context.temp_dir, allow_proposed=True)
        context.allow_proposed_ok = ok
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then("strict check fails on proposed status while allow-proposed check succeeds")
def step_then_proposed_toggled(context) -> None:
    assert context.strict_error is not None, "Expected strict ADR check to reject proposed ADR"
    assert "proposed" in str(context.strict_error).lower()
    assert context.allow_proposed_ok is True
