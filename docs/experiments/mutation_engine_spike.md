# Mutation Testing Engine Spike

## Methodology

Three permissive-licensed Python mutation testing engines were evaluated in parallel, disposable Git worktrees (`spike/mutation-poodle`, `spike/mutation-cosmic-ray`, `spike/mutation-mutmut`) branched from the same repository commit (`c4cb85e`).

- **Targets:** `src/nectr/contracts/engine.py` and `src/nectr/chain/ledger.py`, executed against `tests/`.
- **Controls:** String-literal mutators disabled where supported; minimum per-mutant timeout set to `10s` to verify clean termination of infinite-loop mutations inside `_mine_header` (`while True`, `nonce += 1`) and `compute_merkle_root`.
- **Gate Criteria:** Native Windows PowerShell + sandbox compatibility, zero prohibited transitive licenses under `pip-licenses`, zero third-party CVEs under `pip-audit`, file scoping, timeout handling, and clean working tree preservation.

## Benchmark Comparison

| Metric | `poodle` (`1.4.0`) | `cosmic-ray` (`8.9.0`) | `mutmut` (`3.8.1`) |
| --- | --- | --- | --- |
| **Package License** | `MIT` | `MIT` | `BSD-3-Clause` |
| **Added Dependencies** | `+3` (`poodle`, `wcmatch`, `bracex`) | `+20` (`sqlalchemy`, `aiohttp`, `gitpython`, `yattag`, etc.) | `+6` (`libcst`, `textual`, `setproctitle`, etc.) |
| **`pip-licenses` Gate** | **PASS** (100% MIT) | **FAIL** (`yattag` is LGPL; `aiohttp` `Apache-2.0 AND MIT`) | **PASS** (MIT / BSD-3-Clause) |
| **`pip-audit` (3rd-party CVEs)** | **0 CVEs** | **0 CVEs** | **0 CVEs** |
| **Native Windows Support** | **PASS** (multi-threaded) | **PARTIAL** (mutates `src/` in-place; dirty on abort) | **FAIL** (requires WSL / Linux `os.fork()`) |
| **Timeout / Infinite Loops** | **PASS** (`7` caught cleanly at `10s`) | Timed out / aborted at `15 min` cap | Not benchmarked locally (Linux/CI-only) |
| **File Scoping** | `--only` globs relative to `source_folders` | Single `module-path` TOML per SQLite session | Path config / Linux-only |
| **Machine Output & Threshold** | Built-in `--json` + `--fail_under` | SQLite + `cr-rate` + NDJSON `dump` | `mutmut results` |
| **Targets Benchmarked** | `engine.py` + `ledger.py` | `engine.py` only (15-min cutoff) | None (Windows blocked) |
| **Wall-Clock Time** | **`73.24s`** (31 workers) | **Incomplete at `900s`** (403/633 jobs, sequential) | N/A |
| **Mutant Counts** | `470` trials: `253` killed, `210` survived, `7` timeout (`53.8%` raw, `55.3%` w/ timeouts) | `403/633` completed: `238` killed, `165` survived (`cr-rate 40.94`) | N/A |
| **Working Tree After Run/Abort** | **Clean** (temp copies in `.poodle-temp`) | **Dirty** (`M src/nectr/contracts/engine.py`) | N/A |

### Per-Module `poodle` Breakdown

- **`src/nectr/chain/ledger.py` alone:** `138` trials (`84` killed, `47` survived, `7` timeout, `0` errors); `--fail_under 95` exited with code `1` (`60.8%` raw `success_rate`, `65.9%` counting timeouts as killed).
- **`src/nectr/contracts/engine.py` share:** `332` trials (`169` killed, `163` survived, `0` timeout, `0` errors; `50.9%` kill rate).

## Decision: Adopt `poodle` with Incremental Ratchet Policy

**`poodle` (`MIT`)** is selected as `nectR`'s mutation testing engine because it is the only candidate passing all four hard requirements: native Windows PowerShell execution, clean MIT-only transitive dependencies with zero CVEs, isolated temp-directory execution with clean timeout handling, and `--only` file scoping.

Because current test coverage kills `55.3%` of baseline Tier-1 mutants (`210` survivors in `engine.py` + `ledger.py`), `nectR` adopts an **Incremental Ratchet** enforcement model:

1. **Diff-Scoped Targets (`REFACTOR`, Worktrunk `pre-merge`, `pre-push`, PR CI):** Enforce **`>= 85%`** (Tier 1: `contracts/`, `chain/`) and **`>= 75%`** (Tier 2: `services/`, `devtools/`) strictly on mutants intersecting changed lines (`git diff -U0`), counting timeouts as killed.
2. **Full-Sweep Baseline Floors (Push to `main`, Nightly CI):** Enforce committed per-tier baseline floors in `pyproject.toml` that can only ratchet upward as hardening tests are added.
3. **Excluded Contexts:** `src/nectr/personas/`, `src/nectr/ui/`, and `experiments/` are excluded from blocking mutation runs.

## Operational Pitfalls Discovered

1. **`--only` Glob Base Path:** `poodle --only` matches relative to `source_folders = ["src"]` (pass `nectr/contracts/engine.py`, not `src/nectr/contracts/engine.py`).
2. **Pytest `pythonpath` Override:** `pyproject.toml` sets `pythonpath = ["src"]`, which shadows `poodle`'s mutated temp `PYTHONPATH` unless `runner_opts.command_line` sets `"pytest -x --assert=plain -o pythonpath=."`.
3. **Pragma Suppression Honor:** `poodle` honors inline suppression comments (`pragma: no mutate` / `nomut`), requiring a `pre-commit` ban in `src/` so test gaps cannot be silenced.
4. **Temp Workspace Directory:** `poodle` writes temporary worker archives to `.poodle-temp/` in the working directory, which must be gitignored.
