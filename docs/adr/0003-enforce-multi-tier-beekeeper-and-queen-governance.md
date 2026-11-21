---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Governance & Institutional Architecture
---

# Enforce Multi-Tier Beekeeper and Queen Governance

## Context and Problem Statement

Local Hive administrators ("Queens") need flexibility to certify tutors, arbitrate disputes, and tune Hive presets, yet allowing Queens to tutor for currency creates self-dealing conflicts—and universities require an auditable institutional emergency override before sponsoring campus deployments.

## Considered Options

* **Three-tier hierarchy: `BEEKEEPER` (logged institutional emergency override), non-tutoring `QUEEN` (local steward tuning Hive presets), and `WORKER`/`LEARNER` peers**
* **Unchecked single-tier Queen governance without institutional override**
* **Allowing Queens to both govern and tutor for `nectR`**

## Decision Outcome

Chosen option: "Three-tier hierarchy (`BEEKEEPER`, non-tutoring `QUEEN`, `WORKER`/`LEARNER`)", because prohibiting `QUEEN` accounts from tutoring eliminates Laffont-Tirole competitive self-dealing, Queen-tunable presets adapt each Hive to local exam rhythms, and on-chain logged `BEEKEEPER` overrides satisfy university compliance and safety requirements.

### Consequences

* Good, because separation of powers is cryptographically enforced in `HiveContractEngine` while institutional sponsors retain transparent emergency control.
* Bad, because faculty or student Queens cannot earn tutoring fees inside a Hive they administer.
