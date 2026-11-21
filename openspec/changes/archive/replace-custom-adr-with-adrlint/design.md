# Design: OSS `adrlint` Integration & MADR 4.0 Immutability

## Architecture
- **Configuration (`.adrlint.toml`):** Scopes `adrlint` to `dir = "docs/adr"`, `start = 0`, `allow_gaps = false`, locking `statuses = ["accepted", "rejected", "superseded", "deprecated"]` into `adrlint.lock` via BLAKE3 canonical semantic hashes, with `MD013`/`MD033` disabled to match repo Markdown settings.
- **ADR Format (`docs/adr/0000-*.md`..`0012-*.md`):** Standard MADR 4.0 YAML front matter (`status`, `date`, `decision-makers`) at the top of each record; `ADR-0000` is marked `status: superseded by ADR-0012`.
- **Thin Governance Wrapper (`src/nectr/devtools/decisions.py`):**
  - Invokes external `adrlint` (`lint`, `format --check`, `lock --check`) via `validate_adrlint_repo()`.
  - Strips YAML front matter before counting section bullets in `validate_adr_verbosity()`, enforcing `<= 70` lines, `<= 380` words, `# Title <= 70` chars, and `<= 6` bullets per Markdown section.
  - Enforces `--allow-proposed`: `proposed` status ADRs fail `nectr-decisions check` by default (`main`), and succeed only when `--allow-proposed` is passed on WIP branches.
- **Living Index (`src/nectr/devtools/docs_sync.py` + `docs/adr/index.md`):** Consolidates usage instructions and renders `<!-- BEGIN AUTO-ADR-INDEX -->`..`<!-- END AUTO-ADR-INDEX -->` directly from front matter on disk.
