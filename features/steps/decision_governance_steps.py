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


@then(
    "validation succeeds with at least {min_adrs:d} accepted MADR records and an in-sync ADR index"
)
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
    shutil.copy2(REPO_ROOT / ".adrlint.toml", tmp_dir / ".adrlint.toml")
    shutil.copy2(REPO_ROOT / "adrlint.lock", tmp_dir / "adrlint.lock")
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
    log_path.write_text(
        log_path.read_text(encoding="utf-8") + "\n<!-- unapproved manual edit -->\n",
        encoding="utf-8",
    )
    try:
        check_all_governance(context.temp_dir)
    except DecisionGovernanceError as exc:
        context.gov_error = exc
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then('governance validation fails with "{expected_substring}"')
def step_then_governance_fails(context, expected_substring: str) -> None:
    assert context.gov_error is not None, (
        "Expected DecisionGovernanceError, but validation succeeded"
    )
    assert expected_substring in str(context.gov_error), (
        f"Expected '{expected_substring}' in '{context.gov_error}'"
    )


@given("a temporary MADR 4.0 workspace configured with adrlint")
def step_given_temp_adrlint_workspace(context) -> None:
    import subprocess
    import sys

    adrlint_bin = shutil.which("adrlint") or str(
        Path(sys.executable).resolve().parent
        / ("adrlint.exe" if sys.platform == "win32" else "adrlint")
    )
    tmp_dir = Path(tempfile.mkdtemp(prefix="nectr_adrlint_bdd_"))
    subprocess.run(
        [adrlint_bin, "init", "--dir", "docs/adr", "--start", "0", "--force"],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [adrlint_bin, "lock"],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    context.temp_dir = tmp_dir
    context.adrlint_bin = adrlint_bin
    context.adrlint_strict_error = None
    context.adrlint_allow_ok = False
    context.adrlint_locked_count = 0


@when("a proposed ADR is created with adrlint new and checked before and after acceptance")
def step_when_adrlint_proposed_and_locked(context) -> None:
    import subprocess

    from nectr.devtools.decisions import DecisionGovernanceError, validate_adrlint_repo

    try:
        subprocess.run(
            [context.adrlint_bin, "new", "Evaluate Cache Adapter"],
            cwd=context.temp_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        try:
            validate_adrlint_repo(context.temp_dir, allow_proposed=False)
        except DecisionGovernanceError as exc:
            context.adrlint_strict_error = exc

        count_while_proposed = validate_adrlint_repo(context.temp_dir, allow_proposed=True)
        context.adrlint_allow_ok = count_while_proposed == 1

        proposed_file = context.temp_dir / "docs" / "adr" / "0001-evaluate-cache-adapter.md"
        proposed_file.write_text(
            proposed_file.read_text(encoding="utf-8").replace(
                "status: proposed", "status: accepted", 1
            ),
            encoding="utf-8",
            newline="\n",
        )
        subprocess.run(
            [context.adrlint_bin, "lock"],
            cwd=context.temp_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        context.adrlint_locked_count = validate_adrlint_repo(context.temp_dir, allow_proposed=False)
    finally:
        shutil.rmtree(context.temp_dir, ignore_errors=True)


@then("bespoke adr.py is absent and strict check rejects proposed until accepted and locked")
def step_then_adrlint_ok(context) -> None:
    assert not (REPO_ROOT / "src" / "nectr" / "devtools" / "adr.py").exists()
    assert (REPO_ROOT / ".adrlint.toml").exists()
    assert (REPO_ROOT / "adrlint.lock").exists()
    assert context.adrlint_strict_error is not None
    assert "proposed" in str(context.adrlint_strict_error).lower()
    assert context.adrlint_allow_ok is True
    assert context.adrlint_locked_count == 2


@when(
    "the n8n workflow governance and Milestone 3 roadmap checks inspect decisions and ADR records"
)
def step_when_inspect_n8n_governance(context) -> None:
    from nectr.devtools.decisions import load_registry

    root: Path = context.target_root
    registry = load_registry(root / "docs" / "planning" / "decisions.yaml")
    context.n8n_decisions = {entry.id: entry for entry in registry.decisions}
    context.n8n_experiments = {entry.id: entry for entry in registry.experiments}
    context.n8n_roadmap = (root / "docs" / "planning" / "roadmap.md").read_text(encoding="utf-8")
    context.n8n_adr_path = (
        root / "docs" / "adr" / "0016-scope-external-workflow-automation-off-chain.md"
    )


@then("DEC-009 clarifies CrewAI/n8n while remaining locked to Mesa ABM")
def step_then_dec009_clarified(context) -> None:
    dec009 = context.n8n_decisions["DEC-009"]
    assert dec009.status == "locked"
    assert "CrewAI/n8n" in dec009.title
    assert "CrewAI/n8n" in dec009.decision
    assert "Mesa ABM" in dec009.decision


@then("DEC-016 and EXP-006 enforce an off-chain n8n boundary with permissive OSS roadmap options")
def step_then_dec016_exp006_and_roadmap(context) -> None:
    assert "DEC-016" in context.n8n_decisions
    dec016 = context.n8n_decisions["DEC-016"]
    assert dec016.status == "locked"
    assert "n8n" in dec016.decision
    assert "HiveServiceLayer" in dec016.decision
    assert "EXP-006" in context.n8n_experiments
    exp006 = context.n8n_experiments["EXP-006"]
    assert exp006.status == "open-simulation"
    assert "n8n" in exp006.hypothesis
    roadmap_text: str = context.n8n_roadmap
    assert "CrewAI/n8n" in roadmap_text
    assert "Activepieces" in roadmap_text
    assert "Kestra" in roadmap_text
    assert "Prefect" in roadmap_text
    assert "Temporal" in roadmap_text


@then("an accepted locked MADR record documents the external workflow automation scope")
def step_then_n8n_adr_locked(context) -> None:
    from nectr.devtools.decisions import check_all_governance

    adr_path: Path = context.n8n_adr_path
    assert adr_path.exists(), f"Missing ADR file: {adr_path}"
    adr_text = adr_path.read_text(encoding="utf-8")
    assert "status: accepted" in adr_text
    assert "n8n" in adr_text
    summary = check_all_governance(context.target_root)
    assert summary["adrlint_ok"] is True
    assert summary["decision_log_in_sync"] is True


@when(
    "the Vyper py-evm, PactFlow, and JASSS ODD+D governance checks inspect ADRs, decisions, and OpenSpec proposals"
)
def step_when_inspect_vyper_pactflow_governance(context) -> None:
    from nectr.devtools.decisions import load_registry

    root: Path = context.target_root
    registry = load_registry(root / "docs" / "planning" / "decisions.yaml")
    context.vp_decisions = {entry.id: entry for entry in registry.decisions}
    context.adr0017 = (
        root / "docs" / "adr" / "0017-adopt-vyper-and-zero-gas-py-evm-smart-contracts.md"
    )
    context.adr0018 = (
        root / "docs" / "adr" / "0018-enforce-pact-v4-and-pactflow-bi-directional-contracts.md"
    )
    context.vyper_spec = (
        root / "openspec" / "changes" / "adopt-vyper-and-zero-gas-pyevm" / "proposal.md"
    )
    context.pact_spec = (
        root / "openspec" / "changes" / "add-pactflow-api-and-message-contracts" / "proposal.md"
    )


@then(
    "ADR-0017 and ADR-0018 are accepted and locked for Vyper py-evm and PactFlow bi-directional contracts"
)
def step_then_adr0017_0018_locked(context) -> None:
    from nectr.devtools.decisions import check_all_governance

    assert context.adr0017.exists(), "Missing ADR-0017 for Vyper + zero-gas py-evm"
    assert context.adr0018.exists(), "Missing ADR-0018 for Pact v4 + PactFlow"
    assert "vyper" in context.adr0017.read_text(encoding="utf-8").lower()
    assert "pactflow" in context.adr0018.read_text(encoding="utf-8").lower()
    summary = check_all_governance(context.target_root)
    assert summary["accepted_adr_count"] >= 18
    assert summary["adrlint_ok"] is True


@then(
    "DEC-017 through DEC-020 lock micro_nectr integer math, direct bps learner attestations, layered secp256k1 signing, and JASSS ODD+D framing"
)
def step_then_dec017_to_020_locked(context) -> None:
    for dec_id in ("DEC-017", "DEC-018", "DEC-019", "DEC-020"):
        assert dec_id in context.vp_decisions, f"Missing {dec_id} in decisions.yaml"
        assert context.vp_decisions[dec_id].status == "locked"
    assert "micro_nectr" in context.vp_decisions["DEC-017"].decision
    assert "10,000 bps" in context.vp_decisions["DEC-018"].decision
    assert "secp256k1" in context.vp_decisions["DEC-019"].decision
    assert "JASSS" in context.vp_decisions["DEC-020"].decision
    assert "ODD+D" in context.vp_decisions["DEC-020"].decision


@then("OpenSpec proposals exist for Vyper py-evm migration and PactFlow contract governance")
def step_then_vyper_pact_openspec_exist(context) -> None:
    assert context.vyper_spec.exists(), "Missing adopt-vyper-and-zero-gas-pyevm OpenSpec proposal"
    assert context.pact_spec.exists(), (
        "Missing add-pactflow-api-and-message-contracts OpenSpec proposal"
    )
