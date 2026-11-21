"""Shared cross-platform utilities for nectR custom skill helper scripts.

Designed to work identically on Linux, macOS, and Windows using only the
Python standard library for fast module loading and zero third-party runtime
overhead.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import os
from pathlib import Path
import shutil
import string
import subprocess
import sys
from typing import Final

ALLOWED_SKILL_NAME_CHARS: Final[frozenset[str]] = frozenset(
    string.ascii_lowercase + string.digits
)
MAX_SKILL_NAME_LEN: Final[int] = 64
MAX_DESCRIPTION_LEN: Final[int] = 1024
WHEN_TRIGGERS: Final[tuple[str, ...]] = ("use when", "use before", "use for")
LINK_MARKER: Final[str] = "](./"
LINK_PREFIXES: Final[tuple[str, ...]] = ("scripts/", "references/")
WIN_USER_MARKERS: Final[tuple[str, ...]] = (":\\" + "users\\", ":/" + "users/")
POSIX_USER_MARKERS: Final[tuple[str, ...]] = ("/" + "Users/", "/" + "home/")


def find_repo_root(start: Path | None = None) -> Path:
  """Walk upward from *start* until `.git` or `pyproject.toml` is found.

  Args:
    start: Optional starting file or directory path. Defaults to this module.

  Returns:
    Resolved repository root path.

  Raises:
    FileNotFoundError: If no repository root marker is found in parent dirs.
  """
  current = (start or Path(__file__)).resolve()
  if current.is_file():
    current = current.parent
  for candidate in (current, *current.parents):
    if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
      return candidate
  raise FileNotFoundError(
      "Could not locate repository root (.git or pyproject.toml)"
  )


def resolve_tool_cmd(
    executable: str, fallback_module: str | None = None
) -> list[str]:
  """Return a cross-platform command list for *executable*.

  Args:
    executable: CLI binary name to locate on ``PATH`` or in the active venv.
    fallback_module: Optional Python module name for ``python -m`` fallback.

  Returns:
    Command argument list suitable for ``subprocess.run``.
  """
  found = shutil.which(executable)
  if found:
    return [found]
  suffix = ".exe" if os.name == "nt" else ""
  venv_bin = Path(sys.executable).parent / f"{executable}{suffix}"
  if venv_bin.exists():
    return [str(venv_bin)]
  if fallback_module:
    return [sys.executable, "-m", fallback_module]
  return [executable]


def run_step(label: str, cmd: Sequence[str], cwd: Path) -> int:
  """Execute *cmd* in *cwd* and print a concise status line.

  Args:
    label: Human-readable step name.
    cmd: Command and arguments to execute.
    cwd: Working directory for the subprocess.

  Returns:
    Subprocess exit code (0 on success).
  """
  print(f"[RUN] {label}: {' '.join(cmd)}")
  proc = subprocess.run(list(cmd), cwd=str(cwd), check=False)
  if proc.returncode == 0:
    print(f"[PASS] {label}")
  else:
    print(f"[FAIL] {label} (exit code {proc.returncode})", file=sys.stderr)
  return proc.returncode


def run_steps(
    steps: Sequence[tuple[str, Callable[[], int]]],
) -> int:
  """Run a sequence of callable checks, stopping on the first non-zero exit.

  Args:
    steps: Sequence of ``(label, callable)`` pairs returning an exit code.

  Returns:
    0 if all steps succeed, otherwise the first non-zero exit code.
  """
  for _label, fn in steps:
    rc = fn()
    if rc != 0:
      return rc
  return 0


def run_detect_secrets(files: Sequence[str], cwd: Path) -> int:
  """Run ``detect-secrets-hook`` on *files* or scan the repository.

  Args:
    files: Relative file paths to scan. If empty, scans the repository.
    cwd: Repository root directory.

  Returns:
    Subprocess exit code.
  """
  if files:
    cmd = [
        *resolve_tool_cmd("detect-secrets-hook"),
        "--baseline",
        ".secrets.baseline",
        *files,
    ]
    return run_step("detect-secrets-hook", cmd, cwd)
  cmd = [
      *resolve_tool_cmd("detect-secrets", "detect_secrets"),
      "scan",
      "--exclude-files",
      r"(\.git|\.venv|\.pytest_cache|__pycache__|site|\.worktrees)",
  ]
  return run_step("detect-secrets scan", cmd, cwd)


def run_pytest(
    targets: Sequence[str] | None,
    cwd: Path,
    extra_args: Sequence[str] | None = None,
) -> int:
  """Run pytest using the active Python interpreter.

  Args:
    targets: Optional test file or directory paths.
    cwd: Repository root directory.
    extra_args: Optional additional pytest CLI flags.

  Returns:
    Subprocess exit code.
  """
  cmd = [sys.executable, "-m", "pytest", *(targets or ()), *(extra_args or ())]
  return run_step("pytest", cmd, cwd)


def run_behave(tags: Sequence[str] | None, cwd: Path) -> int:
  """Run the behave BDD suite using the active Python interpreter.

  Args:
    tags: Optional behave tag expressions.
    cwd: Repository root directory.

  Returns:
    Subprocess exit code.
  """
  cmd: list[str] = [sys.executable, "-m", "behave"]
  for tag in tags or ():
    cmd.extend(["--tags", tag])
  return run_step("behave", cmd, cwd)


def run_mkdocs_strict(cwd: Path) -> int:
  """Run ``mkdocs build --strict`` using the active Python interpreter.

  Args:
    cwd: Repository root directory.

  Returns:
    Subprocess exit code.
  """
  cmd = [sys.executable, "-m", "mkdocs", "build", "--strict"]
  return run_step("mkdocs build --strict", cmd, cwd)


def run_mypy(targets: Sequence[str], cwd: Path) -> int:
  """Run ``mypy --strict`` on *targets* using the active Python interpreter.

  Args:
    targets: Relative file or directory paths to type-check.
    cwd: Repository root directory.

  Returns:
    Subprocess exit code.
  """
  cmd = [sys.executable, "-m", "mypy", "--strict", *targets]
  return run_step("mypy --strict", cmd, cwd)


def _git_output(args: Sequence[str], cwd: Path) -> tuple[int, str]:
  """Run a git command and capture stripped stdout."""
  proc = subprocess.run(
      ["git", *args],
      cwd=str(cwd),
      capture_output=True,
      text=True,
      check=False,
  )
  return proc.returncode, proc.stdout.strip()


def check_git_hygiene(cwd: Path, require_ssh_signing: bool = False) -> int:
  """Verify ``core.hooksPath``, optional SSH signing, and clean git status.

  Args:
    cwd: Repository root directory.
    require_ssh_signing: Whether to enforce SSH commit signing configuration.

  Returns:
    0 if all checks pass, otherwise 1.
  """
  rc, hooks_path = _git_output(["config", "--get", "core.hooksPath"], cwd)
  if rc != 0 or hooks_path != ".githooks":
    print(
        f"[FAIL] git core.hooksPath is '{hooks_path or '<unset>'}', "
        "expected '.githooks'",
        file=sys.stderr,
    )
    return 1
  print("[PASS] git core.hooksPath == .githooks")

  if require_ssh_signing:
    _, gpgsign = _git_output(["config", "--get", "commit.gpgsign"], cwd)
    _, gpgfmt = _git_output(["config", "--get", "gpg.format"], cwd)
    if gpgsign.lower() != "true" or gpgfmt.lower() != "ssh":
      print(
          "[FAIL] SSH signing misconfigured "
          f"(commit.gpgsign='{gpgsign}', gpg.format='{gpgfmt}')",
          file=sys.stderr,
      )
      return 1
    print(
        "[PASS] SSH commit signing configured "
        "(commit.gpgsign=true, gpg.format=ssh)"
    )

  rc, status = _git_output(["status", "--porcelain"], cwd)
  if rc != 0:
    print("[FAIL] git status failed", file=sys.stderr)
    return rc
  bad_entries = [
      line
      for line in status.splitlines()
      if "__pycache__" in line or line.rstrip().endswith((".pyc", ".pycc"))
  ]
  if bad_entries:
    print(
        f"[FAIL] Untracked cache artifacts detected: {bad_entries}",
        file=sys.stderr,
    )
    return 1
  print("[PASS] No untracked Python cache artifacts in git status")
  return 0


def contains_local_path(line: str) -> bool:
  """Return True if *line* contains a hardcoded OS user home directory path.

  Uses linear ``str.find`` scanning instead of regular expressions for O(n)
  guaranteed performance with zero backtracking.

  Args:
    line: Single line of text to inspect.

  Returns:
    True if a Windows or POSIX user home prefix is found.
  """
  lower = line.lower()
  for marker in WIN_USER_MARKERS:
    idx = lower.find(marker)
    while idx != -1:
      if idx >= 1 and "a" <= lower[idx - 1] <= "z":
        return True
      idx = lower.find(marker, idx + len(marker))

  for marker in POSIX_USER_MARKERS:
    idx = line.find(marker)
    while idx != -1:
      prev_ok = idx == 0 or (
          not line[idx - 1].isalnum() and line[idx - 1] != "_"
      )
      after = idx + len(marker)
      next_ok = (
          after < len(line)
          and not line[after].isspace()
          and line[after] != "/"
      )
      if prev_ok and next_ok:
        return True
      idx = line.find(marker, after)
  return False


def check_no_local_paths(paths: Sequence[Path], cwd: Path) -> int:
  """Verify none of *paths* contain hardcoded local user paths.

  Args:
    paths: Files or directories to inspect.
    cwd: Repository root directory for relative reporting.

  Returns:
    0 if clean, 1 if any local user path is detected.
  """
  targets: list[Path] = []
  for p in paths:
    resolved = p if p.is_absolute() else (cwd / p)
    if resolved.is_file():
      targets.append(resolved)
    elif resolved.is_dir():
      targets.extend(f for f in resolved.rglob("*") if f.is_file())

  violations: list[str] = []
  for file_path in targets:
    try:
      text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
      continue
    for lineno, line in enumerate(text.splitlines(), start=1):
      if contains_local_path(line):
        rel = file_path.relative_to(cwd)
        violations.append(f"{rel}:{lineno}")

  if violations:
    print(
        f"[FAIL] Local user paths detected: {', '.join(violations)}",
        file=sys.stderr,
    )
    return 1
  print(f"[PASS] No local user paths in {len(targets)} checked file(s)")
  return 0


def is_valid_skill_name(name: str) -> bool:
  """Validate lowercase hyphenated skill name without regular expressions.

  Args:
    name: Candidate skill name.

  Returns:
    True if *name* is 1..64 chars of lowercase ASCII alphanumeric segments
    separated by single hyphens.
  """
  if not name or len(name) > MAX_SKILL_NAME_LEN:
    return False
  parts = name.split("-")
  return all(
      bool(part) and all(ch in ALLOWED_SKILL_NAME_CHARS for ch in part)
      for part in parts
  )


def extract_relative_skill_links(body: str) -> list[str]:
  """Extract ``./scripts/...`` and ``./references/...`` markdown links linearly.

  Uses ``str.find`` instead of regular expressions for O(n) scanning.

  Args:
    body: Markdown body content of ``SKILL.md``.

  Returns:
    List of relative target paths (e.g. ``scripts/run.py``).
  """
  links: list[str] = []
  pos = 0
  marker_len = len(LINK_MARKER)
  while True:
    idx = body.find(LINK_MARKER, pos)
    if idx == -1:
      break
    line_start = body.rfind("\n", 0, idx) + 1
    open_bracket = body.rfind("[", line_start, idx)
    close_paren = body.find(")", idx + marker_len)
    line_end = body.find("\n", idx)
    same_line = line_end == -1 or close_paren < line_end
    if open_bracket != -1 and open_bracket < idx - 1 and close_paren != -1 and same_line:
      target = body[idx + marker_len : close_paren]
      if target.startswith(LINK_PREFIXES):
        links.append(target)
    pos = idx + marker_len
  return links


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], str]:
  """Parse minimal YAML frontmatter (``name`` and ``description``) from ``SKILL.md``.

  Args:
    skill_md: Path to the ``SKILL.md`` file.

  Returns:
    Tuple of ``(frontmatter_dict, body_markdown)``.

  Raises:
    ValueError: If opening or closing ``---`` delimiters are missing.
  """
  content = skill_md.read_text(encoding="utf-8")
  lines = content.splitlines()
  if not lines or lines[0].strip() != "---":
    raise ValueError(f"{skill_md}: missing opening '---' frontmatter delimiter")

  end_idx: int | None = None
  for idx in range(1, len(lines)):
    if lines[idx].strip() == "---":
      end_idx = idx
      break
  if end_idx is None:
    raise ValueError(f"{skill_md}: missing closing '---' frontmatter delimiter")

  fm_lines = lines[1:end_idx]
  body = "\n".join(lines[end_idx + 1 :])
  data: dict[str, str] = {}
  i = 0
  while i < len(fm_lines):
    line = fm_lines[i]
    if ":" in line and not line.startswith((" ", "\t")):
      key, val = line.split(":", 1)
      key = key.strip()
      val = val.strip()
      if val in (">-", ">", "|-", "|"):
        block: list[str] = []
        i += 1
        while i < len(fm_lines) and (
            fm_lines[i].startswith((" ", "\t")) or fm_lines[i] == ""
        ):
          block.append(fm_lines[i].strip())
          i += 1
        data[key] = " ".join(part for part in block if part).strip()
        continue
      data[key] = val.strip("\"'")
    i += 1
  return data, body


def validate_skill_dir(skill_dir: Path) -> list[str]:
  """Validate a single skill directory against the Antigravity/nectR skills spec.

  Args:
    skill_dir: Path to ``.agents/skills/<skill_name>``.

  Returns:
    List of human-readable validation error strings (empty if valid).
  """
  errors: list[str] = []
  skill_md = skill_dir / "SKILL.md"
  if not skill_md.is_file():
    return [f"{skill_dir.name}: missing SKILL.md"]

  try:
    fm, body = parse_frontmatter(skill_md)
  except ValueError as exc:
    return [str(exc)]

  name = fm.get("name", "")
  desc = fm.get("description", "")
  if name != skill_dir.name:
    errors.append(
        f"{skill_dir.name}: frontmatter name '{name}' != directory name"
    )
  if not is_valid_skill_name(name):
    errors.append(f"{skill_dir.name}: invalid skill name '{name}'")
  if not desc or len(desc) > MAX_DESCRIPTION_LEN:
    errors.append(
        f"{skill_dir.name}: description missing or > {MAX_DESCRIPTION_LEN} chars"
    )
  desc_lower = desc.lower()
  if not any(tok in desc_lower for tok in WHEN_TRIGGERS):
    errors.append(
        f"{skill_dir.name}: description must state when to use the skill"
    )

  scripts_dir = skill_dir / "scripts"
  refs_dir = skill_dir / "references"
  if not scripts_dir.is_dir() or not any(scripts_dir.glob("*.py")):
    errors.append(
        f"{skill_dir.name}: scripts/ must exist and contain at least one .py file"
    )
  if not refs_dir.is_dir() or not any(refs_dir.glob("*.md")):
    errors.append(
        f"{skill_dir.name}: references/ must exist and contain at least one .md file"
    )

  if "## Validation" not in body:
    errors.append(
        f"{skill_dir.name}: SKILL.md must contain a '## Validation' section"
    )

  links = extract_relative_skill_links(body)
  if not any(link.startswith("scripts/") for link in links):
    errors.append(
        f"{skill_dir.name}: SKILL.md must link to at least one ./scripts/ file"
    )
  if not any(link.startswith("references/") for link in links):
    errors.append(
        f"{skill_dir.name}: SKILL.md must link to at least one ./references/ file"
    )
  for link in links:
    if not (skill_dir / link).is_file():
      errors.append(f"{skill_dir.name}: broken relative link './{link}'")

  return errors


def validate_all_skills(skills_root: Path | None = None) -> list[str]:
  """Validate every skill directory under ``.agents/skills/``.

  Args:
    skills_root: Optional override for the skills root directory.

  Returns:
    Aggregated list of validation errors across all skill directories.
  """
  root = skills_root or (find_repo_root() / ".agents" / "skills")
  errors: list[str] = []
  for entry in sorted(root.iterdir()):
    if entry.is_dir():
      errors.extend(validate_skill_dir(entry))
  return errors
