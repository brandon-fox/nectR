# Specification Delta: Zero-PII FERPA/GDPR Boundary, LTI 1.3 Roster Port & Title IV Firewall (`hive-persistence-api`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature)
- **Step Definitions:** [features/steps/hive_persistence_api_steps.py](../../../../../features/steps/hive_persistence_api_steps.py)

## Requirements

### Requirement: ADDED — Zero-PII FERPA/GDPR On-Chain Commitment Guard & Off-Chain Erasure (`ADR-0015`)
`HiveServiceLayer` SHALL store all student PII and FERPA education records exclusively in off-chain campus relational storage, anchor only salted cryptographic commitments or Zero-Knowledge membership proofs on-chain, and support GDPR right-to-erasure by deleting off-chain salts without breaking historical block Merkle roots.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)

### Requirement: ADDED — 1EdTech LTI 1.3 / Shibboleth SSO Key Abstraction & Title IV Service-Credit Firewall (`ADR-0015`)
`HiveServiceLayer` SHALL expose hexagonal ports for InCommon Shibboleth SAML 2.0 SSO and 1EdTech LTI 1.3 (`NRPS` course roster scoping and term-rollover deprovisioning) and SHALL enforce a non-monetary service-duration credit boundary on `LIQUID_NECTR` redemptions to prevent unapproved IRS W-2/1099-NEC or federal Title IV financial-aid overaward triggers.
- **Linked Scenario:** `Settled tutoring session persists across HiveServiceLayer repository reload` in [hive_persistence_api.feature](../../../../../features/hive_persistence_api.feature#L6-L10)
