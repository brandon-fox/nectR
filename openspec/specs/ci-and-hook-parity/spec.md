# Specification: End-to-End Hook, `pre-commit.ci`, CI Matrix & Release Parity (`ci-and-hook-parity`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature)
- **Step Definitions:** [features/steps/ci_and_hook_parity_steps.py](../../../features/steps/ci_and_hook_parity_steps.py)

## Requirements

### Requirement: Cross-Platform Local Hook & Pre-Commit Parity with CI
`.githooks/pre-commit`, `.githooks/pre-push`, `.githooks/commit-msg`, and `.pre-commit-config.yaml` SHALL resolve `.venv` executables across Windows Git Bash (`cygpath -u`) and POSIX without manual activation, scan staged files null-delimited (`-z`) against the git index (`--cached`), and mirror every security, governance, lint, format, type, documentation (`mkdocs build --strict`), and test gate enforced in `.github/workflows/`.
- **Linked Scenario:** `Local git hooks and pre-commit config maintain gate parity with GitHub Actions workflows` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L6-L9)

### Requirement: Deterministic `uv.lock` Full-Extra Installs & Multi-OS/Python Matrix
GitHub Actions CI SHALL install dependencies deterministically from `uv.lock` via `astral-sh/setup-uv` (`uv sync --frozen --extra dev --extra research`) so `pip-licenses` and `pip-audit` audit all runtime, dev, and research packages, and SHALL execute unit and BDD suites across Python `3.11`, `3.12`, and `3.13` on `ubuntu-latest` plus `windows-latest`.
- **Linked Scenario:** `CI matrix enforces deterministic uv.lock installs across Python versions, OS runners, and research extras` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L11-L14)

### Requirement: Main-Branch `@red` Merge Guard & 80% Coverage Floor
Pull requests and pushes targeting `main` SHALL fail if any `.feature` file retains an unimplemented `@red` scenario tag and SHALL enforce `--cov=src/nectr --cov-report=xml:coverage.xml --cov-fail-under=80` to satisfy GitHub Ruleset `27810615`.
- **Linked Scenario:** `Main-branch merge guard rejects unimplemented @red BDD scenarios and enforces 80 percent coverage floor` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L16-L19)

### Requirement: Scheduled Baseline Drift, Permissive SPDX Allowlist & Tagged Releases
Scheduled daily (`06:00 UTC`) workflows SHALL verify `.secrets.baseline` drift alongside CVE/license audits, PR dependency reviews SHALL enforce an explicit MIT-compatible SPDX `allow-licenses` list, and `release.yml` SHALL automate Commitizen versioned changelogs and GitHub Releases on version tags.
- **Linked Scenario:** `Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L21-L24)

### Requirement: Node 24 Action Runtimes, Isolated `setup-uv` Caches & Clean Workspace Link/Docs Steps
All `.github/workflows/*.yml` files SHALL pin Node 24-compatible action versions (`astral-sh/setup-uv@v10.4.0`, `softprops/action-gh-release@v3`), assign distinct `cache-suffix` values per job, direct `lychee-action@v2` output to `${{ runner.temp }}/lychee-out.md` while excluding `openspec/changes/archive/` and `docs/theory/research/`, and set `NO_MKDOCS_2_WARNING: "1"` for `mkdocs build --strict`.
- **Linked Scenario:** `GitHub Actions workflows enforce Node 24 runtimes, isolated uv caches, clean lychee temp outputs, and SPDX allow-list review` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L26-L29)

### Requirement: `pre-commit.ci` Cloud Bot Split Execution & Conventional Commit Policy
`.pre-commit-config.yaml` SHALL exclude `.worktrees` and `.poodle-temp`, configure `ci:` with Conventional Commit `autofix_commit_msg` and `autoupdate_commit_msg`, weekly `chore/pre-commit-autoupdate` updates, `submodules: false`, pinned MIT/Apache-2.0 remote hook repositories, and an exact `ci.skip` set covering all `repo: local` `language: system` hooks while keeping cloud-capable remote and `pygrep` hooks active.
- **Linked Scenario:** `pre-commit.ci bot configuration enforces Conventional Commit autofixes, weekly autoupdates, and system-hook skips` in [ci_and_hook_parity.feature](../../../features/ci_and_hook_parity.feature#L31-L35)
