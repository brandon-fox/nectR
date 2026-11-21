# Specification: Citation Validation & Provenance Chain-of-Custody (`ADDED`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/citation_provenance.feature](../../../../../features/citation_provenance.feature)
- **Step Definitions:** [features/steps/citation_provenance_steps.py](../../../../../features/steps/citation_provenance_steps.py)

## ADDED Requirements

### Requirement: Reference Quality Floor and Banned-Domain Guard (`#7`)
All canonical references in `paper/references.yaml` SHALL pass strict Pydantic schema validation, exclude banned secondary/unreliable domains (AI-wikis, social forums, SEO blogs, plagiarism notices), carry a valid DOI or archival URL for external works, and maintain at least a `70%` peer-reviewed ratio.
- **Linked Scenario:** `Reference registry rejects banned domains and insufficient peer-reviewed ratio` in [citation_provenance.feature](../../../../../features/citation_provenance.feature#L6-L10)

### Requirement: Automated Provenance Chain-of-Custody & Downstream Quarantine (`#7`)
A directed lineage graph (`paper/lineage.yaml`) SHALL trace every citation through theory equations, ADRs/DECs, and Python modules/tests, automatically computing impacted downstream artifacts via graph descendants and flagging them for regeneration in `docs/theory/provenance_lineage.md` whenever an upstream source fails plagiarism or verification checks.
- **Linked Scenario:** `Tainted upstream reference propagates downstream rebuild warning across lineage graph` in [citation_provenance.feature](../../../../../features/citation_provenance.feature#L12-L16)
- **Linked Scenario:** `Repository citation registry and provenance lineage report pass checks in sync` in [citation_provenance.feature](../../../../../features/citation_provenance.feature#L18-L21)
