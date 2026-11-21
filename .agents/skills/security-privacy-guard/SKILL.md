---
name: security-privacy-guard
description: Enforces zero-leak open-source hygiene before agent reads, edits, commits, and pushes using scripts/security_scan.py and .githooks.
---

# Security & Privacy Guard Skill

Use this skill before reading untrusted/new files, before committing, and before pushing to ensure no secrets, private references, or personal local build paths exist in `nectR`.

## Commands
- **Pre-Read / Single-File Check:** `python scripts/security_scan.py --path <file>`
- **Pre-Commit (Staged Files):** `python scripts/security_scan.py --staged`
- **Pre-Push (All Tracked/Staged):** `python scripts/security_scan.py --push`
- **Full Workspace Audit:** `python scripts/security_scan.py --all`

## Hook Setup Verification
Ensure git is configured to use the versioned hooks directory:
```powershell
git config --local core.hooksPath .githooks
```
Verify `.githooks/pre-commit` and `.githooks/pre-push` are active and never bypassed (`--no-verify` is strictly forbidden).
