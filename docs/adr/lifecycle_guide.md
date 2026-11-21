# Architecture Decision Records (MADR) Workflow Guide

Architectural decisions in **nectR** use the MADR template managed by our zero-CVE pure-MIT `pyadr` CLI (`nectr.devtools.adr`).

## `.adr` Configuration

The repository root [`.adr`](https://github.com/brandon-fox/nectR/blob/main/.adr) file supports one section and key:

```ini
[adr]
records-dir = docs/adr
```

(`pyadr` intentionally reads only `records-dir` from `.adr`; verbosity thresholds and fast non-architectural registries live in `src/nectr/devtools/decisions.py` and `docs/planning/decisions.yaml`.)

## How `proposed` ADRs & Status Buckets Work

`pyadr` defines five ADR lifecycle statuses:

- **`proposed`** (`XXXX-<slug>.md`): Created by `uv run pyadr new "<Title>"`. Because `proposed` ADRs are temporary pre-merge drafts, `docs/adr/index.md` groups them under **`Records with non-standard statuses` -> `### Status proposed`**.
  - On **`main`** (default `pyadr check-adr-repo` / `nectr-decisions check`), `proposed` ADRs are rejected so unfinished architectural drafts cannot land on `main`.
  - On **feature branches**, pass `--allow-proposed` (`uv run pyadr check-adr-repo --allow-proposed` or `uv run nectr-decisions check-adrs --allow-proposed`).
- **`accepted`**, **`rejected`**, **`superseded`**, **`deprecated`** (`NNNN-<slug>.md`): Finalized via `uv run pyadr accept --toc` or `uv run pyadr reject --toc`, which assigns the next sequential 4-digit ID and updates [index.md](index.md).

## Verbosity Limits

Every MADR file is code-checked against: `<= 70` lines, `<= 380` words, H1 title `<= 70` chars, and `<= 6` bullets per section.
