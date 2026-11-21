# ADR-001: Automated Changelog & Release Roadmapping Tooling

- **Status:** Accepted
- **Date:** 2026-11-21
- **Decision Makers:** nectR Architecture & Governance
- **Related Rules & Specs:**
  - `.agents/rules/open-source-first-and-license-audit.md`
  - `.agents/skills/atomic-conventional-commits/SKILL.md`
  - `.github/workflows/roadmap-and-changelog.yml`

---

## Context

**nectR** is a public, open-source monorepo with strict Conventional Commits enforcement (`.githooks/commit-msg`), multi-agent concurrency, and an academic/system-design portfolio (`docs/`, `mkdocs.yml`). We need a reliable, low-maintenance way to produce accurate release changelogs and release milestones without manual drift or reinventing existing open-source tooling.

---

## Options Considered

### Option 1: Do Nothing (No Tooling / Purely Manual Human Process)
- **Description:** Contributors or maintainers manually edit `CHANGELOG.md` and release notes by hand before each release.
- **Pros:** Zero tooling or dependency footprint.
- **Cons:** High drift and omission risk in a fast-moving multi-agent repo; merges frequently conflict on a single `CHANGELOG.md`; no machine-readable tie between Conventional Commits, PEP 621 version bumps in `pyproject.toml`, and release notes.
- **Verdict:** Rejected.

### Option 2: `commitizen` (Chosen)
- **Description:** MIT-licensed Python CLI (`cz check`, `cz changelog`, `cz bump`) configured in `pyproject.toml` (`[tool.commitizen]`, `version_provider = "pep621"`, `update_changelog_on_bump = true`).
- **License & Transitive Audit:** `MIT` (all transitive dependencies `MIT`, `BSD-*`, `Apache-2.0`, `PSF-2.0` — audited and permitted).
- **Pros:**
  - Single tool handles **both** commit-message validation (`.githooks/commit-msg`) and changelog/version generation (`cz changelog`, `cz bump`).
  - Native Python ecosystem fit (`pyproject.toml` PEP 621 version provider), zero extra runtime binaries (no Rust/Node toolchain required).
  - Eliminates manual `CHANGELOG.md` edits and works identically locally and in `.github/workflows/roadmap-and-changelog.yml`.
- **Cons:** Requires strict adherence to Conventional Commits (which we already enforce).
- **Verdict:** **Accepted.**

### Option 3: `towncrier`
- **Description:** MIT-licensed Python tool where each PR adds a small news-fragment file under `changelog.d/<issue>.<type>.md`, and `towncrier build` assembles them at release time.
- **License:** `MIT`.
- **Pros:** Great for human-curated narrative release notes and avoiding merge conflicts on `CHANGELOG.md` in large teams.
- **Cons:** Requires creating and committing an extra fragment file for every atomic commit/PR, adding friction to the OpenSpec → BDD → TDD Red-Green-Refactor commit cadence when Conventional Commits already capture structured change types.
- **Verdict:** Rejected (overkill given Conventional Commits).

### Option 4: `git-cliff`
- **Description:** Fast Rust CLI (`MIT` / `Apache-2.0`) that parses `git log` using Tera templates to generate `CHANGELOG.md` from Conventional Commits.
- **License:** `MIT` / `Apache-2.0`.
- **Pros:** Very fast, highly customizable Tera templates, supports monorepo filtering.
- **Cons:** Introduces a separate non-Python binary dependency (`git-cliff`) alongside `commitizen`, which is already installed and required for `cz check` in `.githooks/commit-msg`.
- **Verdict:** Rejected (unnecessary second tool when `commitizen` already provides `cz changelog`).

### Option 5: `release-please`
- **Description:** Apache-2.0 GitHub Action by Google that maintains an automated "Release PR" on GitHub, updating `CHANGELOG.md` and `pyproject.toml` versions from Conventional Commits.
- **License:** `Apache-2.0`.
- **Pros:** Zero local CLI needed; automates GitHub Releases and tags via PRs.
- **Cons:** Tightly coupled to GitHub PRs and Actions; does not provide a local `commit-msg` hook validator (`cz check`) for offline/pre-commit enforcement.
- **Verdict:** Rejected as primary tool (can be reconsidered later if automated GitHub Release PRs are desired).

### Option 6: Custom Python Changelog Script
- **Description:** Writing a bespoke `git log` parser and Markdown formatter in `scripts/`.
- **Pros:** Full control over output format.
- **Cons:** Violates `.agents/rules/open-source-first-and-license-audit.md` ("never rebuild or custom when a secure, well-respected open-source licensed solution exists") and creates unnecessary maintenance burden.
- **Verdict:** Rejected.

---

## Consequences

1. **`commitizen`** is the single source of truth for Conventional Commit validation (`.githooks/commit-msg`), PEP 621 version bumping, and automated changelog generation (`cz changelog`).
2. Active feature/milestone roadmapping remains in **OpenSpec** (`openspec/specs/`, `openspec/changes/*/tasks.md`) and GitHub Milestones, surfaced automatically by `.github/workflows/roadmap-and-changelog.yml`.
3. Any future switch (e.g., to `towncrier` or `git-cliff`) requires superseding this ADR.
