"""Deterministic PR lifecycle planner, rebase-linear merge-safety gate, and GitHub CLI adapter."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Protocol

ALLOWED_COMMIT_TYPES: tuple[str, ...] = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
)
PR_NUMBER_SUFFIX_RE = re.compile(r"\s*\(#\d+\)\s*$")
CONVENTIONAL_TITLE_RE = re.compile(
    r"^(?P<type>"
    + "|".join(ALLOWED_COMMIT_TYPES)
    + r")(?:\((?P<scope>[A-Za-z0-9_./-]+)\))?(?P<breaking>!)?:\s+(?P<subject>\S.*)$"
)

OPT_OUT_LABELS: frozenset[str] = frozenset({"do-not-merge", "wip", "hold"})
STALE_EXEMPT_LABELS: frozenset[str] = frozenset({"pinned", "keep-open", "security"})
FORK_APPROVAL_LABEL = "automerge:approved"

CONFLICT_LABEL = "merge-conflict"
INVALID_TITLE_LABEL = "invalid-pr-title"
STALE_LABEL = "stale"

CONFLICT_COMMENT_MARKER = "<!-- nectr-pr-lifecycle:conflict -->"
STALE_COMMENT_MARKER = "<!-- nectr-pr-lifecycle:stale -->"

CONFLICT_GUIDANCE_BODY = (
    f"{CONFLICT_COMMENT_MARKER}\n"
    "### Merge Conflict Detected\n\n"
    "This pull request conflicts with `main` and automatic squash-merge has been paused.\n"
    "Please rebase onto the latest `origin/main` and push with `--force-with-lease`:\n\n"
    "```bash\n"
    "git fetch origin\n"
    "git rebase origin/main\n"
    "git push --force-with-lease\n"
    "```\n"
)

STALE_WARNING_BODY = (
    f"{STALE_COMMENT_MARKER}\n"
    "### Stale Pull Request Notice\n\n"
    "This pull request has had no activity for 14 days and has been marked `stale`.\n"
    "Push a rebased update, comment, or add the `keep-open` label within 7 days to keep it open.\n"
)


class LifecycleActionKind(StrEnum):
    """Atomic operations emitted by the pure PR lifecycle planner."""

    ENABLE_AUTO_MERGE = "ENABLE_AUTO_MERGE"
    DISABLE_AUTO_MERGE = "DISABLE_AUTO_MERGE"
    MERGE_CLEAN_NOW = "MERGE_CLEAN_NOW"
    REBASE_BRANCH = "REBASE_BRANCH"
    SKIP_REBASE_NO_PAT = "SKIP_REBASE_NO_PAT"
    ADD_LABEL = "ADD_LABEL"
    REMOVE_LABEL = "REMOVE_LABEL"
    POST_COMMENT = "POST_COMMENT"
    CLOSE_STALE = "CLOSE_STALE"


@dataclass(frozen=True)
class PullRequestSnapshot:
    """Immutable point-in-time snapshot of an open GitHub pull request."""

    number: int
    title: str
    is_draft: bool
    mergeable: str
    merge_state_status: str
    auto_merge_enabled: bool
    checks_pending: bool
    labels: tuple[str, ...]
    head_ref_name: str
    head_repo_full_name: str
    base_ref_name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class LifecycleAction:
    """Single deterministic action planned for a pull request."""

    pr_number: int
    kind: LifecycleActionKind
    detail: str
    marker: str = ""


@dataclass(frozen=True)
class BranchSafetyReport:
    """Result of verifying PR title, rebase-only linear history, and merge-tree cleanliness."""

    passed: bool
    title_valid: bool
    linear_history: bool
    merge_tree_clean: bool
    errors: tuple[str, ...]


class PullRequestPort(Protocol):
    """Hexagonal port abstracting GitHub pull request queries and mutations."""

    def list_open_prs(self, repo_full_name: str) -> list[PullRequestSnapshot]:
        """Fetch all open pull requests for ``repo_full_name``."""

    def ensure_label_exists(self, repo_full_name: str, label: str, color: str, desc: str) -> None:
        """Create ``label`` idempotently if missing in the repository."""

    def add_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        """Apply ``label`` to a pull request."""

    def remove_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        """Remove ``label`` from a pull request."""

    def post_idempotent_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        marker: str,
        body: str,
    ) -> None:
        """Post ``body`` only if no existing comment on the PR contains ``marker``."""

    def enable_squash_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        """Enable verified squash auto-merge on ``pr_number``."""

    def disable_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        """Disable auto-merge on ``pr_number``."""

    def merge_clean_squash_now(self, repo_full_name: str, pr_number: int) -> None:
        """Immediately squash-merge an already CLEAN pull request and delete its branch."""

    def rebase_branch(self, repo_full_name: str, pr_number: int) -> None:
        """Rebase ``pr_number`` onto its base branch via GitHub's native rebase endpoint."""

    def close_pr(self, repo_full_name: str, pr_number: int, reason_comment: str) -> None:
        """Close an inactive stale pull request with an explanatory comment."""


def validate_pr_title(title: str) -> tuple[bool, str]:
    """Validate that a PR title satisfies Commitizen Conventional Commits for squash merges."""
    normalized = PR_NUMBER_SUFFIX_RE.sub("", title.strip())
    if not normalized:
        return False, "PR title must not be empty."
    if len(normalized) > 100:
        return False, f"PR title exceeds 100 characters ({len(normalized)} chars)."

    match = CONVENTIONAL_TITLE_RE.match(normalized)
    if match is None:
        allowed = ", ".join(ALLOWED_COMMIT_TYPES)
        return (
            False,
            f"PR title '{title}' must match '<type>(<scope>): <summary>' using one of: {allowed}.",
        )

    subject = match.group("subject").strip()
    if len(subject) < 3:
        return False, "PR title summary after ': ' must be at least 3 characters."
    return True, "ok"


_GIT_HOOK_ENV_VARS: frozenset[str] = frozenset(
    {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
    }
)


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    clean_env = {k: v for k, v in os.environ.items() if k not in _GIT_HOOK_ENV_VARS}
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        env=clean_env,
        check=False,
        capture_output=True,
        text=True,
    )


def verify_branch_merge_safety(
    repo_root: Path,
    *,
    base_ref: str,
    pr_title: str | None = None,
) -> BranchSafetyReport:
    """Verify Conventional Commit PR title, zero merge bubbles, and clean merge-tree simulation."""
    errors: list[str] = []
    title_valid = True

    if pr_title is not None:
        title_valid, reason = validate_pr_title(pr_title)
        if not title_valid:
            errors.append(reason)

    merges_proc = _run_git(repo_root, "rev-list", "--merges", f"{base_ref}..HEAD")
    linear_history = True
    if merges_proc.returncode != 0:
        linear_history = False
        errors.append(
            f"Unable to inspect commit range '{base_ref}..HEAD': {merges_proc.stderr.strip()}"
        )
    else:
        merge_shas = [ln.strip() for ln in merges_proc.stdout.splitlines() if ln.strip()]
        if merge_shas:
            linear_history = False
            errors.append(
                f"Branch contains {len(merge_shas)} merge commit(s) ({', '.join(merge_shas[:3])}); "
                f"always rebase onto '{base_ref}' instead of merging."
            )

    merge_tree_proc = _run_git(repo_root, "merge-tree", "--write-tree", base_ref, "HEAD")
    merge_tree_clean = merge_tree_proc.returncode == 0
    if not merge_tree_clean:
        errors.append(
            f"Simulated merge against '{base_ref}' detected conflicts; rebase onto latest '{base_ref}'."
        )

    diff_check_proc = _run_git(repo_root, "diff", "--check", f"{base_ref}...HEAD")
    if diff_check_proc.returncode != 0:
        errors.append(
            f"Whitespace or leftover conflict marker error in diff: {diff_check_proc.stdout.strip()}"
        )

    return BranchSafetyReport(
        passed=len(errors) == 0,
        title_valid=title_valid,
        linear_history=linear_history,
        merge_tree_clean=merge_tree_clean,
        errors=tuple(errors),
    )


def _evaluate_single_pr(
    pr: PullRequestSnapshot,
    *,
    repo_full_name: str,
    now: datetime,
    check_stale: bool,
    stale_days: int,
    close_stale_days: int,
    actions: list[LifecycleAction],
) -> bool:
    """Append hygiene/label actions for ``pr`` and return True if eligible for auto-merge & rebase."""
    if pr.base_ref_name != "main":
        return False

    label_set = set(pr.labels)
    is_same_repo = pr.head_repo_full_name.lower() == repo_full_name.lower()
    if not is_same_repo and FORK_APPROVAL_LABEL not in label_set:
        return False

    title_ok, title_err = validate_pr_title(pr.title)
    if not title_ok:
        if INVALID_TITLE_LABEL not in label_set:
            actions.append(
                LifecycleAction(pr.number, LifecycleActionKind.ADD_LABEL, INVALID_TITLE_LABEL)
            )
        if pr.auto_merge_enabled:
            actions.append(
                LifecycleAction(pr.number, LifecycleActionKind.DISABLE_AUTO_MERGE, title_err)
            )
        return False
    if INVALID_TITLE_LABEL in label_set:
        actions.append(
            LifecycleAction(pr.number, LifecycleActionKind.REMOVE_LABEL, INVALID_TITLE_LABEL)
        )

    is_conflicting = pr.mergeable == "CONFLICTING" or pr.merge_state_status == "DIRTY"
    if is_conflicting:
        if CONFLICT_LABEL not in label_set:
            actions.append(
                LifecycleAction(pr.number, LifecycleActionKind.ADD_LABEL, CONFLICT_LABEL)
            )
        actions.append(
            LifecycleAction(
                pr.number,
                LifecycleActionKind.POST_COMMENT,
                CONFLICT_GUIDANCE_BODY,
                marker=CONFLICT_COMMENT_MARKER,
            )
        )
        if pr.auto_merge_enabled:
            actions.append(
                LifecycleAction(
                    pr.number,
                    LifecycleActionKind.DISABLE_AUTO_MERGE,
                    "Merge conflict with main",
                )
            )
        return False
    if CONFLICT_LABEL in label_set:
        actions.append(LifecycleAction(pr.number, LifecycleActionKind.REMOVE_LABEL, CONFLICT_LABEL))

    if pr.is_draft or bool(OPT_OUT_LABELS & label_set):
        if pr.auto_merge_enabled:
            actions.append(
                LifecycleAction(
                    pr.number,
                    LifecycleActionKind.DISABLE_AUTO_MERGE,
                    "Draft or opt-out label active",
                )
            )
        return False

    if check_stale and not bool(STALE_EXEMPT_LABELS & label_set):
        inactivity = now - pr.updated_at
        if STALE_LABEL in label_set and inactivity >= timedelta(days=close_stale_days):
            actions.append(
                LifecycleAction(
                    pr.number,
                    LifecycleActionKind.CLOSE_STALE,
                    "Closing pull request after 7 additional days of inactivity while marked stale.",
                )
            )
            return False
        if STALE_LABEL not in label_set and inactivity >= timedelta(days=stale_days):
            actions.append(LifecycleAction(pr.number, LifecycleActionKind.ADD_LABEL, STALE_LABEL))
            actions.append(
                LifecycleAction(
                    pr.number,
                    LifecycleActionKind.POST_COMMENT,
                    STALE_WARNING_BODY,
                    marker=STALE_COMMENT_MARKER,
                )
            )
        elif STALE_LABEL in label_set and inactivity < timedelta(days=stale_days):
            actions.append(
                LifecycleAction(pr.number, LifecycleActionKind.REMOVE_LABEL, STALE_LABEL)
            )

    return True


def plan_pr_lifecycle_actions(
    prs: Sequence[PullRequestSnapshot],
    *,
    repo_full_name: str,
    now: datetime,
    has_pat_token: bool,
    check_stale: bool = False,
    stale_days: int = 14,
    close_stale_days: int = 7,
) -> list[LifecycleAction]:
    """Compute the deterministic sequence of PR lifecycle, auto-merge, and serial rebase actions."""
    actions: list[LifecycleAction] = []
    eligible: list[PullRequestSnapshot] = []

    ordered_prs = sorted(prs, key=lambda item: (item.created_at, item.number))
    for pr in ordered_prs:
        if _evaluate_single_pr(
            pr,
            repo_full_name=repo_full_name,
            now=now,
            check_stale=check_stale,
            stale_days=stale_days,
            close_stale_days=close_stale_days,
            actions=actions,
        ):
            eligible.append(pr)

    front_in_flight = False
    behind_candidates: list[PullRequestSnapshot] = []

    for pr in eligible:
        if pr.merge_state_status == "CLEAN":
            front_in_flight = True
            if not pr.auto_merge_enabled:
                actions.append(
                    LifecycleAction(
                        pr.number,
                        LifecycleActionKind.MERGE_CLEAN_NOW,
                        "PR is CLEAN and up-to-date with main; squash-merging immediately.",
                    )
                )
        else:
            if not pr.auto_merge_enabled and pr.merge_state_status in {
                "BLOCKED",
                "BEHIND",
                "UNSTABLE",
                "HAS_HOOKS",
                "UNKNOWN",
            }:
                actions.append(
                    LifecycleAction(
                        pr.number,
                        LifecycleActionKind.ENABLE_AUTO_MERGE,
                        "Enable verified squash auto-merge once required checks pass.",
                    )
                )

            if pr.merge_state_status == "BEHIND":
                behind_candidates.append(pr)
            elif pr.checks_pending:
                front_in_flight = True

    if behind_candidates and not front_in_flight:
        next_to_rebase = behind_candidates[0]
        if has_pat_token:
            actions.append(
                LifecycleAction(
                    next_to_rebase.number,
                    LifecycleActionKind.REBASE_BRANCH,
                    f"Serial FIFO rebase onto main for #{next_to_rebase.number} ({next_to_rebase.head_ref_name}).",
                )
            )
        else:
            actions.append(
                LifecycleAction(
                    next_to_rebase.number,
                    LifecycleActionKind.SKIP_REBASE_NO_PAT,
                    "Skipped automated rebase because PR_LIFECYCLE_TOKEN is not configured "
                    "(rebasing with GITHUB_TOKEN suppresses required pull_request & CodeQL checks).",
                )
            )

    return actions


def _parse_iso_utc(raw: str) -> datetime:
    cleaned = raw.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    parsed = datetime.fromisoformat(cleaned)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def parse_gh_pr_payload(item: dict[str, Any], default_repo: str) -> PullRequestSnapshot:
    """Convert a ``gh pr list --json`` entry into an immutable :class:`PullRequestSnapshot`."""
    rollup = item.get("statusCheckRollup") or []
    checks_pending = any(
        isinstance(chk, dict)
        and str(chk.get("status", "")).upper() in {"IN_PROGRESS", "QUEUED", "PENDING", "WAITING"}
        for chk in rollup
    )
    raw_labels = item.get("labels") or []
    labels = tuple(
        str(lbl["name"])
        for lbl in raw_labels
        if isinstance(lbl, dict) and str(lbl.get("name", "")).strip()
    )
    head_repo_obj = item.get("headRepository") or {}
    head_owner_obj = item.get("headRepositoryOwner") or {}
    owner_login = str(head_owner_obj.get("login", "")).strip()
    repo_name = str(head_repo_obj.get("name", "")).strip()
    head_full = f"{owner_login}/{repo_name}" if owner_login and repo_name else default_repo

    return PullRequestSnapshot(
        number=int(item["number"]),
        title=str(item.get("title", "")),
        is_draft=bool(item.get("isDraft", False)),
        mergeable=str(item.get("mergeable", "UNKNOWN")).upper(),
        merge_state_status=str(item.get("mergeStateStatus", "UNKNOWN")).upper(),
        auto_merge_enabled=item.get("autoMergeRequest") is not None,
        checks_pending=checks_pending,
        labels=labels,
        head_ref_name=str(item.get("headRefName", "")),
        head_repo_full_name=head_full,
        base_ref_name=str(item.get("baseRefName", "main")),
        created_at=_parse_iso_utc(str(item["createdAt"])),
        updated_at=_parse_iso_utc(str(item["updatedAt"])),
    )


class GhCliAdapter:
    """Production adapter executing GitHub CLI (``gh``) operations."""

    _LABEL_META: ClassVar[dict[str, tuple[str, str]]] = {
        CONFLICT_LABEL: ("d93f0b", "Pull request has merge conflicts with main"),
        INVALID_TITLE_LABEL: ("e4e669", "PR title must follow Conventional Commits"),
        STALE_LABEL: ("ededed", "No recent pull request activity"),
    }

    def _run_gh(self, *args: str) -> str:
        proc = subprocess.run(
            ["gh", *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout

    def list_open_prs(self, repo_full_name: str) -> list[PullRequestSnapshot]:
        fields = (
            "number,title,isDraft,mergeable,mergeStateStatus,autoMergeRequest,"
            "statusCheckRollup,labels,headRefName,headRepository,headRepositoryOwner,"
            "baseRefName,createdAt,updatedAt"
        )
        raw = self._run_gh(
            "pr",
            "list",
            "--repo",
            repo_full_name,
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            fields,
        )
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
        return [
            parse_gh_pr_payload(entry, repo_full_name) for entry in items if isinstance(entry, dict)
        ]

    def ensure_label_exists(self, repo_full_name: str, label: str, color: str, desc: str) -> None:
        self._run_gh(
            "label",
            "create",
            label,
            "--repo",
            repo_full_name,
            "--color",
            color,
            "--description",
            desc,
            "--force",
        )

    def add_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        color, desc = self._LABEL_META.get(label, ("cfd3d7", "Managed by nectR PR lifecycle"))
        self.ensure_label_exists(repo_full_name, label, color, desc)
        self._run_gh("pr", "edit", str(pr_number), "--repo", repo_full_name, "--add-label", label)

    def remove_label(self, repo_full_name: str, pr_number: int, label: str) -> None:
        self._run_gh(
            "pr", "edit", str(pr_number), "--repo", repo_full_name, "--remove-label", label
        )

    def post_idempotent_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        marker: str,
        body: str,
    ) -> None:
        raw = self._run_gh(
            "pr",
            "view",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--json",
            "comments",
        )
        data = json.loads(raw)
        comments = data.get("comments", []) if isinstance(data, dict) else []
        if any(isinstance(c, dict) and marker in str(c.get("body", "")) for c in comments):
            return
        self._run_gh("pr", "comment", str(pr_number), "--repo", repo_full_name, "--body", body)

    def enable_squash_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        self._run_gh(
            "pr",
            "merge",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--auto",
            "--squash",
        )

    def disable_auto_merge(self, repo_full_name: str, pr_number: int) -> None:
        self._run_gh(
            "pr",
            "merge",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--disable-auto",
        )

    def merge_clean_squash_now(self, repo_full_name: str, pr_number: int) -> None:
        self._run_gh(
            "pr",
            "merge",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--squash",
            "--delete-branch",
        )

    def rebase_branch(self, repo_full_name: str, pr_number: int) -> None:
        self._run_gh(
            "pr",
            "update-branch",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--rebase",
        )

    def close_pr(self, repo_full_name: str, pr_number: int, reason_comment: str) -> None:
        self._run_gh(
            "pr",
            "close",
            str(pr_number),
            "--repo",
            repo_full_name,
            "--comment",
            reason_comment,
        )


def execute_lifecycle_actions(
    actions: Sequence[LifecycleAction],
    *,
    port: PullRequestPort,
    repo_full_name: str,
    dry_run: bool = False,
) -> list[str]:
    """Execute planned :class:`LifecycleAction` items against ``port`` and return summary lines."""
    logs: list[str] = []
    for act in actions:
        prefix = "[DRY-RUN] " if dry_run else ""
        logs.append(f"{prefix}PR #{act.pr_number}: {act.kind} -> {act.detail.splitlines()[0]}")
        if dry_run:
            continue

        if act.kind == LifecycleActionKind.ADD_LABEL:
            port.add_label(repo_full_name, act.pr_number, act.detail)
        elif act.kind == LifecycleActionKind.REMOVE_LABEL:
            port.remove_label(repo_full_name, act.pr_number, act.detail)
        elif act.kind == LifecycleActionKind.POST_COMMENT:
            port.post_idempotent_comment(repo_full_name, act.pr_number, act.marker, act.detail)
        elif act.kind == LifecycleActionKind.ENABLE_AUTO_MERGE:
            port.enable_squash_auto_merge(repo_full_name, act.pr_number)
        elif act.kind == LifecycleActionKind.DISABLE_AUTO_MERGE:
            port.disable_auto_merge(repo_full_name, act.pr_number)
        elif act.kind == LifecycleActionKind.MERGE_CLEAN_NOW:
            port.merge_clean_squash_now(repo_full_name, act.pr_number)
        elif act.kind == LifecycleActionKind.REBASE_BRANCH:
            port.rebase_branch(repo_full_name, act.pr_number)
        elif act.kind == LifecycleActionKind.CLOSE_STALE:
            port.close_pr(repo_full_name, act.pr_number, act.detail)
        elif act.kind == LifecycleActionKind.SKIP_REBASE_NO_PAT:
            pass
    return logs


def _write_step_summary(lines: Sequence[str], *, has_pat_token: bool) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary_path:
        return
    body = ["## nectR PR Lifecycle Reconciliation", ""]
    if not has_pat_token:
        body.append(
            "> **Note:** Running with fallback `GITHUB_TOKEN`. Configure repository secret "
            "`PR_LIFECYCLE_TOKEN` (fine-grained PAT with `Contents: write`, `Pull requests: write`, "
            "`Workflows: write`) to enable autonomous remote `BEHIND` branch rebasing and check re-triggers."
        )
        body.append("")
    if lines:
        body.extend(f"- {ln}" for ln in lines)
    else:
        body.append("- All open pull requests are already reconciled; no actions required.")
    Path(summary_path).write_text("\n".join(body) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-pr-lifecycle",
        description="Validate PR merge safety and reconcile PR auto-merge, rebase queue, and stale lifecycle.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    title_cmd = sub.add_parser(
        "check-title", help="Validate a PR title against Conventional Commits."
    )
    title_cmd.add_argument("--title", required=True, help="Pull request title string.")

    branch_cmd = sub.add_parser(
        "check-branch",
        help="Verify Conventional Commit PR title, rebase-linear history, and clean merge-tree.",
    )
    branch_cmd.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Git repository root path.",
    )
    branch_cmd.add_argument(
        "--base",
        required=True,
        help="Base git ref (e.g. origin/main).",
    )
    branch_cmd.add_argument(
        "--title",
        default=None,
        help="Optional PR title to validate alongside branch history.",
    )

    rec_cmd = sub.add_parser(
        "reconcile",
        help="Reconcile auto-merge, serial FIFO rebase queue, conflicts, and stale PRs via gh CLI.",
    )
    rec_cmd.add_argument("--repo", required=True, help="GitHub owner/repo slug.")
    rec_cmd.add_argument(
        "--has-pat",
        action="store_true",
        help="Indicate PR_LIFECYCLE_TOKEN is active so remote rebases re-trigger CI & CodeQL.",
    )
    rec_cmd.add_argument(
        "--check-stale",
        action="store_true",
        help="Evaluate 14-day stale warning and 7-day stale closure rules.",
    )
    rec_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without mutating GitHub state.",
    )
    return parser


def main(argv: list[str] | None = None, *, port: PullRequestPort | None = None) -> int:
    """CLI entry point for ``nectr-pr-lifecycle``."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "check-title":
        valid, reason = validate_pr_title(str(args.title))
        if not valid:
            print(f"PR TITLE ERROR: {reason}", file=sys.stderr)
            return 1
        print("PR title is Conventional Commit compliant.")
        return 0

    if args.command == "check-branch":
        report = verify_branch_merge_safety(
            args.root.resolve(),
            base_ref=str(args.base),
            pr_title=args.title,
        )
        if not report.passed:
            for err in report.errors:
                print(f"PR MERGE-SAFETY ERROR: {err}", file=sys.stderr)
            return 1
        print(
            f"PR merge-safety gate passed against '{args.base}' "
            "(Conventional title, 0 merge commits, clean merge-tree)."
        )
        return 0

    adapter = port if port is not None else GhCliAdapter()
    prs = adapter.list_open_prs(str(args.repo))
    actions = plan_pr_lifecycle_actions(
        prs,
        repo_full_name=str(args.repo),
        now=datetime.now(UTC),
        has_pat_token=bool(args.has_pat),
        check_stale=bool(args.check_stale),
    )
    logs = execute_lifecycle_actions(
        actions,
        port=adapter,
        repo_full_name=str(args.repo),
        dry_run=bool(args.dry_run),
    )
    for line in logs:
        print(line)
    if not logs:
        print("No PR lifecycle actions needed.")
    _write_step_summary(logs, has_pat_token=bool(args.has_pat))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
