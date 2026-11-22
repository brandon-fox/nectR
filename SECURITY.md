# Security Policy

## Supported Versions

Only the latest release version on the `main` branch of nectR receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of nectR seriously. If you discover a vulnerability or potential security risk, please **do not** open a public issue.

### Disclosure Process

1. Email findings directly to the repository maintainer at `32090240+brandon-fox@users.noreply.github.com` or submit a private security advisory through [GitHub Security Advisories](https://github.com/brandon-fox/nectR/security/advisories/new).
2. Include a detailed description of the vulnerability, reproduction steps, and proof-of-concept payload if available.
3. You will receive an acknowledgment within 48 hours.
4. We will keep you updated as we investigate and develop a patch.

## Security Best Practices

- **Zero-Secret Hygiene**: Never commit API keys, private keys, `.env` values, or credentials.
- **Commit Signing**: All commits must be cryptographically signed using SSH or GPG keys.
- **Permissive Licenses**: Dependencies are strictly audited for permissive, MIT-compatible licenses.
