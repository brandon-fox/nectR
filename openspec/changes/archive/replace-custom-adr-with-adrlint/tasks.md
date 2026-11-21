# Tasks: `replace-custom-adr-with-adrlint`

- [x] 1. **Reopen Issue `#6` & Author OpenSpec Blueprint:** Create `openspec/changes/replace-custom-adr-with-adrlint/` (`proposal.md`, `design.md`, `tasks.md`, `specs/decision-governance/spec.md`).
- [x] 2. **Phase 1 — RED (BDD + Strict TDD):** Add `@red` Gherkin scenario and `@pytest.mark.xfail(strict=True)` test verifying removal of `src/nectr/devtools/adr.py` and adoption of `adrlint`, verify `pytest`/`behave`, and commit atomically.
- [x] 3. **Phase 2 — GREEN (Delete Custom Engine & Adopt `adrlint`):**
  - [x] Remove `src/nectr/devtools/adr.py`, `.adr`, `docs/adr/template.md`, `docs/adr/lifecycle_guide.md`.
  - [x] Add `adrlint>=0.5.2` to `[project.optional-dependencies].lint`, drop `pyadr` script entry in `pyproject.toml`, configure `.adrlint.toml`, and update `.gitattributes`.
  - [x] Migrate `docs/adr/0000-*.md`..`0011-*.md` to MADR 4.0 YAML front matter (`0000` -> `superseded by ADR-0012`), create `0012-adopt-adrlint-for-madr-linting-and-immutability.md`, and generate `adrlint.lock`.
  - [x] Update `docs/adr/index.md`, `src/nectr/devtools/docs_sync.py`, `src/nectr/devtools/decisions.py`, `docs/planning/decisions.yaml`, `.agents/rules/`, hooks, CI, and test suites.
  - [x] Confirm `XPASS(strict)` -> remove `@pytest.mark.xfail` and `@red`, pass full verification suite (`adrlint`, `pip-audit`, `pip-licenses`, `nectr-*`, `ruff`, `mypy`, `pymarkdown`, `mkdocs build --strict`, `pytest`, `behave`), and commit atomically.
- [x] 4. **Phase 3 — Promote & Close:** Promote `openspec/specs/decision-governance/spec.md`, archive change, update `docs/planning/roadmap.md`, push `main`, and close Issue `#6`.
