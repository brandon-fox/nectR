"""Strict TDD tests for automated PR lifecycle, serial rebase queue, and merge-safety checks."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from nectr.devtools.pr_lifecycle import (
    CONFLICT_COMMENT_MARKER,
    CONFLICT_LABEL,
    FORK_APPROVAL_LABEL,
    INVALID_TITLE_LABEL,
    STALE_COMMENT_MARKER,
    STALE_LABEL,
    GhCliAdapter,
    LifecycleActionKind,
    PullRequestSnapshot,
    execute_lifecycle_actions,
    main,
    parse_gh_pr_payload,
    plan_pr_lifecycle_actions,
    validate_pr_title,
    verify_branch_merge_safety,
)


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


def _make_pr(
    number: int,
    *,
    title: str = "feat(chain): add block check",
    is_draft: bool = False,
    mergeable: str = "MERGEABLE",
    merge_state_status: str = "BLOCKED",
    auto_merge_enabled: bool = False,
    checks_pending: bool = False,
    labels: tuple[str, ...] = (),
    head_ref_name: str = "feat/test",
    head_repo_full_name: str = "brandon-fox/nectR",
    base_ref_name: str = "main",
    created_offset_hours: int = -4,
    updated_offset_days: int = 0,
) -> PullRequestSnapshot:
    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    return PullRequestSnapshot(
        number=number,
        title=title,
        is_draft=is_draft,
        mergeable=mergeable,
        merge_state_status=merge_state_status,
        auto_merge_enabled=auto_merge_enabled,
        checks_pending=checks_pending,
        labels=labels,
        head_ref_name=head_ref_name,
        head_repo_full_name=head_repo_full_name,
        base_ref_name=base_ref_name,
        created_at=now + timedelta(hours=created_offset_hours),
        updated_at=now + timedelta(days=updated_offset_days),
    )


class _RecordingPort:
    """In-memory hexagonal port test double recording all executed PR lifecycle mutations."""

    def __init__(self, prs: list[PullRequestSnapshot] | None = None) -> None:
        self.prs = prs or []
        self.calls: list[tuple[str, Any]] = []

    def list_open_prs(self, repo_full_name: str) -> list[PullRequestSnapshot]:
        self.calls.append(("list_open_prs", repo_full_name))
        return list(self.prs)

    def ensure_label_exists(self, repo_full_name: str, label: str, color: str, desc: str) -> None:
        self.calls.append(("ensure_label_exists", (repo_full_name, label, color, desc)))

    def add_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        self.calls.append(("add_label", (pr_number, label)))

    def remove_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        self.calls.append(("remove_label", (pr_number, label)))

    def post_idempotent_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        marker: str,
        body: str,
    ) -> None:
        self.calls.append(("post_comment", (pr_number, marker, bool(body))))

    def enable_squash_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        self.calls.append(("enable_auto_merge", pr_number))

    def disable_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        self.calls.append(("disable_auto_merge", pr_number))

    def merge_clean_squash_now(self, repo_full_name: str, pr_number: int) -> None:
        self.calls.append(("merge_clean_now", pr_number))

    def rebase_branch(self, repo_full_name: str, pr_number: int) -> None:
        self.calls.append(("rebase_branch", pr_number))

    def close_pr(self, repo_full_name: str, pr_number: int, reason_comment: str) -> None:
        self.calls.append(("close_pr", (pr_number, bool(reason_comment))))


def test_validate_pr_title_enforces_conventional_commits() -> None:
    ok, _ = validate_pr_title("feat(chain): add Merkle proof verification (#21)")
    assert ok is True

    ok_bang, _ = validate_pr_title("refactor(contracts)!: tighten escrow invariant")
    assert ok_bang is True

    for invalid in (
        "",
        "   ",
        "Update README",
        "wip: temporary stuff",
        "feat: ab",
        "feat(chain): " + ("a" * 130),
    ):
        valid, reason = validate_pr_title(invalid)
        assert valid is False, f"Expected '{invalid}' to fail, got reason={reason}"


def test_verify_branch_merge_safety_detects_merge_bubbles_conflicts_and_bad_refs(
    tmp_path: Path,
) -> None:
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

    bad_ref_report = verify_branch_merge_safety(
        tmp_path,
        base_ref="nonexistent-base-ref",
        pr_title="Bad Title",
    )
    assert bad_ref_report.passed is False
    assert bad_ref_report.title_valid is False
    assert bad_ref_report.linear_history is False

    # Trailing whitespace triggers git diff --check failure
    (tmp_path / "feat.txt").write_text("trailing   \n", encoding="utf-8")
    _git(tmp_path, "add", "feat.txt")
    _git(tmp_path, "commit", "-m", "feat(ci): trailing space")
    ws_report = verify_branch_merge_safety(tmp_path, base_ref="main")
    assert ws_report.passed is False

    # Fix whitespace, then introduce conflicting edit on main & branch
    (tmp_path / "feat.txt").write_text("clean-again\n", encoding="utf-8")
    _git(tmp_path, "add", "feat.txt")
    _git(tmp_path, "commit", "-m", "feat(ci): fix trailing space")

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


def test_plan_pr_lifecycle_serial_rebase_clean_merge_and_token_guard() -> None:
    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    prs = [
        _make_pr(10, merge_state_status="CLEAN", created_offset_hours=-3),
        _make_pr(11, merge_state_status="BEHIND", created_offset_hours=-2),
    ]

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

    # Active pending checks on up-to-date PR also hold serial rebase to avoid wasted CI runs
    pending_prs = [
        _make_pr(
            12,
            merge_state_status="BLOCKED",
            checks_pending=True,
            auto_merge_enabled=True,
            created_offset_hours=-3,
        ),
        _make_pr(13, merge_state_status="BEHIND", auto_merge_enabled=True, created_offset_hours=-1),
    ]
    pending_actions = plan_pr_lifecycle_actions(
        pending_prs,
        repo_full_name="brandon-fox/nectR",
        now=now,
        has_pat_token=True,
    )
    assert pending_actions == []


def test_plan_pr_lifecycle_labels_recovery_opt_outs_forks_and_stale() -> None:
    now = datetime(2026, 11, 21, 21, 0, tzinfo=UTC)
    prs = [
        # Non-main base branch ignored
        _make_pr(1, base_ref_name="release/v1"),
        # Approved fork PR IS allowed
        _make_pr(
            2,
            head_repo_full_name="contributor/nectR",
            labels=(FORK_APPROVAL_LABEL,),
            merge_state_status="BLOCKED",
        ),
        # Invalid title labels & disables auto-merge
        _make_pr(3, title="bad title", auto_merge_enabled=True),
        # Fixed title clears INVALID_TITLE_LABEL, fixed conflict clears CONFLICT_LABEL, recent activity clears STALE_LABEL
        _make_pr(
            4,
            labels=(INVALID_TITLE_LABEL, CONFLICT_LABEL, STALE_LABEL),
            merge_state_status="CLEAN",
            auto_merge_enabled=True,
            updated_offset_days=-1,
        ),
        # Hold label disables auto-merge
        _make_pr(5, labels=("do-not-merge",), auto_merge_enabled=True),
        # Pinned PR is exempt from stale warning even after 30 days
        _make_pr(
            6,
            labels=("pinned",),
            merge_state_status="BLOCKED",
            auto_merge_enabled=True,
            updated_offset_days=-30,
        ),
    ]
    actions = plan_pr_lifecycle_actions(
        prs,
        repo_full_name="brandon-fox/nectR",
        now=now,
        has_pat_token=True,
        check_stale=True,
    )
    by_pr: dict[int, list[Any]] = {}
    for act in actions:
        by_pr.setdefault(act.pr_number, []).append(act)

    assert 1 not in by_pr
    assert 6 not in by_pr
    assert any(a.kind == LifecycleActionKind.ENABLE_AUTO_MERGE for a in by_pr[2])
    assert any(
        a.kind == LifecycleActionKind.ADD_LABEL and a.detail == INVALID_TITLE_LABEL
        for a in by_pr[3]
    )
    assert any(a.kind == LifecycleActionKind.DISABLE_AUTO_MERGE for a in by_pr[3])
    removed_on_4 = {a.detail for a in by_pr[4] if a.kind == LifecycleActionKind.REMOVE_LABEL}
    assert removed_on_4 == {INVALID_TITLE_LABEL, CONFLICT_LABEL, STALE_LABEL}
    assert any(a.kind == LifecycleActionKind.DISABLE_AUTO_MERGE for a in by_pr[5])


def test_parse_gh_pr_payload_and_execute_lifecycle_actions_and_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_item = {
        "number": 55,
        "title": "feat(services): add health check",
        "isDraft": False,
        "mergeable": "mergeable",
        "mergeStateStatus": "behind",
        "autoMergeRequest": None,
        "statusCheckRollup": [{"status": "IN_PROGRESS"}],
        "labels": [{"name": "enhancement"}],
        "headRefName": "feat/health",
        "headRepository": {"name": "nectR"},
        "headRepositoryOwner": {"login": "brandon-fox"},
        "baseRefName": "main",
        "createdAt": "2026-11-21T18:00:00Z",
        "updatedAt": "2026-11-21T19:00:00",
    }
    snap = parse_gh_pr_payload(raw_item, "brandon-fox/nectR")
    assert snap.number == 55
    assert snap.checks_pending is True
    assert snap.merge_state_status == "BEHIND"
    assert snap.labels == ("enhancement",)

    # Exercise all action kinds in execute_lifecycle_actions (dry-run and live)
    conflicted = _make_pr(
        60, mergeable="CONFLICTING", merge_state_status="DIRTY", auto_merge_enabled=True
    )
    clean = _make_pr(61, merge_state_status="CLEAN")
    stale_close = _make_pr(62, labels=(STALE_LABEL,), updated_offset_days=-9)
    behind = _make_pr(63, merge_state_status="BEHIND", updated_offset_days=-15)

    port = _RecordingPort([conflicted, stale_close, behind])
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

    # Dry-run CLI reconcile
    rc_dry = main(
        ["reconcile", "--repo", "brandon-fox/nectR", "--check-stale", "--dry-run"],
        port=port,
    )
    assert rc_dry == 0
    assert [c[0] for c in port.calls] == ["list_open_prs"]
    assert "GITHUB_TOKEN" in summary_file.read_text(encoding="utf-8")

    # Live CLI reconcile with --has-pat
    port_live = _RecordingPort([conflicted, stale_close, behind])
    rc_live = main(
        ["reconcile", "--repo", "brandon-fox/nectR", "--has-pat", "--check-stale"],
        port=port_live,
    )
    assert rc_live == 0
    recorded_ops = {c[0] for c in port_live.calls}
    assert {
        "list_open_prs",
        "add_label",
        "post_comment",
        "disable_auto_merge",
        "close_pr",
        "enable_auto_merge",
        "rebase_branch",
    } <= recorded_ops

    # Also test MERGE_CLEAN_NOW and REMOVE_LABEL execution directly
    clean_fixed = _make_pr(64, merge_state_status="CLEAN", labels=(CONFLICT_LABEL,))
    clean_actions = plan_pr_lifecycle_actions(
        [clean, clean_fixed],
        repo_full_name="brandon-fox/nectR",
        now=datetime(2026, 11, 21, 21, 0, tzinfo=UTC),
        has_pat_token=True,
    )
    port_clean = _RecordingPort()
    execute_lifecycle_actions(clean_actions, port=port_clean, repo_full_name="brandon-fox/nectR")
    clean_ops = {c[0] for c in port_clean.calls}
    assert "merge_clean_now" in clean_ops
    assert "remove_label" in clean_ops

    # No-op reconcile summary
    empty_port = _RecordingPort([])
    assert main(["reconcile", "--repo", "brandon-fox/nectR", "--has-pat"], port=empty_port) == 0
    assert "no actions required" in summary_file.read_text(encoding="utf-8")

    # CLI check-title and check-branch exit codes
    assert main(["check-title", "--title", "feat(ci): valid summary"]) == 0
    assert main(["check-title", "--title", "invalid summary"]) == 1

    git_dir = tmp_path / "repo"
    git_dir.mkdir(parents=True, exist_ok=True)
    _git(git_dir, "init", "-b", "main")
    _git(git_dir, "config", "user.name", "Bot")
    _git(git_dir, "config", "user.email", "bot@example.com")
    _git(git_dir, "config", "commit.gpgsign", "false")
    (git_dir / "a.txt").write_text("ok\n", encoding="utf-8")
    _git(git_dir, "add", "a.txt")
    _git(git_dir, "commit", "-m", "chore: init")
    assert (
        main(["check-branch", "--root", str(git_dir), "--base", "main", "--title", "feat: okays"])
        == 0
    )
    assert main(["check-branch", "--root", str(git_dir), "--base", "main", "--title", "bad"]) == 1


def test_gh_cli_adapter_invokes_expected_subcommands(monkeypatch: pytest.MonkeyPatch) -> None:
    invocations: list[tuple[str, ...]] = []

    def _fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        invocations.append(tuple(cmd))
        if cmd[:3] == ["gh", "pr", "list"]:
            payload = [
                {
                    "number": 7,
                    "title": "feat(ci): demo",
                    "isDraft": False,
                    "mergeable": "MERGEABLE",
                    "mergeStateStatus": "CLEAN",
                    "autoMergeRequest": None,
                    "statusCheckRollup": [],
                    "labels": [],
                    "headRefName": "feat/demo",
                    "headRepository": {},
                    "headRepositoryOwner": {},
                    "baseRefName": "main",
                    "createdAt": "2026-11-21T10:00:00Z",
                    "updatedAt": "2026-11-21T11:00:00Z",
                }
            ]
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")
        if cmd[:3] == ["gh", "pr", "view"]:
            # First call has no marker; second call already has marker (idempotent skip)
            has_existing = sum(1 for c in invocations if c[:3] == ("gh", "pr", "view")) > 1
            comments = [{"body": CONFLICT_COMMENT_MARKER}] if has_existing else []
            return subprocess.CompletedProcess(
                cmd, 0, stdout=json.dumps({"comments": comments}), stderr=""
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="{}", stderr="")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    adapter = GhCliAdapter()
    prs = adapter.list_open_prs("brandon-fox/nectR")
    assert len(prs) == 1 and prs[0].head_repo_full_name == "brandon-fox/nectR"

    adapter.add_label("brandon-fox/nectR", 7, CONFLICT_LABEL)
    adapter.remove_label("brandon-fox/nectR", 7, STALE_LABEL)
    adapter.post_idempotent_comment("brandon-fox/nectR", 7, CONFLICT_COMMENT_MARKER, "body1")
    adapter.post_idempotent_comment("brandon-fox/nectR", 7, CONFLICT_COMMENT_MARKER, "body1")
    adapter.enable_squash_auto_merge("brandon-fox/nectR", 7)
    adapter.disable_auto_merge("brandon-fox/nectR", 7)
    adapter.merge_clean_squash_now("brandon-fox/nectR", 7)
    adapter.rebase_branch("brandon-fox/nectR", 7)
    adapter.close_pr("brandon-fox/nectR", 7, STALE_COMMENT_MARKER)

    comment_posts = [c for c in invocations if c[:3] == ("gh", "pr", "comment")]
    assert len(comment_posts) == 1


def test_pr_lifecycle_workflow_does_not_pass_check_stale() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    wf_text = (repo_root / ".github" / "workflows" / "pr-lifecycle.yml").read_text(encoding="utf-8")
    assert "--check-stale" not in wf_text
    assert "nectr.devtools.pr_lifecycle" in wf_text
