---
status: accepted
date: 2026-11-21
decision-makers:
  - nectR Institutional Governance, Privacy & Compliance Architecture
---

# Enforce Zero-PII FERPA GDPR and Title IV Campus Compliance

## Context and Problem Statement

University pilots require strict compliance with FERPA education-record protections, EDPB GDPR right-to-erasure guidelines (which conflict with on-chain PII), IRS Publication 970 and federal Title IV financial-aid overaward rules, and campus CISO LTI 1.3 / Shibboleth / HECVAT 4 procurement gates.

## Considered Options

* **Hybrid off-chain campus PII DB + on-chain salted hashes/ZK proofs + non-monetary service-duration credit firewall + LTI 1.3/Shibboleth SSO + MIT/DCO 1.1 -> Apereo incubation**
* **Storing pseudonymous student emails, course grades, or gift-card payouts directly on-chain**
* **Requiring students to manage self-custodial seed phrases and multi-university Corporate CLAs**

## Decision Outcome

Chosen option: "Hybrid off-chain campus PII DB + on-chain salted hashes/ZK proofs + non-monetary service-duration credit firewall + LTI 1.3/Shibboleth SSO + MIT/DCO 1.1 -> Apereo incubation", because keeping all student records off-chain in campus storage while anchoring salted hashes or BBS+ ZK membership proofs satisfies FERPA and GDPR erasure, abstracting keys behind InCommon Shibboleth SAML 2.0 and 1EdTech LTI 1.3 (`NRPS`) clears HECVAT 4.1.6 review, and framing `LIQUID_NECTR` as non-monetary organizer-cleared service-duration credits prevents IRS W-2/1099-NEC and Title IV overaward penalties.

### Consequences

* Good, because universities can deploy sandbox pilots without FERPA, GDPR, IRS, or Title IV compliance blockers.
* Good, because MIT + DCO 1.1 and Apereo Foundation incubation avoid multi-university Corporate CLA legal bottlenecks.
* Bad, because any tangible stipend off-ramp must route through an explicit campus Payroll/OSFAS adapter.
