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

  Scenario: Zero-nectR session without reciprocal subject is rejected while reciprocal skill barter succeeds
    Given a Hive "HIVE_BARTER" with seed comb 100.0 and registered Learners "bee_a" and "bee_b"
    When "bee_a" attempts a 0.0 LIQUID_NECTR escrow with "bee_b" for "CS-101" without a reciprocal subject
    Then the contract raises a violation matching "Zero-nectR sessions must specify a reciprocal_subject_id"
    When "bee_a" escrows and settles a 0.0 LIQUID_NECTR reciprocal barter with "bee_b" for "CS-101" in exchange for "SPAN-101"
    Then "bee_b" has tutored 1 distinct peer in the Hive

  Scenario: Guard Bee blocks unaccepted Pollinator bridge and permits Accepted Status bridge with Comb toll
    Given a source Hive "HIVE_A" and target Hive "HIVE_B" with threshold 2 and Pollinator "pollinator_1" holding 20.0 LIQUID_NECTR in "HIVE_A"
    When "pollinator_1" attempts to bridge 10.0 LIQUID_NECTR from "HIVE_A" to "HIVE_B" before earning Accepted Status
    Then the contract raises a violation matching "Guard Bee Rejection"
    When "pollinator_1" tutors 2 distinct peers in "HIVE_B" and bridges 10.0 LIQUID_NECTR from "HIVE_A" to "HIVE_B"
    Then "pollinator_1" has 10.0 LIQUID_NECTR in "HIVE_A" and 9.5 LIQUID_NECTR in "HIVE_B"

  Scenario: Queen cannot arbitrate undisputed escrow or charge 100 percent fee
    Given a Hive "HIVE_DISPUTE_GUARD" with seed comb 200.0, Queen "queen_1", Certified Worker "worker_1" for "PHYS-101", and Learner "learner_1" with 20.0 RAW_POLLEN
    When "learner_1" escrows 20.0 RAW_POLLEN with "worker_1" for "PHYS-101" and "queen_1" attempts to resolve without a dispute at 1.0 fee rate
    Then the contract raises a violation matching "Only disputed sessions can be arbitrated"

  Scenario: Learner cancels expired escrow and recovers full original token state
    Given a Hive "HIVE_EXPIRY" with seed comb 200.0, Queen "queen_1", Certified Worker "worker_1" for "PHYS-101", and Learner "learner_1" with 20.0 RAW_POLLEN
    When "learner_1" escrows 15.0 RAW_POLLEN with "worker_1" for "PHYS-101" at epoch 0 with expiry 5 and cancels at epoch 6
    Then "learner_1" has 20.0 RAW_POLLEN
    And "learner_1" has 0.0 LIQUID_NECTR
