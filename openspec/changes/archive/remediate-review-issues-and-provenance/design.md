# Design: Devtools Governance, Citation Provenance & Living Docs Automation

## 1. Zero-CVE MIT `pyadr` Replacement & Persona Extras (`#6`, `#10`, `#11`)
- `src/nectr/devtools/adr.py`: Pure-stdlib, MIT-attributed replacement for `pyadr` implementing `init`, `config`, `new`/`propose`, `accept`, `reject`, `toc`, and `check-adr-repo [--allow-proposed]`.
- `pyproject.toml`: Split optional dependencies into `test`, `lint`, `security`, `docs`, `research`, and `dev = ["nectr[test,lint,security,docs]"]`, with zero CVEs and zero Artistic/GPL dependencies.

## 2. Citation & Provenance Chain-of-Custody (`#7`)
- `paper/references.yaml` & `paper/lineage.yaml` validated by `src/nectr/devtools/citations.py` (`nectr-citations`):
  - Enforces banned-domain blacklist, `>= 70%` peer-reviewed ratio floor, archival/DOI presence, and clean plagiarism-screen status.
  - Builds a `networkx.DiGraph` (`Source -> Theory -> Decision -> Code/Test`), computes transitive blast radius for tainted references, and renders `docs/theory/provenance_lineage.md`.

## 3. Living Docs, Glossary & Formatting Controls (`#5`, `#8`, `#9`, `#12`)
- `.gitattributes` enforces LF endings; `ruff format --check` and `pymarkdownlnt` guard formatting in hooks and CI.
- `docs/glossary.md` defines `MV=PQ`, `PoUW-PoW`, and all core domain terms; `README.md` removes IDE/skill assumptions and syncs bounded-context spaces via `nectr-docs`.
- `src/nectr/devtools/docs_sync.py` (`nectr-docs`) validates zero orphan pages under `docs/` and deterministic ADR `nav:` synchronization in `mkdocs.yml`.
