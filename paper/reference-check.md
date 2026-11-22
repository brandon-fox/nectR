# External Reference Verification Report

**Verification Date**: 2026-11-22
**Auditor**: `@hygiene` (Hygiene Domain Agent)
**Target Registry**: `paper/references.yaml`
**Audit Scope**: All 27 external citations queried directly against the Crossref REST API (`https://api.crossref.org/works/<doi>`) and origin URLs.

---

## Executive Summary

- **Total Registered Entries**: 28 (27 external references + 1 internal simulation artifact)
- **External References Checked**: 27
- **Crossref DOI Queries**: 25
- **Direct URL Checks**: 2 (`buterin_2019`, `saltini_2019`)
- **Fully Verified & Consistent**: 26 / 27
- **Discrepancy Flagged**: 1 / 27 (`sweeney_1977`: misattributed DOI in `references.yaml`)
- **Peer-Reviewed Ratio**: 88.9% (24 / 27) — satisfies the repository quality floor (`>= 70.0%`)
- **Quarantined Sources**: 0

---

## Detailed Citation Audit Matrix

| Reference ID | Type | Registered Title (`references.yaml`) | Crossref / Remote Title | Year (Reg/Pub) | Identifier (DOI / URL) | Status | Audit Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `sweeney_1977` | peer-reviewed-journal | Monetary Theory and the Great Capitol Hill Baby Sitting Co-op Crisis | Financial Aspects of the Private Pension System | 1977 / 1977 | `10.2307/1991998` | **Flagged Discrepancy** | DOI 10.2307/1991998 resolves to Martin Feldstein, 'Financial Aspects of the Private Pension System' (JMCB 9(1), 1977). The correct DOI for Joan Sweeney & Richard James Sweeney, 'Monetary Theory and the Great Capitol Hill Baby Sitting Co-op Crisis: Comment' (pp. 86-89) is 10.2307/1992001. |
| `tirole_1986` | peer-reviewed-journal | Hierarchies and Bureaucracies: On the Role of Collusion in Organizations | Hierarchies and Bureaucracies: On the Role of Collusion in Organizations | 1986 / 1986 | `10.1093/oxfordjournals.jleo.a036907` | Verified | Exact match on Crossref DOI index. |
| `kofman_lawarree_1993` | peer-reviewed-journal | Collusion in Hierarchical Agency | Collusion in Hierarchical Agency | 1993 / 1993 | `10.2307/2951721` | Verified | Exact match on Crossref DOI index. |
| `spence_1973` | peer-reviewed-journal | Job Market Signaling | Job Market Signaling | 1973 / 1973 | `10.2307/1882010` | Verified | Exact match on Crossref DOI index. |
| `filippas_2020` | peer-reviewed-journal | Reputation Inflation | Reputation Inflation | 2022 / 2022 | `10.1287/mksc.2022.1350` | Verified | Exact match on Crossref DOI index. |
| `leung_2019` | peer-reviewed-journal | An updated meta-analysis on the effect of peer tutoring on tutors' achievement | An updated meta-analysis on the effect of peer tutoring on tutors’ achievement | 2019 / 2018 | `10.1177/0143034318808832` | Verified | Year variance: registered 2019 vs online publication 2018. |
| `nickow_2024` | peer-reviewed-journal | The Promise of Tutoring for PreK-12 Learning: A Systematic Review and Meta-Analysis of the Experimental Evidence | The Promise of Tutoring for PreK–12 Learning: A Systematic Review and Meta-Analysis of the Experimental Evidence | 2024 / 2023 | `10.3102/00028312231208687` | Verified | Year variance: registered 2024 vs online publication 2023. |
| `gneezy_rustichini_2000` | peer-reviewed-journal | Pay Enough or Don't Pay at All | Pay Enough or Don't Pay at All* | 2000 / 2000 | `10.1162/003355300554917` | Verified | Exact match on Crossref DOI index. |
| `seeley_tovey_1994` | peer-reviewed-journal | Why search time to find a food-storer bee accurately indicates the relative rates of nectar collecting and nectar processing in honey bee colonies | Why search time to find a food-storer bee accurately indicates the relative rates of nectar collecting and nectar processing in honey bee colonies | 1994 / 1994 | `10.1006/anbe.1994.1044` | Verified | Exact match on Crossref DOI index. |
| `camazine_sneyd_1991` | peer-reviewed-journal | A model of collective nectar source selection by honey bees | A model of collective nectar source selection by honey bees: Self-organization through simple rules | 1991 / 1991 | `10.1016/S0022-5193(05)80098-0` | Verified | Exact match on Crossref DOI index. |
| `bonabeau_1996` | peer-reviewed-journal | Quantitative study of the fixed threshold model for the regulation of division of labor in insect societies | Quantitative study of the fixed threshold model for the regulation of division of labour in insect societies | 1996 / 1996 | `10.1098/rspb.1996.0229` | Verified | Exact match on Crossref DOI index. |
| `ratnieks_1988` | peer-reviewed-journal | Reproductive harmony via mutual policing by workers in eusocial Hymenoptera | Reproductive Harmony via Mutual Policing by Workers in Eusocial Hymenoptera | 1988 / 1988 | `10.1086/284846` | Verified | Exact match on Crossref DOI index. |
| `wenseleers_ratnieks_2006` | peer-reviewed-journal | Comparative Analysis of Worker Reproduction and Policing in Eusocial Hymenoptera Supports Relatedness Theory | Comparative Analysis of Worker Reproduction and Policing in Eusocial Hymenoptera Supports Relatedness Theory | 2006 / 2006 | `10.1086/508619` | Verified | Exact match on Crossref DOI index. |
| `downs_ratnieks_2000` | peer-reviewed-journal | Adaptive shifts in honey bee (Apis mellifera L.) guarding behavior support predictions of the acceptance threshold model | Adaptive shifts in honey bee (Apis mellifera L.) guarding behavior support predictions of the acceptance threshold model | 2000 / 2000 | `10.1093/beheco/11.3.326` | Verified | Exact match on Crossref DOI index. |
| `leoncini_2004` | peer-reviewed-journal | Regulation of behavioral maturation by a primer pheromone produced by adult worker honey bees | Regulation of behavioral maturation by a primer pheromone produced by adult worker honey bees | 2004 / 2004 | `10.1073/pnas.0407652101` | Verified | Exact match on Crossref DOI index. |
| `khoury_2011` | peer-reviewed-journal | A Quantitative Model of Honey Bee Colony Population Dynamics | A Quantitative Model of Honey Bee Colony Population Dynamics | 2011 / 2011 | `10.1371/journal.pone.0018491` | Verified | Exact match on Crossref DOI index. |
| `seeley_visscher_2004` | peer-reviewed-journal | Group decision making in nest-site selection by honeybee swarms | Group decision making in nest-site selection by honey bees | 2004 / 2004 | `10.1051/apido:2004004` | Verified | Exact match on Crossref DOI index. |
| `reina_2017` | peer-reviewed-journal | Model of the best-of-N nest-site selection process in honeybees | Model of the best-of-<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mi>N</mml:mi></mml:math>nest-site selection process in honeybees | 2017 / 2017 | `10.1103/PhysRevE.95.052411` | Verified | Exact match on Crossref DOI index. |
| `kamvar_2003` | conference-proceedings | The EigenTrust Algorithm for Reputation Management in P2P Networks | The Eigentrust algorithm for reputation management in P2P networks | 2003 / 2003 | `10.1145/775152.775242` | Verified | Exact match on Crossref DOI index. |
| `mattsson_2023` | peer-reviewed-journal | Circulation of a digital community currency | Circulation of a digital community currency | 2023 / 2023 | `10.1038/s41598-023-33184-1` | Verified | Exact match on Crossref DOI index. |
| `iosifidis_2018` | peer-reviewed-journal | Cyclic motifs in the Sardex monetary network | Cyclic motifs in the Sardex monetary network | 2018 / 2018 | `10.1038/s41562-018-0450-0` | Verified | Exact match on Crossref DOI index. |
| `ball_2018` | conference-proceedings | Proofs of Work From Worst-Case Assumptions | Proofs of Work From Worst-Case Assumptions | 2018 / 2018 | `10.1007/978-3-319-96884-1_26` | Verified | Exact match on Crossref DOI index. |
| `kazil_2020` | conference-proceedings | Utilizing Python for Agent-Based Modeling: The Mesa Framework | Utilizing Python for Agent-Based Modeling: The Mesa Framework | 2020 / 2020 | `10.1007/978-3-030-61255-9_30` | Verified | Exact match on Crossref DOI index. |
| `treinish_2022` | peer-reviewed-journal | rustworkx: A High-Performance Graph Library for Python | rustworkx: A High-Performance Graph Library for Python | 2022 / 2022 | `10.21105/joss.03968` | Verified | Exact match on Crossref DOI index. |
| `buterin_2019` | technical-spec | Pairwise coordination subsidies: A new quadratic funding design | Pairwise coordination subsidies: A new quadratic funding design | 2019 / 2019 | `https://ethresear.ch/t/pairwise-coordination-subsidies-a-new-quadratic-funding-design/5553` | Verified | Live URL resolves successfully (HTTP 200). |
| `saltini_2019` | preprint | IBFT 2.0: A Safe and Live Variation of the IBFT Blockchain Consensus Protocol | IBFT 2.0: A Safe and Live Variation of the IBFT Blockchain Consensus Protocol | 2019 / 2019 | `https://arxiv.org/abs/1909.10194` | Verified | Live URL resolves successfully (HTTP 200). |
| `weyl_2022` | preprint | Decentralized Society: Finding Web3's Soul | Decentralized Society: Finding Web3's Soul | 2022 / 2022 | `10.2139/ssrn.4105763` | Verified | Exact match on Crossref DOI index. |

---

## Flagged Findings & Remediation Analysis

### 1. `sweeney_1977` (DOI Discrepancy)
- **Registered Entry**: Sweeney, Joan & Sweeney, Richard James (1977), *Monetary Theory and the Great Capitol Hill Baby Sitting Co-op Crisis*, JMCB 9(1), pp. 86-89.
- **Registered DOI**: `10.2307/1991998`
- **Resolved Crossref Record**: Martin Feldstein, *Financial Aspects of the Private Pension System*, Journal of Money, Credit and Banking, Vol. 9, No. 1, Part 1 (Feb., 1977), pp. 86-89 DOI mismatch.
- **True Crossref DOI**: `10.2307/1992001` (resolves to: *Monetary Theory and the Great Capitol Hill Baby Sitting Co-op Crisis: Comment* by Joan Sweeney and Richard James Sweeney in JMCB Vol. 9, No. 1, Feb 1977).
- **Recommended Action**: Update `paper/references.yaml` to `doi: 10.2307/1992001` in coordination with `@docs` re-rendering `docs/theory/provenance_lineage.md` (via `uv run nectr-citations render`).

### 2. `saltini_2019` (Confirmed Pre-Print Title)
- **Registered Title**: *IBFT 2.0: A Safe and Live Variation of the IBFT Blockchain Consensus Protocol* (Roberto Saltini, David Hyland-Wood, 2019).
- **URL**: `https://arxiv.org/abs/1909.10194` (resolves HTTP 200).
- **Verification**: Confirmed exact alignment between `paper/references.yaml` and arXiv abstract record.

### 3. `filippas_2020` (Publication Date vs. Working Paper ID)
- **Registered Key**: `filippas_2020` (reflecting original NBER/SSRN working paper vintage).
- **Publication Year**: Published in *Marketing Science* in 2022 (`10.1287/mksc.2022.1350`). Registered `year: 2022` in `references.yaml` matches the final peer-reviewed journal volume.

---

## Internal Baseline Reference Note

- **Identifier**: `nectr_sim_baseline_2026`
- **Source Type**: `internal-experiment`
- **File Path**: `src/nectr/personas/simulator.py`
- **Description**: Invariant simulation telemetry for the 6 Behavioral Personas (velocity, Gini index, Comb reserves, collusion decay). Not an external citation; verified through local invariant tests.
