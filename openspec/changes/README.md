# OpenSpec Change Proposals

Every new capability, protocol modification, or bugfix in `nectR` MUST begin with a change folder under `openspec/changes/<change-id>/` containing:

1. `proposal.md` — Why the change is needed, bounded contexts affected, and acceptance criteria.
2. `design.md` — Domain-Driven Design (DDD) entities, value objects, invariants, and architectural trade-offs.
3. `tasks.md` — Ordered checklist following `OpenSpec -> Behave BDD -> Strict TDD (Red-Green-Refactor)`.
4. `specs/<capability>/spec.md` — Delta requirements (`ADDED`, `MODIFIED`, `REMOVED`) stating intent/invariants and linking directly to the corresponding `features/<capability>.feature` and `features/steps/<capability>_steps.py` (never hardcode user stories or Given/When/Then blocks inside `spec.md`).

Once implemented and verified by `pytest`, `behave`, and `scripts/security_scan.py`, merge the delta into `openspec/specs/` and archive the change under `openspec/changes/archive/`.

## Active Changes

Proposals currently in progress under the Plan to B+:

- `harden-authority-and-accounting` — Protocol authority, token conservation invariants, and signed audit-log accounting (owned by Core team for Plan to B+).

## Deferred Changes

Proposals deferred until after the v0.1.0 release per the Plan to B+ and the structure freeze in `AGENTS.md`:

- `add-biomimetic-lifecycle-and-swarming-contracts` — Phase 2 biomimetic colony lifecycle, Waggle surge co-pay, demurrage, and reproductive swarming contracts.
- `add-campus-compliance-lti-and-zk-identity` — FERPA/GDPR zero-PII boundary, LTI 1.3 / Shibboleth SSO, and Title IV compliance firewall.
- `add-nats-jetstream-cross-hive-federation` — NATS Leaf Node JetStream cross-Hive federation and Kurtosis chaos testing.
- `add-pactflow-api-and-message-contracts` — Pact v4 and PactFlow bi-directional HTTP and async message contracts.
- `add-telemetry-dashboard-ui` — Read-only Streamlit and NetworkX telemetry dashboard.
- `adopt-vyper-and-zero-gas-pyevm` — Vyper smart contracts on zero-gas py-evm execution backend.

## Archived Changes

Completed change proposals merged into `main` and archived under `openspec/changes/archive/`:

- `add-github-actions-and-schema-hooks` — Automated GitHub Actions CI workflows and JSON Schema verification hooks.
- `add-n8n-workflow-roadmap-decisions` — Multi-agent workflow automation and roadmap decision governance.
- `add-sqlmodel-persistence-and-api` — SQLModel persistence layer and FastAPI service endpoints.
- `adopt-ed25519-and-pymerkle` — Ed25519 cryptographic signing and Merkle inclusion proofs.
- `adopt-mesa-abm-and-hypothesis` — Mesa agent-based modeling and Hypothesis property tests.
- `automate-pr-lifecycle-and-merge-safety` — PR lifecycle validation, squash-safety checks, and branch verification tooling.
- `enforce-spec-feature-links` — OpenSpec to Behave feature single source of truth linking.
- `expand-specs-long-term-vision-and-swarm-plan` — Initial architecture vision and swarm coordination framework.
- `harden-ci-action-runtimes-and-review` — Immutable commit SHA action pinning and automated dependency reviews.
- `lock-vyper-pactflow-and-grill-me-decisions` — Architecture decision locking for Vyper and PactFlow.
- `remediate-review-issues-and-provenance` — Code review remediation and bibliographic provenance tracking.
- `replace-custom-adr-with-adrlint` — Migration from custom ADR scripts to standard adrlint.
- `split-madr-and-decision-registry` — MADR architectural decision records and rule registry separation.
- `standardize-custom-skills` — Antigravity skill structure and typing standardization.
