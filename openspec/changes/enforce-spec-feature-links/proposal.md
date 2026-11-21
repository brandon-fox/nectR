# Proposal: Enforce OpenSpec-to-Feature Linking & Block Hardcoded Scenarios

## Why
OpenSpec `spec.md` files must state requirement intent and invariants while linking directly to executable Behave `.feature` and `features/steps/*_steps.py` files. Without automated validation, agents can accidentally duplicate Given/When/Then scenarios inside `spec.md` or leave specs unlinked from acceptance tests.

## Scope
- `src/nectr/devtools/spec_links.py` (validator + CLI)
- `.agents/skills/openspec-bdd-tdd/scripts/run_bdd_tdd_gate.py`
- `.agents/skills/openspec-bdd-tdd/references/openspec_tdd_checklist.md`
- `.githooks/pre-commit`, `.pre-commit-config.yaml`, `.github/workflows/license-and-security-scan.yml`
- `openspec/changes/split-madr-and-decision-registry/specs/decision-governance/spec.md`
