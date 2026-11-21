# Design: Dual-Track Decision Governance (`pyadr` MADR + Fast Structured Registry)

## 1. Separation Principle
| Track | Scope | Source of Truth | Tooling & Code Controls |
| :--- | :--- | :--- | :--- |
| **Architectural (ADR)** | Cross-cutting consensus, smart-contract state machines, governance roles, cross-hive bridges, and hexagonal boundaries | `docs/adr/NNNN-*.md` (MADR) | `pyadr` (`AdrCore.check_adr_repo`, `AdrCore.generate_toc`) + `nectr-decisions check-adrs` verbosity budgets |
| **Non-Architectural (`DEC`/`EXP`)** | Hive parameter defaults, citation/research hygiene, workflow rules, and open simulation hypotheses | `docs/planning/decisions.yaml` | Pydantic v2 strict models + `nectr-decisions render` / `nectr-decisions check` sync gate |

## 2. MADR Verbosity & Length Constraints (`src/nectr/devtools/decisions.py`)
To prevent bloated architecture prose while retaining `pyadr` compatibility (`# Title`, `* Status: accepted`, `* Date: YYYY-MM-DD`):
- **Max Lines per ADR:** `70` lines (`MAX_ADR_LINES = 70`)
- **Max Words per ADR:** `380` words (`MAX_ADR_WORDS = 380`)
- **Max H1 Title Length:** `70` characters (`MAX_ADR_TITLE_CHARS = 70`)
- **Max Bullets per Section:** `6` bullet items (`MAX_ADR_SECTION_BULLETS = 6`)
- **Required MADR Headings (for `0001+`):** `## Context and Problem Statement`, `## Considered Options`, `## Decision Outcome` (`0000` retains Michael Nygard's compact `Context`/`Decision`/`Consequences` bootstrap per `pyadr init`).
- **TOC Sync:** `docs/adr/index.md` MUST byte-match `pyadr toc` output (normalized to LF).

## 3. Fast Decision Registry Schema (`docs/planning/decisions.yaml`)
Validated via Pydantic v2 (`ConfigDict(extra="forbid")`):
- `DecisionEntry` (`DEC-NNN`):
  - `id`: `^DEC-[0-9]{3}$` (unique, monotonically ordered)
  - `category`: `Enum["parameter-default", "research-hygiene", "workflow-policy", "security-oss"]`
  - `status`: `Enum["locked", "superseded", "deprecated"]`
  - `title`: `10..60` chars
  - `decision`: `15..180` chars (concise single-sentence rule)
  - `owner_agent`: one of the 8 Domain Builder Agents or `meta-orchestrator`
  - `related_adr`: optional `docs/adr/NNNN-*.md` path (verified to exist on disk)
  - `openspec_ref`: optional `openspec/...` path (verified to exist on disk)
- `ExperimentEntry` (`EXP-NNN`):
  - `id`: `^EXP-[0-9]{3}$`
  - `status`: `Enum["open-simulation", "validated", "rejected"]`
  - `title`: `10..60` chars
  - `hypothesis`: `15..180` chars
  - `risk_note`: `10..160` chars
  - `owner_agents`: non-empty list of Domain Builder Agents

## 4. CLI & Hook Integration
- Entry point `nectr-decisions` (`python -m nectr.devtools.decisions`):
  - `nectr-decisions render` — validates `decisions.yaml` and writes `docs/planning/decision_log.md`.
  - `nectr-decisions add` — appends a validated `DEC-NNN` or `EXP-NNN` entry and re-renders `decision_log.md`.
  - `nectr-decisions check` — runs full registry schema validation, verifies `decision_log.md` is byte-in-sync with `decisions.yaml`, executes `pyadr` repo & TOC verification, and enforces MADR verbosity limits.
- Wired into `.pre-commit-config.yaml` and `.githooks/pre-commit`.
