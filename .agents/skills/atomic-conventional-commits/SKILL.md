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

1. **Stage Explicitly:** Run `git add <file1> <file2>` for only the files you created or modified. Never use `git add .` or `git commit -a`.
2. **Check Commit Readiness:** Run the cross-platform readiness script [verify_commit_readiness.py](./scripts/verify_commit_readiness.py):
   ```bash
   uv run python .agents/skills/atomic-conventional-commits/scripts/verify_commit_readiness.py
   ```
3. **Format Message:** Follow the `<type>(<scope>): <imperative summary>` rules and Red-Green-Refactor sequencing in [commit_conventions.md](./references/commit_conventions.md).
4. **Commit with Hooks & SSH Signing:** Run `git commit -m "<type>(<scope>): <summary>"`. Never pass `--no-verify`.

## Validation

- Confirm `verify_commit_readiness.py` exits `0` (verifying `core.hooksPath == .githooks`, `commit.gpgsign == true`, `gpg.format == ssh`, and no untracked cache artifacts).
- If validating a message directly, pass `--message "<type>(<scope>): <summary>"` and confirm `cz check` exits `0`.
