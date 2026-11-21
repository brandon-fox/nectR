# Proposal: Split MADR Architecture Decision Records (`pyadr`) & Fast Non-Architectural Decision Registry

## Why
Currently, `docs/planning/decision_log.md` mixes structural protocol/system architecture invariants (`D-01`–`D-10`) with tunable economic presets, operational rules, and open experimental hypotheses (`EXP-01`) inside a hand-edited Markdown table with zero schema validation, lifecycle tooling, or verbosity guards.

To scale multi-agent development cleanly alongside OpenSpec:
1. **Architectural Decisions (ADRs)** MUST be separated into concise **MADR** records in `docs/adr/`, managed by **`pyadr`** (`pyadr check-adr-repo`, `pyadr toc` -> `docs/adr/index.md`), with strict code-enforced limits on line count, word count, title length, and section verbosity.
2. **Non-Architectural Decisions** (tunable Hive parameter presets, research/citation rules, workflow policies, and open simulation experiments) MUST live in a fast, structured, machine-validated registry (`docs/planning/decisions.yaml`) managed by Pydantic v2 + CLI tooling (`nectr-decisions`) that deterministically renders and verifies `docs/planning/decision_log.md`.

## Bounded Contexts & Paths Affected
- **Developer & Governance Tooling (`src/nectr/devtools/`):** Isolated outside the 4 core domain contexts (`chain`, `contracts`, `services`, `personas`).
- **ADR Repository (`.adr`, `docs/adr/`):** MADR records `0000`–`0007` + `pyadr`-generated `index.md`.
- **Fast Decision Registry (`docs/planning/decisions.yaml`, `docs/planning/decision_log.md`):** Canonical YAML source + auto-rendered Markdown table with ADR & OpenSpec cross-links.
- **Git & CI Controls (`.pre-commit-config.yaml`, `.githooks/pre-commit`, `pyproject.toml`):** Automated pre-commit and test-suite enforcement.

## Acceptance Criteria
1. All architectural decisions from `D-01`–`D-10` and `docs/architecture/` are extracted into `docs/adr/0000-*.md` through `0007-*.md` passing `pyadr check-adr-repo` and `pyadr toc` sync.
2. Every MADR record strictly obeys code-enforced verbosity limits (`<= 70` lines, `<= 380` words, `# Title <= 70` chars, `<= 6` bullets per section).
3. All non-architectural decisions (`DEC-001`..`DEC-007`) and experimental hypotheses (`EXP-001`) are validated in `docs/planning/decisions.yaml` (strict field length caps, unique IDs, valid ADR/OpenSpec paths) and deterministically rendered to `docs/planning/decision_log.md`.
4. Pre-commit hooks, `pytest`, and `behave` reject drifted `decision_log.md` files, invalid YAML entries, broken `pyadr` repos, or overly verbose ADRs.
