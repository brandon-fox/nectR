"""Behave step definitions for end-to-end hook, CI, scheduled audit, and release parity."""

from __future__ import annotations

import json
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from behave import given, then, when

from nectr.devtools.ci_parity import (
    REQUIRED_PIPELINE_FILES,
    check_no_red_scenarios,
    check_pipeline_parity,
    check_workflow_action_hygiene,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@given("the repository root hook, pre-commit, and GitHub Actions workflow definitions")
def step_given_hook_and_ci_defs(context: Any) -> None:
    context.repo_root = REPO_ROOT
    context.pipeline_texts = {}
    for rel_path in REQUIRED_PIPELINE_FILES:
        file_path = REPO_ROOT / rel_path
        assert file_path.is_file(), f"Missing required pipeline file: {rel_path}"
        context.pipeline_texts[rel_path] = file_path.read_text(encoding="utf-8")


@when("the CI and hook parity validator inspects local and remote pipeline stages")
def step_when_parity_validator_runs(context: Any) -> None:
    context.parity_report = check_pipeline_parity(context.repo_root)


@then(
    "every local security, governance, lint, format, type, docs, and test gate is mirrored in CI with cross-platform venv PATH resolution"
)
def step_then_parity_verified(context: Any) -> None:
    report = context.parity_report
    assert report.passed, f"CI parity errors: {report.errors}"

    diag_by_gate = {diag.gate: diag for diag in report.diagnostics}
    expected_gates = {
        "detect-secrets",
        "local-path-regex",
        "cygpath-venv-path",
        "adrlint",
        "nectr-decisions",
        "nectr-citations",
        "nectr-docs",
        "nectr-spec-links",
        "ruff-check",
        "ruff-format",
        "pymarkdown",
        "mypy",
        "mkdocs-strict",
        "pytest-coverage",
        "behave",
        "check-jsonschema",
    }
    missing_gates = expected_gates - set(diag_by_gate)
    assert not missing_gates, f"Missing diagnostics for gates: {sorted(missing_gates)}"
    for gate in expected_gates:
        assert diag_by_gate[gate].passed, f"Gate {gate} failed: {diag_by_gate[gate].details}"

    for hook_path in (".githooks/pre-commit", ".githooks/pre-push"):
        hook_text = context.pipeline_texts[hook_path]
        assert "cygpath -u" in hook_text, f"{hook_path} missing cygpath -u"
        assert ".venv/Scripts" in hook_text, f"{hook_path} missing .venv/Scripts"
        assert ".venv/bin" in hook_text, f"{hook_path} missing .venv/bin"


@given("the repository pyproject.toml, uv.lock, and GitHub Actions CI workflow")
def step_given_lock_and_matrix(context: Any) -> None:
    context.repo_root = REPO_ROOT
    pyproject_path = REPO_ROOT / "pyproject.toml"
    lock_path = REPO_ROOT / "uv.lock"
    ci_path = REPO_ROOT / ".github/workflows/license-and-security-scan.yml"

    assert pyproject_path.is_file(), "Missing pyproject.toml"
    assert lock_path.is_file(), "Missing uv.lock"
    assert ci_path.is_file(), "Missing .github/workflows/license-and-security-scan.yml"

    context.pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    context.ci_text = ci_path.read_text(encoding="utf-8")
    context.ci_workflow = yaml.safe_load(context.ci_text)


@when("the CI matrix and dependency audit configuration is validated")
def step_when_matrix_validated(context: Any) -> None:
    context.parity_report = check_pipeline_parity(context.repo_root)


@then(
    "CI installs locked dev and research extras via uv and runs tests across Python 3.11 to 3.13 on Linux and Windows"
)
def step_then_matrix_and_uv_verified(context: Any) -> None:
    diag_by_gate = {diag.gate: diag for diag in context.parity_report.diagnostics}
    assert diag_by_gate["uv-frozen-sync"].passed, diag_by_gate["uv-frozen-sync"].details
    assert diag_by_gate["ci-matrix"].passed, diag_by_gate["ci-matrix"].details

    optional_deps = context.pyproject_data["project"]["optional-dependencies"]
    assert "dev" in optional_deps and "research" in optional_deps

    jobs = context.ci_workflow["jobs"]
    scan_steps = "\n".join(
        str(step.get("run", "")) for step in jobs["license-and-security-scan"]["steps"]
    )
    assert "uv sync --frozen --extra dev --extra research" in scan_steps
    assert "pip-licenses" in scan_steps
    assert "pip-audit" in scan_steps

    matrix_job = jobs["test-matrix"]
    matrix = matrix_job["strategy"]["matrix"]
    assert "ubuntu-latest" in matrix["os"]
    assert set(matrix["python-version"]) >= {"3.11", "3.12", "3.13"}
    include_oses = {entry.get("os") for entry in matrix.get("include", [])}
    assert "windows-latest" in include_oses

    matrix_runs = "\n".join(str(step.get("run", "")) for step in matrix_job["steps"])
    assert "uv sync --frozen --extra dev" in matrix_runs
    assert "pytest" in matrix_runs
    assert "behave --tags=-red" in matrix_runs


@given("a simulated main-branch CI check with an active @red feature scenario")
def step_given_main_branch_red_scenario(context: Any) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._tmp = tmp
    tmp_root = Path(tmp.name)
    features_dir = tmp_root / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "sample_red.feature").write_text(
        "Feature: Simulated Red Gate\n"
        "  @red\n"
        "  Scenario: Unimplemented scenario\n"
        "    Given a pending requirement\n",
        encoding="utf-8",
    )
    context.sim_root = tmp_root
    context.ci_text = (REPO_ROOT / ".github/workflows/license-and-security-scan.yml").read_text(
        encoding="utf-8"
    )


@when("the main-branch readiness gate evaluates BDD tags and pytest coverage configuration")
def step_when_main_readiness_evaluated(context: Any) -> None:
    context.red_hits = check_no_red_scenarios(context.sim_root)
    context.allowed_red_hits = check_no_red_scenarios(
        context.sim_root, allowed_files=["features/sample_red.feature"]
    )
    context.parity_report = check_pipeline_parity(REPO_ROOT)


@then(
    "validation fails on lingering @red scenarios and requires at least 90 percent XML-reported branch coverage"
)
def step_then_red_rejected_and_coverage_enforced(context: Any) -> None:
    assert len(context.red_hits) == 1, f"Expected 1 @red hit, got: {context.red_hits}"
    assert context.red_hits[0].startswith("features/sample_red.feature:")
    assert context.allowed_red_hits == []

    assert "github.ref == 'refs/heads/main' || github.base_ref == 'main'" in context.ci_text
    assert "nectr.devtools.ci_parity" in context.ci_text
    assert "--forbid-red" in context.ci_text
    assert "--cov-branch" in context.ci_text
    assert "--cov-report=xml:coverage.xml" in context.ci_text
    assert "--cov-fail-under=90" in context.ci_text


@given("the scheduled security scan, PR policy, and release workflow configurations")
def step_given_scheduled_and_release_workflows(context: Any) -> None:
    ci_path = REPO_ROOT / ".github/workflows/license-and-security-scan.yml"
    release_path = REPO_ROOT / ".github/workflows/release.yml"
    schema_path = REPO_ROOT / "docs/planning/decisions.schema.json"
    decisions_path = REPO_ROOT / "docs/planning/decisions.yaml"

    context.ci_workflow = yaml.safe_load(ci_path.read_text(encoding="utf-8"))
    context.release_workflow = yaml.safe_load(release_path.read_text(encoding="utf-8"))
    context.decisions_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    context.decisions_data = yaml.safe_load(decisions_path.read_text(encoding="utf-8"))


@when("scheduled cron, JSON Schema, link-check, and Commitizen release steps are inspected")
def step_when_scheduled_and_release_inspected(context: Any) -> None:
    context.parity_report = check_pipeline_parity(REPO_ROOT)
    jsonschema.validate(instance=context.decisions_data, schema=context.decisions_schema)


@then(
    "daily cron verifies secrets baseline drift, decisions.yaml schema, permissive SPDX allow-licenses, lychee links, and tagged release automation"
)
def step_then_scheduled_and_release_verified(context: Any) -> None:
    diag_by_gate = {diag.gate: diag for diag in context.parity_report.diagnostics}
    for gate in ("check-jsonschema", "lychee", "release-workflow"):
        assert diag_by_gate[gate].passed, diag_by_gate[gate].details

    # YAML 1.1 safe_load parses unquoted `on:` as boolean True
    on_block = context.ci_workflow.get("on", context.ci_workflow.get(True, {}))
    schedules = on_block.get("schedule", [])
    assert any(entry.get("cron") == "0 6 * * *" for entry in schedules), schedules

    scan_steps = context.ci_workflow["jobs"]["license-and-security-scan"]["steps"]
    drift_steps = [
        step for step in scan_steps if step.get("if") == "github.event_name == 'schedule'"
    ]
    assert drift_steps and "detect-secrets" in str(drift_steps[0].get("run", ""))

    lychee_steps = [
        step
        for step in scan_steps
        if str(step.get("uses", "")).startswith("lycheeverse/lychee-action")
    ]
    assert lychee_steps
    lychee_with = lychee_steps[0].get("with", {})
    assert lychee_with.get("fail") is True
    assert "docs/ paper/ openspec/" in str(lychee_with.get("args", ""))

    dep_review_steps = context.ci_workflow["jobs"]["dependency-review"]["steps"]
    dep_step = next(
        step
        for step in dep_review_steps
        if str(step.get("uses", "")).startswith("actions/dependency-review-action")
    )
    dep_with = dep_step.get("with", {})
    assert "deny-licenses" not in dep_with, "Deprecated deny-licenses must not be used"
    allow_licenses = str(dep_with.get("allow-licenses", ""))
    for spdx in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"):
        assert spdx in allow_licenses, f"Missing {spdx} in allow-licenses"

    release_on = context.release_workflow.get("on", context.release_workflow.get(True, {}))
    assert "v*" in release_on["push"]["tags"]
    release_steps = context.release_workflow["jobs"]["release"]["steps"]
    release_runs = "\n".join(str(step.get("run", "")) for step in release_steps)
    assert "cz check" in release_runs
    assert "cz changelog --dry-run" in release_runs
    assert any(
        str(step.get("uses", "")).startswith("softprops/action-gh-release")
        for step in release_steps
    )


@given("all GitHub Actions workflow definitions under .github/workflows")
def step_given_all_workflow_defs(context: Any) -> None:
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir(), "Missing .github/workflows directory"
    context.workflow_files = sorted(workflows_dir.glob("*.yml"))
    assert len(context.workflow_files) >= 3


@when("the CI workflow runtime and action hygiene validator inspects all workflow files")
def step_when_workflow_hygiene_runs(context: Any) -> None:
    context.hygiene_errors = check_workflow_action_hygiene(REPO_ROOT)


@then(
    "workflows require Node 24 action versions, isolated setup-uv cache suffixes, permissive SPDX allow-licenses with action license exclusions, clean lychee temp output, and quiet MkDocs logs"
)
def step_then_workflow_hygiene_verified(context: Any) -> None:
    assert context.hygiene_errors == [], f"Workflow hygiene errors: {context.hygiene_errors}"
