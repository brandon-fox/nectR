# Use Commitizen for Automated Changelogs and Releases

* Status: accepted
* Deciders: nectR Architecture & Governance
* Date: 2026-11-21

## Context and Problem Statement

The monorepo enforces Conventional Commits across concurrent Domain Builder Agents and needs zero-drift changelog generation and PEP 621 version bumping without introducing redundant non-Python binaries or custom scripts.

## Considered Options

* **Commitizen (`cz check`, `cz changelog`, `cz bump` with PEP 621 provider)**
* **Manual `CHANGELOG.md` human editing**
* **`towncrier` fragment files per PR**
* **`git-cliff` external Rust binary**
* **`release-please` GitHub-only PR automation**
* **Custom Python `git log` parser script**

## Decision Outcome

Chosen option: "Commitizen", because it is MIT-licensed, native to Python (`pyproject.toml`), and unifies offline `.githooks/commit-msg` validation (`cz check`) with automated changelog and PEP 621 version bumps in a single dependency.

### Consequences

* Good, because commit validation and release note generation share one single source of truth locally and in GitHub Actions.
* Good, because it avoids merge-conflict fragments (`towncrier`), extra Rust binaries (`git-cliff`), and custom script maintenance.
* Bad, because every commit must strictly obey Conventional Commits syntax.
