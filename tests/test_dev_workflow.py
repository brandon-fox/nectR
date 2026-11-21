"""Strict TDD tests for Worktrunk worktree isolation and tiered mutation gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PRAGMA_ONE = "# pra" + "gma: no mutate"
PRAGMA_TWO = "# no" + "mut"


def test_worktrees_dir_is_gitignored() -> None:
    lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".worktrees/" in lines


def test_ruff_and_pytest_exclude_worktrees() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    ruff_excl = data.get("tool", {}).get("ruff", {}).get("extend-exclude", [])
    pytest_excl = (
        data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("norecursedirs", [])
    )
    assert ".worktrees" in ruff_excl
    assert ".worktrees" in pytest_excl


def test_detect_secrets_and_docs_sync_exclude_worktrees() -> None:
    from nectr.devtools import docs_sync

    skill_common_src = (REPO_ROOT / ".agents" / "lib" / "skill_common.py").read_text(
        encoding="utf-8"
    )
    assert r"\.worktrees" in skill_common_src
    assert ".worktrees" in docs_sync.EXCLUDED_TREE_DIRS


def test_worktrunk_project_config_hooks() -> None:
    wt_path = REPO_ROOT / ".config" / "wt.toml"
    assert wt_path.is_file()
    data = tomllib.loads(wt_path.read_text(encoding="utf-8"))
    pre_start = data.get("pre-start", [])
    pre_merge = data.get("pre-merge", [])
    assert isinstance(pre_start, list) and len(pre_start) >= 2
    assert isinstance(pre_merge, list) and len(pre_merge) >= 2
    pre_start_cmds = " ".join(str(v) for step in pre_start for v in step.values())
    pre_merge_cmds = " ".join(str(v) for step in pre_merge for v in step.values())
    assert "uv sync --frozen --extra dev" in pre_start_cmds
    assert "verify_commit_readiness.py" in pre_start_cmds
    assert "nectr.devtools.mutation_gate diff" in pre_merge_cmds
    assert "verify_orchestration_gate.py" in pre_merge_cmds


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_load_mutation_policy_tiers_and_baseline() -> None:
    from nectr.devtools.mutation_gate import load_mutation_policy

    policy = load_mutation_policy(REPO_ROOT / "pyproject.toml")
    assert policy.engine == "poodle"
    assert policy.tiers == {
        "src/nectr/contracts": 85.0,
        "src/nectr/chain": 85.0,
        "src/nectr/services": 75.0,
        "src/nectr/devtools": 75.0,
    }
    assert set(policy.excluded) == {"src/nectr/personas", "src/nectr/ui", "experiments"}
    assert set(policy.baseline.keys()) == set(policy.tiers.keys())


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_classify_and_select_targets() -> None:
    from nectr.devtools.mutation_gate import MutationPolicy, classify, select_targets

    policy = MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={
            "src/nectr/contracts": 85.0,
            "src/nectr/chain": 85.0,
            "src/nectr/services": 75.0,
            "src/nectr/devtools": 75.0,
        },
        baseline={},
        excluded=("src/nectr/personas", "src/nectr/ui", "experiments"),
    )
    assert classify("src/nectr/contracts/engine.py", policy) == "src/nectr/contracts"
    assert classify(r"src\nectr\chain\ledger.py", policy) == "src/nectr/chain"
    assert classify("src/nectr/personas/simulator.py", policy) is None
    assert classify("src/nectr/ui/app.py", policy) is None
    assert classify("docs/readme.md", policy) is None

    selected = select_targets(
        [
            "src/nectr/contracts/engine.py",
            "src/nectr/contracts/README.md",
            "src/nectr/services/hive_service.py",
            "src/nectr/personas/simulator.py",
            "tests/test_invariants.py",
        ],
        policy,
    )
    assert selected == {
        "src/nectr/contracts": ["src/nectr/contracts/engine.py"],
        "src/nectr/services": ["src/nectr/services/hive_service.py"],
    }


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_parse_changed_line_ranges_hunk_headers() -> None:
    from nectr.devtools.mutation_gate import parse_changed_line_ranges

    diff_text = (
        "diff --git a/src/nectr/contracts/engine.py b/src/nectr/contracts/engine.py\n"
        "--- a/src/nectr/contracts/engine.py\n"
        "+++ b/src/nectr/contracts/engine.py\n"
        "@@ -5 +10 @@ def single_line():\n"
        "@@ -20,3 +25,4 @@ def multi_line():\n"
        "@@ -40,5 +50,0 @@ def deletion_only():"
    )
    ranges = parse_changed_line_ranges(diff_text)
    assert ranges == {
        "src/nectr/contracts/engine.py": [(10, 10), (25, 28)],
    }


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_filter_trials_to_changed_lines() -> None:
    from nectr.devtools.mutation_gate import filter_trials_to_changed_lines

    trials = [
        {
            "mutant": {
                "source_file": r"src\nectr\contracts\engine.py",
                "lineno": 10,
                "end_lineno": 12,
            }
        },
        {"mutant": {"source_file": "nectr/contracts/engine.py", "lineno": 14, "end_lineno": 16}},
        {
            "mutant": {
                "source_file": "src/nectr/contracts/engine.py",
                "lineno": 20,
                "end_lineno": 22,
            }
        },
    ]
    ranges = {"src/nectr/contracts/engine.py": [(11, 15)]}
    kept = filter_trials_to_changed_lines(trials, ranges)
    assert len(kept) == 2


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_score_trials_counts_timeouts_as_killed() -> None:
    from nectr.devtools.mutation_gate import score_trials

    trials = [
        {"result": {"found": True, "reason_code": "Mutant Found"}},
        {"result": {"found": False, "reason_code": "Trial Exceeded Timeout"}},
        {"result": {"found": False, "reason_code": "Mutant Not Found"}},
        {"result": {"found": True, "reason_code": "Other, See Description"}},
    ]
    score = score_trials(trials)
    assert score.killed == 2
    assert score.timeout == 1
    assert score.survived == 1
    assert score.total == 4
    assert score.effective_score_pct == pytest.approx(75.0)


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_evaluate_targets_and_total_zero_passes() -> None:
    from nectr.devtools.mutation_gate import MutationPolicy, MutationScore, evaluate_targets

    policy = MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={"src/nectr/contracts": 85.0, "src/nectr/services": 75.0},
        baseline={},
        excluded=(),
    )
    empty_res = evaluate_targets({}, policy)
    assert empty_res.passed is True
    assert "no tiered source changes" in empty_res.summary.lower()

    zero_res = evaluate_targets(
        {"src/nectr/contracts": MutationScore(killed=0, survived=0, timeout=0, total=0)},
        policy,
    )
    assert zero_res.passed is True

    fail_res = evaluate_targets(
        {"src/nectr/contracts": MutationScore(killed=8, survived=2, timeout=0, total=10)},
        policy,
    )
    assert fail_res.passed is False


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_evaluate_floors_ratchet_check() -> None:
    from nectr.devtools.mutation_gate import MutationPolicy, MutationScore, evaluate_floors

    policy = MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={"src/nectr/contracts": 85.0},
        baseline={"src/nectr/contracts": 55.0},
        excluded=(),
    )
    pass_res = evaluate_floors(
        {"src/nectr/contracts": MutationScore(killed=55, survived=45, timeout=0, total=100)},
        policy,
    )
    assert pass_res.passed is True

    fail_res = evaluate_floors(
        {"src/nectr/contracts": MutationScore(killed=54, survived=46, timeout=0, total=100)},
        policy,
    )
    assert fail_res.passed is False


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing mutation_gate not yet implemented",
)
def test_find_suppression_pragmas_detects_both_tokens(tmp_path: Path) -> None:
    from nectr.devtools.mutation_gate import find_suppression_pragmas

    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    c = tmp_path / "clean.py"
    a.write_text(f"x = 1  {PRAGMA_ONE}\n", encoding="utf-8")
    b.write_text(f"y = 2  {PRAGMA_TWO}\n", encoding="utf-8")
    c.write_text("z = 3\n", encoding="utf-8")
    hits = find_suppression_pragmas([a, b, c])
    assert len(hits) == 2
    assert any("a.py:1" in h for h in hits)
    assert any("b.py:1" in h for h in hits)


@pytest.mark.xfail(
    strict=True,
    reason="RED: adopt-worktrees-and-mutation-testing hooks/CI not yet wired",
)
def test_hooks_and_ci_workflow_wired() -> None:
    pre_commit = (REPO_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    pre_push = (REPO_ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    pre_commit_cfg = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    workflow = REPO_ROOT / ".github" / "workflows" / "mutation-testing.yml"
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "nectr.devtools.mutation_gate check-pragmas" in pre_commit
    assert "nectr.devtools.mutation_gate diff" in pre_push
    assert "forbid-mutation-pragmas" in pre_commit_cfg
    assert "nectr-mutation-gate" in pre_commit_cfg
    assert workflow.is_file()
    assert ".poodle-temp/" in gitignore
    assert "mutation-report*.json" in gitignore
