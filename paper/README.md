# nectR Academic Manuscript Workspace

This directory holds the formal publication manuscript, verified bibliography, and provenance chain-of-custody DAG owned by `sci-research-agent`:

- `nectR_whitepaper.md`: Master academic paper combining honeybee (*Apis mellifera*) biomimicry, closed-loop monetary game theory, and Agent-Based Computational Economics (ACE) results from `experiments/`.
- [`references.yaml`](references.yaml): Schema-validated primary bibliography (`>= 70%` peer-reviewed floor, banned-domain guard, DOI/URL custody) verified by `uv run nectr-citations check`.
- [`lineage.yaml`](lineage.yaml): Directed acyclic provenance graph tracing `Sources -> Theory -> ADRs/Decisions -> Code & Tests`.

## Six Foundational Deep Research Inputs

The manuscript synthesizes the six deep research reports archived in `docs/theory/research/`:

1. [`federated_barter_tokenomics.md`](../docs/theory/research/federated_barter_tokenomics.md) — Closed-loop token minting, Comb treasury mechanics ($MV=PQ$), and graph-theoretic anti-collusion (`EigenTrust`, Pairwise Discoordination, `COCM`).
2. [`student_tutoring_mechanism_design.md`](../docs/theory/research/student_tutoring_mechanism_design.md) — Campus 15-week semester volatility, OLG lifecycle, 3-tier Queen agency theory, Spence signalling, and university retention ROI.
3. [`biomimetic_hive_economics.md`](../docs/theory/research/biomimetic_hive_economics.md) — *Apis mellifera* behavioral ecology and 1-to-1 differential-equation / state-machine protocol translations.
4. [`permissive_tooling_survey_for_nectR.md`](../docs/theory/research/permissive_tooling_survey_for_nectR.md) — Permissively licensed cryptographic primitives (`PyNaCl`, `rfc8785`, `remerkleable`), `icontract` + `Hypothesis` + `Quint/TLA+` formal verification, and `NetworKit`/`rustworkx`/`Mesa` benchmarks.
5. [`federated_PoUW-PoW_blockchain_infrastructure.md`](../docs/theory/research/federated_PoUW-PoW_blockchain_infrastructure.md) — Outbound NATS Leaf Node + JetStream cross-Hive proof relay, deterministic WAL storage, CQRS graph isolation, transcript-oracle `PoUW-PoW`, and Kurtosis + Pumba/Toxiproxy + Perses testbeds.
6. [`nectR_funding_and_pilot_strategy.md`](../docs/theory/research/nectR_funding_and_pilot_strategy.md) — Top 15 non-dilutive academic/DPG grant targets (NSF PESOSE, IUSE, Future CoRe, RSF, Sloan, EF ESP, Sovereign Tech Agency), Zero-PII FERPA/GDPR/Title IV compliance, LTI 1.3/HECVAT 4.1.6, and Apereo Foundation governance.
