Feature: End-to-End Hook, CI Pipeline, Scheduled Audit, and Release Parity
  As a nectR maintainer and multi-agent contributor across Windows and POSIX
  I want local git hooks, pre-commit config, GitHub Actions workflows, scheduled security scans, and main-branch protections to stay in lockstep
  So that regressions, unapproved transitive licenses, @red leaks, and coverage drops are caught deterministically before merge

  Scenario: Local git hooks and pre-commit config maintain gate parity with GitHub Actions workflows
    Given the repository root hook, pre-commit, and GitHub Actions workflow definitions
    When the CI and hook parity validator inspects local and remote pipeline stages
    Then every local security, governance, lint, format, type, docs, and test gate is mirrored in CI with cross-platform venv PATH resolution

  Scenario: CI matrix enforces deterministic uv.lock installs across Python versions, OS runners, and research extras
    Given the repository pyproject.toml, uv.lock, and GitHub Actions CI workflow
    When the CI matrix and dependency audit configuration is validated
    Then CI installs locked dev and research extras via uv and runs tests across Python 3.11 to 3.13 on Linux and Windows

  Scenario: Main-branch merge guard rejects unimplemented @red BDD scenarios and enforces 80 percent coverage floor
    Given a simulated main-branch CI check with an active @red feature scenario
    When the main-branch readiness gate evaluates BDD tags and pytest coverage configuration
    Then validation fails on lingering @red scenarios and requires at least 80 percent XML-reported test coverage

  Scenario: Scheduled security scan and release workflow enforce baseline drift, schema validation, and tagged changelogs
    Given the scheduled security scan, PR policy, and release workflow configurations
    When scheduled cron, JSON Schema, link-check, and Commitizen release steps are inspected
    Then daily cron verifies secrets baseline drift, decisions.yaml schema, expanded SPDX deny-licenses, lychee links, and tagged release automation

  @red
  Scenario: GitHub Actions workflows enforce Node 24 runtimes, isolated uv caches, clean lychee temp outputs, and SPDX allow-list review
    Given all GitHub Actions workflow definitions under .github/workflows
    When the CI workflow runtime and action hygiene validator inspects all workflow files
    Then workflows require Node 24 action versions, isolated setup-uv cache suffixes, permissive SPDX allow-licenses with action license exclusions, clean lychee temp output, and quiet MkDocs logs
