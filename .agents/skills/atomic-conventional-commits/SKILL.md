---
name: atomic-conventional-commits
description: Enforces atomic, SSH-signed Conventional Commits with strict file isolation and Red-Green-Refactor commit sequencing.
---

# Atomic Conventional Commits Skill

## 1. Non-Negotiable Commit Rules
- **NEVER** run `git add .` or `git commit -a`. Always stage only the explicit files you created or modified (`git add <file1> <file2>`).
- **NEVER** use `--no-verify`. All `.githooks/` (`pre-commit`, `commit-msg`, `pre-push`) must execute and pass.
- **Mandatory SSH Signing:** Ensure commits are signed (`commit.gpgsign=true`, `gpg.format=ssh`).
- **Conventional Commits Format** (enforced by `.githooks/commit-msg` via `commitizen` `cz check`):
  `<type>(<scope>): <imperative summary>` (<= 100 chars)
  - Allowed `<type>`: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

## 2. Atomic Commit Grouping
Split unrelated changes into separate, focused commits:
- `chore(security): ...` — security scanner, `.gitignore`, `.githooks/`, `.pre-commit-config.yaml`
- `docs(spec): ...` — `openspec/` specs and proposals
- `test(bdd): ...` — `features/` Gherkin scenarios and `tests/` RED tests
- `feat(<domain>): ...` — minimal GREEN implementation
- `refactor(<domain>): ...` — cleanup keeping tests 100% green
- `chore(agents): ...` — `.agents/` rules, skills, and `AGENTS.md`
