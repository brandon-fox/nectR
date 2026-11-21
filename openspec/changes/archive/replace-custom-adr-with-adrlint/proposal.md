# Proposal: Replace Custom `adr.py` with OSS `adrlint` (`polylint/adrlint`)

## Why
Rebuilding `pyadr` inside `src/nectr/devtools/adr.py` violated the Open-Source-First policy and introduced ~440 lines of custom ADR lifecycle code. Upstream `pyadr==0.19.0` also pulls vulnerable `cleo 0.8.1` (`PYSEC-2022-43178`) and dual-licensed `text-unidecode`.

## Decision & Outcome
- Remove `src/nectr/devtools/adr.py`, `.adr`, `docs/adr/template.md`, and `docs/adr/lifecycle_guide.md`.
- Adopt **`adrlint`** (`polylint/adrlint`, `adrlint>=0.5.2` on PyPI, MIT license, zero CVEs) configured via `.adrlint.toml` and `adrlint.lock`.
- Upgrade `docs/adr/0000-*.md`..`0011-*.md` to MADR 4.0 YAML front matter, add `ADR-0012` superseding `ADR-0000`, and consolidate the workflow guide + auto-synced ADR index table inside `docs/adr/index.md` via `nectr-docs`.
- Retain only project-specific verbosity caps and `--allow-proposed` branch gating inside `src/nectr/devtools/decisions.py`, calling `adrlint lint`, `adrlint format --check`, and `adrlint lock --check` via subprocess.
