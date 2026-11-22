"""Behave BDD step definitions for automated PR lifecycle, serial rebase, and merge-safety gates."""

from __future__ import annotations

import os
import subprocess
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from behave import given, then, when


def _git(cwd: Path, *args: str) -> None:
    clean_env = {
        k: v
        for k, v in os.environ.items()
        if k
        not in {
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES",
            "GIT_COMMON_DIR",
        }
    }
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=clean_env,
        check=True,
        capture_output=True,
        text=True,
    )


@given("a temporary git repository with a main branch and a feature branch")
def step_given_temp_git_repo(context: Any) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._pr_tmp = tmp
    repo = Path(tmp.name)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test Bot")
    _git(repo, "config", "user.email", "bot@example.com")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "app.txt").write_text("line1\n", encoding="utf-8")
    _git(repo, "add", "app.txt")
    _git(repo, "commit", "-m", "chore(init): seed main")
    _git(repo, "checkout", "-b", "feat/clean-branch")
    (repo / "feature.txt").write_text("ok\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feat(core): add feature")
    context.sim_git_repo = repo


@when(
    "the PR merge-safety validator checks Conventional Commit titles, merge-commit history, and merge-tree cleanliness"
)
def step_when_merge_safety_runs(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import validate_pr_title, verify_branch_merge_safety

    repo: Path = context.sim_git_repo
    context.clean_report = verify_branch_merge_safety(
        repo,
        base_ref="main",
        pr_title="feat(core): add deterministic safety check (#42)",
    )
    context.bad_title_ok, _ = validate_pr_title("Update files randomly")

    # Introduce a merge bubble onto main -> feature to verify rebase-only enforcement
    _git(repo, "checkout", "main")
    (repo / "main_advance.txt").write_text("advance\n", encoding="utf-8")
    _git(repo, "add", "main_advance.txt")
    _git(repo, "commit", "-m", "chore(main): advance base")
    _git(repo, "checkout", "feat/clean-branch")
    _git(repo, "merge", "--no-ff", "main", "-m", "Merge branch 'main' into feat/clean-branch")
    context.merge_bubble_report = verify_branch_merge_safety(
        repo,
        base_ref="main",
        pr_title="feat(core): add deterministic safety check",
    )


@then(
    "clean rebased branches with Conventional Commit titles pass while merge bubbles and non-conventional titles fail"
)
def step_then_merge_safety_verified(context: Any) -> None:
    assert context.clean_report.passed is True, context.clean_report.errors
    assert context.bad_title_ok is False
    assert context.merge_bubble_report.passed is False
    assert context.merge_bubble_report.linear_history is False


@given("a queue of open pull requests across CLEAN, BLOCKED, UNSTABLE, and BEHIND states")
def step_given_pr_queue(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import PullRequestSnapshot

    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    context.now = now
    context.pr_queue = [
        PullRequestSnapshot(
            number=30,
            title="fix(ci): broken check that already finished failing",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="UNSTABLE",
            auto_merge_enabled=True,
            checks_pending=False,
            labels=(),
            head_ref_name="fix/broken",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=1),
        ),
        PullRequestSnapshot(
            number=31,
            title="feat(chain): older behind PR",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="BEHIND",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/older",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=2),
        ),
        PullRequestSnapshot(
            number=32,
            title="feat(services): newer behind PR",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="BEHIND",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/newer",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=1),
        ),
    ]


@when(
    "the PR lifecycle planner evaluates actions both with PR_LIFECYCLE_TOKEN and with fallback GITHUB_TOKEN"
)
def step_when_lifecycle_evaluates_tokens(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import plan_pr_lifecycle_actions

    context.pat_actions = plan_pr_lifecycle_actions(
        context.pr_queue,
        repo_full_name="brandon-fox/nectR",
        now=context.now,
        has_pat_token=True,
    )
    context.fallback_actions = plan_pr_lifecycle_actions(
        context.pr_queue,
        repo_full_name="brandon-fox/nectR",
        now=context.now,
        has_pat_token=False,
    )


@then(
    "eligible PRs enroll in squash auto-merge, only the oldest BEHIND PR rebases when PAT is present, and fallback mode avoids stranding checks"
)
def step_then_queue_actions_verified(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import LifecycleActionKind

    auto_merge_prs = [
        a.pr_number for a in context.pat_actions if a.kind == LifecycleActionKind.ENABLE_AUTO_MERGE
    ]
    rebased_prs = [
        a.pr_number for a in context.pat_actions if a.kind == LifecycleActionKind.REBASE_BRANCH
    ]
    assert auto_merge_prs == [31, 32]
    assert rebased_prs == [31]

    fallback_rebases = [
        a.pr_number for a in context.fallback_actions if a.kind == LifecycleActionKind.REBASE_BRANCH
    ]
    skipped_no_pat = [
        a.pr_number
        for a in context.fallback_actions
        if a.kind == LifecycleActionKind.SKIP_REBASE_NO_PAT
    ]
    assert fallback_rebases == []
    assert skipped_no_pat == [31]


@given(
    "open pull requests from an untrusted fork, a conflicted branch, a draft branch, and an inactive stale branch"
)
def step_given_hygiene_prs(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import STALE_LABEL, PullRequestSnapshot

    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    context.now = now
    context.hygiene_prs = [
        PullRequestSnapshot(
            number=40,
            title="feat(chain): fork contribution",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="CLEAN",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/fork",
            head_repo_full_name="external-user/nectR",
            base_ref_name="main",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=1),
        ),
        PullRequestSnapshot(
            number=41,
            title="feat(contracts): conflicting change",
            is_draft=False,
            mergeable="CONFLICTING",
            merge_state_status="DIRTY",
            auto_merge_enabled=True,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/conflict",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=2),
        ),
        PullRequestSnapshot(
            number=42,
            title="feat(ui): work in progress draft",
            is_draft=True,
            mergeable="MERGEABLE",
            merge_state_status="DRAFT",
            auto_merge_enabled=True,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/draft",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=1),
        ),
        PullRequestSnapshot(
            number=43,
            title="chore(docs): inactive 15 days",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="BLOCKED",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="chore/stale-warn",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=15),
        ),
        PullRequestSnapshot(
            number=44,
            title="chore(docs): already stale 8 more days",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="BLOCKED",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(STALE_LABEL,),
            head_ref_name="chore/stale-close",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=8),
        ),
    ]


@when("the PR lifecycle planner evaluates scheduled hygiene and conflict rules")
def step_when_hygiene_evaluated(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import plan_pr_lifecycle_actions

    context.hygiene_actions = plan_pr_lifecycle_actions(
        context.hygiene_prs,
        repo_full_name="brandon-fox/nectR",
        now=context.now,
        has_pat_token=True,
        check_stale=True,
    )


@then(
    "untrusted forks and drafts are skipped, conflicts receive rebase guidance labels, and stale PRs warn at 14 days then close after 7 more days"
)
def step_then_hygiene_verified(context: Any) -> None:
    from nectr.devtools.pr_lifecycle import CONFLICT_LABEL, STALE_LABEL, LifecycleActionKind

    by_pr: dict[int, list[Any]] = {}
    for act in context.hygiene_actions:
        by_pr.setdefault(act.pr_number, []).append(act)

    assert 40 not in by_pr
    assert any(
        a.kind == LifecycleActionKind.ADD_LABEL and a.detail == CONFLICT_LABEL for a in by_pr[41]
    )
    assert any(a.kind == LifecycleActionKind.DISABLE_AUTO_MERGE for a in by_pr[41])
    assert any(a.kind == LifecycleActionKind.DISABLE_AUTO_MERGE for a in by_pr[42])
    assert any(
        a.kind == LifecycleActionKind.ADD_LABEL and a.detail == STALE_LABEL for a in by_pr[43]
    )
    assert any(a.kind == LifecycleActionKind.CLOSE_STALE for a in by_pr[44])


@given("the nectR multi-hive smart contract engine and PoUW-PoW blockchain")
def step_given_chain_and_contracts(context: Any) -> None:
    from nectr.services.hive_service import HiveServiceLayer

    context.hive_a = HiveServiceLayer(
        hive_id="HIVE_BDD_A", difficulty=1, accepted_status_peer_threshold=2
    )
    context.hive_b = HiveServiceLayer(
        hive_id="HIVE_BDD_B", difficulty=1, accepted_status_peer_threshold=2
    )


@when("adversarial tampering checks and stateful multi-step transaction sequences execute")
def step_when_adversarial_and_stateful_run(context: Any) -> None:
    from nectr.contracts.engine import BeeRole, ContractViolationError, TokenState

    hive_a = context.hive_a
    hive_b = context.hive_b
    hive_a.bootstrap_sponsored_hive(500.0, ["queen_a"], {"worker_a": ["CS-101"]})
    hive_b.bootstrap_sponsored_hive(300.0, ["queen_b"], {"worker_b": ["MATH-101"]})
    hive_a.contracts.register_bee("learner_a", role=BeeRole.LEARNER_BEE)
    hive_a.contracts.allocate_raw_pollen_to_learner("queen_a", "learner_a", 50.0)
    hive_a.execute_tutoring_handshake(
        session_id="bdd_s1",
        tutor_id="worker_a",
        learner_id="learner_a",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.RAW_POLLEN,
    )
    hive_a.mine_epoch_block()

    # Verify Guard Bee rejection before Accepted Status
    context.unaccepted_bridge_rejected = False
    try:
        hive_a.contracts.bridge_nectr_to_target_hive("worker_a", hive_b.contracts, 5.0)
    except ContractViolationError:
        context.unaccepted_bridge_rejected = True

    # Tamper with mined block transactions and verify PoUW-PoW chain rejects it
    hive_a.blockchain.chain[-1].transactions.append({"forged": True})
    context.tampered_valid = hive_a.blockchain.verify_chain()

    ci_yml = (
        Path(__file__).resolve().parents[2] / ".github/workflows/license-and-security-scan.yml"
    ).read_text(encoding="utf-8")
    context.ci_yml = ci_yml


@then(
    "tampered blocks are rejected and supply conservation, Queen separation of powers, and Guard Bee bridge invariants hold at 90 percent branch coverage"
)
def step_then_invariants_and_90_coverage_verified(context: Any) -> None:
    assert context.unaccepted_bridge_rejected is True
    assert context.tampered_valid is False
    context.hive_a.contracts.assert_supply_conservation()
    context.hive_b.contracts.assert_supply_conservation()
    assert context.hive_a.contracts.accounts["queen_a"].liquid_nectr_balance == 0.0
    assert "--cov-branch" in context.ci_yml
    assert "--cov-fail-under=90" in context.ci_yml
