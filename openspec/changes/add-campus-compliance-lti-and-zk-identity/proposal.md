# Proposal: Add Zero-PII FERPA/GDPR Boundary, LTI 1.3 / Shibboleth SSO & Title IV Compliance Perimeter (`add-campus-compliance-lti-and-zk-identity`)

## Why
As established in `nectR_funding_and_pilot_strategy.md` and `federated_PoUW-PoW_blockchain_infrastructure.md`, converting `nectR` from an academic simulation testbed into a funded university pilot requires clearing four institutional gates:
1. **FERPA & GDPR Zero-PII Ledger Boundary (`ADR-0015`):** Under FERPA (protected student education records) and EDPB GDPR guidance (right to rectification/erasure vs. blockchain immutability), zero student names, campus IDs, emails, grades, or raw transcripts may ever touch the blockchain ledger. All PII must reside in a campus-controlled relational database supporting erasure, while the chain records only salted/peppered one-way commitments or **BBS+ / Groth-Kohlweiss Zero-Knowledge membership proofs** anchored to **eduGAIN / InCommon Shibboleth** certificates.
2. **IRS Pub 970 & Federal Title IV Financial Aid Firewall (`ADR-0015`):** To prevent `LIQUID_NECTR` tutoring credits from triggering IRS W-2/1099-NEC wage reporting or federal Title IV financial-aid overaward penalties, student-facing `LIQUID_NECTR` redemptions must operate in a strict **Non-Monetary Service-Duration Credit Mode** (modeled on Japan's two-mandate organizer-cleared time-credit framework) or route any tangible university-sponsored stipends through campus Payroll/OSFAS adapters.
3. **Campus CISO & LMS Standards (HECVAT 4.1.6, 1EdTech LTI 1.3 & Shibboleth SAML 2.0):** Universities require **1EdTech LTI 1.3 & LTI Advantage** (OIDC/JWT launch, Names and Role Provisioning Services `NRPS` for course rosters, Deep Linking 2.0 for Canvas/Moodle/Blackboard), **InCommon Shibboleth SAML 2.0 SSO** with SCIM/SIS term-rollover deprovisioning (100% wallet key abstraction for students), and a completed **EDUCAUSE HECVAT 4 (v4.1.6)** workbook.
4. **Inbound IP & Multi-Campus OSS Governance (`DEC-015`):** Enforce **MIT License + Developer Certificate of Origin (DCO 1.1)** with SSH-signed commits to avoid multi-university Corporate CLA bottlenecks, transitioning from a Stage 1 Multi-Campus Academic Maintainer Consortium to Stage 2 **Apereo Foundation** 501(c)(3) incubation.

## Affected Bounded Contexts
- **Hive Service Layer (`src/nectr/services/`)** — `CampusIdentityPort`, `LtiAdvantageRosterPort`, `ZeroPiiCommitmentGuard`, and `TitleIvComplianceFirewall`.
- **Institutional Business & Compliance (`business/`, `docs/business/`)** — HECVAT 4.1.6 readiness matrix, DPIA template, and non-dilutive grant packages (NSF PESOSE, IUSE, Future CoRe, DRMS, RSF/J-PAL, Sloan, EF ESP, Sovereign Tech Agency).
- **Architectural Decision:** [ADR-0015](../../../docs/adr/0015-enforce-zero-pii-ferpa-gdpr-and-title-iv-campus-compliance.md).

## Acceptance Criteria
1. `ZeroPiiCommitmentGuard` rejects any transaction or log payload containing raw email addresses, SSNs/student IDs, or unhashed PII fields before mempool submission.
2. `CampusIdentityPort` abstracts Ed25519 wallet custody behind Shibboleth SAML 2.0 / LTI 1.3 OIDC claims and supports term-end account deprovisioning and GDPR off-chain erasure without invalidating on-chain Merkle roots.
3. `TitleIvComplianceFirewall` blocks cash-equivalent or gift-card redemptions in standard closed-loop mode unless an explicit `PayrollOsfasExportPort` adapter is configured by the `BEEKEEPER`.
