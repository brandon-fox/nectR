# Proposal: Remediate Review Issues (#5-#12), Provenance Chain-of-Custody, and Repo Hygiene

## Why
Code and documentation review surfaced 8 open GitHub issues (`#5`–`#12`) plus 3 CI/repo drift bugs:
1. `HANDOFF.md` remains tracked in Git despite being in `.gitignore` (`#5`), and a stray unarchived OpenSpec file + duplicated pre-commit hook + incomplete SPDX allowlist exist (`B1`–`B3`).
2. `pyadr==0.19.0` carries `cleo 0.8.1` (`PYSEC-2022-43178`) and `text-unidecode` (Artistic/GPL), while `dev` extras bundle unrelated user personas (`#6`, `#10`) and lack `--allow-proposed` branch support and `.adr` documentation (`#11`).
3. Research citations lack machine-enforced quality floors, banned-domain guards, plagiarism screening, and automated downstream provenance regeneration (`#7`).
4. Repo formatting (`LF` `.gitattributes`, Markdown lint, `ruff format`) and living docs (`docs/glossary.md`, IDE-agnostic `README.md`, automated `mkdocs.yml` nav sync) are not yet enforced in code (`#8`, `#9`, `#12`).

## Bounded Contexts & Paths Affected
- `src/nectr/devtools/` (`adr.py`, `decisions.py`, `citations.py`, `docs_sync.py`)
- `paper/references.yaml`, `paper/lineage.yaml`, `docs/theory/provenance_lineage.md`
- `docs/glossary.md`, `docs/adr/lifecycle_guide.md`, `README.md`, `mkdocs.yml`, `.adr`, `.gitattributes`, `pyproject.toml`, `.pre-commit-config.yaml`, `.githooks/pre-commit`, `.github/workflows/license-and-security-scan.yml`
