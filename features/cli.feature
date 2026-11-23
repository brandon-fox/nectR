Feature: nectr Command-Line Interface (simulate and serve)
  As a nectR user or operator
  I want a top-level `nectr` CLI with `simulate` and `serve` subcommands
  So that I can reproduce deterministic multi-hive simulations and launch the FastAPI node cleanly

  Scenario: nectr simulate prints deterministic multi-hive JSON telemetry
    Given the nectr CLI application
    When the user runs the CLI with arguments "simulate"
    Then the CLI exits with status 0 and prints valid deterministic simulation JSON

  Scenario: nectr serve builds the FastAPI Hive service app and delegates to uvicorn
    Given the nectr CLI application and a temporary SQLite database path
    When the user runs the CLI serve command with a stubbed ASGI server
    Then the CLI exits with status 0 and serves the Hive FastAPI app for the requested host, port, and hive id

  Scenario: nectr serve reports a helpful error when the optional api extra is missing
    Given the nectr CLI application without uvicorn installed
    When the user runs the CLI with arguments "serve"
    Then the CLI exits with status 1 and prints an install hint for the api extra
