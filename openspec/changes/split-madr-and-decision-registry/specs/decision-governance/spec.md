# Delta Specification: Dual-Track Decision Governance (`ADDED`)

## ADDED Requirements

### Requirement: MADR Architectural Decision Records Managed by `pyadr`
All structural, cross-cutting architectural decisions SHALL be stored as individual Markdown Architectural Decision Records (MADR) in `docs/adr/NNNN-<slug>.md`, configured by `.adr` and validated by `pyadr` (`AdrCore.check_adr_repo`) with an auto-generated `docs/adr/index.md` table of contents (`pyadr toc`).

#### Scenario: Repository ADRs pass `pyadr` structure and TOC synchronization checks
- **GIVEN** the `docs/adr/` directory configured in `.adr`
- **WHEN** `nectr-decisions check` runs
- **THEN** `pyadr` repository validation SHALL pass with unique 4-digit IDs, matching title slugs, and `accepted` status
- **AND** `docs/adr/index.md` SHALL match the output of `pyadr toc`.

### Requirement: Strict ADR Length and Verbosity Limits
Every ADR in `docs/adr/` (excluding `template.md` and `index.md`) SHALL obey automated verbosity budgets: at most `70` lines, at most `380` words, an H1 title of at most `70` characters, and at most `6` bullet items per Markdown section.

#### Scenario: Overly verbose ADR is rejected by code-level controls
- **GIVEN** an ADR file in a temporary ADR directory exceeding `70` lines or `380` words
- **WHEN** the ADR verbosity validator inspects the directory
- **THEN** validation SHALL fail with a `DecisionGovernanceError` naming the verbosity limit exceeded.

### Requirement: Tool-Managed Fast Non-Architectural Decision Log
Non-architectural decisions (`DEC-NNN`) and open experimental hypotheses (`EXP-NNN`) SHALL be defined in `docs/planning/decisions.yaml`, validated against strict Pydantic field-length and cross-reference schemas, and deterministically rendered to `docs/planning/decision_log.md`.

#### Scenario: Hand-edited drift in `decision_log.md` or verbose YAML entry is rejected
- **GIVEN** a validated `docs/planning/decisions.yaml` registry and rendered `docs/planning/decision_log.md`
- **WHEN** a manual edit introduces drift into `decision_log.md` or an entry exceeds `180` characters
- **THEN** `nectr-decisions check` SHALL fail and report the exact schema or synchronization violation.
