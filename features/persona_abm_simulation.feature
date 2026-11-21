Feature: Mesa ABM Persona Simulation & Hypothesis Invariant Fuzzing
  As a nectR behavioral economy researcher
  I want persona simulations orchestrated via Mesa with DataCollector telemetry and Hypothesis property-based contract fuzzing
  So that empirical Gini, velocity, and collusion-decay metrics are reproducible and contract invariants hold over arbitrary sequences

  @red
  Scenario: Seeded Mesa multi-hive simulation reproduces deterministic telemetry
    Given a seeded Mesa HiveModel with the 6 Behavioral Persona Sub-Agents
    When the simulation advances for 10 epochs
    Then the DataCollector emits reproducible Gini, velocity, and Comb reserve series
