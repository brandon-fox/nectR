# Proposal: Add the `nectr` CLI (`simulate` and `serve`)

## Problem Statement

`nectR` currently exposes governance developer scripts (`nectr-decisions`, `nectr-citations`, `nectr-docs`, `nectr-ci-parity`, `nectr-pr-lifecycle`) in `pyproject.toml`, but has no top-level `nectr` command for users to run the multi-hive simulation or launch the Hive FastAPI service.

## Motivation & Goals

- Provide a unified `nectr` console script (`nectr = "nectr.cli:main"`) with `simulate` and `serve` subcommands.
- Ensure `nectr simulate` executes `run_multi_hive_persona_simulation()` and emits deterministic, byte-reproducible JSON telemetry.
- Ensure `nectr serve` hydrates or initializes a `HiveServiceLayer` backed by `SQLModelHiveRepository`, builds the FastAPI app via `create_app`, and runs it with `uvicorn` (lazily imported so `[api]` remains an optional extra).

## Scope

- **TL5:** Create `src/nectr/cli.py`, register `nectr` in `pyproject.toml` `[project.scripts]`, and cover behavior with `openspec/changes/add-nectr-cli/`, `features/cli.feature`, `features/steps/cli_steps.py`, and `tests/test_cli.py`.
- **TL6:** Add byte-identical smoke verification for `nectr simulate`.
