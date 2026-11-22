# Design: OpenSpec Feature-Link Validator

## Domain Boundary
Lives in `src/nectr/devtools/spec_links.py` (Developer & Governance Tooling, isolated from `chain`, `contracts`, `services`, `personas`).

## Validation Rules
1. Scan every `spec.md` under `openspec/specs/` and `openspec/changes/` (excluding `archive/`).
2. Reject any line matching `(?i)^\s*(####\s*Scenario:|[-*]\s*\*\*(GIVEN|WHEN|THEN|AND)\*\*)`.
3. Extract Markdown links `[...](...)`, resolve relative to `spec.md.parent`, and require at least one existing `features/*.feature` target and at least one existing `features/steps/*_steps.py` target.
