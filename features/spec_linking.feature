Feature: OpenSpec-to-Feature Single Source of Truth Linking
  As a nectR maintainer
  I want OpenSpec spec.md files to link to Behave feature files instead of hardcoding scenarios
  So that user stories and acceptance steps never drift from executable BDD tests

  Scenario: Spec with hardcoded Given/When/Then scenario is rejected
    Given a temporary workspace with a spec containing a hardcoded Given/When/Then scenario
    When the OpenSpec feature-link validator runs on the temporary workspace
    Then spec-link validation fails with "hardcoded scenario"

  Scenario: Spec without feature or step links is rejected
    Given a temporary workspace with a spec missing feature and step links
    When the OpenSpec feature-link validator runs on the temporary workspace
    Then spec-link validation fails with "missing linked"

  Scenario: Repository OpenSpec files pass spec-to-feature link validation
    Given the repository root OpenSpec workspace
    When the OpenSpec feature-link validator runs on the repository root
    Then all OpenSpec spec.md files pass link validation
