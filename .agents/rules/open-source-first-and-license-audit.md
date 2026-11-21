---
trigger: always_on
---

# Mandatory Open-Source-First & Transitive License Audit Rule

**NEVER rebuild or write custom code when a secure, well-respected, permissively licensed open-source solution exists.**

## 1. Pre-Build Deep Research Gate (Before Writing Any Code)
Before designing or implementing any capability, module, or script:
1. **Research Existing OSS Solutions:** Deeply search for established, actively maintained open-source libraries, packages, and services (e.g., `gitleaks`, `detect-secrets`, `bandit`, `pip-audit`, `pip-licenses`, `cryptography`, `pydantic`, `networkx`, `fastapi`, `behave`).
2. **Adopt Over Custom:** Only write custom code for **nectR's core domain logic** (e.g., biomimetic tokenomics, smart contract state machines, PoUW-PoW coupling) or thin glue/project-specific rules not covered by OSS tools.

## 2. Transitive & Sub-Dependency License Scanning (Mandatory)
**nectR** is licensed under **MIT**. Before adding or using ANY dependency (direct or indirect):
1. **Audit the Entire Dependency Tree:** Inspect all direct, sub-, and chained transitive dependencies (e.g., via `pip-licenses` / `uv` lockfile inspection / `licensecheck`).
2. **Allowed Licenses Only (Free & Permissive):**
   - **Allowed:** `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `PSF-2.0`, `MPL-2.0` (file-level), `Unlicense`, `CC0-1.0`.
   - **Prohibited (Block Immediately):** `GPL-*`, `AGPL-*`, `SSPL`, `LGPL-*` (without explicit review), proprietary/commercial licenses, or `UNKNOWN` / unlicensed packages.
3. **Security & Maintenance Check:** Verify no known critical CVEs (`pip-audit`) and confirm active maintenance before adopting.
