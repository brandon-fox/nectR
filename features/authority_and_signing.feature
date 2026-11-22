Feature: Authority Binding and Signed Command Verification
  As a nectR Hive operator
  I want all state-changing service, API, and ledger commands bound to Ed25519 keys with monotonic nonces and bootstrap-only Queen appointment
  So that actors cannot forge identities, self-assign Queen privileges, submit unsigned writes, or replay commands

  @D-02
  Scenario: Role cannot be self-assigned
    Given a bootstrapped Hive "HIVE_AUTH" with a bootstrap Queen and key registry
    When a Bee "rogue_bee" submits a self-signed register command requesting role "QUEEN"
    Then the command is rejected with an authorization error and "rogue_bee" is not registered

  Scenario: No unsigned writes
    Given a bootstrapped Hive "HIVE_AUTH" with a registered Learner "learner_1"
    When an unsigned dictionary or invalid-signature write is submitted to the API or blockchain
    Then the API rejects bad signatures with 401 and the blockchain rejects unsigned transactions

  Scenario: A replayed command is rejected
    Given a bootstrapped Hive "HIVE_AUTH" with a registered Learner "learner_1"
    When the Queen executes a signed pollen allocation at nonce 2 and replays the same signed command
    Then the first allocation succeeds and the replayed command is rejected without modifying balances
