"""Strict TDD tests for automated PR lifecycle, serial rebase queue, and merge-safety checks."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.xfail(
    strict=True,
    reason="RED: automate-pr-lifecycle-and-merge-safety not yet implemented",
)
def test_validate_pr_title_enforces_conventional_commits() -> None:
    from nectr.devtools.pr_lifecycle import validate_pr_title

    ok, _ = validate_pr_title("feat(chain): add Merkle proof verification (#21)")
    assert ok is True

    ok_bang, _ = validate_pr_title("refactor(contracts)!: tighten escrow invariant")
    assert ok_bang is True

    for invalid in (
        "",
        "Update README",
        "wip: temporary stuff",
        "feat: x",
        "feat(chain): " + ("a" * 130),
    ):
        valid, reason = validate_pr_title(invalid)
        assert valid is False, f"Expected '{invalid}' to fail, got reason={reason}"


@pytest.mark.xfail(
    strict=True,
    reason="RED: automate-pr-lifecycle-and-merge-safety not yet implemented",
)
def test_verify_branch_merge_safety_detects_merge_bubbles_and_conflicts(tmp_path: Path) -> None:
    from nectr.devtools.pr_lifecycle import verify_branch_merge_safety

    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "Test Bot")
    _git(tmp_path, "config", "user.email", "bot@example.com")
    _git(tmp_path, "config", "commit.gpgsign", "false")

    (tmp_path / "shared.txt").write_text("base\n", encoding="utf-8")
    _git(tmp_path, "add", "shared.txt")
    _git(tmp_path, "commit", "-m", "chore: initial")

    _git(tmp_path, "checkout", "-b", "feat/rebased")
    (tmp_path / "feat.txt").write_text("clean\n", encoding="utf-8")
    _git(tmp_path, "add", "feat.txt")
    _git(tmp_path, "commit", "-m", "feat(ci): add clean commit")

    report = verify_branch_merge_safety(
        tmp_path,
        base_ref="main",
        pr_title="feat(ci): add clean commit",
    )
    assert report.passed is True
    assert report.linear_history is True
    assert report.merge_tree_clean is True

    # Advance main with conflicting edit on shared.txt
    _git(tmp_path, "checkout", "main")
    (tmp_path / "shared.txt").write_text("main-edit\n", encoding="utf-8")
    _git(tmp_path, "add", "shared.txt")
    _git(tmp_path, "commit", "-m", "fix: main edit")

    _git(tmp_path, "checkout", "feat/rebased")
    (tmp_path / "shared.txt").write_text("branch-edit\n", encoding="utf-8")
    _git(tmp_path, "add", "shared.txt")
    _git(tmp_path, "commit", "-m", "feat: conflicting edit")

    conflict_report = verify_branch_merge_safety(
        tmp_path,
        base_ref="main",
        pr_title="feat(ci): conflicting branch",
    )
    assert conflict_report.passed is False
    assert conflict_report.merge_tree_clean is False


@pytest.mark.xfail(
    strict=True,
    reason="RED: automate-pr-lifecycle-and-merge-safety not yet implemented",
)
def test_plan_pr_lifecycle_serial_rebase_clean_merge_and_token_guard() -> None:
    from nectr.devtools.pr_lifecycle import (
        LifecycleActionKind,
        PullRequestSnapshot,
        plan_pr_lifecycle_actions,
    )

    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    prs = [
        PullRequestSnapshot(
            number=10,
            title="feat(docs): already clean and ready",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="CLEAN",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/clean",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(minutes=10),
        ),
        PullRequestSnapshot(
            number=11,
            title="feat(chain): behind waiting for front of queue",
            is_draft=False,
            mergeable="MERGEABLE",
            merge_state_status="BEHIND",
            auto_merge_enabled=False,
            checks_pending=False,
            labels=(),
            head_ref_name="feat/behind",
            head_repo_full_name="brandon-fox/nectR",
            base_ref_name="main",
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(minutes=5),
        ),
    ]

    # While PR #10 is CLEAN (merging now), PR #11 enables auto-merge but waits to rebase until #10 lands!
    actions = plan_pr_lifecycle_actions(
        prs,
        repo_full_name="brandon-fox/nectR",
        now=now,
        has_pat_token=True,
    )
    assert any(a.pr_number == 10 and a.kind == LifecycleActionKind.MERGE_CLEAN_NOW for a in actions)
    assert any(
        a.pr_number == 11 and a.kind == LifecycleActionKind.ENABLE_AUTO_MERGE for a in actions
    )
    assert not any(a.kind == LifecycleActionKind.REBASE_BRANCH for a in actions)
