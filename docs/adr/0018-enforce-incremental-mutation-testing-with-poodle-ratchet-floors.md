---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Meta-Orchestrator
---

# Enforce Incremental Mutation Testing with Poodle Ratchet Floors

## Context and Problem Statement

Line coverage alone misses boundary regressions (`contracts/`, `chain/`). In the 3-worktree [Mutation Engine Spike](../experiments/mutation_engine_spike.md), `mutmut` (`BSD-3-Clause`) failed on Windows (`os.fork()`) and `cosmic-ray` (`MIT`) pulled `LGPL` `yattag` and mutated `src/` in-place, whereas `poodle` (`MIT`) passed cross-platform in `73.24s` (`470` trials, `55.3%` Tier-1 score).

## Considered Options

* **`poodle` (`MIT`) via `nectr.devtools.mutation_gate` with diff-scoped tier targets and upward-only baseline floors**
* **`cosmic-ray` (`MIT`, `LGPL` `yattag`) or `mutmut` (`BSD-3-Clause`, Unix-only)**
* **Blocking `>= 85%` full-repository sweeps on every local `pre-commit` run**

## Decision Outcome

Chosen option: "`poodle` (`MIT`) via `nectr.devtools.mutation_gate` with diff-scoped tier targets and upward-only baseline floors", because `poodle` is 100% MIT (`DEC-007`), runs safely in `.poodle-temp/` on Windows and Linux, and catches infinite-loop timeouts cleanly. `REFACTOR`, Worktrunk `[[pre-merge]]`, `.githooks/pre-push`, and PR CI enforce `>= 85%` (`contracts/`, `chain/`) and `>= 75%` (`services/`, `devtools/`) on `git diff -U0` changed lines (timeouts counted as killed). `main` and nightly CI enforce upward-only `[tool.nectr.mutation.baseline]` floors; `personas/`, `ui/`, and `experiments/` are excluded, and inline suppression pragmas in `src/` are rejected at `pre-commit`.

### Consequences

* Good, because changed lines hit `85%`/`75%` test strength without slowing `RED`/`GREEN` iterations.
* Good, because ratcheting baseline floors (`floor(score) - 1`) prevent regressions while closing legacy survivors incrementally.
* Bad, because `pyproject.toml` must pass `-o pythonpath=.` to `poodle` and `.poodle-temp/` must remain gitignored.
