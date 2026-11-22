"""Step definitions for Isolated Worktrees and Tiered Mutation Testing Gate."""

from __future__ import annotations

import tempfile
import tomllib
from pathlib import Path
from typing import Any

from behave import given, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]
PRAGMA_ONE = "# pra" + "gma: no mutate"


@given("the repository root workspace")
def step_given_repo_root(context: Any) -> None:
    context.repo_root = REPO_ROOT


@when("I inspect the worktree ignore and tool exclusion rules")
def step_when_inspect_worktree_exclusions(context: Any) -> None:
    root: Path = context.repo_root
    context.gitignore_lines = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    context.ruff_extend_exclude = (
        pyproject.get("tool", {}).get("ruff", {}).get("extend-exclude", [])
    )
    context.pytest_norecursedirs = (
        pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("norecursedirs", [])
    )
    skill_common_src = (root / ".agents" / "lib" / "skill_common.py").read_text(encoding="utf-8")
    context.skill_common_src = skill_common_src
    from nectr.devtools import docs_sync

    context.docs_sync_excluded = docs_sync.EXCLUDED_TREE_DIRS


@then(
    '".worktrees" is excluded across gitignore, ruff, pytest, detect-secrets, and docs tree rendering'
)
def step_then_worktree_excluded_everywhere(context: Any) -> None:
    assert ".worktrees/" in context.gitignore_lines
    assert ".worktrees" in context.ruff_extend_exclude
    assert ".worktrees" in context.pytest_norecursedirs
    assert r"\.worktrees" in context.skill_common_src
    assert ".worktrees" in context.docs_sync_excluded


@given('the Worktrunk project configuration in ".config/wt.toml"')
def step_given_wt_config(context: Any) -> None:
    context.wt_config_path = REPO_ROOT / ".config" / "wt.toml"


@when("I parse the Worktrunk lifecycle hooks")
def step_when_parse_wt_config(context: Any) -> None:
    path: Path = context.wt_config_path
    assert path.is_file(), f"Missing Worktrunk config: {path}"
    context.wt_data = tomllib.loads(path.read_text(encoding="utf-8"))


@then("ordered pre-start hooks run isolated uv sync and commit readiness checks")
def step_then_wt_pre_start(context: Any) -> None:
    pre_start = context.wt_data.get("pre-start", [])
    assert isinstance(pre_start, list) and len(pre_start) >= 2
    joined = " ".join(str(v) for block in pre_start for v in block.values())
    assert "uv sync --frozen --extra dev" in joined
    assert "verify_commit_readiness.py" in joined


@then("ordered pre-merge hooks run the diff mutation gate and orchestration verification gate")
def step_then_wt_pre_merge(context: Any) -> None:
    pre_merge = context.wt_data.get("pre-merge", [])
    assert isinstance(pre_merge, list) and len(pre_merge) >= 2
    joined = " ".join(str(v) for block in pre_merge for v in block.values())
    assert "nectr.devtools.mutation_gate diff" in joined
    assert "verify_orchestration_gate.py" in joined


@given("a temporary source directory containing a file with an inline mutation suppression pragma")
def step_given_pragma_src(context: Any) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._tmp = tmp
    src_file = Path(tmp.name) / "sample.py"
    src_file.write_text(f"def ok() -> int:\n    return 1  {PRAGMA_ONE}\n", encoding="utf-8")
    context.pragma_files = [src_file]


@when("the mutation pragma scanner inspects the temporary source directory")
def step_when_scan_pragmas(context: Any) -> None:
    from nectr.devtools.mutation_gate import find_suppression_pragmas

    context.pragma_hits = find_suppression_pragmas(context.pragma_files)


@then("pragma validation fails listing the offending file and line")
def step_then_pragma_hits(context: Any) -> None:
    assert len(context.pragma_hits) == 1
    assert "sample.py:2" in context.pragma_hits[0]


@given(
    "a Tier-1 module diff affecting lines 10 to 20 and engine trials scoring 50.0% on changed lines"
)
def step_given_diff_trials(context: Any) -> None:
    diff_text = (
        "diff --git a/src/nectr/contracts/engine.py b/src/nectr/contracts/engine.py\n"
        "--- a/src/nectr/contracts/engine.py\n"
        "+++ b/src/nectr/contracts/engine.py\n"
        "@@ -10,2 +10,11 @@ def sample():"
    )
    trials = [
        {
            "mutant": {
                "source_file": r"src\nectr\contracts\engine.py",
                "lineno": 12,
                "end_lineno": 12,
            },
            "result": {"found": True, "reason_code": "Mutant Found"},
        },
        {
            "mutant": {
                "source_file": "nectr/contracts/engine.py",
                "lineno": 18,
                "end_lineno": 18,
            },
            "result": {"found": False, "reason_code": "Mutant Not Found"},
        },
        {
            "mutant": {
                "source_file": "src/nectr/contracts/engine.py",
                "lineno": 50,
                "end_lineno": 50,
            },
            "result": {"found": True, "reason_code": "Mutant Found"},
        },
    ]
    context.diff_text = diff_text
    context.raw_trials = trials


@when("the diff-scoped mutation gate evaluates the changed-line trials")
def step_when_eval_diff_trials(context: Any) -> None:
    from nectr.devtools.mutation_gate import (
        MutationPolicy,
        evaluate_targets,
        filter_trials_to_changed_lines,
        score_trials,
    )

    ranges = parse_ranges_helper(context.diff_text)
    filtered = filter_trials_to_changed_lines(context.raw_trials, ranges)
    score = score_trials(filtered)
    policy = MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={
            "src/nectr/contracts": 85.0,
            "src/nectr/chain": 85.0,
            "src/nectr/services": 75.0,
            "src/nectr/devtools": 75.0,
        },
        baseline={
            "src/nectr/contracts": 55.0,
            "src/nectr/chain": 65.0,
            "src/nectr/services": 0.0,
            "src/nectr/devtools": 0.0,
        },
        excluded=("src/nectr/personas", "src/nectr/ui", "experiments"),
    )
    context.diff_outcome = evaluate_targets({"src/nectr/contracts": score}, policy)


def parse_ranges_helper(diff_text: str) -> dict[str, list[tuple[int, int]]]:
    from nectr.devtools.mutation_gate import parse_changed_line_ranges

    return parse_changed_line_ranges(diff_text)


@then('the mutation gate fails for tier "src/nectr/contracts" below target 85.0%')
def step_then_diff_gate_fails(context: Any) -> None:
    outcome = context.diff_outcome
    assert outcome.passed is False
    assert any("src/nectr/contracts" in f and "85.0" in f for f in outcome.failures)


@given('committed baseline floors of 55% for "src/nectr/contracts" and 65% for "src/nectr/chain"')
def step_given_baseline_floors(context: Any) -> None:
    from nectr.devtools.mutation_gate import MutationPolicy

    context.floor_policy = MutationPolicy(
        engine="poodle",
        per_mutant_timeout_seconds=10,
        tiers={"src/nectr/contracts": 85.0, "src/nectr/chain": 85.0},
        baseline={"src/nectr/contracts": 55.0, "src/nectr/chain": 65.0},
        excluded=("src/nectr/personas", "src/nectr/ui", "experiments"),
    )


@when("the full-sweep mutation gate evaluates scores of 54.0% and 66.0%")
def step_when_eval_below_floor(context: Any) -> None:
    from nectr.devtools.mutation_gate import MutationScore, evaluate_floors

    scores = {
        "src/nectr/contracts": MutationScore(killed=54, survived=46, timeout=0, total=100),
        "src/nectr/chain": MutationScore(killed=60, survived=34, timeout=6, total=100),
    }
    context.floor_outcome = evaluate_floors(scores, context.floor_policy)


@then('the full-sweep gate fails for tier "src/nectr/contracts" below baseline floor 55.0%')
def step_then_floor_fails(context: Any) -> None:
    assert context.floor_outcome.passed is False
    assert any("src/nectr/contracts" in f and "55.0" in f for f in context.floor_outcome.failures)


@when("the full-sweep mutation gate evaluates scores of 55.0% and 66.0%")
def step_when_eval_above_floor(context: Any) -> None:
    from nectr.devtools.mutation_gate import MutationScore, evaluate_floors

    scores = {
        "src/nectr/contracts": MutationScore(killed=55, survived=45, timeout=0, total=100),
        "src/nectr/chain": MutationScore(killed=60, survived=34, timeout=6, total=100),
    }
    context.floor_outcome = evaluate_floors(scores, context.floor_policy)


@then("the full-sweep gate passes all baseline floors")
def step_then_floor_passes(context: Any) -> None:
    assert context.floor_outcome.passed is True


@given('changed files restricted to "src/nectr/personas/simulator.py" and "src/nectr/ui/app.py"')
def step_given_excluded_changes(context: Any) -> None:
    context.changed_paths = [
        "src/nectr/personas/simulator.py",
        "src/nectr/ui/app.py",
    ]


@when("the mutation gate classifies target files across bounded-context tiers")
def step_when_classify_targets(context: Any) -> None:
    from nectr.devtools.mutation_gate import (
        MutationPolicy,
        evaluate_targets,
        select_targets,
    )

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
    context.selected_targets = select_targets(context.changed_paths, policy)
    context.excluded_outcome = evaluate_targets({}, policy)


@then('zero tiered targets are selected and the gate reports "no tiered source changes"')
def step_then_no_tiered_targets(context: Any) -> None:
    assert context.selected_targets == {}
    assert context.excluded_outcome.passed is True
    assert "no tiered source changes" in context.excluded_outcome.summary.lower()


@when("I parse the Worktrunk lifecycle hooks and pre-commit exclusions")
def step_when_parse_wt_and_precommit(context: Any) -> None:
    import yaml

    path: Path = context.wt_config_path
    assert path.is_file(), f"Missing Worktrunk config: {path}"
    context.wt_data = tomllib.loads(path.read_text(encoding="utf-8"))
    context.precommit_data = yaml.safe_load(
        (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )


@then(
    'pre-merge hooks run "nectr.devtools.ci_parity check" and ".pre-commit-config.yaml" excludes ".worktrees" and ".poodle-temp"'
)
def step_then_wt_ci_parity_and_exclude(context: Any) -> None:
    pre_merge = context.wt_data.get("pre-merge", [])
    joined = " ".join(str(v) for block in pre_merge for v in block.values())
    assert "nectr.devtools.ci_parity check" in joined
    exclude_pattern = str(context.precommit_data.get("exclude", ""))
    assert ".worktrees" in exclude_pattern
    assert ".poodle-temp" in exclude_pattern
