---
name: atomic-conventional-commits
description: >-
  Enforces atomic, SSH-signed Conventional Commits with strict file isolation
  and Red-Green-Refactor commit sequencing. Use when staging files, writing
  commit messages, or verifying SSH-signed commits in nectR.
---

# Atomic Conventional Commits

Follow this workflow whenever preparing or verifying commits in `nectR`.

## Steps

1. **Stay Inside Your Isolated Worktree (`ADR-0019`):** Work inside `.worktrees/<branch-slug>/` (via `git-wt`) or your harness shared worktree; keep `.poodle-temp/` and `mutation-report*.json` untracked/ignored.
2. **Stage Explicitly:** Run `git add <file1> <file2>` for only the files you created or modified. Never use `git add .` or `git commit -a`.
3. **Check Commit Readiness:** Run the cross-platform readiness script [verify_commit_readiness.py](./scripts/verify_commit_readiness.py):

   ```bash
   uv run python .agents/skills/atomic-conventional-commits/scripts/verify_commit_readiness.py
   ```

4. **Format Message & Commit:** Follow `<type>(<scope>): <imperative summary>` and Red-Green-Refactor sequencing in [commit_conventions.md](./references/commit_conventions.md), and run `uv run git commit -m "<type>(<scope>): <summary>"` (never `--no-verify`; `pre-commit` bans `src/` mutation pragmas via `mutation_gate check-pragmas`, and `pre-push` / `git-wt merge main --no-squash` enforce `mutation_gate diff`, `ADR-0020`, `DEC-021`).

## Validation

- Confirm `verify_commit_readiness.py` and `git verify-commit HEAD` exit `0` (verifying `core.hooksPath == .githooks`, `commit.gpgsign == true`, `gpg.format == ssh`, and no untracked cache artifacts).
- If validating a message directly, pass `--message "<type>(<scope>): <summary>"` and confirm `cz check` exits `0`.
