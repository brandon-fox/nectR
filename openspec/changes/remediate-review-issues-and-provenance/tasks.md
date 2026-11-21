# Tasks: `remediate-review-issues-and-provenance`

- [x] 1. **OpenSpec Blueprint:** Author `proposal.md`, `design.md`, `tasks.md`, and delta specs (`decision-governance`, `citation-provenance`, `docs-and-hygiene`).
- [ ] 2. **Phase 1 — RED (BDD + Strict TDD):** Add `@red` Gherkin scenarios and `@pytest.mark.xfail(strict=True)` tests for issues `#5`–`#12`, verify `pytest` + `behave` pass, and commit atomically.
- [ ] 3. **Phase 2 — GREEN (Implementation & Repo Fixes):**
  - [ ] Untrack `HANDOFF.md` (`#5`), remove stray unarchived spec (`B2`), add `.gitattributes` + `pymarkdownlnt` + `types-PyYAML` (`#8`), and split persona extras (`#10`).
  - [ ] Implement zero-CVE MIT `src/nectr/devtools/adr.py` (`#6`), `--allow-proposed`, and `docs/adr/lifecycle_guide.md` (`#11`).
  - [ ] Implement `src/nectr/devtools/citations.py`, `paper/references.yaml`, `paper/lineage.yaml`, and `docs/theory/provenance_lineage.md` (`#7`).
  - [ ] Implement `docs/glossary.md`, IDE-agnostic `README.md` (`#12`), and `src/nectr/devtools/docs_sync.py` (`#9`).
  - [ ] Observe `XPASS(strict)` on `pytest`, remove `@pytest.mark.xfail` and `@red` tags, run full verification gate, and commit atomically.
- [ ] 4. **Phase 3 — Promote & Close:** Promote delta specs to `openspec/specs/`, archive change, update `docs/planning/roadmap.md`, push, and close GitHub Issues `#5`–`#12`.
