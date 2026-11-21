# Design: Zero-PII FERPA/GDPR Boundary, LTI 1.3 / Shibboleth Adapter & Title IV Firewall (`add-campus-compliance-lti-and-zk-identity`)

## DDD Hexagonal Ports & Compliance Guards
- **`CampusIdentityPort` (Driving/Driven Port):** Maps InCommon Shibboleth SAML 2.0 / eduGAIN assertions and 1EdTech LTI 1.3 OIDC/JWT launches (`NRPS` course roster claims) to unlinkable pseudonymous `bee_id` commitments and BBS+ / Groth-Kohlweiss ZK membership proofs.
- **`ZeroPiiCommitmentGuard` (Domain Policy):** Inspects outbound `SignedTransaction` and `structlog` payloads to ensure only salted SHA-256/BLAKE2b hashes (`H(salt || campus_record_id)`) enter `HiveBlockchain`, preserving GDPR right-to-erasure via off-chain salt deletion.
- **`TitleIvComplianceFirewall` (Domain Policy):** Enforces Japan's two-mandate non-monetary service-duration credit boundary on `LIQUID_NECTR` swaps and gates any tangible perk or stipend off-ramp behind `Beekeeper`-authorized OSFAS/Payroll reporting hooks (`ADR-0015`).

## Invariants
1. **Zero On-Chain PII:** On-chain blocks and `UsefulComputeProof` commitments contain zero FERPA education records or GDPR personal data after off-chain salt rotation/deletion.
2. **100% Key Abstraction:** End-user learners and tutors authenticate via campus SSO / LMS LTI 1.3 without managing raw cryptographic seed phrases.
3. **Non-Monetary Service Credit Default:** Direct cash-equivalent redemption of `LIQUID_NECTR` is disabled by default to prevent IRS Pub 970 W-2/1099-NEC and Title IV overaward violations.
