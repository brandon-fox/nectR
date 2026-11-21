---
name: security-privacy-guard
description: Enforces zero-leak open-source hygiene before agent reads, edits, commits, and pushes using detect-secrets, pygrep, pip-licenses, and .githooks.
---

# Security & Privacy Guard Skill

Use established open-source tools before reading untrusted/new files, before committing, and before pushing to ensure no secrets, private references, or personal local build paths exist in `nectR`.

## Commands
- **Pre-Read / Single-File Secret Check:** `detect-secrets-hook --baseline .secrets.baseline <file>`
- **Full Workspace Secret Scan:** `detect-secrets scan --exclude-files '(\.git|\.venv|\.pytest_cache|__pycache__)'`
- **Pre-Commit All-Hooks Check:** `pre-commit run --all-files`
- **Transitive License & CVE Audit:** `pip-licenses` and `pip-audit`

## Hook Setup Verification
Ensure git is configured to use the versioned hooks directory:
```powershell
git config --local core.hooksPath .githooks
```
Verify `.githooks/pre-commit`, `.githooks/commit-msg`, and `.githooks/pre-push` are active and never bypassed (`--no-verify` is strictly forbidden).
