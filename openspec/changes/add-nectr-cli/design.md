# Design: `nectr` CLI Entrypoint (`simulate` & `serve`)

## Architecture & Bounded Context Boundaries

- **`src/nectr/cli.py` (Driving CLI Adapter):**
  - Thin `argparse`-based driving adapter with `main(argv: Sequence[str] | None = None) -> int`.
  - Contains zero domain, smart-contract, or persistence business logic; delegates exclusively to `nectr.personas.simulator.run_multi_hive_persona_simulation` and `nectr.services` (`SQLModelHiveRepository`, `HiveServiceLayer`, `create_app`).
- **Lazy Optional Extra Handling (`[api]`):**
  - `uvicorn` is an optional dependency under `[project.optional-dependencies].api`.
  - `cli.py` imports `uvicorn` lazily inside `serve` so `nectr --help` and `nectr simulate` work in base installs without `uvicorn`, while `nectr serve` emits an actionable error and exits `1` if `uvicorn` is unavailable.
- **Deterministic Simulation Output:**
  - `nectr simulate` serializes `{"telemetry": asdict(telemetry), "metadata": metadata}` with `json.dumps(..., indent=2, sort_keys=True)` so repeated runs produce byte-identical output.
