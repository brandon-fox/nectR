---
trigger: always_on
---

# Mandatory Outside-In OpenSpec + Behave BDD + Strict TDD (Red-Green-Refactor) + DDD Charter

All development in **nectR** MUST strictly follow this **Outside-In** pipeline before, during, and after every action, with **no exceptions**:

## 1. Domain-Driven Design (DDD) Boundaries (Outside-In First)

- Respect Bounded Contexts defined in `openspec/project.md`:
  - `src/nectr/chain/`: Consensus (`PoUW-PoW`), blocks, headers, Merkle roots. No tutoring business logic.
  - `src/nectr/contracts/`: Deterministic smart contract state machines (`HiveContractEngine`, `ServiceBarterSession`, `BeeAccount`).
  - `src/nectr/services/`: Application services (`HiveServiceLayer`), hexagonal ports/adapters.
  - `src/nectr/personas/`: Behavioral economy actors & simulations.
- Use Ubiquitous Language (`RAW_POLLEN`, `LIQUID_NECTR`, `ROYAL_COMB_RESERVE`, `QUEEN`, `CERTIFIED_WORKER_BEE`, `LEARNER_BEE`, `POLLINATOR_VISITOR`, `Accepted Status`) consistently across specs, Gherkin features, tests, and code.

## 2. OpenSpec Spec-Driven Development & `adrlint` ADR Governance

- **No implementation without a spec.** Before modifying behavior, creating ADRs, or adding features:
  1. Check BOTH `openspec/specs/` AND active `openspec/changes/` for existing requirements or pending governance specs.
  2. Create or update an OpenSpec change under `openspec/changes/<change-id>/` (`proposal.md`, `design.md`, `tasks.md`, and `specs/<domain>/spec.md`).
  3. All Architectural Decision Records MUST be created, linted, and locked with **`adrlint`** (`adrlint new`, `adrlint lint`, `adrlint format`, `adrlint lock`) under `docs/adr/NNNN-<slug>.md` (MADR 4.0 YAML front matter, `<= 70` lines, `<= 380` words, `# Title <= 70` chars, `<= 6` bullets per section). Never bypass `adrlint` or hand-roll custom ADR tooling.

## 3. Outside-In Behave BDD & Strict TDD Red-Green-Refactor Commit Protocol

- **Worktree Isolation (`ADR-0017`):** Execute every change inside an isolated Worktrunk worktree (`.worktrees/<branch-slug>/` via `git-wt`) or harness shared-repo worktree with its own synced `.venv`, and merge via `git-wt merge main --no-squash`.
- **Single Source of Truth for User Stories:** Never hardcode user stories or Given/When/Then scenarios inside OpenSpec `spec.md` files. Instead, `spec.md` MUST state requirement intent/invariants and link directly to `features/<domain>.feature` and `features/steps/<domain>_steps.py`.

Every behavior change MUST be executed and committed in three strict phases, enforced by `xfail_strict = true` in `pyproject.toml`, `.githooks/pre-commit`, `.githooks/commit-msg`, `.githooks/pre-push`, and `.config/wt.toml`:

1. **Phase 1 — RED (Tests Written First & Committed as 100% Passing with Expected Failure):**
   - Write the outside-in Gherkin acceptance scenario in `features/*.feature` + step definitions in `features/steps/`.
   - Write the failing unit/invariant test(s) in `tests/` marked with `@pytest.mark.xfail(strict=True, reason="RED: <spec-id> not yet implemented")` (and tag new unimplemented Gherkin scenarios `@red` only until GREEN).
   - Run `python -m pytest` (must exit `0` with `xfailed`, proving 100% suite pass with expected failure).
   - Commit atomically: `test(<scope>): add RED failing tests for <feature>`.

2. **Phase 2 — GREEN (Minimal Code -> Confirm XPASS Failure -> Remove `xfail` & Stay Green):**
   - Write the minimal DDD-compliant production code in `src/nectr/` to satisfy the spec. Never insert inline mutation suppression pragmas (`# pragma: no mutate` / `# nomut`) in `src/`.
   - Run `python -m pytest`: because `xfail_strict = true` is enforced in `pyproject.toml`, the test suite **MUST FAIL with `XPASS`** (confirming the previously expected-to-fail test now passes for the right reason!).
   - Remove `@pytest.mark.xfail(...)` from the test(s) (and remove `@red` from the `.feature` scenario).
   - Re-run `python -m pytest` and `python -m behave` — both MUST exit `0` (100% passing).
   - Commit atomically: `feat(<scope>): implement <feature> to turn RED tests GREEN`.

3. **Phase 3 — REFACTOR (Keep 100% Green & Pass Mutation Gate):**
   - Refactor for clarity, modularity, and DDD purity while keeping `python -m pytest` and `python -m behave` 100% green.
   - Run `uv run python -m nectr.devtools.mutation_gate diff` (`ADR-0018`, `DEC-017`) and verify changed lines meet tier targets (`>= 85%` Tier 1 `contracts/`/`chain/`, `>= 75%` Tier 2 `services/`/`devtools/`); ratchet `[tool.nectr.mutation.baseline]` upward (`floor(score) - 1`) when full-sweep scores improve.
   - Commit atomically: `refactor(<scope>): <clean up description>`.

## 4. Post-Action Verification (Mandatory)

Before reporting completion of any task, run and verify all gates pass:

1. `detect-secrets-hook --baseline .secrets.baseline` (on modified/tracked files)
2. `uv run python -m nectr.devtools.mutation_gate check-pragmas`
3. `python -m pytest`
4. `python -m behave`
5. `uv run python -m nectr.devtools.mutation_gate diff` (before pre-merge / pre-push)
