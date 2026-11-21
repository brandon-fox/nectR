# Proposal: Clarify n8n ("k8n") Boundary, Decisions & Milestone 3 Roadmap Options (`add-n8n-workflow-roadmap-decisions`)

## Why
`DEC-009` (`docs/planning/decisions.yaml`) previously rejected `"CrewAI/k8n"` without clarifying `"k8n"` as **`n8n`** (node-based workflow/webhook automation) or detailing how `n8n` and permissive-OSS workflow orchestrators fit into Milestone 3 experimentation while preserving `DEC-009` (deterministic Mesa ABM + ML/RL) and `DEC-007` (MIT-compatible dependency hygiene), complementing [ADR-0013](../../../docs/adr/0013-restrict-crewai-to-isolated-off-chain-peripherals.md) (`DEC-010`, CrewAI isolation).

## Affected Bounded Contexts
- **Planning & Decision Governance (`docs/planning/decisions.yaml`, `docs/planning/decision_log.md`, `docs/planning/roadmap.md`, `docs/adr/`, `adrlint.lock`, `mkdocs.yml`)**
- **Verification & Specs (`openspec/`, `features/decision_governance.feature`, `features/steps/decision_governance_steps.py`, `tests/test_decision_governance.py`)**

## OSS License & CVE Audit
| Tool / Option | License | `DEC-007` Status | Scope in `nectR` |
| --- | --- | --- | --- |
| `n8n` | Sustainable Use License (fair-code) | **Out-of-process only** | Excluded from `pyproject.toml`; external webhook sidecar only |
| `Activepieces` | `MIT` (Community core) | **Approved** | Optional visual webhook orchestrator |
| `Kestra` / `Prefect` | `Apache-2.0` (Core) | **Approved** | Optional batch experiment DAG runners |
| `Temporal` | `MIT` | **Approved** | Optional durable multi-semester workflow engine |
| `CrewAI` | `MIT` | **Approved (isolated)** | Optional off-chain peripheral ([ADR-0013](../../../docs/adr/0013-restrict-crewai-to-isolated-off-chain-peripherals.md)) |

## Acceptance Criteria
1. `DEC-009` remains `locked` to Mesa ABM + Hypothesis (`ADR-0010`) + ML/RL while clarifying `k8n` as `n8n`.
2. `DEC-016` (`workflow-policy`, `locked`) and `EXP-006` (`open-simulation`) define the off-chain webhook boundary, permissive-OSS preference, and hybrid benchmark arm.
3. MADR `0016` (`adrlint` `accepted` + locked in `adrlint.lock`) codifies external workflow automation boundaries and `docs/planning/roadmap.md` expands Milestone 3 with Options A–D.
