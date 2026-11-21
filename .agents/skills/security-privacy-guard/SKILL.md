---
name: security-privacy-guard
description: >-
  Enforces zero-leak open-source hygiene using detect-secrets, pygrep,
  pip-licenses, pip-audit, and .githooks. Use before reading unfamiliar files,
  before committing, before pushing, or when auditing dependencies.
---

# Security & Privacy Guard

Keep `nectR` free of leaked secrets, hardcoded local paths, prohibited dependency licenses, and CVEs.

## Steps

1. **Review Policy:** Consult [license_and_secret_policy.md](./references/license_and_secret_policy.md) for allowed/prohibited licenses and local-path rules.
2. **Run Security Audit:** Execute [run_security_audit.py](./scripts/run_security_audit.py) in the appropriate mode:
   - Pre-read single file:
     ```bash
     uv run python .agents/skills/security-privacy-guard/scripts/run_security_audit.py --mode pre-read --files <relative-path>
     ```
   - Pre-commit / full audit:
     ```bash
     uv run python .agents/skills/security-privacy-guard/scripts/run_security_audit.py --mode full
     ```

## Validation

- Confirm `run_security_audit.py` exits `0` (`core.hooksPath == .githooks`, `detect-secrets`, `pre-commit`, and dependency checks pass).
