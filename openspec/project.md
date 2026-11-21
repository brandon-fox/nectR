# nectR — OpenSpec Project Context & Domain-Driven Design (DDD) Charter

## Purpose
**nectR** is an open-source, research-driven monorepo for a private, closed-loop Proof-of-Useful-Work & Proof-of-Work (`PoUW-PoW`) blockchain and multi-agent behavioral economy modeled after honeybee (*Apis mellifera*) colony dynamics.

## Domain-Driven Design (DDD) Bounded Contexts
All code, specs, and tests MUST respect strict Bounded Context boundaries and Ubiquitous Language:

1. **Consensus & Ledger Context (`src/nectr/chain/`)**
   - *Aggregate Roots:* `Block`, `BlockchainLedger`
   - *Value Objects:* `BlockHeader`, `SignedTransaction`, `UsefulComputeRoot`
   - *Constraint:* Pure cryptographic PoW + `useful_compute_root` commitment. Zero tutoring/subject business logic.

2. **Smart Contracts Context (`src/nectr/contracts/`)**
   - *Aggregate Roots:* `HiveContractEngine`, `ServiceBarterSession`, `BeeAccount`
   - *Value Objects:* `TokenState` (`RAW_POLLEN`, `LIQUID_NECTR`, `ROYAL_COMB_RESERVE`), `BeeRole`, `SessionStatus`
   - *Domain Events:* `PollenAllocated`, `WorkerCertified`, `BarterEscrowed`, `SessionSettled`, `DisputeResolvedToComb`, `AcceptedStatusGranted`
   - *Constraint:* Deterministic finite-state machines enforcing supply conservation and protocol invariants `D-01` through `D-05`.

3. **Hive Service Layer Context (`src/nectr/services/`)**
   - *Application Services:* `HiveServiceLayer` (Relayer, Knowledge Graph Telemetry, Escrow Coordinator, Cross-Hive Bridge)
   - *Constraint:* Hexagonal ports-and-adapters; orchestrates contract calls and chain commits without leaking infrastructure details into contracts.

4. **Behavioral Economy & Persona Context (`src/nectr/personas/`, `experiments/`)**
   - *Domain Actors:* `Freshman_Forager`, `Certified_Senior_Worker`, `Finals_Week_Panicker`, `Sybil_Roommate_Ring`, `Drifting_Pollinator`, `Queen_Facilitator`
   - *Constraint:* Executes real signed transactions against the ledger and contracts to produce reproducible telemetry.

## Mandatory Engineering Workflow (No Exceptions)
Every feature, bugfix, or protocol change MUST follow this exact sequence:
1. **Security & Privacy Gate:** Verify no secrets, private references, or local hardcoded paths exist (`python scripts/security_scan.py --all`).
2. **OpenSpec (`openspec/changes/<change-id>/`):** Author `proposal.md`, `design.md`, `tasks.md`, and `specs/<domain>/spec.md` delta before writing code.
3. **BDD (`features/*.feature`):** Define executable Gherkin acceptance scenarios in `features/` and verify they fail (`behave`) before implementation.
4. **Strict TDD (Red-Green-Refactor):**
   - **RED:** Write a failing unit/invariant test in `tests/` first and observe it fail.
   - **GREEN:** Write the minimal domain code to make the test pass.
   - **REFACTOR:** Clean up while keeping all `pytest` and `behave` tests green.
5. **Pre-Commit & Pre-Push Verification:** `python scripts/security_scan.py`, `python -m pytest`, and `python -m behave` must all pass.
