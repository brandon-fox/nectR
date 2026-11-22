Feature: Dual-Track Decision Governance (adrlint MADR 4.0 and Fast Decision Registry)
  As a nectR maintainer and multi-agent orchestrator
  I want architectural decisions managed separately by OSS adrlint with strict verbosity limits and non-architectural decisions managed by a schema-validated YAML registry
  So that ADRs stay concise, immutability-locked, and verifiable while fast decisions never drift from code controls

  Scenario: Repository MADR records pass adrlint validation, lock check, and verbosity limits
    Given the repository root decision governance workspace
    When the full decision and ADR governance check runs
    Then validation succeeds with at least 8 accepted MADR records and an in-sync ADR index

  Scenario: Verbose MADR record exceeding line or word limits is rejected
    Given a temporary ADR directory containing a verbose MADR record of 85 lines
    When the ADR verbosity validator inspects the temporary ADR directory
    Then governance validation fails with "exceeds max line limit"

  Scenario: Manual drift in rendered non-architectural decision_log.md is rejected
    Given a temporary copy of the fast decision registry and rendered decision log
    When manual text drift is injected into the rendered decision_log.md
    Then governance validation fails with "out of sync with decisions.yaml"

  Scenario: OSS adrlint replaces bespoke ADR module and enforces lock and proposed gating
    Given a temporary MADR 4.0 workspace configured with adrlint
    When a proposed ADR is created with adrlint new and checked before and after acceptance
    Then bespoke adr.py is absent and strict check rejects proposed until accepted and locked

  Scenario: Decision registry and Milestone 3 roadmap define n8n off-chain boundaries and options
    Given the repository root decision governance workspace
    When the n8n workflow governance and Milestone 3 roadmap checks inspect decisions and ADR records
    Then DEC-009 clarifies CrewAI/n8n while remaining locked to Mesa ABM
    And DEC-016 and EXP-006 enforce an off-chain n8n boundary with permissive OSS roadmap options
    And an accepted locked MADR record documents the external workflow automation scope

  @red
  Scenario: Vyper py-evm chain contracts, PactFlow API contracts, micro_nectr math, and JASSS ODD+D framing are locked
    Given the repository root decision governance workspace
    When the Vyper py-evm, PactFlow, and JASSS ODD+D governance checks inspect ADRs, decisions, and OpenSpec proposals
    Then ADR-0017 and ADR-0018 are accepted and locked for Vyper py-evm and PactFlow bi-directional contracts
    And DEC-017 through DEC-020 lock micro_nectr integer math, direct bps learner attestations, layered secp256k1 signing, and JASSS ODD+D framing
    And OpenSpec proposals exist for Vyper py-evm migration and PactFlow contract governance
