# Specification: Dual-Track Decision Governance

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: MADR 4.0 Architectural Decision Records Managed by OSS `adrlint`
All structural, cross-cutting architectural decisions SHALL be stored as MADR 4.0 YAML front-matter records in `docs/adr/NNNN-<slug>.md`, configured by `.adrlint.toml` and enforced by external MIT OSS **`adrlint`** (`lint`, `format --check`, and semantic BLAKE3 `adrlint.lock` verification), with an auto-synced `docs/adr/index.md` table (`nectr-docs sync`) and zero bespoke ADR engine code (`src/nectr/devtools/adr.py` MUST NOT exist). `nectr.devtools.decisions` adds `--allow-proposed` branch gating (rejecting `status: proposed` on `main`).
- **Linked Scenario:** `Repository MADR records pass adrlint validation, lock check, and verbosity limits` in [decision_governance.feature](../../../features/decision_governance.feature#L6-L9)
- **Linked Scenario:** `OSS adrlint replaces bespoke ADR module and enforces lock and proposed gating` in [decision_governance.feature](../../../features/decision_governance.feature#L21-L24)

### Requirement: Strict ADR Length and Verbosity Limits
Every numbered ADR in `docs/adr/` (excluding `index.md`) SHALL obey automated verbosity budgets: at most `70` lines, at most `380` words, an H1 title of at most `70` characters, and at most `6` bullet items per Markdown section (after stripping YAML front matter).
- **Linked Scenario:** `Verbose MADR record exceeding line or word limits is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L11-L14)

### Requirement: Tool-Managed Fast Non-Architectural Decision Log
Non-architectural decisions (`DEC-NNN`) and open experimental hypotheses (`EXP-NNN`) SHALL be defined in `docs/planning/decisions.yaml`, validated against strict Pydantic field-length and cross-reference schemas, and deterministically rendered to `docs/planning/decision_log.md`.
- **Linked Scenario:** `Manual drift in rendered non-architectural decision_log.md is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L16-L19)
