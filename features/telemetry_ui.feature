Feature: Read-Only Telemetry Dashboard UI (Streamlit & NetworkX)
  As a nectR researcher or campus administrator
  I want a read-only Streamlit + NetworkX dashboard for Knowledge Graph, Collusion Matrix, Gini, and Comb reserves
  So that Hive health can be inspected visually without coupling write-side contract logic

  @red
  Scenario: Read-only dashboard renders Hive telemetry without mutating ledger state
    Given an exported Hive telemetry snapshot and NetworkX interaction graph
    When the Streamlit dashboard data loader prepares the Knowledge Graph, Collusion Matrix, Gini, and Comb views
    Then all four telemetry panels render cleanly in read-only mode
