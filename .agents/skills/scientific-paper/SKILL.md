---
name: scientific-paper
description: >-
  Guides authoring of the published academic whitepaper, formal game-theory
  proofs, honeybee biomimetic mappings, and empirical simulation analyses. Use
  when authoring or reviewing paper/nectR_whitepaper.md or docs/theory/*.md.
---

# Scientific Paper & Biomimetic Theory

Follow this workflow when writing or updating `paper/nectR_whitepaper.md` or `docs/theory/*.md`.

## Steps

1. **Follow Formalism Rubric:** Ensure every section, equation, and *Apis mellifera* mapping conforms to [biomimetic_formalism_rubric.md](./references/biomimetic_formalism_rubric.md).
2. **Trace Mechanisms to Code & Telemetry:** Link every formal equation to implemented contracts/chain modules and reproducible outputs in `experiments/`.
3. **Verify Docs & Hygiene:** Run [verify_theory_docs.py](./scripts/verify_theory_docs.py):
   ```bash
   uv run python .agents/skills/scientific-paper/scripts/verify_theory_docs.py
   ```

## Validation

- Confirm `verify_theory_docs.py` exits `0` (`mkdocs build --strict`, `detect-secrets-hook`, and local-path checks all pass).
