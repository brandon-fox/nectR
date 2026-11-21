"""Behave step definitions for ci_and_hook_parity (Phase 1 RED pending)."""

from __future__ import annotations

from behave import given, then, when


@given("the repository root hook, pre-commit, and GitHub Actions workflow definitions")
def step_given_hook_and_ci_defs(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@when("the CI and hook parity validator inspects local and remote pipeline stages")
def step_when_parity_validator_runs(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@then(
    "every local security, governance, lint, format, type, docs, and test gate is mirrored in CI with cross-platform venv PATH resolution"
)
def step_then_parity_verified(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@given("the repository pyproject.toml, uv.lock, and GitHub Actions CI workflow")
def step_given_lock_and_matrix(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@when("the CI matrix and dependency audit configuration is validated")
def step_when_matrix_validated(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@then(
    "CI installs locked dev and research extras via uv and runs tests across Python 3.11 to 3.13 on Linux and Windows"
)
def step_then_matrix_and_uv_verified(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@given("a simulated main-branch CI check with an active @red feature scenario")
def step_given_main_branch_red_scenario(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@when("the main-branch readiness gate evaluates BDD tags and pytest coverage configuration")
def step_when_main_readiness_evaluated(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@then(
    "validation fails on lingering @red scenarios and requires at least 80 percent XML-reported test coverage"
)
def step_then_red_rejected_and_coverage_enforced(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@given("the scheduled security scan, PR policy, and release workflow configurations")
def step_given_scheduled_and_release_workflows(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@when("scheduled cron, JSON Schema, link-check, and Commitizen release steps are inspected")
def step_when_scheduled_and_release_inspected(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")


@then(
    "daily cron verifies secrets baseline drift, decisions.yaml schema, expanded SPDX deny-licenses, lychee links, and tagged release automation"
)
def step_then_scheduled_and_release_verified(context: object) -> None:
    raise NotImplementedError("RED: add-github-actions-and-schema-hooks not yet implemented")
