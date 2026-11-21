# Conventional Commits & Atomic Isolation Reference

## 1. Non-Negotiable Rules
- **Atomic Staging:** Only `git add <explicit-file-list>`. Never `git add .` or `git commit -a`.
- **Hooks Active:** `.githooks/pre-commit`, `.githooks/commit-msg`, and `.githooks/pre-push` must run cleanly (`--no-verify` is forbidden).
- **SSH Signing:** `commit.gpgsign=true` and `gpg.format=ssh` must be enabled.

## 2. Conventional Commits Format
`<type>(<scope>): <imperative summary>` (`<= 100` chars), enforced by `cz check`.

- **Allowed `<type>`:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- **Recommended `<scope>` groupings:**
  - `chore(security): ...` — security scanner, `.gitignore`, `.githooks/`, `.pre-commit-config.yaml`
  - `docs(spec): ...` — `openspec/` specs and proposals
  - `test(bdd): ...` — `features/` Gherkin scenarios and `tests/` RED tests
  - `feat(<domain>): ...` — minimal GREEN implementation
  - `refactor(<domain>): ...` — cleanup keeping tests 100% green
  - `chore(agents): ...` — `.agents/` rules, skills, and `AGENTS.md`
