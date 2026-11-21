"""Step definitions for OpenSpec-to-Feature Single Source of Truth Linking."""

from __future__ import annotations

import tempfile
from pathlib import Path

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]


@given("a temporary workspace with a spec containing a hardcoded Given/When/Then scenario")
def step_given_hardcoded_spec(context) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._tmp = tmp
    root = Path(tmp.name)
    (root / "features" / "steps").mkdir(parents=True)
    (root / "features" / "demo.feature").write_text("Feature: Demo\n", encoding="utf-8")
    (root / "features" / "steps" / "demo_steps.py").write_text("", encoding="utf-8")
    spec_dir = root / "openspec" / "specs" / "demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Demo\n"
        "- [demo.feature](../../../features/demo.feature)\n"
        "- [demo_steps.py](../../../features/steps/demo_steps.py)\n"
        "#### Scenario: Inline\n"
        "- **GIVEN** something\n",
        encoding="utf-8",
    )
    context.target_root = root
    context.last_error = None


@given("a temporary workspace with a spec missing feature and step links")
def step_given_unlinked_spec(context) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._tmp = tmp
    root = Path(tmp.name)
    spec_dir = root / "openspec" / "specs" / "demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Demo\n### Requirement: X\n", encoding="utf-8")
    context.target_root = root
    context.last_error = None


@given("the repository root OpenSpec workspace")
def step_given_repo_root(context) -> None:
    context.target_root = REPO_ROOT
    context.last_error = None


@when("the OpenSpec feature-link validator runs on the temporary workspace")
@when("the OpenSpec feature-link validator runs on the repository root")
def step_when_validator_runs(context) -> None:
    from nectr.devtools.spec_links import SpecLinkError, validate_spec_links

    try:
        context.validated_specs = validate_spec_links(context.target_root)
    except SpecLinkError as exc:
        context.last_error = exc


@then('spec-link validation fails with "{expected}"')
def step_then_fails(context, expected: str) -> None:
    assert context.last_error is not None, "Expected SpecLinkError"
    assert expected.lower() in str(context.last_error).lower(), str(context.last_error)


@then("all OpenSpec spec.md files pass link validation")
def step_then_passes(context) -> None:
    assert context.last_error is None, f"Unexpected error: {context.last_error}"
    assert len(context.validated_specs) >= 2
