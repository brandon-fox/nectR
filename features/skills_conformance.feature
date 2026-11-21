Feature: Custom Agent Skills Conformance & Strict Typing
  As a nectR maintainer
  I want all custom Antigravity skills under .agents/skills/ to conform to the shared skill spec
  So that skill metadata, scripts, references, and local-path hygiene remain consistent

  Scenario: All custom skills pass structure, link, and local-path checks
    Given the repository custom skills workspace
    When the skill conformance validator runs on ".agents/skills"
    Then all 7 custom skills pass validation with zero local paths
