"""Validate local hook, pre-commit, and GitHub Actions CI pipeline parity and @red guards."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

RED_TAG_LINE_RE = re.compile(r"^\s*@(?:.*\s)?red(?:\s|$)")
DEPRECATED_SETUP_UV_RE = re.compile(r"^astral-sh/setup-uv@v([1-6])(?:\.|$)")
DEPRECATED_GH_RELEASE_RE = re.compile(r"^softprops/action-gh-release@v([12])(?:\.|$)")
REQUIRED_PERMISSIVE_SPDX: tuple[str, ...] = (
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "PSF-2.0",
    "Python-2.0",
    "MPL-2.0",
    "0BSD",
    "Zlib",
    "Unlicense",
    "CC0-1.0",
)

REQUIRED_PIPELINE_FILES: tuple[str, ...] = (
    ".githooks/pre-commit",
    ".githooks/pre-push",
    ".pre-commit-config.yaml",
    ".github/workflows/license-and-security-scan.yml",
    ".github/workflows/pr-lifecycle.yml",
    ".github/workflows/release.yml",
)


class CiParityError(ValueError):
    """Raised when pipeline parity or @red main-branch guard validation fails."""


@dataclass(frozen=True)
class GateDiagnostic:
    """Structured parity result for a single governance, security, or test gate."""

    gate: str
    passed: bool
    missing_in: tuple[str, ...]
    details: str


@dataclass(frozen=True)
class ParityReport:
    """Aggregate result returned by :func:`check_pipeline_parity`."""

    passed: bool
    diagnostics: tuple[GateDiagnostic, ...]
    errors: tuple[str, ...]
    red_scenarios: tuple[str, ...] = ()


@dataclass(frozen=True)
class _GateSpec:
    """Declarative specification mapping a gate name to per-file regex patterns."""

    gate: str
    stage_patterns: tuple[tuple[str, tuple[str, ...]], ...]


_GATE_SPECS: tuple[_GateSpec, ...] = (
    _GateSpec(
        gate="detect-secrets",
        stage_patterns=(
            (".githooks/pre-commit", (r"detect-secrets-hook\s+--baseline\s+\.secrets\.baseline",)),
            (".githooks/pre-push", (r"detect-secrets-hook\s+--baseline\s+\.secrets\.baseline",)),
            (
                ".pre-commit-config.yaml",
                (r"detect-secrets-hook\s+--baseline\s+\.secrets\.baseline",),
            ),
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"detect-secrets-hook\s+--baseline\s+\.secrets\.baseline",),
            ),
        ),
    ),
    _GateSpec(
        gate="local-path-regex",
        stage_patterns=(
            (".githooks/pre-commit", (r"\(Users\|home\)",)),
            (".githooks/pre-push", (r"\(Users\|home\)",)),
            (".pre-commit-config.yaml", (r"\(Users\|home\)",)),
            (".github/workflows/license-and-security-scan.yml", (r"\(Users\|home\)",)),
        ),
    ),
    _GateSpec(
        gate="cygpath-venv-path",
        stage_patterns=(
            (".githooks/pre-commit", (r"cygpath\s+-u", r"\.venv/Scripts", r"\.venv/bin")),
            (".githooks/pre-push", (r"cygpath\s+-u", r"\.venv/Scripts", r"\.venv/bin")),
        ),
    ),
    _GateSpec(
        gate="adrlint",
        stage_patterns=(
            (".githooks/pre-commit", (r"adrlint\b",)),
            (".pre-commit-config.yaml", (r"adrlint\b",)),
            (".github/workflows/license-and-security-scan.yml", (r"adrlint\b",)),
        ),
    ),
    _GateSpec(
        gate="nectr-decisions",
        stage_patterns=(
            (".githooks/pre-commit", (r"(?:nectr\.devtools\.decisions|nectr-decisions)",)),
            (".pre-commit-config.yaml", (r"(?:nectr\.devtools\.decisions|nectr-decisions)",)),
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"(?:nectr\.devtools\.decisions|nectr-decisions)",),
            ),
        ),
    ),
    _GateSpec(
        gate="nectr-citations",
        stage_patterns=(
            (".githooks/pre-commit", (r"(?:nectr\.devtools\.citations|nectr-citations)",)),
            (".pre-commit-config.yaml", (r"(?:nectr\.devtools\.citations|nectr-citations)",)),
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"(?:nectr\.devtools\.citations|nectr-citations)",),
            ),
        ),
    ),
    _GateSpec(
        gate="nectr-docs",
        stage_patterns=(
            (".githooks/pre-commit", (r"(?:nectr\.devtools\.docs_sync|nectr-docs)",)),
            (".pre-commit-config.yaml", (r"(?:nectr\.devtools\.docs_sync|nectr-docs)",)),
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"(?:nectr\.devtools\.docs_sync|nectr-docs)",),
            ),
        ),
    ),
    _GateSpec(
        gate="nectr-spec-links",
        stage_patterns=(
            (".githooks/pre-commit", (r"nectr\.devtools\.spec_links",)),
            (".pre-commit-config.yaml", (r"nectr\.devtools\.spec_links",)),
            (".github/workflows/license-and-security-scan.yml", (r"nectr\.devtools\.spec_links",)),
        ),
    ),
    _GateSpec(
        gate="ruff-check",
        stage_patterns=(
            (".githooks/pre-commit", (r"ruff\s+check",)),
            (".pre-commit-config.yaml", (r"ruff\s+check",)),
            (".github/workflows/license-and-security-scan.yml", (r"ruff\s+check",)),
        ),
    ),
    _GateSpec(
        gate="ruff-format",
        stage_patterns=(
            (".githooks/pre-commit", (r"ruff\s+format\s+--check",)),
            (".pre-commit-config.yaml", (r"ruff\s+format\s+--check",)),
            (".github/workflows/license-and-security-scan.yml", (r"ruff\s+format\s+--check",)),
        ),
    ),
    _GateSpec(
        gate="pymarkdown",
        stage_patterns=(
            (".githooks/pre-commit", (r"pymarkdown\b",)),
            (".pre-commit-config.yaml", (r"pymarkdown\b",)),
            (".github/workflows/license-and-security-scan.yml", (r"pymarkdown\b",)),
        ),
    ),
    _GateSpec(
        gate="mypy",
        stage_patterns=(
            (".githooks/pre-push", (r"\bmypy\b",)),
            (".pre-commit-config.yaml", (r"\bmypy\b",)),
            (".github/workflows/license-and-security-scan.yml", (r"\bmypy\b",)),
        ),
    ),
    _GateSpec(
        gate="mkdocs-strict",
        stage_patterns=(
            (".githooks/pre-push", (r"mkdocs\s+build\s+--strict",)),
            (".pre-commit-config.yaml", (r"mkdocs\s+build\s+--strict",)),
            (".github/workflows/license-and-security-scan.yml", (r"mkdocs\s+build\s+--strict",)),
        ),
    ),
    _GateSpec(
        gate="pytest-coverage",
        stage_patterns=(
            (".githooks/pre-push", (r"\bpytest\b",)),
            (".pre-commit-config.yaml", (r"\bpytest\b",)),
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"\bpytest\b", r"--cov-branch", r"--cov-fail-under=90"),
            ),
        ),
    ),
    _GateSpec(
        gate="behave",
        stage_patterns=(
            (".githooks/pre-push", (r"\bbehave\b", r"--tags=-red")),
            (".pre-commit-config.yaml", (r"\bbehave\b",)),
            (".github/workflows/license-and-security-scan.yml", (r"\bbehave\b",)),
        ),
    ),
    _GateSpec(
        gate="check-jsonschema",
        stage_patterns=(
            (".githooks/pre-commit", (r"check-jsonschema\b",)),
            (".pre-commit-config.yaml", (r"check-jsonschema\b",)),
            (".github/workflows/license-and-security-scan.yml", (r"check-jsonschema\b",)),
        ),
    ),
    _GateSpec(
        gate="lychee",
        stage_patterns=((".github/workflows/license-and-security-scan.yml", (r"\blychee\b",)),),
    ),
    _GateSpec(
        gate="uv-frozen-sync",
        stage_patterns=(
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"uv\s+sync\s+--frozen\s+--extra\s+dev\s+--extra\s+research",),
            ),
        ),
    ),
    _GateSpec(
        gate="ci-matrix",
        stage_patterns=(
            (
                ".github/workflows/license-and-security-scan.yml",
                (r"3\.11", r"3\.12", r"3\.13", r"windows-latest"),
            ),
        ),
    ),
    _GateSpec(
        gate="release-workflow",
        stage_patterns=((".github/workflows/release.yml", (r"\b(?:cz|commitizen)\b",)),),
    ),
    _GateSpec(
        gate="pr-merge-safety",
        stage_patterns=(
            (
                ".github/workflows/license-and-security-scan.yml",
                (
                    r"nectr\.devtools\.pr_lifecycle\s+check-branch",
                    r"uv\s+lock\s+--check",
                    r"pull_request\.head\.sha",
                ),
            ),
        ),
    ),
    _GateSpec(
        gate="pr-lifecycle-workflow",
        stage_patterns=(
            (
                ".github/workflows/pr-lifecycle.yml",
                (r"nectr\.devtools\.pr_lifecycle", r"PR_LIFECYCLE_TOKEN"),
            ),
        ),
    ),
)


def _read_pipeline_files(repo_root: Path) -> tuple[dict[str, str], list[str]]:
    contents: dict[str, str] = {}
    errors: list[str] = []
    for rel_path in REQUIRED_PIPELINE_FILES:
        file_path = repo_root / rel_path
        if not file_path.is_file():
            errors.append(f"Missing required pipeline file: {rel_path}")
            contents[rel_path] = ""
        else:
            contents[rel_path] = file_path.read_text(encoding="utf-8")
    return contents, errors


def check_pipeline_parity(repo_root: Path) -> ParityReport:
    """Verify local hooks, pre-commit config, and GitHub workflows share required gates."""
    contents, errors = _read_pipeline_files(repo_root)
    diagnostics: list[GateDiagnostic] = []

    for spec in _GATE_SPECS:
        missing_in: list[str] = []
        for rel_path, patterns in spec.stage_patterns:
            text = contents.get(rel_path, "")
            if not text or any(re.search(pat, text) is None for pat in patterns):
                missing_in.append(rel_path)

        passed = len(missing_in) == 0
        details = (
            "All required stages aligned."
            if passed
            else f"Missing or incomplete in: {', '.join(missing_in)}"
        )
        if not passed:
            errors.append(f"Gate '{spec.gate}' failed parity: {details}")
        diagnostics.append(
            GateDiagnostic(
                gate=spec.gate,
                passed=passed,
                missing_in=tuple(missing_in),
                details=details,
            )
        )

    unpinned_actions = check_workflow_sha_pinning(repo_root)
    if unpinned_actions:
        details = (
            f"Unpinned GitHub Actions (require 40-char commit SHA): {', '.join(unpinned_actions)}"
        )
        errors.append(details)
        diagnostics.append(
            GateDiagnostic(
                gate="github-actions-sha-pinning",
                passed=False,
                missing_in=tuple(unpinned_actions),
                details=details,
            )
        )
    else:
        diagnostics.append(
            GateDiagnostic(
                gate="github-actions-sha-pinning",
                passed=True,
                missing_in=(),
                details="All GitHub Actions pinned to 40-char commit SHAs.",
            )
        )

    return ParityReport(
        passed=len(errors) == 0,
        diagnostics=tuple(diagnostics),
        errors=tuple(errors),
    )


_USES_LINE_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*['\"]?([^'\"#\s]+)['\"]?")
_SHA_PINNED_RE = re.compile(r"^[^@]+@[0-9a-fA-F]{40}$")


def check_workflow_sha_pinning(repo_root: Path) -> list[str]:
    """Return ``path:line (uses_ref)`` for any GitHub Action not pinned to a 40-char SHA."""
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []

    violations: list[str] = []
    workflow_files = sorted(list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml")))
    for wf_path in workflow_files:
        rel_posix = wf_path.relative_to(repo_root).as_posix()
        for line_no, line in enumerate(wf_path.read_text(encoding="utf-8").splitlines(), start=1):
            match = _USES_LINE_RE.match(line)
            if not match:
                continue
            ref = match.group(1)
            if ref.startswith(("./", "docker://")):
                continue
            if not _SHA_PINNED_RE.match(ref):
                violations.append(f"{rel_posix}:{line_no} ({ref})")
    return violations


def check_no_red_scenarios(
    repo_root: Path,
    *,
    feature_files: Sequence[Path] | None = None,
    allowed_files: Collection[str] = (),
) -> list[str]:
    """Return ``path:line`` entries for any ``@red`` Gherkin tag in feature files."""
    if feature_files is not None:
        candidates = sorted(feature_files)
    else:
        features_dir = repo_root / "features"
        candidates = sorted(features_dir.glob("*.feature")) if features_dir.is_dir() else []

    normalized_allowed = {item.replace("\\", "/") for item in allowed_files}
    hits: list[str] = []

    for feature_path in candidates:
        resolved = feature_path if feature_path.is_absolute() else (repo_root / feature_path)
        try:
            rel_posix = resolved.relative_to(repo_root).as_posix()
        except ValueError:
            rel_posix = resolved.as_posix()

        if rel_posix in normalized_allowed or resolved.name in normalized_allowed:
            continue

        for line_no, line in enumerate(resolved.read_text(encoding="utf-8").splitlines(), start=1):
            if RED_TAG_LINE_RE.match(line):
                hits.append(f"{rel_posix}:{line_no}")

    return hits


def _has_env_var(var_name: str, *containers: object) -> bool:
    for container in containers:
        if isinstance(container, dict):
            env_map = container.get("env")
            if isinstance(env_map, dict) and str(env_map.get(var_name, "")).strip():
                return True
    return False


def _validate_setup_uv_step(
    rel_path: str,
    job_name: str,
    step: dict[str, Any],
    seen_suffixes: set[str],
) -> list[str]:
    errors: list[str] = []
    uses = str(step.get("uses", "")).strip()
    if DEPRECATED_SETUP_UV_RE.match(uses):
        errors.append(
            f"{rel_path} ({job_name}): '{uses}' targets deprecated Node.js 20; use v10.4.0+ (Node 24)."
        )

    step_with = step.get("with")
    suffix = ""
    if isinstance(step_with, dict):
        suffix = str(step_with.get("cache-suffix", "")).strip()
    if not suffix:
        errors.append(
            f"{rel_path} ({job_name}): astral-sh/setup-uv must set a non-empty 'cache-suffix'."
        )
    elif suffix in seen_suffixes:
        errors.append(
            f"{rel_path} ({job_name}): duplicate setup-uv cache-suffix '{suffix}' risks cache collisions."
        )
    else:
        seen_suffixes.add(suffix)
    return errors


def _validate_dependency_review_step(
    rel_path: str,
    job_name: str,
    step: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    step_with = step.get("with")
    if not isinstance(step_with, dict):
        return [f"{rel_path} ({job_name}): dependency-review-action missing 'with' configuration."]

    if "deny-licenses" in step_with:
        errors.append(
            f"{rel_path} ({job_name}): deprecated 'deny-licenses' must be replaced with 'allow-licenses'."
        )

    allow_raw = str(step_with.get("allow-licenses", ""))
    allow_tokens = {item.strip() for item in allow_raw.split(",") if item.strip()}
    missing_spdx = [spdx for spdx in REQUIRED_PERMISSIVE_SPDX if spdx not in allow_tokens]
    if missing_spdx:
        errors.append(
            f"{rel_path} ({job_name}): allow-licenses missing permissive SPDX IDs: {', '.join(missing_spdx)}."
        )

    exclusions_raw = str(step_with.get("allow-dependencies-licenses", ""))
    if "pkg:githubactions/astral-sh/setup-uv" not in exclusions_raw:
        errors.append(
            f"{rel_path} ({job_name}): allow-dependencies-licenses should cover audited pkg:githubactions/astral-sh/setup-uv."
        )
    return errors


def _validate_lychee_step(rel_path: str, job_name: str, step: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    step_with = step.get("with")
    if not isinstance(step_with, dict):
        return [f"{rel_path} ({job_name}): lychee-action missing 'with' configuration."]

    args_str = str(step_with.get("args", ""))
    if "openspec/changes/archive/" not in args_str:
        errors.append(
            f"{rel_path} ({job_name}): lychee args must exclude 'openspec/changes/archive/'."
        )
    if "docs/theory/research/" not in args_str:
        errors.append(f"{rel_path} ({job_name}): lychee args must exclude 'docs/theory/research/'.")

    output_path = str(step_with.get("output", ""))
    if "runner.temp" not in output_path:
        errors.append(
            f"{rel_path} ({job_name}): lychee output must target '${{{{ runner.temp }}}}/...' to keep workspace clean."
        )
    return errors


def _validate_workflow_file(wf_path: Path, repo_root: Path) -> list[str]:
    rel_path = wf_path.relative_to(repo_root).as_posix()
    data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [f"{rel_path}: workflow root must be a YAML mapping."]

    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return []

    errors: list[str] = []
    seen_suffixes: set[str] = set()
    for job_name, job_body in jobs.items():
        if not isinstance(job_body, dict):
            continue
        steps = job_body.get("steps")
        if not isinstance(steps, list):
            continue

        for step in steps:
            if not isinstance(step, dict):
                continue
            uses = str(step.get("uses", "")).strip()
            run_cmd = str(step.get("run", ""))

            if uses.startswith("astral-sh/setup-uv@"):
                errors.extend(_validate_setup_uv_step(rel_path, str(job_name), step, seen_suffixes))
            elif DEPRECATED_GH_RELEASE_RE.match(uses):
                errors.append(
                    f"{rel_path} ({job_name}): '{uses}' targets deprecated Node.js 20; use v3+ (Node 24)."
                )
            elif uses.startswith("actions/dependency-review-action@"):
                errors.extend(_validate_dependency_review_step(rel_path, str(job_name), step))
            elif uses.startswith("lycheeverse/lychee-action@"):
                errors.extend(_validate_lychee_step(rel_path, str(job_name), step))

            if "mkdocs build --strict" in run_cmd and not _has_env_var(
                "NO_MKDOCS_2_WARNING", step, job_body, data
            ):
                errors.append(
                    f"{rel_path} ({job_name}): mkdocs build --strict should set NO_MKDOCS_2_WARNING='1'."
                )
    return errors


def check_pre_commit_ci_compatibility(repo_root: Path) -> list[str]:
    """Verify .pre-commit-config.yaml is safe and runnable on pre-commit.ci."""
    cfg_path = repo_root / ".pre-commit-config.yaml"
    if not cfg_path.is_file():
        return []

    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [".pre-commit-config.yaml: root must be a YAML mapping."]

    errors: list[str] = []
    ci_cfg = data.get("ci")
    if not isinstance(ci_cfg, dict):
        return [".pre-commit-config.yaml: missing 'ci' configuration for pre-commit.ci."]

    if ci_cfg.get("autofix_prs") is not False:
        errors.append(
            ".pre-commit-config.yaml: ci.autofix_prs must be false to prevent unsigned bot commits."
        )

    skip_raw = ci_cfg.get("skip", [])
    skip_ids = set(skip_raw) if isinstance(skip_raw, list) else set()
    for repo in data.get("repos", []):
        if not isinstance(repo, dict):
            continue
        for hook in repo.get("hooks", []):
            if not isinstance(hook, dict):
                continue
            stages = hook.get("stages", ["pre-commit"])
            if (
                hook.get("language") == "system"
                and isinstance(stages, list)
                and "pre-commit" in stages
                and hook.get("id") not in skip_ids
            ):
                errors.append(
                    f".pre-commit-config.yaml: pre-commit hook '{hook.get('id')}' uses "
                    "language: system without being listed in ci.skip for pre-commit.ci."
                )
    return errors


def check_workflow_action_hygiene(repo_root: Path) -> list[str]:
    """Validate Node 24 action runtimes, cache isolation, lychee output, and SPDX allow-list."""
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return ["Missing .github/workflows directory."]

    workflow_files = sorted(workflows_dir.glob("*.yml"))
    if not workflow_files:
        return ["No GitHub Actions workflow YAML files found under .github/workflows."]

    errors: list[str] = []
    for wf_path in workflow_files:
        errors.extend(_validate_workflow_file(wf_path, repo_root))
    return errors


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-ci-parity",
        description="Validate local hook / CI pipeline parity and main-branch @red guards.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="Run pipeline parity checks.")
    check_parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root directory.",
    )
    check_parser.add_argument(
        "--forbid-red",
        action="store_true",
        help="Fail if any .feature file contains an active @red Gherkin tag.",
    )
    check_parser.add_argument(
        "--allow-file",
        action="append",
        default=[],
        help="Relative feature file path (or filename) allowed to retain @red tags.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for ``nectr-ci-parity``."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    repo_root: Path = args.root.resolve()

    report = check_pipeline_parity(repo_root)
    hygiene_errors = check_workflow_action_hygiene(repo_root)
    pre_commit_ci_errors = check_pre_commit_ci_compatibility(repo_root)
    red_hits: list[str] = []
    if args.forbid_red:
        red_hits = check_no_red_scenarios(repo_root, allowed_files=args.allow_file)

    if not report.passed or hygiene_errors or pre_commit_ci_errors or red_hits:
        for err in report.errors:
            print(f"CI PARITY ERROR: {err}", file=sys.stderr)
        for err in hygiene_errors:
            print(f"CI WORKFLOW HYGIENE ERROR: {err}", file=sys.stderr)
        for err in pre_commit_ci_errors:
            print(f"PRE-COMMIT.CI COMPATIBILITY ERROR: {err}", file=sys.stderr)
        for hit in red_hits:
            print(f"FORBIDDEN @red SCENARIO: {hit}", file=sys.stderr)
        return 1

    print(
        f"CI parity check passed ({len(report.diagnostics)} gate(s) verified, workflow hygiene clean"
        + (", 0 @red tags" if args.forbid_red else "")
        + ")."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
