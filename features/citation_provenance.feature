Feature: Citation Validation and Provenance Chain-of-Custody
  As a nectR scientific author and maintainer
  I want citations strictly vetted against quality floors and linked through a directed provenance graph
  So that hallucinated or plagiarized sources are caught and impacted downstream reports regenerate automatically

  @red
  Scenario: Reference registry rejects banned domains and insufficient peer-reviewed ratio
    Given a temporary citation registry containing a banned wiki URL
    When the citation quality validator checks the temporary registry
    Then citation validation fails with "banned domain"

  @red
  Scenario: Tainted upstream reference propagates downstream rebuild warning across lineage graph
    Given a temporary lineage workspace where source "bad_ref" has failed plagiarism screening
    When the provenance renderer rebuilds the lineage report with allow-quarantined
    Then the rendered provenance report flags downstream theory, ADR, and code artifacts for rebuild

  @red
  Scenario: Repository citation registry and provenance lineage report pass checks in sync
    Given the repository root citation and lineage workspace
    When the full citation and provenance check runs
    Then citation validation succeeds with peer-reviewed ratio at least 0.70 and report in sync
