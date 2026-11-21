Feature: Dual-Track Decision Governance (pyadr MADR and Fast Decision Registry)
  As a nectR maintainer and multi-agent orchestrator
  I want architectural decisions managed separately by pyadr with strict verbosity limits and non-architectural decisions managed by a schema-validated YAML registry
  So that ADRs stay concise and verifiable while fast decisions never drift from code controls

  @red
  Scenario: Repository MADR records pass pyadr validation and verbosity limits
    Given the repository root decision governance workspace
    When the full decision and ADR governance check runs
    Then validation succeeds with at least 8 accepted MADR records and an in-sync ADR index

  @red
  Scenario: Verbose MADR record exceeding line or word limits is rejected
    Given a temporary ADR directory containing a verbose MADR record of 85 lines
    When the ADR verbosity validator inspects the temporary ADR directory
    Then governance validation fails with "exceeds max line limit"

  @red
  Scenario: Manual drift in rendered non-architectural decision_log.md is rejected
    Given a temporary copy of the fast decision registry and rendered decision log
    When manual text drift is injected into the rendered decision_log.md
    Then governance validation fails with "out of sync with decisions.yaml"
