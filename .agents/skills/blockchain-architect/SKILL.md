---
name: blockchain-architect
description: >-
  Guides implementation and verification of the private nectR PoUW-PoW blockchain,
  the 5 deterministic smart contracts, and the Hive Service Layer. Use when
  designing, implementing, or reviewing src/nectr/chain/, src/nectr/contracts/,
  src/nectr/services/, or docs/architecture/.
---

# nectR Blockchain, Smart Contracts & Service Layer

Follow this workflow when building or reviewing nectR's core blockchain, contracts, and service layer.

## Steps

1. **Review Contract & Service Specifications:** Consult [contracts_and_services_spec.md](./references/contracts_and_services_spec.md) for the 5 deterministic smart contracts, state transitions, and Hive Service Layer interfaces.
2. **Respect DDD Boundaries:** Keep `src/nectr/chain/` free of `nectr.contracts` and `nectr.services` imports; keep `src/nectr/contracts/` deterministic and transport-agnostic.
3. **Run Architecture Gate:** Execute [verify_architecture_gate.py](./scripts/verify_architecture_gate.py):
   ```bash
   uv run python .agents/skills/blockchain-architect/scripts/verify_architecture_gate.py
   ```

## Validation

- Confirm `verify_architecture_gate.py` exits `0` (all contract/invariant tests pass and DDD import boundary checks report zero violations).
