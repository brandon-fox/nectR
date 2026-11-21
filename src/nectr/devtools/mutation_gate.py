"""Tiered, diff-scoped mutation testing gate with ratcheting baseline floors."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import tokenize
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

_PRAGMA_PATTERN = re.compile(
    r"#\s*(?:" + "pra" + r"gma:\s*no\s+mutate|" + "no" + r"mut\b)",
    re.IGNORECASE,
)
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_TIMEOUT_REASON = "Trial Exceeded Timeout"


@dataclass(frozen=True)
class MutationPolicy:
    """Configuration policy for tiered mutation testing and baseline floors."""

    engine: str
    per_mutant_timeout_seconds: int
    tiers: dict[str, float]
    baseline: dict[str, float]
    excluded: tuple[str, ...]


@dataclass(frozen=True)
class MutationScore:
    """Aggregated mutant execution counts for one bounded-context tier."""

    killed: int
    survived: int
    timeout: int
    total: int

    @property
    def effective_score_pct(self) -> float:
        """Return effective kill percentage counting timeouts as caught."""
        if self.total == 0:
            return 100.0
        return ((self.killed + self.timeout) / self.total) * 100.0


@dataclass(frozen=True)
class GateOutcome:
    """Pass/fail evaluation across evaluated bounded-context tiers."""

    passed: bool
    summary: str
    failures: tuple[str, ...]
    scores: dict[str, MutationScore]


class MutationEngine(Protocol):
    """Protocol for pluggable mutation engine runners."""

    def run_tier(
        self,
        tier: str,
        files: Sequence[str],
        repo_root: Path,
        policy: MutationPolicy,
    ) -> list[dict[str, Any]]:
        """Execute mutation trials for *files* under *tier* and return raw trial records."""


def normalize_repo_path(path_str: str) -> str:
    """Normalize OS path separators and leading diff prefixes to forward-slash form."""
    cleaned = path_str.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if cleaned.startswith(("a/", "b/")):
        cleaned = cleaned[2:]
    return cleaned


def _canonicalize_source_path(source_file: str) -> str:
    norm = normalize_repo_path(source_file)
    if norm.startswith("nectr/"):
        return f"src/{norm}"
    return norm


def load_mutation_policy(pyproject_path: Path) -> MutationPolicy:
    """Load `[tool.nectr.mutation]` policy tables from *pyproject_path*."""
    raw = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    cfg = raw.get("tool", {}).get("nectr", {}).get("mutation", {})
    if not cfg:
        raise ValueError(f"Missing [tool.nectr.mutation] configuration in {pyproject_path}")
    tiers_raw = cfg.get("tiers", {})
    baseline_raw = cfg.get("baseline", {})
    excluded_raw = cfg.get("excluded", [])
    return MutationPolicy(
        engine=str(cfg.get("engine", "poodle")),
        per_mutant_timeout_seconds=int(cfg.get("per_mutant_timeout_seconds", 10)),
        tiers={normalize_repo_path(k).rstrip("/"): float(v) for k, v in tiers_raw.items()},
        baseline={normalize_repo_path(k).rstrip("/"): float(v) for k, v in baseline_raw.items()},
        excluded=tuple(normalize_repo_path(str(item)).rstrip("/") for item in excluded_raw),
    )


def _matches_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")


def classify(path: str, policy: MutationPolicy) -> str | None:
    """Return the bounded-context tier prefix for *path*, or None if excluded/untracked."""
    norm = normalize_repo_path(path)
    if any(_matches_prefix(norm, prefix) for prefix in policy.excluded):
        return None
    for prefix in sorted(policy.tiers, key=len, reverse=True):
        if _matches_prefix(norm, prefix):
            return prefix
    return None


def select_targets(paths: Sequence[str], policy: MutationPolicy) -> dict[str, list[str]]:
    """Group Python source files in *paths* by their bounded-context tier."""
    grouped: dict[str, list[str]] = {}
    seen: set[str] = set()
    for raw_path in paths:
        norm = normalize_repo_path(raw_path)
        if not norm.endswith(".py") or norm in seen:
            continue
        tier = classify(norm, policy)
        if tier is None:
            continue
        seen.add(norm)
        grouped.setdefault(tier, []).append(norm)
    return {tier: sorted(files) for tier, files in sorted(grouped.items())}


def parse_changed_line_ranges(diff_text: str) -> dict[str, list[tuple[int, int]]]:
    """Parse `git diff -U0` text into new-side inclusive `(start, end)` line ranges."""
    ranges: dict[str, list[tuple[int, int]]] = {}
    current_file: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            target = line[4:].strip()
            current_file = None if target == "/dev/null" else _canonicalize_source_path(target)
            continue
        match = _HUNK_HEADER_RE.match(line)
        if match and current_file is not None:
            start = int(match.group(1))
            count = int(match.group(2)) if match.group(2) is not None else 1
            if count > 0:
                ranges.setdefault(current_file, []).append((start, start + count - 1))
    return ranges


def filter_trials_to_changed_lines(
    trials: Sequence[Mapping[str, Any]],
    ranges: Mapping[str, Sequence[tuple[int, int]]],
) -> list[dict[str, Any]]:
    """Keep only trials whose mutated span intersects changed hunk ranges."""
    kept: list[dict[str, Any]] = []
    for trial in trials:
        mutant = trial.get("mutant", {})
        raw_file = str(mutant.get("source_file", ""))
        if not raw_file:
            continue
        norm_file = _canonicalize_source_path(raw_file)
        file_ranges = ranges.get(norm_file, ())
        if not file_ranges:
            continue
        lineno = int(mutant.get("lineno", 0))
        end_lineno = int(mutant.get("end_lineno", lineno))
        if any(lineno <= end and end_lineno >= start for start, end in file_ranges):
            kept.append(dict(trial))
    return kept


def score_trials(trials: Sequence[Mapping[str, Any]]) -> MutationScore:
    """Compute killed, survived, timeout, and total counts from engine trials."""
    killed = 0
    timeout = 0
    survived = 0
    for trial in trials:
        result = trial.get("result", {})
        found = bool(result.get("found", False))
        reason_code = str(result.get("reason_code", ""))
        if found:
            killed += 1
        elif reason_code == _TIMEOUT_REASON:
            timeout += 1
        else:
            survived += 1
    return MutationScore(killed=killed, survived=survived, timeout=timeout, total=len(trials))


def _evaluate_against_map(
    scores: Mapping[str, MutationScore],
    thresholds: Mapping[str, float],
    label: str,
    empty_message: str,
) -> GateOutcome:
    if not scores:
        return GateOutcome(passed=True, summary=empty_message, failures=(), scores={})

    failures: list[str] = []
    lines: list[str] = []
    for tier, score in sorted(scores.items()):
        threshold = thresholds.get(tier, 0.0)
        pct = score.effective_score_pct
        status = "PASS"
        if score.total > 0 and pct + 1e-9 < threshold:
            status = "FAIL"
            failures.append(
                f"{tier}: {pct:.1f}% < {label} {threshold:.1f}% "
                f"(killed={score.killed}, timeout={score.timeout}, "
                f"survived={score.survived}, total={score.total})"
            )
        lines.append(
            f"[{status}] {tier}: {pct:.1f}% ({label} {threshold:.1f}%, "
            f"killed={score.killed}, timeout={score.timeout}, "
            f"survived={score.survived}, total={score.total})"
        )

    return GateOutcome(
        passed=not failures,
        summary="\n".join(lines),
        failures=tuple(failures),
        scores=dict(scores),
    )


def evaluate_targets(
    scores: Mapping[str, MutationScore],
    policy: MutationPolicy,
) -> GateOutcome:
    """Evaluate changed-line scores against tier percentage targets."""
    return _evaluate_against_map(
        scores=scores,
        thresholds=policy.tiers,
        label="target",
        empty_message="No tiered source changes to mutation-test.",
    )


def evaluate_floors(
    scores: Mapping[str, MutationScore],
    policy: MutationPolicy,
) -> GateOutcome:
    """Evaluate full-sweep scores against committed ratcheting baseline floors."""
    return _evaluate_against_map(
        scores=scores,
        thresholds=policy.baseline,
        label="floor",
        empty_message="No tiered source changes evaluated.",
    )


def find_suppression_pragmas(
    paths: Sequence[Path],
    repo_root: Path | None = None,
) -> list[str]:
    """Return `path:line` entries for any inline mutation-suppression pragmas."""
    hits: list[str] = []
    for file_path in paths:
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        display = _format_display_path(file_path, repo_root)
        hit_lines = _scan_comment_pragmas(text)
        for lineno in sorted(hit_lines):
            hits.append(f"{display}:{lineno}")
    return hits


def _format_display_path(file_path: Path, repo_root: Path | None) -> str:
    if repo_root is not None:
        try:
            return file_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            pass
    return file_path.as_posix()


def _scan_comment_pragmas(text: str) -> set[int]:
    lines_found: set[int] = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT and _PRAGMA_PATTERN.search(tok.string):
                lines_found.add(tok.start[0])
    except tokenize.TokenError:
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _PRAGMA_PATTERN.search(line):
                lines_found.add(lineno)
    return lines_found


class PoodleEngine:
    """Adapter executing Poodle mutation trials and parsing its JSON report."""

    def run_tier(
        self,
        tier: str,
        files: Sequence[str],
        repo_root: Path,
        policy: MutationPolicy,
    ) -> list[dict[str, Any]]:
        """Run Poodle scoped to *files* and return raw `mutant_trials` records."""
        _ = tier, policy
        only_args: list[str] = []
        for file_path in files:
            norm = normalize_repo_path(file_path)
            rel = norm.removeprefix("src/")
            only_args.extend(["--only", rel])

        env = os.environ.copy()
        venv_bin = str(Path(sys.executable).resolve().parent)
        env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")

        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "poodle-report.json"
            cmd = [
                sys.executable,
                "-m",
                "poodle",
                "-q",
                *only_args,
                "--json",
                str(report_path),
                "src",
            ]
            proc = subprocess.run(
                cmd,
                cwd=str(repo_root),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 5:
                return []
            if proc.returncode != 0:
                raise RuntimeError(
                    f"Poodle failed (exit {proc.returncode}): {proc.stderr or proc.stdout}"
                )
            data = json.loads(report_path.read_text(encoding="utf-8"))
            trials = data.get("mutant_trials", [])
            return [dict(item) for item in trials]


def _run_git(args: Sequence[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )


def resolve_base_ref(base: str | None, repo_root: Path) -> str:
    """Resolve explicit *base* or default to `origin/main` falling back to `main`."""
    if base:
        return base
    for candidate in ("origin/main", "main"):
        probe = _run_git(["rev-parse", "--verify", "--quiet", candidate], repo_root)
        if probe.returncode == 0:
            return candidate
    return "HEAD"


def changed_files(base: str | None, repo_root: Path) -> tuple[str, list[str]]:
    """Return `(merge_base_sha, changed_py_files_under_src_nectr)`."""
    base_ref = resolve_base_ref(base, repo_root)
    mb_proc = _run_git(["merge-base", base_ref, "HEAD"], repo_root)
    mb_sha = mb_proc.stdout.strip() if mb_proc.returncode == 0 else base_ref
    diff_proc = _run_git(
        ["diff", "--name-only", "--diff-filter=ACMR", mb_sha, "HEAD", "--", "src/nectr"],
        repo_root,
    )
    if diff_proc.returncode != 0:
        raise RuntimeError(f"git diff failed: {diff_proc.stderr}")
    files = [normalize_repo_path(line) for line in diff_proc.stdout.splitlines() if line.strip()]
    return mb_sha, files


def diff_text_for_files(base_ref: str, files: Sequence[str], repo_root: Path) -> str:
    """Return `git diff -U0` output between *base_ref* and `HEAD` for *files*."""
    if not files:
        return ""
    proc = _run_git(["diff", "-U0", base_ref, "HEAD", "--", *files], repo_root)
    if proc.returncode != 0:
        raise RuntimeError(f"git diff -U0 failed: {proc.stderr}")
    return proc.stdout


def discover_source_files(repo_root: Path) -> list[str]:
    """Return all `.py` files under `src/nectr` relative to *repo_root*."""
    src_nectr = repo_root / "src" / "nectr"
    if not src_nectr.is_dir():
        return []
    return sorted(
        p.relative_to(repo_root).as_posix()
        for p in src_nectr.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def run_diff_gate(
    repo_root: Path,
    base: str | None = None,
    engine: MutationEngine | None = None,
    report_path: Path | None = None,
) -> GateOutcome:
    """Run changed-line diff mutation checks against tier targets."""
    policy = load_mutation_policy(repo_root / "pyproject.toml")
    mb_sha, modified = changed_files(base, repo_root)
    targets = select_targets(modified, policy)
    if not targets:
        outcome = evaluate_targets({}, policy)
        _write_report(report_path, "diff", outcome, policy, {})
        return outcome

    selected_files = [f for files in targets.values() for f in files]
    hunk_ranges = parse_changed_line_ranges(diff_text_for_files(mb_sha, selected_files, repo_root))
    runner = engine or PoodleEngine()

    scores: dict[str, MutationScore] = {}
    survivors_by_tier: dict[str, list[dict[str, Any]]] = {}
    for tier, files in targets.items():
        raw_trials = runner.run_tier(tier, files, repo_root, policy)
        changed_trials = filter_trials_to_changed_lines(raw_trials, hunk_ranges)
        scores[tier] = score_trials(changed_trials)
        survivors_by_tier[tier] = [
            t
            for t in changed_trials
            if not bool(t.get("result", {}).get("found", False))
            and str(t.get("result", {}).get("reason_code", "")) != _TIMEOUT_REASON
        ]

    outcome = evaluate_targets(scores, policy)
    _write_report(report_path, "diff", outcome, policy, survivors_by_tier)
    return outcome


def run_full_gate(
    repo_root: Path,
    engine: MutationEngine | None = None,
    report_path: Path | None = None,
) -> GateOutcome:
    """Run full bounded-context sweep against ratcheting baseline floors."""
    policy = load_mutation_policy(repo_root / "pyproject.toml")
    targets = select_targets(discover_source_files(repo_root), policy)
    runner = engine or PoodleEngine()

    scores: dict[str, MutationScore] = {}
    survivors_by_tier: dict[str, list[dict[str, Any]]] = {}
    for tier, files in targets.items():
        raw_trials = runner.run_tier(tier, files, repo_root, policy)
        scores[tier] = score_trials(raw_trials)
        survivors_by_tier[tier] = [
            t
            for t in raw_trials
            if not bool(t.get("result", {}).get("found", False))
            and str(t.get("result", {}).get("reason_code", "")) != _TIMEOUT_REASON
        ]

    outcome = evaluate_floors(scores, policy)
    _write_report(report_path, "full", outcome, policy, survivors_by_tier)
    return outcome


def _write_report(
    report_path: Path | None,
    mode: str,
    outcome: GateOutcome,
    policy: MutationPolicy,
    survivors_by_tier: Mapping[str, Sequence[Mapping[str, Any]]],
) -> None:
    if report_path is None:
        return
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": mode,
        "engine": policy.engine,
        "passed": outcome.passed,
        "failures": list(outcome.failures),
        "tiers": {
            tier: {
                "killed": sc.killed,
                "timeout": sc.timeout,
                "survived": sc.survived,
                "total": sc.total,
                "score_pct": round(sc.effective_score_pct, 2),
                "target_pct": policy.tiers.get(tier, 0.0),
                "floor_pct": policy.baseline.get(tier, 0.0),
                "survivors": list(survivors_by_tier.get(tier, ())),
            }
            for tier, sc in outcome.scores.items()
        },
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _default_pragma_targets(repo_root: Path) -> list[Path]:
    proc = _run_git(["ls-files", "src/nectr"], repo_root)
    if proc.returncode == 0 and proc.stdout.strip():
        return [
            repo_root / line.strip()
            for line in proc.stdout.splitlines()
            if line.strip().endswith(".py")
        ]
    return [repo_root / rel for rel in discover_source_files(repo_root)]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-mutation",
        description="Tiered mutation testing gate and anti-gaming pragma checker.",
    )
    parser.add_argument("--root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)

    prag = sub.add_parser("check-pragmas", help="Reject inline mutation suppression pragmas.")
    prag.add_argument("files", nargs="*", help="Optional explicit file paths to scan.")

    diff_cmd = sub.add_parser("diff", help="Run changed-line mutation checks against tier targets.")
    diff_cmd.add_argument("--base", default=None, help="Base git ref (defaults to origin/main).")
    diff_cmd.add_argument("--report", default=None, help="Optional JSON report path.")

    full_cmd = sub.add_parser(
        "full", help="Run full bounded-context sweep against baseline floors."
    )
    full_cmd.add_argument("--report", default=None, help="Optional JSON report path.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for `nectr.devtools.mutation_gate`."""
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    repo_root = Path(args.root).resolve()

    if args.command == "check-pragmas":
        targets = (
            [Path(p) if Path(p).is_absolute() else repo_root / p for p in args.files]
            if args.files
            else _default_pragma_targets(repo_root)
        )
        hits = find_suppression_pragmas(targets, repo_root=repo_root)
        if hits:
            for hit in hits:
                print(f"MUTATION PRAGMA FORBIDDEN: {hit}", file=sys.stderr)
            return 1
        print(f"Mutation pragma check passed ({len(targets)} file(s) scanned).")
        return 0

    report_path = Path(args.report) if args.report else None
    if report_path is not None and not report_path.is_absolute():
        report_path = repo_root / report_path

    if args.command == "diff":
        outcome = run_diff_gate(repo_root, base=args.base, report_path=report_path)
    else:
        outcome = run_full_gate(repo_root, report_path=report_path)
        policy = load_mutation_policy(repo_root / "pyproject.toml")
        for tier, sc in sorted(outcome.scores.items()):
            target = policy.tiers.get(tier, 0.0)
            print(f"[INFO] {tier}: target {target:.1f}%, actual {sc.effective_score_pct:.1f}%")

    print(outcome.summary)
    if not outcome.passed:
        for failure in outcome.failures:
            print(f"MUTATION GATE FAILED: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
