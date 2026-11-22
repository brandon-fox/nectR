# Specification: Dual-Track Decision Governance

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: MADR 4.0 Architectural Decision Records Managed by OSS `adrlint`
All structural, cross-cutting architectural decisions SHALL be stored as MADR 4.0 YAML front-matter records in `docs/adr/NNNN-<slug>.md` (`ADR-0000` through `ADR-0016`), configured by `.adrlint.toml` and enforced by external MIT OSS **`adrlint`** (`lint`, `format --check`, and semantic BLAKE3 `adrlint.lock` verification), with an auto-synced `docs/adr/index.md` table (`nectr-docs sync`) and zero bespoke ADR engine code (`src/nectr/devtools/adr.py` MUST NOT exist). `nectr.devtools.decisions` adds `--allow-proposed` branch gating (rejecting `status: proposed` on `main`).
- **Linked Scenario:** `Repository MADR records pass adrlint validation, lock check, and verbosity limits` in [decision_governance.feature](../../../features/decision_governance.feature#L6-L9)
- **Linked Scenario:** `OSS adrlint replaces bespoke ADR module and enforces lock and proposed gating` in [decision_governance.feature](../../../features/decision_governance.feature#L21-L24)

### Requirement: Strict ADR Length and Verbosity Limits
Every numbered ADR in `docs/adr/` (excluding `index.md`) SHALL obey automated verbosity budgets: at most `70` lines, at most `380` words, an H1 title of at most `70` characters, and at most `6` bullet items per Markdown section (after stripping YAML front matter).
- **Linked Scenario:** `Verbose MADR record exceeding line or word limits is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L11-L14)

### Requirement: Tool-Managed Fast Non-Architectural Decision Log
Non-architectural decisions (`DEC-001` through `DEC-016`) and open experimental hypotheses (`EXP-001` through `EXP-006`) SHALL be defined in `docs/planning/decisions.yaml`, validated against strict Pydantic field-length and cross-reference schemas, and deterministically rendered to `docs/planning/decision_log.md`.
- **Linked Scenario:** `Manual drift in rendered non-architectural decision_log.md is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L16-L19)

### Requirement: External Workflow Automation (`n8n` / "k8n") Off-Chain Boundary
The decision registry (`docs/planning/decisions.yaml`), MADR log (`docs/adr/0016-scope-external-workflow-automation-off-chain.md`), and Milestone 3 roadmap (`docs/planning/roadmap.md`) SHALL clarify `"k8n"` as `n8n` while keeping `DEC-009` locked to Mesa ABM, isolate `n8n` (Sustainable Use License) out of Python packaging behind `HiveServiceLayer` webhook ports (`DEC-016`), define hybrid evaluation hypothesis `EXP-006`, and document permissive-OSS Milestone 3 orchestration options.
- **Linked Scenario:** `Decision registry and Milestone 3 roadmap define n8n off-chain boundaries and options` in [decision_governance.feature](../../../features/decision_governance.feature#L26-L31)
