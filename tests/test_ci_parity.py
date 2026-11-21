"""Strict TDD tests for local-hook and CI pipeline parity + @red main-branch guard."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


def _write_synthetic_workspace(root: Path, *, include_release: bool = True) -> None:
    """Create a minimal synthetic workspace with all required hook and CI files."""
    githooks = root / ".githooks"
    workflows = root / ".github" / "workflows"
    features = root / "features"
    githooks.mkdir(parents=True, exist_ok=True)
    workflows.mkdir(parents=True, exist_ok=True)
    features.mkdir(parents=True, exist_ok=True)

    (githooks / "pre-commit").write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env sh
            REPO_ROOT=$(cygpath -u "$(git rev-parse --show-toplevel)")
            PATH="$REPO_ROOT/.venv/Scripts:$REPO_ROOT/.venv/bin:$PATH"
            git diff --cached --name-only -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline
            git grep --cached -nE '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
            adrlint --no-color lint
            adrlint --no-color format --check
            adrlint --no-color lock --check
            check-jsonschema --schemafile docs/planning/decisions.schema.json docs/planning/decisions.yaml
            python -m nectr.devtools.decisions check
            python -m nectr.devtools.citations check
            python -m nectr.devtools.docs_sync check
            python -m nectr.devtools.spec_links
            ruff check src tests features
            ruff format --check src tests features
            pymarkdown --config pyproject.toml scan README.md docs/theory paper
            mkdocs build --strict
            python -m mypy src
            python -m pytest
            python -m behave --tags=-red
            """
        ),
        encoding="utf-8",
    )

    (githooks / "pre-push").write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env sh
            REPO_ROOT=$(cygpath -u "$(git rev-parse --show-toplevel)")
            PATH="$REPO_ROOT/.venv/Scripts:$REPO_ROOT/.venv/bin:$PATH"
            git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline
            git grep -nE '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
            mkdocs build --strict
            python -m pytest
            python -m behave
            """
        ),
        encoding="utf-8",
    )

    (root / ".pre-commit-config.yaml").write_text(
        textwrap.dedent(
            """\
            repos:
              - repo: local
                hooks:
                  - id: detect-secrets
                    entry: detect-secrets-hook --baseline .secrets.baseline
                  - id: forbid-local-paths
                    entry: '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
                  - id: adrlint-check
                    entry: adrlint lint
                  - id: check-jsonschema-decisions
                    entry: check-jsonschema --schemafile docs/planning/decisions.schema.json docs/planning/decisions.yaml
                  - id: nectr-decisions-check
                    entry: python -m nectr.devtools.decisions check
                  - id: nectr-citations-check
                    entry: python -m nectr.devtools.citations check
                  - id: nectr-docs-check
                    entry: python -m nectr.devtools.docs_sync check
                  - id: nectr-spec-links-check
                    entry: python -m nectr.devtools.spec_links
                  - id: ruff-check
                    entry: ruff check src tests features
                  - id: ruff-format-check
                    entry: ruff format --check src tests features
                  - id: mkdocs-build-strict
                    entry: mkdocs build --strict
                  - id: pymarkdown-lint
                    entry: pymarkdown --config pyproject.toml scan README.md docs/theory paper
                  - id: mypy-strict-typecheck
                    entry: python -m mypy src
                  - id: nectr-tdd-unit-tests
                    entry: python -m pytest
                  - id: nectr-bdd-behave-precommit
                    entry: python -m behave --tags=-red
            """
        ),
        encoding="utf-8",
    )

    (workflows / "license-and-security-scan.yml").write_text(
        textwrap.dedent(
            """\
            name: License, Security & Quality Scan
            jobs:
              matrix-test:
                strategy:
                  matrix:
                    os: [ubuntu-latest, windows-latest]
                    python-version: ['3.11', '3.12', '3.13']
                steps:
                  - run: uv sync --frozen --extra dev --extra research
                  - run: detect-secrets-hook --baseline .secrets.baseline
                  - run: git grep -nE '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
                  - run: adrlint lint && adrlint format --check && adrlint lock --check
                  - run: check-jsonschema --schemafile docs/planning/decisions.schema.json docs/planning/decisions.yaml
                  - run: nectr-decisions check && nectr-citations check && nectr-docs check && python -m nectr.devtools.spec_links
                  - run: ruff check src tests features
                  - run: ruff format --check src tests features
                  - run: pymarkdown --config pyproject.toml scan README.md docs/theory paper
                  - run: lychee docs paper openspec
                  - run: mypy src
                  - run: mkdocs build --strict
                  - run: python -m pytest --cov=src/nectr --cov-fail-under=80
                  - run: python -m behave
            """
        ),
        encoding="utf-8",
    )

    if include_release:
        (workflows / "release.yml").write_text(
            "name: Release\njobs:\n  release:\n    steps:\n      - run: cz bump --check-consistency\n",
            encoding="utf-8",
        )


@pytest.mark.xfail(strict=True, reason="RED: add-github-actions-and-schema-hooks")
def test_check_pipeline_parity_passes_on_complete_workspace(tmp_path: Path) -> None:
    from nectr.devtools.ci_parity import check_pipeline_parity

    _write_synthetic_workspace(tmp_path, include_release=True)
    report = check_pipeline_parity(tmp_path)

    assert report.passed is True
    assert report.errors == ()
    assert len(report.diagnostics) >= 10
    assert all(diag.passed for diag in report.diagnostics)


@pytest.mark.xfail(strict=True, reason="RED: add-github-actions-and-schema-hooks")
def test_check_pipeline_parity_reports_missing_gates_and_release_yml(tmp_path: Path) -> None:
    from nectr.devtools.ci_parity import check_pipeline_parity

    _write_synthetic_workspace(tmp_path, include_release=False)
    ci_file = tmp_path / ".github" / "workflows" / "license-and-security-scan.yml"
    ci_text = ci_file.read_text(encoding="utf-8")
    ci_text = ci_text.replace("lychee", "echo skipped").replace("--cov-fail-under=80", "")
    ci_file.write_text(ci_text, encoding="utf-8")

    report = check_pipeline_parity(tmp_path)

    assert report.passed is False
    failed_gates = {diag.gate for diag in report.diagnostics if not diag.passed}
    assert "lychee" in failed_gates
    assert "pytest-coverage" in failed_gates
    assert "release-workflow" in failed_gates


@pytest.mark.xfail(strict=True, reason="RED: add-github-actions-and-schema-hooks")
def test_check_no_red_scenarios_detects_red_tag_and_ignores_prose(tmp_path: Path) -> None:
    from nectr.devtools.ci_parity import check_no_red_scenarios

    features = tmp_path / "features"
    features.mkdir(parents=True)
    (features / "clean.feature").write_text(
        "Feature: Clean\n  So that @red leaks are prevented\n  Scenario: Ok\n    Given x\n",
        encoding="utf-8",
    )
    (features / "dirty.feature").write_text(
        "Feature: Dirty\n  @red\n  Scenario: Pending\n    Given x\n",
        encoding="utf-8",
    )

    hits = check_no_red_scenarios(tmp_path)
    assert hits == ["features/dirty.feature:2"]

    filtered_hits = check_no_red_scenarios(tmp_path, allowed_files={"features/dirty.feature"})
    assert filtered_hits == []


@pytest.mark.xfail(strict=True, reason="RED: add-github-actions-and-schema-hooks")
def test_cli_main_check_and_forbid_red(tmp_path: Path) -> None:
    from nectr.devtools.ci_parity import main

    _write_synthetic_workspace(tmp_path, include_release=True)
    (tmp_path / "features" / "pending.feature").write_text(
        "Feature: Pending\n  @red\n  Scenario: Still red\n    Given x\n",
        encoding="utf-8",
    )

    assert main(["check", "--root", str(tmp_path)]) == 0
    assert main(["check", "--root", str(tmp_path), "--forbid-red"]) == 1
    assert (
        main(
            [
                "check",
                "--root",
                str(tmp_path),
                "--forbid-red",
                "--allow-file",
                "features/pending.feature",
            ]
        )
        == 0
    )
