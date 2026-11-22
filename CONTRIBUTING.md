# Contributing to nectR

Everything here is MIT licensed and built in the open. Issues and pull requests are welcome; this document outlines requirements and practices for contributing.

## Before Writing Code

The specification comes first. Every behavioral change starts with an OpenSpec proposal or an Architectural Decision Record in `docs/adr/`. If a change is small enough that a full specification proposal is unnecessary, please explain the rationale in your pull request.

## Commit Guidelines

- **Cryptographically Signed**: All commits must be signed using SSH or GPG keys (`git commit -S`). Unsigned commits are rejected by repository merge gates.
- **Developer Certificate of Origin**: Use `git commit -s` to include a `Signed-off-by` line certifying your right to submit the contribution under the MIT License.
- **Conventional Commits**: Format commit subjects as `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `chore: ...`. The commit body should explain the rationale for the change.
- **Strict File Isolation**: Only stage explicit files for your contribution (`git add <file>`). Never run `git add .` or `git commit -a`.
- **Zero Secrets and Privacy**: Never commit private keys, credentials, local filesystem paths, or personal identifiers.

## Pull Request Requirements

- All CI checks must pass cleanly: unit tests, BDD scenarios, static typing, and governance checks.
- Keep pull requests focused on a single concern.
- Maintain linear git history by rebasing against `origin/main` rather than creating merge commits.
- Ensure all tests pass with `uv run pytest` and `uv run behave --tags=-red`.

## Independence

This project is personal open-source research and engineering work by Brandon Fox and is not affiliated with any employer. Contributions are accepted under the same terms: your own work, submitted under your name, licensed under the MIT License.
