"""Policy controls for MADR verbosity and branch gating (via OSS adrlint) plus fast YAML decision logs."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

IGNORED_ADR_FILES = frozenset({"index.md", "README.md"})
MAX_ADR_LINES = 70
MAX_ADR_WORDS = 380
MAX_ADR_TITLE_CHARS = 70
MAX_ADR_SECTION_BULLETS = 6

REQUIRED_MADR_SECTIONS = (
    "## Context and Problem Statement",
    "## Considered Options",
    "## Decision Outcome",
)

ALLOWED_AGENTS = frozenset(
    {
        "meta-orchestrator",
        "sci-research-agent",
        "business-proposal-agent",
        "product-lifecycle-agent",
        "system-arch-agent",
        "contracts-service-agent",
        "pow-compute-agent",
        "design-ui-agent",
        "ux-behavior-agent",
    }
)


class DecisionGovernanceError(ValueError):
    """Raised when an ADR or fast decision entry violates format, sync, or verbosity controls."""


class DecisionCategory(StrEnum):
    PARAMETER_DEFAULT = "parameter-default"
    RESEARCH_HYGIENE = "research-hygiene"
    WORKFLOW_POLICY = "workflow-policy"
    SECURITY_OSS = "security-oss"


class DecisionStatus(StrEnum):
    LOCKED = "locked"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"


class ExperimentStatus(StrEnum):
    OPEN_SIMULATION = "open-simulation"
    VALIDATED = "validated"
    REJECTED = "rejected"


class DecisionEntry(BaseModel):
    """Fast, concise non-architectural decision record."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^DEC-[0-9]{3}$")
    category: DecisionCategory
    status: DecisionStatus = DecisionStatus.LOCKED
    title: str = Field(min_length=8, max_length=60)
    decision: str = Field(min_length=15, max_length=180)
    owner_agent: str
    related_adr: str | None = None
    openspec_ref: str | None = None

    @field_validator("owner_agent")
    @classmethod
    def _check_owner(cls, value: str) -> str:
        if value not in ALLOWED_AGENTS:
            raise ValueError(f"Unknown owner_agent '{value}'. Allowed: {sorted(ALLOWED_AGENTS)}")
        return value


class ExperimentEntry(BaseModel):
    """Open behavioral or gamification hypothesis awaiting simulation validation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^EXP-[0-9]{3}$")
    status: ExperimentStatus = ExperimentStatus.OPEN_SIMULATION
    title: str = Field(min_length=8, max_length=60)
    hypothesis: str = Field(min_length=15, max_length=180)
    risk_note: str = Field(min_length=10, max_length=160)
    owner_agents: list[str] = Field(min_length=1, max_length=4)
    related_adr: str | None = None

    @field_validator("owner_agents")
    @classmethod
    def _check_owners(cls, values: list[str]) -> list[str]:
        for agent in values:
            if agent not in ALLOWED_AGENTS:
                raise ValueError(f"Unknown owner_agent '{agent}'.")
        return values


class DecisionRegistry(BaseModel):
    """Schema-validated fast non-architectural decision log."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1, le=1)
    decisions: list[DecisionEntry] = Field(default_factory=list)
    experiments: list[ExperimentEntry] = Field(default_factory=list)

    @field_validator("decisions")
    @classmethod
    def _unique_dec_ids(cls, items: list[DecisionEntry]) -> list[DecisionEntry]:
        seen: set[str] = set()
        for item in items:
            if item.id in seen:
                raise ValueError(f"Duplicate decision ID '{item.id}'.")
            seen.add(item.id)
        return items

    @field_validator("experiments")
    @classmethod
    def _unique_exp_ids(cls, items: list[ExperimentEntry]) -> list[ExperimentEntry]:
        seen: set[str] = set()
        for item in items:
            if item.id in seen:
                raise ValueError(f"Duplicate experiment ID '{item.id}'.")
            seen.add(item.id)
        return items


def load_registry(yaml_path: Path) -> DecisionRegistry:
    if not yaml_path.exists():
        raise DecisionGovernanceError(f"Missing decision registry at {yaml_path}")
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    return DecisionRegistry.model_validate(raw)


def save_registry(registry: DecisionRegistry, yaml_path: Path) -> None:
    payload = registry.model_dump(mode="json", exclude_none=True)
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)
    yaml_path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def validate_registry_links(registry: DecisionRegistry, repo_root: Path) -> None:
    for dec in registry.decisions:
        if dec.related_adr and not (repo_root / dec.related_adr).exists():
            raise DecisionGovernanceError(
                f"{dec.id}: Missing related_adr file '{dec.related_adr}'."
            )
        if dec.openspec_ref and not (repo_root / dec.openspec_ref).exists():
            raise DecisionGovernanceError(
                f"{dec.id}: Missing openspec_ref path '{dec.openspec_ref}'."
            )
    for exp in registry.experiments:
        if exp.related_adr and not (repo_root / exp.related_adr).exists():
            raise DecisionGovernanceError(
                f"{exp.id}: Missing related_adr file '{exp.related_adr}'."
            )


def _format_adr_link(related_adr: str | None) -> str:
    if not related_adr:
        return "—"
    adr_name = Path(related_adr).name
    adr_num = adr_name.split("-", 1)[0]
    return f"[ADR-{adr_num}](../adr/{adr_name})"


def render_decision_log(registry: DecisionRegistry, repo_root: Path | None = None) -> str:
    """Deterministically render docs/planning/decision_log.md from decisions.yaml."""
    _ = repo_root
    lines = [
        "<!-- AUTO-GENERATED by `nectr-decisions render` from `docs/planning/decisions.yaml`. Do not edit manually. -->",
        "",
        "# Fast Operational & Parameter Decision Log",
        "",
        "This log tracks fast, non-architectural parameter presets, research hygiene rules, workflow policies, and open simulation hypotheses.",
        "Structural **Architecture Decision Records (MADR 4.0)** are managed separately via `adrlint` in [Architecture Decision Records](../adr/index.md).",
        "",
        "## Locked Non-Architectural Decisions (`DEC`)",
        "",
        "| ID | Category | Title | Concise Decision Rule | Owner | Linked ADR | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    if registry.decisions:
        for d in registry.decisions:
            adr_cell = _format_adr_link(d.related_adr)
            lines.append(
                f"| **{d.id}** | `{d.category}` | **{d.title}** | {d.decision} | `{d.owner_agent}` | {adr_cell} | `{d.status}` |"
            )
    else:
        lines.append("| — | — | — | No fast decisions recorded yet. | — | — | — |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Open Experimental Hypotheses (`EXP`)",
            "",
            "| ID | Title | Testable Hypothesis | Risk / Gamification Guardrail | Owners | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    if registry.experiments:
        for e in registry.experiments:
            owners = ", ".join(f"`{o}`" for o in e.owner_agents)
            lines.append(
                f"| **{e.id}** | **{e.title}** | {e.hypothesis} | {e.risk_note} | {owners} | `{e.status}` |"
            )
    else:
        lines.append("| — | — | — | No open experimental hypotheses. | — | — |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Tooling & Code-Level Controls",
            "",
            "- **Add/update fast decisions:** Edit `docs/planning/decisions.yaml` or run `uv run nectr-decisions add-decision ...`, then `uv run nectr-decisions render`.",
            '- **Propose/accept MADR architecture records:** Run `uv run adrlint new "<Title>"`, promote `status: accepted` in YAML front matter, and run `uv run adrlint lock` (`<= 70` lines, `<= 380` words).',
            "- **Verify all governance gates:** Run `uv run nectr-decisions check` (use `--allow-proposed` on WIP feature branches).",
            "",
        ]
    )
    return "\n".join(lines)


def _split_frontmatter(raw: str, filename: str) -> tuple[dict[str, Any], str]:
    normalized = raw.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return {}, normalized
    end_idx = normalized.find("\n---\n", 4)
    if end_idx == -1:
        if normalized.endswith("\n---"):
            end_idx = len(normalized) - 4
            body = ""
        else:
            raise DecisionGovernanceError(f"{filename}: Unterminated YAML front matter.")
    else:
        body = normalized[end_idx + 5 :]
    loaded = yaml.safe_load(normalized[4:end_idx]) or {}
    if not isinstance(loaded, dict):
        raise DecisionGovernanceError(f"{filename}: YAML front matter must be a mapping.")
    return loaded, body


def validate_adr_verbosity(adr_dir: Path) -> list[Path]:
    """Enforce strict MADR length, word-count, title-length, section, and bullet caps."""
    if not adr_dir.exists():
        raise DecisionGovernanceError(f"ADR directory does not exist: {adr_dir}")

    adr_files = sorted(p for p in adr_dir.glob("*.md") if p.name not in IGNORED_ADR_FILES)
    if not adr_files:
        raise DecisionGovernanceError(f"No ADR files found in {adr_dir}")

    bullet_re = re.compile(r"^\s*[-*]\s+")
    for adr_file in adr_files:
        content = adr_file.read_text(encoding="utf-8").replace("\r\n", "\n")
        _, body = _split_frontmatter(content, adr_file.name)
        all_lines = content.splitlines()
        if len(all_lines) > MAX_ADR_LINES:
            raise DecisionGovernanceError(
                f"{adr_file.name}: {len(all_lines)} lines exceeds max line limit ({MAX_ADR_LINES})."
            )

        words = re.findall(r"\S+", content)
        if len(words) > MAX_ADR_WORDS:
            raise DecisionGovernanceError(
                f"{adr_file.name}: {len(words)} words exceeds max word limit ({MAX_ADR_WORDS})."
            )

        body_lines = body.splitlines()
        h1_lines = [ln[2:].strip() for ln in body_lines if ln.startswith("# ")]
        if not h1_lines:
            raise DecisionGovernanceError(f"{adr_file.name}: Missing H1 '# <Title>' header.")
        if len(h1_lines[0]) > MAX_ADR_TITLE_CHARS:
            raise DecisionGovernanceError(
                f"{adr_file.name}: Title '{h1_lines[0]}' ({len(h1_lines[0])} chars) "
                f"exceeds max title length ({MAX_ADR_TITLE_CHARS})."
            )

        if not adr_file.name.startswith("0000-"):
            for req_sec in REQUIRED_MADR_SECTIONS:
                if req_sec not in body:
                    raise DecisionGovernanceError(
                        f"{adr_file.name}: Missing required MADR section '{req_sec}'."
                    )

        in_section = False
        current_section = ""
        bullet_count = 0
        for ln in body_lines:
            if ln.startswith(("## ", "### ")):
                if in_section and bullet_count > MAX_ADR_SECTION_BULLETS:
                    raise DecisionGovernanceError(
                        f"{adr_file.name}: Section '{current_section}' ({bullet_count} bullets) "
                        f"exceeds max bullets per section ({MAX_ADR_SECTION_BULLETS})."
                    )
                in_section = True
                current_section = ln.strip()
                bullet_count = 0
            elif in_section and bullet_re.match(ln):
                bullet_count += 1
        if in_section and bullet_count > MAX_ADR_SECTION_BULLETS:
            raise DecisionGovernanceError(
                f"{adr_file.name}: Section '{current_section}' ({bullet_count} bullets) "
                f"exceeds max bullets per section ({MAX_ADR_SECTION_BULLETS})."
            )

    return adr_files


def _resolve_adrlint_bin() -> str:
    found = shutil.which("adrlint")
    if found:
        return found
    sibling = Path(sys.executable).resolve().parent / (
        "adrlint.exe" if sys.platform == "win32" else "adrlint"
    )
    if sibling.exists():
        return str(sibling)
    raise DecisionGovernanceError(
        "Missing 'adrlint' executable. Install dev/lint extras (`uv sync --extra lint`)."
    )


def _run_adrlint(adrlint_bin: str, args: list[str], cwd: Path) -> None:
    proc = subprocess.run(
        [adrlint_bin, "--no-color", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DecisionGovernanceError(f"adrlint {' '.join(args)} failed:\n{detail}")


def validate_adrlint_repo(repo_root: Path, allow_proposed: bool = False) -> int:
    """Validate MADR 4.0 ADRs with OSS adrlint (lint, format --check, lock --check)."""
    if not (repo_root / ".adrlint.toml").exists():
        raise DecisionGovernanceError(f"Missing .adrlint.toml config file in {repo_root}")

    adr_dir = repo_root / "docs" / "adr"
    adr_files = sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md"))
    if not adr_files:
        raise DecisionGovernanceError(f"No numbered ADR files found in {adr_dir}")

    adrlint_bin = _resolve_adrlint_bin()
    _run_adrlint(adrlint_bin, ["lint"], repo_root)
    _run_adrlint(adrlint_bin, ["format", "--check"], repo_root)
    _run_adrlint(adrlint_bin, ["lock", "--check"], repo_root)

    finalized_count = 0
    for adr_file in adr_files:
        meta, _ = _split_frontmatter(adr_file.read_text(encoding="utf-8"), adr_file.name)
        status = str(meta.get("status", "")).strip().lower()
        if not status:
            raise DecisionGovernanceError(
                f"{adr_file.name}: Missing 'status' in YAML front matter."
            )
        if status.startswith("proposed"):
            if not allow_proposed:
                raise DecisionGovernanceError(
                    f"{adr_file.name}: status is 'proposed' "
                    "(promote status and run `adrlint lock`, or pass --allow-proposed)."
                )
        else:
            finalized_count += 1

    return finalized_count


def check_all_governance(repo_root: Path, allow_proposed: bool = False) -> dict[str, Any]:
    """Validate both MADR ADRs (verbosity + adrlint) and fast decisions.yaml -> decision_log.md."""
    adr_dir = repo_root / "docs" / "adr"
    validate_adr_verbosity(adr_dir)
    accepted_count = validate_adrlint_repo(repo_root, allow_proposed=allow_proposed)

    yaml_path = repo_root / "docs" / "planning" / "decisions.yaml"
    md_path = repo_root / "docs" / "planning" / "decision_log.md"
    registry = load_registry(yaml_path)
    validate_registry_links(registry, repo_root)

    expected_md = render_decision_log(registry, repo_root).replace("\r\n", "\n")
    if not md_path.exists():
        raise DecisionGovernanceError("Missing docs/planning/decision_log.md.")
    actual_md = md_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if actual_md != expected_md:
        raise DecisionGovernanceError(
            "docs/planning/decision_log.md is out of sync with decisions.yaml (run `nectr-decisions render`)."
        )

    return {
        "accepted_adr_count": accepted_count,
        "adrlint_ok": True,
        "toc_in_sync": True,
        "decision_count": len(registry.decisions),
        "experiment_count": len(registry.experiments),
        "decision_log_in_sync": True,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-decisions",
        description="Manage fast non-architectural decisions and enforce MADR verbosity limits.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root path (defaults to current working directory).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    chk = sub.add_parser("check", help="Validate YAML decisions, Markdown sync, and ADRs.")
    chk.add_argument(
        "--allow-proposed",
        action="store_true",
        help="Allow XXXX-*.md proposed ADRs on feature branches.",
    )

    chk_adrs = sub.add_parser("check-adrs", help="Validate ADR repo via adrlint and verbosity.")
    chk_adrs.add_argument(
        "--allow-proposed",
        action="store_true",
        help="Allow status: proposed ADRs on feature branches.",
    )

    sub.add_parser("render", help="Render docs/planning/decision_log.md from decisions.yaml.")

    add_dec = sub.add_parser(
        "add-decision", help="Add a validated DEC-NNN entry and re-render decision_log.md."
    )
    add_dec.add_argument("--id", required=True, help="Decision ID (e.g., DEC-008).")
    add_dec.add_argument("--category", required=True, choices=[c.value for c in DecisionCategory])
    add_dec.add_argument("--title", required=True, help="Concise title (8..60 chars).")
    add_dec.add_argument("--decision", required=True, help="Concise rule (15..180 chars).")
    add_dec.add_argument("--owner", required=True, help="Owning Domain Builder Agent.")
    add_dec.add_argument("--related-adr", default=None, help="Optional docs/adr/NNNN-*.md path.")
    add_dec.add_argument("--openspec-ref", default=None, help="Optional openspec/... path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.root).resolve()

    try:
        if args.command == "check":
            summary = check_all_governance(repo_root, allow_proposed=args.allow_proposed)
            print(
                f"Governance OK: {summary['accepted_adr_count']} MADR ADRs, "
                f"{summary['decision_count']} DEC rules, {summary['experiment_count']} EXP hypotheses."
            )
            return 0
        if args.command == "check-adrs":
            validate_adr_verbosity(repo_root / "docs" / "adr")
            accepted_count = validate_adrlint_repo(repo_root, allow_proposed=args.allow_proposed)
            print(
                f"ADR Governance OK: {accepted_count} finalized MADR records verified and locked via adrlint."
            )
            return 0
        if args.command == "render":
            yaml_path = repo_root / "docs" / "planning" / "decisions.yaml"
            md_path = repo_root / "docs" / "planning" / "decision_log.md"
            reg = load_registry(yaml_path)
            validate_registry_links(reg, repo_root)
            md_path.write_text(render_decision_log(reg, repo_root), encoding="utf-8", newline="\n")
            print(f"Rendered {md_path.relative_to(repo_root).as_posix()}.")
            return 0
        if args.command == "add-decision":
            yaml_path = repo_root / "docs" / "planning" / "decisions.yaml"
            md_path = repo_root / "docs" / "planning" / "decision_log.md"
            reg = load_registry(yaml_path)
            entry = DecisionEntry(
                id=args.id,
                category=DecisionCategory(args.category),
                title=args.title,
                decision=args.decision,
                owner_agent=args.owner,
                related_adr=args.related_adr,
                openspec_ref=args.openspec_ref,
            )
            updated = DecisionRegistry(
                schema_version=reg.schema_version,
                decisions=[*reg.decisions, entry],
                experiments=reg.experiments,
            )
            validate_registry_links(updated, repo_root)
            save_registry(updated, yaml_path)
            md_path.write_text(
                render_decision_log(updated, repo_root), encoding="utf-8", newline="\n"
            )
            return 0
    except (
        DecisionGovernanceError,
        ValidationError,
        ValueError,
        OSError,
        yaml.YAMLError,
    ) as exc:
        print(f"Decision governance error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
