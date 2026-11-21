"""Hardening unit tests for mutation_gate PoodleEngine adapter, git helpers, and CLI."""

from __future__ import annotations

import json
import subprocess
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from nectr.devtools import mutation_gate

PRAGMA_ONE = "# pra" + "gma: no mutate"
PRAGMA_TWO = "# no" + "mut: String"


class _FakeEngine:
    def __init__(self, trials_by_tier: dict[str, list[dict[str, Any]]]) -> None:
        self.trials_by_tier = trials_by_tier
        self.calls: list[tuple[str, list[str]]] = []

    def run_tier(
        self,
        tier: str,
        files: Sequence[str],
        repo_root: Path,
        policy: mutation_gate.MutationPolicy,
    ) -> list[dict[str, Any]]:
        _ = repo_root, policy
        self.calls.append((tier, list(files)))
        return list(self.trials_by_tier.get(tier, []))


def _write_pyproject(root: Path, floor_contracts: float = 50.0, min_timeout: int = 10) -> None:
    content = (
        "[tool.poodle]\n"
        'source_folders = ["src"]\n'
        'skip_mutators = ["String"]\n'
        f"min_timeout = {min_timeout}\n"
        "timeout_multiplier = 5\n\n"
        "[tool.poodle.runner_opts]\n"
        'command_line = "pytest -x"\n\n'
        "[tool.nectr.mutation]\n"
        'engine = "poodle"\n'
        "per_mutant_timeout_seconds = 10\n"
        'excluded = ["src/nectr/personas", "src/nectr/ui", "experiments"]\n\n'
        "[tool.nectr.mutation.tiers]\n"
        '"src/nectr/contracts" = 85.0\n'
        '"src/nectr/devtools" = 75.0\n\n'
        "[tool.nectr.mutation.baseline]\n"
        f'"src/nectr/contracts" = {floor_contracts}\n'
        '"src/nectr/devtools" = 40.0\n'
    )
    (root / "pyproject.toml").write_text(content, encoding="utf-8")


def test_normalize_and_load_policy_errors(tmp_path: Path) -> None:
    assert mutation_gate.normalize_repo_path(r".\a\src\nectr\chain\ledger.py") == (
        "src/nectr/chain/ledger.py"
    )
    assert mutation_gate.normalize_repo_path("b/src/nectr/contracts/engine.py") == (
        "src/nectr/contracts/engine.py"
    )
    empty_pyproject = tmp_path / "pyproject.toml"
    empty_pyproject.write_text("[project]\nname = 'x'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing \\[tool.nectr.mutation\\]"):
        mutation_gate.load_mutation_policy(empty_pyproject)


def test_classify_select_dedup_and_diff_deletions() -> None:
    policy = mutation_gate.MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={"src/nectr/contracts": 85.0, "src/nectr/contracts/sub": 90.0},
        baseline={},
        excluded=("src/nectr/personas",),
    )
    assert mutation_gate.classify("src/nectr/contracts/sub/x.py", policy) == (
        "src/nectr/contracts/sub"
    )
    selected = mutation_gate.select_targets(
        [
            "src/nectr/contracts/engine.py",
            r".\src\nectr\contracts\engine.py",
            "src/nectr/contracts/notes.txt",
        ],
        policy,
    )
    assert selected == {"src/nectr/contracts": ["src/nectr/contracts/engine.py"]}

    diff_text = (
        "diff --git a/src/nectr/contracts/old.py b/dev/null\n"
        "--- a/src/nectr/contracts/old.py\n"
        "+++ /dev/null\n"
        "@@ -1,3 +0,0 @@\n"
        "+++ b/src/nectr/contracts/engine.py\n"
        "@@ -10,0 +15,2 @@\n"
    )
    assert mutation_gate.parse_changed_line_ranges(diff_text) == {
        "src/nectr/contracts/engine.py": [(15, 16)]
    }

    trials = [
        {"mutant": {"lineno": 1, "end_lineno": 1}},
        {"mutant": {"source_file": "src/nectr/contracts/other.py", "lineno": 15, "end_lineno": 15}},
        {"mutant": {"source_file": "nectr/contracts/engine.py", "lineno": 14, "end_lineno": 15}},
    ]
    kept = mutation_gate.filter_trials_to_changed_lines(
        trials,
        {"src/nectr/contracts/engine.py": [(15, 16)]},
    )
    assert len(kept) == 1


def test_pragma_scanner_token_error_fallback_and_relative_paths(tmp_path: Path) -> None:
    sub = tmp_path / "src" / "nectr"
    sub.mkdir(parents=True)
    bad_syntax = sub / "broken.py"
    bad_syntax.write_text(f'x = "unclosed\ny = 1  {PRAGMA_TWO}\n', encoding="utf-8")
    outside = tmp_path.parent / "outside_missing.py"

    hits = mutation_gate.find_suppression_pragmas([bad_syntax, outside], repo_root=tmp_path)
    assert hits == ["src/nectr/broken.py:2"]

    outside_real = tmp_path / "other" / "mod.py"
    outside_real.parent.mkdir()
    outside_real.write_text(f"z = 1  {PRAGMA_ONE}\n", encoding="utf-8")
    abs_hits = mutation_gate.find_suppression_pragmas([outside_real], repo_root=sub)
    assert len(abs_hits) == 1 and abs_hits[0].endswith("mod.py:1")


def test_pragma_scanner_recurses_directories_and_deduplicates(tmp_path: Path) -> None:
    nested = tmp_path / "pkg" / "deep"
    nested.mkdir(parents=True)
    hit_file = nested / "module.py"
    hit_file.write_text(f"a = 1\nb = 2  {PRAGMA_ONE}\n", encoding="utf-8")
    (nested / "clean.py").write_text("ok = True\n", encoding="utf-8")
    (nested / "notes.txt").write_text(f"{PRAGMA_TWO}\n", encoding="utf-8")
    pycache = nested / "__pycache__"
    pycache.mkdir()
    (pycache / "cached.py").write_text(f"c = 3  {PRAGMA_TWO}\n", encoding="utf-8")

    hits = mutation_gate.find_suppression_pragmas([tmp_path, hit_file], repo_root=tmp_path)
    assert hits == ["pkg/deep/module.py:2"]
    assert mutation_gate.main(["--root", str(tmp_path), "check-pragmas", "pkg"]) == 1


def test_poodle_engine_run_tier_cli_override_exit5_and_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_pyproject(tmp_path, min_timeout=5)
    policy = mutation_gate.load_mutation_policy(tmp_path / "pyproject.toml")
    engine = mutation_gate.PoodleEngine()

    recorded_cmds: list[list[str]] = []
    seen_override: dict[str, Any] = {}

    def fake_run_ok(
        cmd: list[str],
        cwd: str,
        env: dict[str, str],
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        _ = cwd, env, capture_output, text, check
        recorded_cmds.append(cmd)
        cfg_idx = cmd.index("-c") + 1
        seen_override.update(tomllib.loads(Path(cmd[cfg_idx]).read_text(encoding="utf-8")))
        json_idx = cmd.index("--json") + 1
        Path(cmd[json_idx]).write_text(
            json.dumps(
                {
                    "mutant_trials": [
                        {
                            "mutant": {
                                "source_file": "nectr/contracts/engine.py",
                                "lineno": 1,
                                "end_lineno": 1,
                            },
                            "result": {"found": True, "reason_code": "Mutant Found"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run_ok)
    trials = engine.run_tier(
        "src/nectr/contracts",
        ["src/nectr/contracts/engine.py"],
        tmp_path,
        policy,
    )
    assert len(trials) == 1
    assert "poodle.cli" in recorded_cmds[0]
    assert "--only" in recorded_cmds[0]
    assert "nectr/contracts/engine.py" in recorded_cmds[0]
    assert seen_override["tool"]["poodle"]["min_timeout"] == 10

    def fake_run_empty(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        return subprocess.CompletedProcess(cmd, 5, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run_empty)
    assert (
        engine.run_tier(
            "src/nectr/contracts",
            ["src/nectr/contracts/engine.py"],
            tmp_path,
            policy,
        )
        == []
    )

    def fake_run_err(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        return subprocess.CompletedProcess(cmd, 3, "", "Clean Run Failed")

    monkeypatch.setattr(subprocess, "run", fake_run_err)
    with pytest.raises(RuntimeError, match="Clean Run Failed"):
        engine.run_tier(
            "src/nectr/contracts",
            ["src/nectr/contracts/engine.py"],
            tmp_path,
            policy,
        )


def test_git_helpers_discover_and_run_gates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_pyproject(tmp_path)
    contracts_dir = tmp_path / "src" / "nectr" / "contracts"
    contracts_dir.mkdir(parents=True)
    (contracts_dir / "engine.py").write_text("def f() -> int:\n    return 1\n", encoding="utf-8")
    pycache_dir = contracts_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "engine.cpython-312.pyc").write_bytes(b"0")
    (pycache_dir / "skip.py").write_text("x = 1\n", encoding="utf-8")

    assert mutation_gate.discover_source_files(tmp_path) == ["src/nectr/contracts/engine.py"]
    assert mutation_gate.discover_source_files(tmp_path / "missing") == []

    def fake_git(args: Sequence[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
        _ = repo_root
        if args[0] == "rev-parse":
            rc = 0 if args[-1] == "main" else 1
            return subprocess.CompletedProcess(list(args), rc, "", "")
        if args[0] == "merge-base":
            return subprocess.CompletedProcess(list(args), 0, "abc123\n", "")
        if args[0] == "diff" and "--name-only" in args:
            return subprocess.CompletedProcess(list(args), 0, "src/nectr/contracts/engine.py\n", "")
        if args[0] == "diff" and "-U0" in args:
            return subprocess.CompletedProcess(
                list(args),
                0,
                "+++ b/src/nectr/contracts/engine.py\n@@ -1 +1,2 @@\n",
                "",
            )
        return subprocess.CompletedProcess(list(args), 0, "", "")

    monkeypatch.setattr(mutation_gate, "_run_git", fake_git)
    assert mutation_gate.resolve_base_ref(None, tmp_path) == "main"
    assert mutation_gate.resolve_base_ref("custom", tmp_path) == "custom"
    assert mutation_gate.diff_text_for_files("abc123", [], tmp_path) == ""

    fake_engine = _FakeEngine(
        {
            "src/nectr/contracts": [
                {
                    "mutant": {
                        "source_file": "nectr/contracts/engine.py",
                        "lineno": 2,
                        "end_lineno": 2,
                    },
                    "result": {"found": True, "reason_code": "Mutant Found"},
                },
                {
                    "mutant": {
                        "source_file": "nectr/contracts/engine.py",
                        "lineno": 99,
                        "end_lineno": 99,
                    },
                    "result": {"found": False, "reason_code": "Mutant Not Found"},
                },
            ]
        }
    )
    report_diff = tmp_path / "reports" / "diff.json"
    diff_outcome = mutation_gate.run_diff_gate(
        tmp_path, base=None, engine=fake_engine, report_path=report_diff
    )
    assert diff_outcome.passed is True
    assert diff_outcome.scores["src/nectr/contracts"].total == 1
    assert json.loads(report_diff.read_text(encoding="utf-8"))["mode"] == "diff"

    report_full = tmp_path / "reports" / "full.json"
    full_outcome = mutation_gate.run_full_gate(
        tmp_path, engine=fake_engine, report_path=report_full
    )
    assert full_outcome.passed is True
    parsed_full = json.loads(report_full.read_text(encoding="utf-8"))
    assert parsed_full["tiers"]["src/nectr/contracts"]["score_pct"] == 50.0
    assert len(parsed_full["tiers"]["src/nectr/contracts"]["survivors"]) == 1


def test_main_cli_subcommands_pass_and_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_pyproject(tmp_path, floor_contracts=80.0)
    contracts_dir = tmp_path / "src" / "nectr" / "contracts"
    contracts_dir.mkdir(parents=True)
    clean_file = contracts_dir / "ok.py"
    clean_file.write_text("x = 1\n", encoding="utf-8")

    monkeypatch.setattr(
        mutation_gate,
        "_run_git",
        lambda args, root: subprocess.CompletedProcess(list(args), 1, "", ""),
    )
    assert mutation_gate.main(["--root", str(tmp_path), "check-pragmas"]) == 0

    bad_file = contracts_dir / "bad.py"
    bad_file.write_text(f"y = 2  {PRAGMA_ONE}\n", encoding="utf-8")
    assert (
        mutation_gate.main(["--root", str(tmp_path), "check-pragmas", "src/nectr/contracts/bad.py"])
        == 1
    )

    monkeypatch.setattr(mutation_gate, "changed_files", lambda base, root: ("HEAD", []))
    report_out = tmp_path / "out.json"
    assert mutation_gate.main(["--root", str(tmp_path), "diff", "--report", str(report_out)]) == 0
    assert report_out.is_file()

    sub_root = tmp_path / "sub_repo"
    sub_root.mkdir()
    (sub_root / "pyproject.toml").write_text(
        (tmp_path / "pyproject.toml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert mutation_gate.main(["--root", str(sub_root), "diff", "--report", "rel.json"]) == 0
    assert (sub_root / "rel.json").is_file()

    fail_outcome = mutation_gate.GateOutcome(
        passed=False,
        summary="[FAIL] src/nectr/contracts: 50.0% < floor 80.0%",
        failures=("src/nectr/contracts: 50.0% < floor 80.0%",),
        scores={"src/nectr/contracts": mutation_gate.MutationScore(1, 1, 0, 2)},
    )
    monkeypatch.setattr(mutation_gate, "run_full_gate", lambda root, report_path=None: fail_outcome)
    assert mutation_gate.main(["--root", str(tmp_path), "full"]) == 1
