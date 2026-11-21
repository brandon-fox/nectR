# OpenSpec Change Proposals

Every new capability, protocol modification, or bugfix in `nectR` MUST begin with a change folder under `openspec/changes/<change-id>/` containing:

1. `proposal.md` — Why the change is needed, bounded contexts affected, and acceptance criteria.
2. `design.md` — Domain-Driven Design (DDD) entities, value objects, invariants, and architectural trade-offs.
3. `tasks.md` — Ordered checklist following `OpenSpec -> Behave BDD -> Strict TDD (Red-Green-Refactor)`.
4. `specs/<capability>/spec.md` — Delta requirements (`ADDED`, `MODIFIED`, `REMOVED`) with Gherkin scenarios.

Once implemented and verified by `pytest`, `behave`, and `scripts/security_scan.py`, merge the delta into `openspec/specs/` and archive the change under `openspec/changes/archive/`.
