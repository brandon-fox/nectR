# Specification: Dual-Track Decision Governance

## Linked Behavior & Executable Steps
- **Feature File:** [features/decision_governance.feature](../../../features/decision_governance.feature)
- **Step Definitions:** [features/steps/decision_governance_steps.py](../../../features/steps/decision_governance_steps.py)

## Requirements

### Requirement: MADR Architectural Decision Records Managed by `pyadr`
All structural, cross-cutting architectural decisions SHALL be stored as individual Markdown Architectural Decision Records (MADR) in `docs/adr/NNNN-<slug>.md`, configured by `.adr` and validated by `pyadr` (`AdrCore.check_adr_repo`) with an auto-generated `docs/adr/index.md` table of contents (`pyadr toc`).
- **Linked Scenario:** `Repository MADR records pass pyadr validation and verbosity limits` in [decision_governance.feature](../../../features/decision_governance.feature#L6-L9)

### Requirement: Strict ADR Length and Verbosity Limits
Every ADR in `docs/adr/` (excluding `template.md` and `index.md`) SHALL obey automated verbosity budgets: at most `70` lines, at most `380` words, an H1 title of at most `70` characters, and at most `6` bullet items per Markdown section.
- **Linked Scenario:** `Verbose MADR record exceeding line or word limits is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L11-L14)

### Requirement: Tool-Managed Fast Non-Architectural Decision Log
Non-architectural decisions (`DEC-NNN`) and open experimental hypotheses (`EXP-NNN`) SHALL be defined in `docs/planning/decisions.yaml`, validated against strict Pydantic field-length and cross-reference schemas, and deterministically rendered to `docs/planning/decision_log.md`.
- **Linked Scenario:** `Manual drift in rendered non-architectural decision_log.md is rejected` in [decision_governance.feature](../../../features/decision_governance.feature#L16-L19)
