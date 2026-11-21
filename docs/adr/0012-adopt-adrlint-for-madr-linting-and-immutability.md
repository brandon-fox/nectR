---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Architecture & Meta-Orchestrator
---

# Adopt adrlint for MADR Linting and Immutability

Supersedes [ADR-0000](0000-use-markdown-architectural-decision-records.md).

## Context and Problem Statement

Upstream `pyadr==0.19.0` depends on vulnerable `cleo 0.8.1` (`PYSEC-2022-43178`) and dual-licensed `text-unidecode`, while reimplementing `pyadr` inside `src/nectr/devtools/` violates our Open-Source-First rule by adding custom ADR maintenance burden.

## Considered Options

* **`adrlint` (`polylint/adrlint`, MIT, PyPI) with MADR 4.0 YAML front matter and `adrlint.lock`**
* **Maintain an external personal fork of `pyadr` on GitHub**
* **Run custom `pyadr`-clone code inside `src/nectr/devtools/`**

## Decision Outcome

Chosen option: "`adrlint` (`polylint/adrlint`, MIT, PyPI)", because it is actively maintained with zero CVEs, natively enforces MADR 4.0 structure, sequential numbering, Markdown formatting (`rumdl`), and semantic BLAKE3 immutability hashes (`adrlint.lock`), and keeps `src/nectr/devtools/` free of custom ADR engine code. Project-specific verbosity caps and `--allow-proposed` branch checks remain thin policy wrappers in `nectr.devtools.decisions`.

### Consequences

* Good, because nectR deletes bespoke ADR plumbing and delegates MADR lifecycle, formatting, and tamper detection to an upstream MIT OSS tool.
* Bad, because contributors use MADR 4.0 YAML front matter (`status: proposed` -> `accepted`) and run `adrlint lock` after finalizing an ADR.
