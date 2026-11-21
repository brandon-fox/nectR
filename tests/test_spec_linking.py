"""Strict TDD tests for OpenSpec-to-feature single-source-of-truth linking."""

from __future__ import annotations

from pathlib import Path

import pytest

from nectr.devtools.spec_links import SpecLinkError, validate_spec_links

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_rejects_hardcoded_scenario_in_spec(tmp_path: Path) -> None:
    (tmp_path / "features" / "steps").mkdir(parents=True)
    (tmp_path / "features" / "demo.feature").write_text("Feature: Demo\n", encoding="utf-8")
    (tmp_path / "features" / "steps" / "demo_steps.py").write_text("", encoding="utf-8")
    spec_dir = tmp_path / "openspec" / "specs" / "demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Demo\n"
        "- [demo.feature](../../../features/demo.feature)\n"
        "- [demo_steps.py](../../../features/steps/demo_steps.py)\n"
        "#### Scenario: Hardcoded\n- **GIVEN** x\n",
        encoding="utf-8",
    )

    with pytest.raises(SpecLinkError, match="hardcoded scenario"):
        validate_spec_links(tmp_path)


def test_rejects_missing_feature_or_step_links(tmp_path: Path) -> None:
    spec_dir = tmp_path / "openspec" / "specs" / "demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Demo\n### Requirement: Only intent\n", encoding="utf-8")

    with pytest.raises(SpecLinkError, match="missing linked"):
        validate_spec_links(tmp_path)


def test_repo_openspec_files_pass_link_validation() -> None:
    specs = validate_spec_links(REPO_ROOT)
    assert len(specs) >= 2
