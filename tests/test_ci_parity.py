"""Strict TDD tests for local-hook and CI pipeline parity + @red main-branch guard."""

from __future__ import annotations

import textwrap
from pathlib import Path

from nectr.devtools.ci_parity import (
    check_no_red_scenarios,
    check_pipeline_parity,
    check_workflow_action_hygiene,
    main,
)


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
            exclude: ^(\\.worktrees|\\.poodle-temp)/
            ci:
              autofix_prs: true
              autofix_commit_msg: "style(pre-commit.ci): auto fixes from pre-commit hooks"
              autoupdate_prs: true
              autoupdate_branch: "chore/pre-commit-autoupdate"
              autoupdate_commit_msg: "chore(deps): pre-commit.ci weekly hook autoupdate"
              autoupdate_schedule: weekly
              submodules: false
              skip:
                - adrlint-check
                - nectr-decisions-check
                - nectr-citations-check
                - nectr-docs-check
                - nectr-spec-links-check
                - mkdocs-build-strict
                - pymarkdown-lint
                - mypy-strict-typecheck
                - nectr-tdd-unit-tests
                - nectr-bdd-behave-precommit
            repos:
              - repo: https://github.com/Yelp/detect-secrets
                rev: v1.5.0
                hooks:
                  - id: detect-secrets
                    args: ["--baseline", ".secrets.baseline"]
              - repo: https://github.com/python-jsonschema/check-jsonschema
                rev: 0.39.0
                hooks:
                  - id: check-jsonschema
                    args: ["--schemafile", "docs/planning/decisions.schema.json", "docs/planning/decisions.yaml"]
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: v0.17.6
                hooks:
                  - id: ruff-check
                  - id: ruff-format
              - repo: local
                hooks:
                  - id: forbid-local-paths
                    language: pygrep
                    entry: '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
                  - id: adrlint-check
                    language: system
                    entry: adrlint lint
                  - id: nectr-decisions-check
                    language: system
                    entry: python -m nectr.devtools.decisions check
                  - id: nectr-citations-check
                    language: system
                    entry: python -m nectr.devtools.citations check
                  - id: nectr-docs-check
                    language: system
                    entry: python -m nectr.devtools.docs_sync check
                  - id: nectr-spec-links-check
                    language: system
                    entry: python -m nectr.devtools.spec_links
                  - id: mkdocs-build-strict
                    language: system
                    entry: mkdocs build --strict
                  - id: pymarkdown-lint
                    language: system
                    entry: pymarkdown --config pyproject.toml scan README.md docs/theory paper
                  - id: mypy-strict-typecheck
                    language: system
                    entry: python -m mypy src
                  - id: nectr-tdd-unit-tests
                    language: system
                    entry: python -m pytest
                  - id: nectr-bdd-behave-precommit
                    language: system
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
                  - uses: astral-sh/setup-uv@v10.4.0
                    with:
                      python-version: '3.12'
                      enable-cache: true
                      cache-suffix: dev-research
                  - run: uv sync --frozen --extra dev --extra research
                  - run: detect-secrets-hook --baseline .secrets.baseline
                  - run: git grep -nE '([A-Za-z]:[/\\\\]Users[/\\\\]|/(Users|home)/)'
                  - run: adrlint lint && adrlint format --check && adrlint lock --check
                  - run: check-jsonschema --schemafile docs/planning/decisions.schema.json docs/planning/decisions.yaml
                  - run: nectr-decisions check && nectr-citations check && nectr-docs check && python -m nectr.devtools.spec_links
                  - run: ruff check src tests features
                  - run: ruff format --check src tests features
                  - run: pymarkdown --config pyproject.toml scan README.md docs/theory paper
                  - uses: lycheeverse/lychee-action@v2
                    with:
                      args: --exclude-path "openspec/changes/archive/" --exclude-path "docs/theory/research/" docs/ paper/ openspec/
                      output: ${{ runner.temp }}/lychee-out.md
                  - run: mypy src
                  - env:
                      NO_MKDOCS_2_WARNING: "1"
                    run: mkdocs build --strict
                  - run: python -m pytest --cov=src/nectr --cov-fail-under=80
                  - run: python -m behave
              dependency-review:
                steps:
                  - uses: actions/dependency-review-action@v5
                    with:
                      fail-on-severity: high
                      allow-licenses: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, PSF-2.0, Python-2.0, MPL-2.0, 0BSD, Zlib, Unlicense, CC0-1.0
                      allow-dependencies-licenses: pkg:githubactions/astral-sh/setup-uv
            """
        ),
        encoding="utf-8",
    )

    if include_release:
        (workflows / "release.yml").write_text(
            textwrap.dedent(
                """\
                name: Release
                jobs:
                  release:
                    steps:
                      - uses: astral-sh/setup-uv@v10.4.0
                        with:
                          cache-suffix: release
                      - run: cz bump --check-consistency
                      - uses: softprops/action-gh-release@v3
                """
            ),
            encoding="utf-8",
        )


def test_check_pipeline_parity_passes_on_complete_workspace(tmp_path: Path) -> None:
    _write_synthetic_workspace(tmp_path, include_release=True)
    report = check_pipeline_parity(tmp_path)

    assert report.passed is True
    assert report.errors == ()
    assert len(report.diagnostics) >= 10
    assert all(diag.passed for diag in report.diagnostics)


def test_check_pipeline_parity_reports_missing_gates_and_release_yml(tmp_path: Path) -> None:
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


def test_check_no_red_scenarios_detects_red_tag_and_ignores_prose(tmp_path: Path) -> None:
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


def test_cli_main_check_and_forbid_red(tmp_path: Path) -> None:
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


def test_check_workflow_action_hygiene_accepts_hardened_workflows(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "license-and-security-scan.yml").write_text(
        textwrap.dedent(
            """\
            name: License, Security & Quality Scan
            jobs:
              license-and-security-scan:
                steps:
                  - uses: astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d # v10.4.0
                    with:
                      python-version: "3.12"
                      enable-cache: true
                      cache-suffix: dev-research
                  - env:
                      NO_MKDOCS_2_WARNING: "1"
                    run: uv run mkdocs build --strict
                  - uses: lycheeverse/lychee-action@e7477775783ea5526144ba13e8db5eec57747ce8 # v2.9.0
                    with:
                      args: --exclude-path "openspec/changes/archive/" --exclude-path "docs/theory/research/" docs/ paper/ openspec/
                      output: ${{ runner.temp }}/lychee-out.md
              test-matrix:
                steps:
                  - uses: astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d # v10.4.0
                    with:
                      python-version: "3.12"
                      enable-cache: true
                      cache-suffix: dev
              dependency-review:
                steps:
                  - uses: actions/dependency-review-action@bbc44d14a204704ccc493733616cd1e93a0321ec # v5.0.1
                    with:
                      fail-on-severity: high
                      allow-licenses: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, PSF-2.0, Python-2.0, MPL-2.0, 0BSD, Zlib, Unlicense, CC0-1.0
                      allow-dependencies-licenses: pkg:githubactions/astral-sh/setup-uv
            """
        ),
        encoding="utf-8",
    )
    (workflows / "release.yml").write_text(
        textwrap.dedent(
            """\
            name: Release
            jobs:
              release:
                steps:
                  - uses: astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d # v10.4.0
                    with:
                      python-version: "3.12"
                      enable-cache: true
                      cache-suffix: release
                  - uses: softprops/action-gh-release@8a0cd651e5b2365bd640854a3fa5dfc70e4875f3 # v3.0.4
            """
        ),
        encoding="utf-8",
    )
    (workflows / "roadmap-and-changelog.yml").write_text(
        textwrap.dedent(
            """\
            name: Automated Changelog & OpenSpec Roadmap
            jobs:
              changelog-and-openspec-summary:
                steps:
                  - uses: astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d # v10.4.0
                    with:
                      python-version: "3.12"
                      enable-cache: true
                      cache-suffix: lint
            """
        ),
        encoding="utf-8",
    )

    violations = check_workflow_action_hygiene(tmp_path)
    assert violations == []


def test_check_workflow_action_hygiene_flags_node20_and_deprecated_review(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "license-and-security-scan.yml").write_text(
        textwrap.dedent(
            """\
            name: License, Security & Quality Scan
            jobs:
              license-and-security-scan:
                steps:
                  - uses: astral-sh/setup-uv@v5
                    with:
                      python-version: "3.12"
                  - run: uv run mkdocs build --strict
                  - uses: lycheeverse/lychee-action@v2
                    with:
                      args: docs/ paper/ openspec/
              matrix-a:
                steps:
                  - uses: astral-sh/setup-uv@v10.4.0
                    with:
                      cache-suffix: shared
              matrix-b:
                steps:
                  - uses: astral-sh/setup-uv@v10.4.0
                    with:
                      cache-suffix: shared
              dependency-review:
                steps:
                  - uses: actions/dependency-review-action@v5
                    with:
                      deny-licenses: GPL-3.0
            """
        ),
        encoding="utf-8",
    )
    (workflows / "release.yml").write_text(
        textwrap.dedent(
            """\
            name: Release
            jobs:
              release:
                steps:
                  - uses: astral-sh/setup-uv@v5
                  - uses: softprops/action-gh-release@v2
            """
        ),
        encoding="utf-8",
    )

    violations = check_workflow_action_hygiene(tmp_path)
    joined = "\n".join(violations)
    assert "setup-uv" in joined
    assert "action-gh-release" in joined
    assert "deny-licenses" in joined
    assert "cache-suffix" in joined
    assert "duplicate setup-uv cache-suffix" in joined
    assert "lychee" in joined
    assert "NO_MKDOCS_2_WARNING" in joined


def _write_valid_pre_commit_ci_yaml(root: Path) -> None:
    (root / ".pre-commit-config.yaml").write_text(
        textwrap.dedent(
            """\
            exclude: ^(\\.worktrees|\\.poodle-temp)/
            ci:
              autofix_prs: true
              autofix_commit_msg: "style(pre-commit.ci): auto fixes from pre-commit hooks"
              autoupdate_prs: true
              autoupdate_branch: "chore/pre-commit-autoupdate"
              autoupdate_commit_msg: "chore(deps): pre-commit.ci weekly hook autoupdate"
              autoupdate_schedule: weekly
              submodules: false
              skip:
                - adrlint-check
                - mypy-strict-typecheck
            repos:
              - repo: https://github.com/pre-commit/pre-commit-hooks
                rev: v6.0.0
                hooks:
                  - id: end-of-file-fixer
                  - id: trailing-whitespace
              - repo: https://github.com/Yelp/detect-secrets
                rev: v1.5.0
                hooks:
                  - id: detect-secrets
                    args: ["--baseline", ".secrets.baseline"]
              - repo: https://github.com/python-jsonschema/check-jsonschema
                rev: 0.39.0
                hooks:
                  - id: check-jsonschema
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: v0.17.6
                hooks:
                  - id: ruff-check
                  - id: ruff-format
              - repo: local
                hooks:
                  - id: forbid-local-paths
                    language: pygrep
                    entry: '(Users|home)'
                  - id: forbid-mutation-pragmas
                    language: pygrep
                    entry: 'nomut'
                  - id: adrlint-check
                    language: system
                    entry: adrlint lint
                  - id: mypy-strict-typecheck
                    language: system
                    entry: python -m mypy src
            """
        ),
        encoding="utf-8",
    )


def test_real_repo_pre_commit_ci_config_is_valid() -> None:
    from nectr.devtools import ci_parity

    repo_root = Path(__file__).resolve().parents[1]
    assert ci_parity.check_pre_commit_ci_config(repo_root) == []


def test_check_pre_commit_ci_config_accepts_valid_split_config(tmp_path: Path) -> None:
    from nectr.devtools import ci_parity

    _write_valid_pre_commit_ci_yaml(tmp_path)
    assert ci_parity.check_pre_commit_ci_config(tmp_path) == []


def test_check_pre_commit_ci_config_flags_missing_and_invalid_ci_fields(
    tmp_path: Path,
) -> None:
    from nectr.devtools import ci_parity

    missing_errors = ci_parity.check_pre_commit_ci_config(tmp_path)
    assert len(missing_errors) == 1
    assert "Missing .pre-commit-config.yaml" in missing_errors[0]

    (tmp_path / ".pre-commit-config.yaml").write_text("- not-a-mapping\n", encoding="utf-8")
    non_map_errors = ci_parity.check_pre_commit_ci_config(tmp_path)
    assert len(non_map_errors) == 1
    assert "YAML mapping" in non_map_errors[0]

    (tmp_path / ".pre-commit-config.yaml").write_text(
        textwrap.dedent(
            """\
            exclude: ^site/
            ci:
              autofix_prs: false
              autofix_commit_msg: "[pre-commit.ci] auto fixes"
              autoupdate_prs: false
              autoupdate_branch: "pre-commit-ci-update-config"
              autoupdate_commit_msg: "[pre-commit.ci] pre-commit autoupdate"
              autoupdate_schedule: daily
              submodules: true
              skip:
                - ruff-check
                - unknown-stale-hook
            repos:
              - repo: https://github.com/example/unapproved-gpl-hooks
                rev: main
                hooks:
                  - id: bad-hook
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: ""
                hooks:
                  - id: ruff-check
              - repo: local
                hooks:
                  - id: unskipped-system-hook
                    language: system
                    entry: pytest
            """
        ),
        encoding="utf-8",
    )
    errors = ci_parity.check_pre_commit_ci_config(tmp_path)
    joined = "\n".join(errors)
    assert ".worktrees" in joined
    assert ".poodle-temp" in joined
    assert "autofix_prs" in joined
    assert "autoupdate_prs" in joined
    assert "autofix_commit_msg" in joined
    assert "autoupdate_commit_msg" in joined
    assert "autoupdate_branch" in joined
    assert "autoupdate_schedule" in joined
    assert "submodules" in joined
    assert "unapproved-gpl-hooks" in joined
    assert "rev" in joined
    assert "unskipped-system-hook" in joined
    assert "ruff-check" in joined
    assert "unknown-stale-hook" in joined


def test_cli_main_fails_when_pre_commit_ci_config_is_invalid(tmp_path: Path) -> None:
    _write_synthetic_workspace(tmp_path, include_release=True)
    cfg = tmp_path / ".pre-commit-config.yaml"
    cfg.write_text(
        cfg.read_text(encoding="utf-8") + "\nci:\n  autofix_prs: false\n", encoding="utf-8"
    )
    assert main(["check", "--root", str(tmp_path)]) == 1
