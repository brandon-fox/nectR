# Institutional Business, Compliance & Campus Sponsorship Proposal

## 1. Executive Summary: The Sponsored Seed Comb Multiplier

Universities spend heavily on centralized tutoring centers with static hourly wages (`$15–$27/hr` base student wages + fixed administrative overhead = **`$42.50/hr` all-in cost**), low peer-to-peer visibility, help-seeking stigma (reaching only `~20%–25%` of undergraduates), and severe bottlenecks during midterms and finals. **nectR** replaces static hourly wage lines with a **Sponsored Seed Comb**:

1. **The Money Multiplier of a Seed Comb:** Every `1 nectR` injected as `RAW_POLLEN` by a sponsoring university first funds a verified gateway session with a Faculty-Queen-Certified Worker Bee, then refines into `LIQUID_NECTR` (`ADR-0006`) that circulates `5x–10x` across the student body at **`0%` P2P transaction fee** and zero marginal wage cost to the university.
2. **Counter-Cyclical Finals Liquidity (`38.0%` $\rightarrow$ `67.4%` Fill Rate):** By recycling Weeks 1–13 idle-balance demurrage (`~2%/month` above a student safety buffer, `DEC-001`) and Queen governance fees into a **Comb Waggle Surge Bounty Pool** that co-pays `60%` of `2.2x` peak Midterm/Finals tutor payouts (`DEC-002`), **nectR** eliminates the Capitol Hill Babysitting Co-op liquidity freeze (`sweeney_1977`).
3. **Verifiable Academic Telemetry & Organic Swarming:** Every transaction records a zero-PII directional service proof (`Course Code`, `Duration >= 25 min`, `Downstream Mastery Lineage`), giving departments real-time visibility into course bottlenecks while veteran student tutors graduate into Founding Queens of daughter Hives (`ADR-0006`, `DEC-012`).

---

## 2. 10,000-Student University ROI & Retention Model

Calibrated against postsecondary tutoring meta-analyses (`nickow_2024`, `leung_2019`), Supplemental Instruction (`SI`) GPA lift benchmarks (`+0.50` course GPA), and National Student Clearinghouse retention data (`student_tutoring_mechanism_design.md`) for a representative 10,000-student university (`2,500-student` freshman cohort at `$25,000` blended net tuition/year):

| Financial & Operational Metric | Traditional Hourly Tutoring Center | nectR Treasury-Seeded P2P Hive | Institutional Impact |
| :--- | :--- | :--- | :--- |
| **Annual Delivered Tutoring Volume** | `6,000 hrs/yr` (capped by center hours & wage budget; `~20%` freshman reach) | **`18,000 hrs/yr`** (`3x` volume via 24/7 stigma-free peer matching & Learn-then-Teach cascades) | **`+200%` tutoring capacity** |
| **Annual Institutional Cost Structure** | `$22.50/hr` loaded student wage (`$18` base + `25%` fringe) + `$120,000` fixed staff = **`$255,000/yr`** | `$25,000` Queen stipends + `$25,000` low-marginal-cost campus perk sinks + `$10,000` audit/ops = **`$60,000/yr`** | **`-76.5%` annual budget** |
| **All-In Institutional Cost per Tutoring Hour** | **`$42.50 / hr`** | **`$3.33 / hr`** | **`-92.2%` cost / delivered hour** |
| **Break-Even Retained Freshmen (`$25K` Net Tuition)** | `10.20 students` (`0.41%` of cohort) | **`2.40 students`** (`0.10%` of a 2,500-student freshman cohort) | **`4.25x` lower break-even bar** |
| **Projected Retention Revenue (`+3 pp` lift on `1,000` newly reached freshmen)** | Baseline (`0` incremental reach) | **`30 retained students = $750,000` Year-1 net tuition** (`$2.25M` 3-year LTV) | **`1,150%` Year-1 Net ROI** |

### 2.1 Closing the Overlapping-Generations (`OLG`) Loop: 3-Door Senior Graduation Sinks (`DEC-004`)

To prevent upperclassmen from graduating with unspent token surpluses (which would drain `~2,500 tokens/yr` per 250-student graduating class), **nectR** clears Senior balances across three institutional off-ramps (`ADR-0006`):

1. **Credential Lock & Daughter-Hive Queen Staking (`40%` / `1,000 tokens/yr`):** Converts surplus into verified transcript honors, portable career micro-credentials, or Honey Engorgement seed stakes (`6.25x–8.0x` Honey-to-Wax burn, `DEC-012`) to found a daughter Hive.
2. **Low-Marginal-Cost Campus Perk Sink (`35%` / `875 tokens/yr`):** Redeems balances for non-cash university perks (priority course registration, lab time, parking passes, campus event tickets) that carry near-zero cash liability for the Bursar.
3. **Pay-It-Forward Freshman Scholarship Bounty Pool (`25%` / `625 tokens/yr` + Dormant Alumni Sweep):** Recycles graduating and dormant alumni balances directly into incoming freshman `RAW_POLLEN` vouchers and Finals Waggle surge subsidies.

---

## 3. University Compliance, Legal, Tax & CISO Procurement Architecture (`ADR-0015`)

As detailed in [`nectR_funding_and_pilot_strategy.md`](../theory/research/nectR_funding_and_pilot_strategy.md), university pilots must clear four institutional compliance gates before onboarding students:

| Institutional Gate | Regulatory / Procurement Standard | nectR Architectural Solution (`ADR-0015`, `DEC-015`) |
| :--- | :--- | :--- |
| **1. Educational Privacy & Right to Erasure** | **FERPA** (20 U.S.C. § 1232g) & **EDPB GDPR** (Right to Rectification/Erasure vs. Blockchain Immutability) | **Hybrid Zero-PII Architecture:** 100% of student names, emails, course enrollments, and session notes reside in a campus-hosted relational DB supporting instant deletion; on-chain blocks store only salted hashes $H(\text{salt} \parallel \text{record\_id})$ or **BBS+ Zero-Knowledge membership proofs** + reusable DPIA template. |
| **2. Bursar, IRS Tax & Financial Aid Firewall** | **IRS Publication 970** (`W-2`/`1099-NEC` taxable service awards) & **Federal Title IV** (`OSFAS` overaward rules) | **Non-Monetary Service-Duration Credit Framing:** Models `LIQUID_NECTR` on Japan's two-mandate organizer-cleared non-monetary service-duration credit framework (`1:1` peer tutoring hours and academic badges, zero cash/gift-card convertibility), or routes tangible stipends strictly through campus Payroll/OSFAS adapters. |
| **3. Campus CISO & LMS Integration** | **EDUCAUSE HECVAT 4 (`v4.1.6`)**, **1EdTech LTI 1.3 (`NRPS` + Deep Linking 2.0)** & **InCommon Shibboleth SAML 2.0** | **100% Wallet Key Abstraction:** Students launch `nectR` directly inside Canvas, Moodle, or Blackboard via LTI 1.3 OIDC/JWT and Shibboleth SSO with automated SCIM/SIS term-rollover deprovisioning; pre-completed HECVAT 4.1.6 workbook ("Core 60" + AI/ML + Privacy tabs). |
| **4. Tech Transfer Office (`TTO`) & Multi-Campus IP** | **Bayh-Dole Act (2 CFR 200.315)**, MIT Policy 13.1 & Multi-University Contributor Governance | **MIT License + DCO 1.1 (`DEC-015`):** Per-commit `Signed-off-by` + SSH signature verification eliminates multi-university Corporate CLA Schedule A legal bottlenecks; graduates from a **Stage 1 Multi-Campus Academic Consortium** (Months 1–12) to **Stage 2 Apereo Foundation `501(c)(3)` Incubation** (Months 12–24+). |

---

## 4. Non-Dilutive Academic & Public-Goods Funding Pipeline (2026–2028)

Rather than launching a speculative public token (which disqualifies campus IT procurement), **nectR** targets non-dilutive federal, philanthropic, and Digital Public Goods (`DPG`) grants cataloged in [`nectR_funding_and_pilot_strategy.md`](../theory/research/nectR_funding_and_pilot_strategy.md):

| Target Window | Funder & Program Solicitation | Award Range | Target Deliverable & Alignment |
| :--- | :--- | :--- | :--- |
| **Jan 20, 2027** | **NSF IUSE: EDU (`NSF 23-510`)** — Capacity / Level 1 | `$200,000` (single) / `$400,000` (multi-campus, 2 yrs) | Single-campus IRB matched-cohort gateway STEM pilot with campus Learning Center co-PI. |
| **Q1 2027 (Primary Track, `DEC-020`)** | **NSF DRMS** & **Russell Sage Foundation (`RSF`)** Pipeline / Presidential (+ **J-PAL North America**) | `$50,000–$200,000` (`RSF`) / `~$185K/yr` (`DRMS`) | **Primary behavioral economics & ACE track** paired with **JASSS / JEBO (`ODD+D`)**: RCT validating `RAW_POLLEN` demurrage, Waggle co-pay, and Spence downstream signalling. |
| **Feb 2027** | **NSF Future CoRe (`CISE`, `NSF 25-543`)** & **Ethereum Foundation `ESP`** (Academic Round / Wishlist) | Up to `$1,000,000` (`CISE`) / `$24K–$250K` (`EF ESP`) | Distributed systems & mechanism design: Transcript-Oracle `PoUW-PoW`, graph anti-collusion bounds, and BBS+ ZK credentials. |
| **Mar 2, 2027** | **NSF PESOSE (`NSF 26-506`, Track 1 Scoping)** & **Alfred P. Sloan Foundation** (Open Source in Science) | Up to `$300,000` (`PESOSE Track 1`) / `$50K–$500K` (`Sloan`) | Open-source ecosystem scoping, LTI 1.3 / Shibboleth / NATS federation security architecture, and campus OSPO governance. |
| **2028 (Stage 2)** | **NSF PESOSE Track 2/3**, **NSF IUSE Level 2/3**, **Horizon Europe (`Cluster 4`)** & **Sovereign Tech Agency** | `$750,000–$2,000,000` (`NSF`) / `EUR 50K–500K` (`STA`) | Multi-campus autonomous daughter-Hive federation (3+ universities) and **Apereo Foundation** incubation. |
