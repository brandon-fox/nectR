---
trigger: always_on
---

# Mandatory Security, Privacy & Open-Source Hygiene Gate

**nectR** is a public, open-source repository. Zero secrets, private references, or personal local build paths may ever enter the workspace, git history, or agent context.

## 1. Pre-Read & Pre-Edit Gate (Before Any Agent Action)
- **Before reading or editing** any unfamiliar or newly introduced file, run:
  `detect-secrets-hook --baseline .secrets.baseline <relative-file-path>`
- **Before committing or pushing**, verify with OSS tooling:
  - `detect-secrets scan` / `detect-secrets-hook --baseline .secrets.baseline`
  - `pip-licenses` & `pip-audit` for dependency license & CVE compliance
- Never hardcode:
  - User-specific home paths (Windows user profile paths, macOS user paths, Linux home paths)
  - Local drive-letter build paths or local AI agent configuration directories
  - API keys, tokens, private keys, `.env` values, or personal emails/hostnames.
- Always use repository-relative paths, `Path(__file__).resolve()`, or environment variables documented in `.env.example`.

## 2. Pre-Commit & Pre-Push Enforcement (Git Hooks)
- Git hooks are versioned in `.githooks/` (`core.hooksPath = .githooks`) and mirrored in `.pre-commit-config.yaml` using `detect-secrets`, `commitizen`, and `pygrep`.
- **NEVER** use `--no-verify` on `git commit` or `git push`.
- If any hook reports a violation, halt immediately, remediate the leak or local path, and re-run until exit code `0`.

## 3. GitHub Actions Immutable Commit SHA Pinning (Mandatory)
- Every `uses:` reference to a third-party or official GitHub Action in `.github/workflows/*.yml` **MUST** be pinned to a full 40-character hexadecimal commit SHA (`uses: owner/repo@<40-hex-sha> # vX.Y.Z`), **never** a mutable version tag (`@v7`, `@v10.4.0`, `@main`).
- Always include an inline `# vX.Y.Z` comment after the SHA so Dependabot (`github-actions` ecosystem) and reviewers can track the resolved release tag.
- Enforced programmatically by `nectr.devtools.ci_parity` in pre-commit and CI.
