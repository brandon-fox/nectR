Feature: Isolated Worktrees and Tiered Mutation Testing Gate
  As a nectR maintainer coordinating concurrent agents
  I want ephemeral Git worktrees isolated from repo scans and an incremental tiered mutation gate
  So that parallel branches never collide and changed code meets strict invariant test strength

  @red
  Scenario: Worktree directory is excluded from git, ruff, pytest, detect-secrets, and tree sync
    Given the repository root workspace
    When I inspect the worktree ignore and tool exclusion rules
    Then ".worktrees" is excluded across gitignore, ruff, pytest, detect-secrets, and docs tree rendering

  @red
  Scenario: Worktrunk project config provisions isolated environments and enforces merge gates
    Given the Worktrunk project configuration in ".config/wt.toml"
    When I parse the Worktrunk lifecycle hooks
    Then ordered pre-start hooks run isolated uv sync and commit readiness checks
    And ordered pre-merge hooks run the diff mutation gate and orchestration verification gate

  @red
  Scenario: Inline mutation suppression pragmas in src are rejected
    Given a temporary source directory containing a file with an inline mutation suppression pragma
    When the mutation pragma scanner inspects the temporary source directory
    Then pragma validation fails listing the offending file and line

  @red
  Scenario: A Tier-1 change whose changed-line mutants score below 85% fails the diff gate
    Given a Tier-1 module diff affecting lines 10 to 20 and engine trials scoring 50.0% on changed lines
    When the diff-scoped mutation gate evaluates the changed-line trials
    Then the mutation gate fails for tier "src/nectr/contracts" below target 85.0%

  @red
  Scenario: A full sweep below a committed baseline floor fails, and at or above the floor passes
    Given committed baseline floors of 55% for "src/nectr/contracts" and 65% for "src/nectr/chain"
    When the full-sweep mutation gate evaluates scores of 54.0% and 66.0%
    Then the full-sweep gate fails for tier "src/nectr/contracts" below baseline floor 55.0%
    When the full-sweep mutation gate evaluates scores of 55.0% and 66.0%
    Then the full-sweep gate passes all baseline floors

  @red
  Scenario: Changes outside tiered source contexts pass with no tiered source changes
    Given changed files restricted to "src/nectr/personas/simulator.py" and "src/nectr/ui/app.py"
    When the mutation gate classifies target files across bounded-context tiers
    Then zero tiered targets are selected and the gate reports "no tiered source changes"
