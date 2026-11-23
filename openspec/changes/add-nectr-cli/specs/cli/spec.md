# Specification: `nectr` CLI (`cli`)

## Linked Behavior & Executable Steps

- **Feature File:** [features/cli.feature](../../../../../features/cli.feature)
- **Step Definitions:** [features/steps/cli_steps.py](../../../../../features/steps/cli_steps.py)

> User stories and Given/When/Then scenarios are maintained exclusively in the linked `.feature` file above (never hardcoded in `spec.md`).

## Requirements

### Requirement: ADDED — Deterministic Multi-Hive Simulation Command (`nectr simulate`)
The `nectr simulate` command SHALL execute `run_multi_hive_persona_simulation()`, exit with status `0`, and print deterministic, valid JSON containing `telemetry` and `metadata` fields that remain byte-identical across repeated invocations.

- **Linked Scenario:** `nectr simulate prints deterministic multi-hive JSON telemetry` in [cli.feature](../../../../../features/cli.feature)

### Requirement: ADDED — Hive API Server Command (`nectr serve`)
The `nectr serve` command SHALL initialize or hydrate a `HiveServiceLayer` backed by `SQLModelHiveRepository`, build the FastAPI application via `create_app`, and serve it via `uvicorn.run` for the configured `--host`, `--port`, `--hive-id`, and `--database-url`.

- **Linked Scenario:** `nectr serve builds the FastAPI Hive service app and delegates to uvicorn` in [cli.feature](../../../../../features/cli.feature)

### Requirement: ADDED — Graceful Optional `[api]` Extra Error Handling
When `uvicorn` is not installed, `nectr serve` SHALL exit with status `1` and print an actionable message instructing the user to install the `api` extra without breaking `nectr --help` or `nectr simulate`.

- **Linked Scenario:** `nectr serve reports a helpful error when the optional api extra is missing` in [cli.feature](../../../../../features/cli.feature)
