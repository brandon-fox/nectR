#!/usr/bin/env python3
"""Zero-dependency security, privacy, and local-path scanner for nectR.

Used as:
- Pre-read / pre-edit agent gate: ``python scripts/security_scan.py --path <file>``
- Pre-commit hook:               ``python scripts/security_scan.py --staged``
- Pre-push hook:                 ``python scripts/security_scan.py --push``
- Full repository audit:         ``python scripts/security_scan.py --all``
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_FILENAMES = re.compile(
    r"(^|/)\.env(\.[^/]+)?$"
    r"|\.(pem|key|p12|pfx|secret|keystore)$"
    r"|(^|/)(id_rsa|id_ed25519|id_ecdsa)(\.pub)?$",
    re.IGNORECASE,
)

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "site",
    "node_modules",
}

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".zip",
    ".tar",
    ".gz",
    ".pyc",
    ".pyo",
}

# Each tuple: (rule_id, description, compiled_regex)
SECRET_AND_PATH_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "SEC-001",
        "Private key block header",
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    ),
    (
        "SEC-002",
        "AWS Access Key ID",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    (
        "SEC-003",
        "GitHub personal access token",
        re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
    ),
    (
        "SEC-004",
        "Google API key",
        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    ),
    (
        "SEC-005",
        "Generic sk- secret key",
        re.compile(r"\bsk-[A-Za-z0-9\-_]{20,}\b"),
    ),
    (
        "SEC-006",
        "Slack token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"),
    ),
    (
        "SEC-007",
        "Hardcoded credential assignment",
        re.compile(
            r"""(?i)\b(password|passwd|secret|api_key|apikey|access_token|private_key)\s*[:=]\s*['"][^'"\s]{8,}['"]"""
        ),
    ),
    (
        "PATH-001",
        "Hardcoded Windows user home path",
        re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"'`<>]+", re.IGNORECASE),  # scan:ignore-pattern
    ),
    (
        "PATH-002",
        "Hardcoded forward-slash Windows user home path",
        re.compile(r"[A-Za-z]:/Users/[^/\s\"'`<>]+", re.IGNORECASE),  # scan:ignore-pattern
    ),
    (
        "PATH-003",
        "Hardcoded macOS or Linux home path",
        re.compile(r"(?<![A-Za-z0-9_])/(Users|home)/[^/\s\"'`<>]+"),  # scan:ignore-pattern
    ),
    (
        "PATH-004",
        "Hardcoded Windows drive path",
        re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\(?![nrt\s\"'`])"),  # scan:ignore-pattern
    ),
    (
        "PRIV-001",
        "Local AI/agent configuration path reference",
        re.compile(r"(?i)(\.gemini[/\\]|\.ollama[/\\])"),  # scan:ignore-pattern
    ),
]


def _run_git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    return False


def _collect_files(mode: str, explicit_paths: list[str]) -> list[Path]:
    if explicit_paths:
        return [
            (REPO_ROOT / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
            for p in explicit_paths
        ]
    if mode == "staged":
        rel_paths = _run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        return [(REPO_ROOT / p).resolve() for p in rel_paths]
    if mode == "push":
        tracked = set(_run_git(["ls-files"]))
        staged = set(_run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"]))
        return [(REPO_ROOT / p).resolve() for p in sorted(tracked | staged)]
    # mode == "all"
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if path.is_file() and not _should_skip(path.relative_to(REPO_ROOT)):
            files.append(path.resolve())
    return files


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    if not path.exists() or not path.is_file():
        return findings

    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = path.as_posix()

    if _should_skip(Path(rel)):
        return findings

    if FORBIDDEN_FILENAMES.search(rel) and not rel.endswith(".env.example"):
        findings.append(f"[FILE-001] Forbidden secret/key filename: {rel}")

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings

    is_self = rel == "scripts/security_scan.py"
    for line_no, line in enumerate(content.splitlines(), start=1):
        if is_self and "# scan:ignore-pattern" in line:
            continue
        for rule_id, desc, pattern in SECRET_AND_PATH_RULES:
            if pattern.search(line):
                findings.append(f"[{rule_id}] {desc} at {rel}:{line_no}: {line.strip()[:120]}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan nectR for secrets, private refs, and local paths.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="Scan git staged files (pre-commit).")
    group.add_argument("--push", action="store_true", help="Scan tracked/staged files (pre-push).")
    group.add_argument("--all", action="store_true", help="Scan all non-ignored workspace files.")
    parser.add_argument("--path", action="append", default=[], help="Scan specific file path(s).")
    args = parser.parse_args(argv)

    mode = "staged" if args.staged else "push" if args.push else "all"
    files = _collect_files(mode, args.path)

    all_findings: list[str] = []
    for file_path in files:
        all_findings.extend(scan_file(file_path))

    if all_findings:
        print("SECURITY / PRIVACY SCAN FAILED:", file=sys.stderr)
        for finding in all_findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print(f"Security/privacy scan passed ({len(files)} file(s) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
