# License, Secret & Privacy Policy Reference

## 1. Transitive Dependency License Policy (`MIT`-Compatible Only)
- **Allowed:** `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `PSF-2.0`, `MPL-2.0` (file-level), `Unlicense`, `CC0-1.0`.
- **Prohibited:** `GPL-*`, `AGPL-*`, `SSPL`, `LGPL-*` (without explicit review), commercial/proprietary, or `UNKNOWN`.

## 2. Zero-Leak Hygiene Rules
- Never hardcode OS user profile paths, drive-letter build paths, API keys, tokens, private keys, or personal hostnames.
- Use repository-relative paths, `Path(__file__).resolve()`, or documented `.env.example` variables.
- Ensure `git config --local core.hooksPath .githooks` is set and never use `--no-verify`.
