# Design: Standardize Custom Skills & Enforce `mypy --strict`

## Architecture Decisions
1. **Shared DRY Library (`.agents/lib/skill_common.py`):** Placed outside `.agents/skills/` so every directory under `.agents/skills/` remains a valid skill package. Uses only Python stdlib for fast module loading and cross-platform execution (Linux, macOS, Windows).
2. **Zero-Regex Linear Scanning:**
   - `is_valid_skill_name()` uses `split("-")` and a precomputed `Final[frozenset[str]]`.
   - `extract_relative_skill_links()` uses linear `str.find("./")` scanning.
   - `contains_local_path()` uses `str.find()` on `WIN_USER_MARKERS` and `POSIX_USER_MARKERS`.
3. **Google Style & Strict Typing:** All new/updated Python files use explicit parameter/return annotations, `Final` constants, sorted imports, and Google-style docstrings (`Args:`, `Returns:`, `Raises:`).
4. **Commit-Time Type Gate:** `mypy==2.4.1` (`MIT`) is configured in `pyproject.toml` (`strict = true`, `mypy_path = "src"`) and enforced in `.pre-commit-config.yaml` and `.githooks/pre-commit`.
