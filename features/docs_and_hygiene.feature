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

  Scenario: README documents plain-language intro, status, personal-capacity notice, and license
    Given the repository documentation root
    When the README transparency validator inspects README and LICENSE
    Then README has a status line within ten lines and an Independence section and license link

  Scenario: OpenSpec change proposals enforce archiving of merged work and deferral notice for out-of-scope waves
    Given the repository documentation root
    When the OpenSpec lifecycle validator inspects active, archived, and deferred proposals
    Then merged proposals are archived and out-of-scope proposals carry a deferral notice

  Scenario: Architecture decision records treat the chain as a signed audit log superseding PoW consensus
    Given the repository documentation root
    When the ADR and audit log wording validator inspects ADR records, README, architecture, theory, and glossary
    Then ADR-0019 is accepted superseding ADR-0007 and consensus wording describes the signed audit log

  Scenario: Documentation labels unsourced figures as assumptions and smoke scenarios as non-experimental
    Given the repository documentation root
    When the assumption and smoke scenario validator inspects institutional proposal and tokenomics game theory
    Then institutional proposal labels fill rates and ROI inputs as assumptions and tokenomics game theory retitles smoke scenario output

  Scenario: Documentation labels AI-generated research reports and the honeybee design metaphor
    Given the repository documentation root
    When the AI research and metaphor validator inspects research reports, README, biomimicry model, and tokenomics
    Then all deep research reports carry an AI-generated notice and bee terminology is labeled as a design metaphor

  Scenario: Documentation separates long-term product vision from the active Plan to B+ roadmap
    Given the repository documentation root
    When the roadmap and vision validator inspects roadmap.md, vision.md, and mkdocs.yml
    Then vision.md documents the three-horizon product vision and roadmap.md details the Plan to B+

  Scenario: Roadmap accurately reflects Plan to B+ workstreams and landed status
    Given the repository documentation root
    When the roadmap and vision validator inspects roadmap.md, vision.md, and mkdocs.yml
    Then roadmap.md accurately details all Plan to B+ workstream deliverables and unmerged hold statuses

  Scenario: README documents Quick Start guide with nectr simulate and serve commands
    Given the repository documentation root
    When the README quick start validator inspects README.md
    Then README contains quick start instructions for nectr simulate and nectr serve
