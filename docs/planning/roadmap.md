# Project Roadmap: The Plan to B+ (v0.1.0 Remediation & Hardening)

> **Notice:** Under the **Structure Freeze** (`AGENTS.md`) adopted for v0.1.0, active project development is strictly scoped to the **Plan to B+** to remediate code-review findings, complete test hardening, and establish release transparency. Long-term horizons and multi-year milestones are documented in the [Product Vision & Three-Horizon North Star](vision.md).

---

## 1. Plan to B+ Executive Summary

The Plan to B+ organizes all current development into five coordinated, parallel workstreams executed with strict Outside-In OpenSpec $\rightarrow$ Behave BDD $\rightarrow$ Strict TDD Red-Green-Refactor discipline and zero git cross-contamination:

| Track | Focus Domain | Key Objectives | Status |
| :--- | :--- | :--- | :--- |
| **Track CA** | Core Contracts & Accounting Invariants | Integer accounting (`micro_nectr`), exact supply conservation, escrow resolution & expiry, Guard Bee mover rejection | In Progress |
| **Track CB** | Hive Service Layer, Authority & Cryptographic Signing | Queen-signed registration commands, Bee Keys registry (`0003`), Ed25519 session signatures, replay nonces | In Progress |
| **Track TL** | Tooling, Developer Experience & CI Parity | Move mypy to pre-push, cross-platform CI venv PATH resolution, PR lifecycle automation, local `nectr` CLI | In Progress |
| **Track HY** | Repository Hygiene, Licensing & Community | MIT License, full community health suite, automated citation audits (`reference-check.md`), smoke-scenario labeling | Completed / Landed |
| **Track DC** | Living Documentation, Transparency & OpenSpec | Structure freeze, plain-language README, OpenSpec wave archiving, signed audit log ADR-0019, assumption labeling | In Progress |

---

## 2. Workstream Breakdown & Deliverables

### Track CA: Core Contracts & Accounting Invariants

- [x] **CA1:** Strict xfail test harness in `tests/test_contracts.py` and `tests/test_services.py` for review findings 1, 3, 4, and 5 (`harden-authority-and-accounting`).
- [x] **CA2:** Migration `0002` integer accounting conversion (`micro_nectr`) with exact supply conservation across 500-round randomized escrow loops.
- [ ] **CA3:** Require dispute state, cap fee < 1, and add escrow expiry returning tokens to original token state (open `hold` PR).
- [ ] **CA4:** Cross-hive migration capital control & Guard Bee verification: unaccepted movers holding target-hive registrations without home Hive sponsorship are rejected upon bridging.
- [ ] **CA5:** Clean test suite verification: removal of all remaining finding xfails and 100% green contract tests.

### Track CB: Hive Service Layer, Authority & Cryptographic Signing

- [ ] **CB1:** Require signed commands and bind roles to keys: Key registry (`bee_public_keys` + per-bee nonce in `HiveSnapshot` & new `bee_keys` table migration `0003`); `bootstrap_sponsored_hive` takes Queens/seed workers public keys; `SignedTransaction` for all state-changing service methods; self-signed `register_bee` creates `LEARNER_BEE` only; settlement requires two identical-payload `SignedTransactions` (learner + tutor); signed bridge between two `HiveServiceLayer` instances; `HiveBlockchain.submit_transaction` accepts only verified `SignedTransactions`; API POST bodies are signed envelopes; simulator uses deterministic test-only signer and epoch timestamps; remove Finding 1 xfail (open `hold` PR).
- [ ] **CB2:** Expose dispute and escrow-cancel commands through `HiveServiceLayer` and API endpoints.
- [ ] **CB3:** Make blocks append-only and verify the chain on load: append-only `hive_blocks`, persist `block_hash`, `verify_chain()` on load raising `ChainIntegrityError` naming bad height, default `difficulty=0`.
- [ ] **CB4:** Compute velocity per epoch and accrue Royal Jelly dividends.

### Track TL: Tooling, Developer Experience & CI Parity

- [x] **TL1:** Keep pre-commit fast and move test suites (`mypy`, `pytest`, `behave --tags=-red`, `mkdocs build --strict`) to `.githooks/pre-push` with CI parity.
- [x] **TL2:** Remove `--check-stale` step from `.github/workflows/pr-lifecycle.yml`.
- [x] **TL3:** Set MIT license metadata and author in `pyproject.toml`.
- [x] **TL4:** Trim runtime dependencies: drop `numpy` and `rich`, move `httpx` to test dependency and `uvicorn` to api extra in `pyproject.toml` and relock.
- [ ] **TL5:** Local developer CLI (`nectr`) commands for node `simulate` and `serve`.
- [ ] **TL6:** Smoke-test `nectr simulate` byte-identical run reproduction.
- [ ] **TL7:** Spec link validation: update `spec_links` devtool to verify scenario names in Gherkin and remove `#L` line anchors.

### Track HY: Repository Hygiene, Licensing & Community Standards

- [x] **HY0:** Read-only repository audit and GitHub repository settings configuration.
- [x] **HY1:** Canonical MIT License file matching `brandon-fox/repo-template`.
- [x] **HY2:** Full community health suite (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CITATION.cff`, and issue/PR templates).
- [x] **HY3:** Automated Crossref REST & URL audit of all 27 references with peer-review breakdown in `paper/reference-check.md`.
- [x] **HY4:** Scripted smoke-scenario annotation for `nectr_sim_baseline_2026` in `paper/references.yaml`.

### Track DC: Living Documentation, Transparency & OpenSpec

- [x] **DC1:** Governance freeze in `AGENTS.md` and superseded banner in `docs/planning/agent_orchestration.md`.
- [x] **DC2:** Plain-language README intro, status badge, personal-capacity notice, and MIT License alignment.
- [x] **DC3:** OpenSpec archiving of 8 merged change proposals and deferral notices on Waves 3–5 proposals.
- [x] **DC4:** Architectural Decision Record `ADR-0019` treating the chain as a signed audit log, superseding `ADR-0007`.
- [x] **DC5:** Explicit labeling of unsourced figures and ROI metrics as planning assumptions; smoke-scenario retitling.
- [x] **DC6:** AI-generated research notices on deep research reports and explicit framing of the honeybee design metaphor.
- [x] **DC7:** Roadmap alignment with the Plan to B+ and extraction of multi-horizon vision into `vision.md`.
- [ ] **DC8:** Quick Start guide in `README.md` following delivery of the `nectr` CLI (post-TL5).
- [ ] **DC9:** Final v0.1.0 claim-to-code alignment, known limits documentation, and release polish.

---

## 3. Long-Term Horizons & Subsequent Milestones

For details on post-v0.1.0 development—including Milestone 2 (Federated NATS Infrastructure), Milestone 3 (Full Mesa ABM Sweeps over frameworks like CrewAI/n8n, with permissive workflow options Activepieces, Kestra, Prefect, Temporal, and EXP-006 benchmark arms), Milestone 4 (Published Academic Paper), and Milestone 5: University IRB Sandbox Pilot, LTI 1.3 Integration & Apereo Foundation Incubation—refer to the [Product Vision & Three-Horizon North Star](vision.md).
