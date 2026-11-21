Feature: Core nectR Protocol Invariants
  As a nectR Hive participant
  I want the smart contracts to enforce biomimetic and game-theoretic invariants
  So that no Queen can self-deal, RAW_POLLEN cannot be colluded, and supply is conserved

  Scenario: Queen Separation of Powers blocks Queen from tutoring
    Given a Hive "HIVE_BDD" with seed comb 500.0
    And a registered Queen "queen_1" and Learner "student_1" with 20.0 RAW_POLLEN
    When "queen_1" attempts to create a tutoring escrow for "student_1" in "CS-101" for 5.0 RAW_POLLEN
    Then the contract raises a violation matching "Queen Separation of Powers Violation"

  Scenario: RAW_POLLEN cannot be spent with an uncertified peer
    Given a Hive "HIVE_BDD" with seed comb 500.0
    And a registered Queen "queen_1", Learner "freshman_1" with 15.0 RAW_POLLEN, and uncertified peer "roommate_1"
    When "freshman_1" attempts to escrow 10.0 RAW_POLLEN with "roommate_1" for "CALC-101"
    Then the contract raises a violation matching "RAW_POLLEN can only be spent"
    And "freshman_1" still has 15.0 RAW_POLLEN

  Scenario: RAW_POLLEN refines into LIQUID_NECTR when settled with a Certified Worker Bee
    Given a Hive "HIVE_BDD" with seed comb 500.0
    And a registered Queen "queen_1", Learner "freshman_1" with 15.0 RAW_POLLEN, and Certified Worker "worker_1" for "CALC-101"
    When "freshman_1" escrows and settles 10.0 RAW_POLLEN with "worker_1" for "CALC-101"
    Then "worker_1" has 10.0 LIQUID_NECTR
    And "freshman_1" has 5.0 RAW_POLLEN

  Scenario: Queen dispute resolution routes 100% of fees to Comb and conserves supply
    Given a Hive "HIVE_DISPUTE" with seed comb 200.0, Queen "queen_1", Certified Worker "worker_1" for "PHYS-101", and Learner "learner_1" with 20.0 RAW_POLLEN
    When "learner_1" escrows 20.0 RAW_POLLEN with "worker_1" for "PHYS-101" and "queen_1" resolves the dispute at 0.5 tutor share and 0.10 fee rate
    Then the Hive comb reserve is 182.0
    And "worker_1" has 9.0 LIQUID_NECTR
    And "learner_1" has 9.0 RAW_POLLEN
