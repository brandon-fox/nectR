Feature: Living Documentation, Domain Glossary, Persona Extras, and Repo Hygiene
  As a nectR contributor across any IDE or CLI workflow
  I want defined terminology, IDE-agnostic docs, synced navigation, LF normalization, and persona dependency splits
  So that onboarding, CI checks, and multi-agent commits remain reliable

  Scenario: Repository glossary and README define core terms without IDE lock-in
    Given the repository documentation root
    When the onboarding and glossary validator inspects README and glossary
    Then docs/glossary.md defines MV=PQ and PoUW-PoW and README contains no IDE lock-in

  Scenario: Docs synchronization passes with zero orphaned docs pages and synced README spaces
    Given the repository documentation root
    When the docs synchronization validator checks README and mkdocs.yml
    Then docs validation succeeds with zero orphaned pages and synced ADR navigation

  Scenario: Repository git tracking, LF attributes, and persona extras conform to hygiene policy
    Given the repository root configuration
    When git tracking, .gitattributes, and pyproject.toml extras are inspected
    Then HANDOFF.md is untracked, LF normalization is configured, and persona extras exist

  Scenario: Agent operating rules enforce structure freeze until v0.1.0 and orchestration banner
    Given the repository documentation root
    When the documentation freeze validator inspects AGENTS.md and agent_orchestration.md
    Then AGENTS.md enforces the structure freeze and agent_orchestration.md displays the superseded banner
