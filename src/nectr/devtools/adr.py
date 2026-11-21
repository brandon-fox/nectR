"""Zero-CVE, pure-MIT Markdown Architectural Decision Record (MADR) engine.

Adapted from pyadr (MIT License, Copyright Opinionated Digital Center) — modernized
for Python 3.11+ with strict typing, relative ``.adr`` path safety, ``--allow-proposed``
branch checks, and zero external CLI/unidecode dependencies.
"""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Final

STATUS_PROPOSED: Final[str] = "proposed"
STATUS_ACCEPTED: Final[str] = "accepted"
STATUS_REJECTED: Final[str] = "rejected"
STATUS_DEPRECATED: Final[str] = "deprecated"
STATUS_SUPERSEDED: Final[str] = "superseded"
STANDARD_STATUSES: Final[tuple[str, ...]] = (
    STATUS_ACCEPTED,
    STATUS_REJECTED,
    STATUS_SUPERSEDED,
    STATUS_DEPRECATED,
)
IGNORED_ADR_FILES: Final[frozenset[str]] = frozenset(
    {"index.md", "template.md", "lifecycle_guide.md"}
)
WITH_ID_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^([0-9]{4})-([a-z0-9-]+)\.md$")
PROPOSED_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^XXXX-([a-z0-9-]+)\.md$")

MADR_TEMPLATE: Final[str] = """# [short title of solved problem and solution]

* Status: [proposed | rejected | accepted | deprecated | superseded by [0005](0005-example.md)]
* Deciders: [list everyone involved in the decision]
* Date: [YYYY-MM-DD]

## Context and Problem Statement

[Describe the architectural problem in 2-3 concise sentences.]

## Considered Options

* [Option 1]
* [Option 2]
* [Option 3]

## Decision Outcome

Chosen option: "[Option 1]", because [concise architectural rationale within 70-line / 380-word MADR budget].

### Consequences

* Good, because [key architectural benefit].
* Bad, because [known trade-off or constraint].
"""

INIT_0000_CONTENT: Final[str] = """# Record architecture decisions

* Status: accepted
* Date: {today}

## Context

We need to record architectural decisions made in this project.

## Decision

We will use Architecture Decision Records (ADRs) in MADR format.

## Consequences

Architectural invariants remain concise, traceable, and verifiable.
"""

INIT_0001_CONTENT: Final[str] = """# Use Markdown Architectural Decision Records

* Status: accepted
* Date: {today}

## Context and Problem Statement

We want to keep architectural decisions concise, versioned, and machine-validated alongside code.

## Considered Options

* MADR in `docs/adr/`
* Ad-hoc design docs

## Decision Outcome

Chosen option: "MADR in `docs/adr/`", because MADR keeps architectural trade-offs structured and enforceable.
"""


class AdrError(ValueError):
    """Raised when an ADR repository, file format, slug, or lifecycle rule fails."""


def slugify_title(title: str) -> str:
    """Convert an ADR H1 title into a lowercase ASCII hyphenated filename slug."""
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not slug:
        raise AdrError(f"Title '{title}' produced an empty ADR filename slug.")
    return slug


def parse_adr_metadata(adr_path: Path) -> tuple[str, str, str | None, str]:
    """Extract ``(title, status_keyword, status_phrase, date)`` from a MADR file."""
    lines = adr_path.read_text(encoding="utf-8").splitlines()
    title = ""
    raw_status = ""
    date_val = ""
    for line in lines:
        stripped = line.strip()
        if not title and stripped.startswith("# "):
            title = stripped[2:].strip()
        elif not raw_status and stripped.startswith("* Status:"):
            raw_status = stripped[len("* Status:") :].strip()
        elif not date_val and stripped.startswith("* Date:"):
            date_val = stripped[len("* Date:") :].strip()

    if not title:
        raise AdrError(f"{adr_path.name}: Missing '# <Title>' heading.")
    if not raw_status:
        raise AdrError(f"{adr_path.name}: Missing '* Status: <status>' metadata line.")
    if not date_val:
        raise AdrError(f"{adr_path.name}: Missing '* Date: YYYY-MM-DD' metadata line.")

    parts = raw_status.split(" ", 1)
    status = parts[0].strip().lower()
    phrase = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    return title, status, phrase, date_val


def _rewrite_adr_status(adr_path: Path, new_status: str) -> None:
    content = adr_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    today = dt.date.today().isoformat()
    lines = content.splitlines()
    updated: list[str] = []
    for line in lines:
        if line.strip().startswith("* Status:"):
            updated.append(f"* Status: {new_status}")
        elif line.strip().startswith("* Date:"):
            updated.append(f"* Date: {today}")
        else:
            updated.append(line)
    adr_path.write_text("\n".join(updated) + "\n", encoding="utf-8", newline="\n")


class AdrCore:
    """Pure-MIT manager for `.adr` config, MADR lifecycle, TOC generation, and verification."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.config_path = self.repo_root / ".adr"

    @property
    def records_dir(self) -> Path:
        if not self.config_path.exists():
            return self.repo_root / "docs" / "adr"
        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding="utf-8")
        rel = parser.get("adr", "records-dir", fallback="docs/adr").strip()
        return (self.repo_root / rel).resolve()

    def configure(self, setting: str, value: str) -> None:
        if setting != "records-dir":
            raise AdrError(f"Unsupported .adr setting '{setting}'. Supported keys: records-dir.")
        rel_value = Path(value).as_posix()
        self.config_path.write_text(
            "# pyadr configuration — supported keys in [adr]: records-dir\n"
            "[adr]\n"
            f"records-dir = {rel_value}\n",
            encoding="utf-8",
            newline="\n",
        )

    def print_config(self, setting: str | None = None) -> str:
        if setting and setting != "records-dir":
            raise AdrError(f"Unsupported .adr setting '{setting}'.")
        rel = self.records_dir.relative_to(self.repo_root).as_posix()
        return f"records-dir = {rel}"

    def init_adr_repo(self, force: bool = False) -> list[Path]:
        adr_dir = self.records_dir
        if adr_dir.exists():
            if not force:
                raise AdrError(f"ADR directory already exists: {adr_dir}")
            shutil.rmtree(adr_dir)
        adr_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.configure("records-dir", "docs/adr")

        today = dt.date.today().isoformat()
        template_path = adr_dir / "template.md"
        adr_0000 = adr_dir / "0000-record-architecture-decisions.md"
        adr_0001 = adr_dir / "0001-use-markdown-architectural-decision-records.md"
        template_path.write_text(MADR_TEMPLATE, encoding="utf-8", newline="\n")
        adr_0000.write_text(INIT_0000_CONTENT.format(today=today), encoding="utf-8", newline="\n")
        adr_0001.write_text(INIT_0001_CONTENT.format(today=today), encoding="utf-8", newline="\n")
        self.generate_toc()
        return [template_path, adr_0000, adr_0001]

    def new_adr(self, title: str) -> Path:
        adr_dir = self.records_dir
        if not adr_dir.exists():
            raise AdrError(f"ADR directory does not exist: {adr_dir}")
        slug = slugify_title(title)
        target = adr_dir / f"XXXX-{slug}.md"
        if target.exists():
            raise AdrError(f"Proposed ADR already exists: {target.name}")
        today = dt.date.today().isoformat()
        content = (
            f"# {title.strip()}\n\n"
            f"* Status: {STATUS_PROPOSED}\n"
            "* Deciders: nectR Architecture\n"
            f"* Date: {today}\n\n"
            "## Context and Problem Statement\n\n"
            "[Describe the architectural problem in 2-3 concise sentences.]\n\n"
            "## Considered Options\n\n"
            "* [Option 1]\n"
            "* [Option 2]\n\n"
            "## Decision Outcome\n\n"
            'Chosen option: "[Option 1]", because [concise rationale].\n\n'
            "### Consequences\n\n"
            "* Good, because [benefit].\n"
            "* Bad, because [trade-off].\n"
        )
        target.write_text(content, encoding="utf-8", newline="\n")
        return target

    def _next_id(self) -> str:
        ids = []
        for path in self.records_dir.glob("[0-9][0-9][0-9][0-9]-*.md"):
            ids.append(int(path.stem.split("-", 1)[0]))
        return f"{(max(ids) + 1) if ids else 0:04d}"

    def accept_or_reject(self, file: Path | None, status: str, toc: bool = False) -> Path:
        if status not in {STATUS_ACCEPTED, STATUS_REJECTED}:
            raise AdrError(f"Target status must be 'accepted' or 'rejected', got '{status}'.")
        adr_dir = self.records_dir
        if file is None:
            proposed = sorted(adr_dir.glob("XXXX-*.md"))
            if len(proposed) != 1:
                raise AdrError(
                    f"Expected exactly 1 proposed XXXX-*.md file, found {len(proposed)}."
                )
            src_path = proposed[0]
        else:
            src_path = file if file.is_absolute() else (self.repo_root / file)
            if not src_path.exists():
                raise AdrError(f"ADR file not found: {src_path}")

        title, _, _, _ = parse_adr_metadata(src_path)
        next_id = self._next_id()
        dest_path = adr_dir / f"{next_id}-{slugify_title(title)}.md"
        _rewrite_adr_status(src_path, status)
        src_path.rename(dest_path)
        if toc:
            self.generate_toc()
        return dest_path

    def render_toc_content(self) -> str:
        """Render deterministic `docs/adr/index.md` grouping ADRs by status."""
        adr_dir = self.records_dir
        by_status: dict[str, list[str]] = {s: [] for s in STANDARD_STATUSES}
        non_standard: dict[str, list[str]] = {}

        candidates = sorted(
            list(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")) + list(adr_dir.glob("XXXX-*.md"))
        )
        for path in candidates:
            title, status, phrase, _ = parse_adr_metadata(path)
            adr_id = path.stem.split("-", 1)[0]
            supplement = f": {status} {phrase}" if phrase else ""
            entry = f"* [{adr_id} - {title}]({path.name}){supplement}\n"
            if status in by_status:
                by_status[status].append(entry)
            else:
                non_standard.setdefault(status, []).append(entry)

        titles = {
            STATUS_ACCEPTED: "Accepted Records",
            STATUS_REJECTED: "Rejected Records",
            STATUS_SUPERSEDED: "Superseded Records",
            STATUS_DEPRECATED: "Deprecated Records",
        }
        out: list[str] = [
            "<!-- This file has been generated by `pyadr`. Manual changes will be erased at next generation. -->\n",
            "\n",
            "# Architecture Decision Records\n",
        ]
        for st in STANDARD_STATUSES:
            out.extend(["\n", f"## {titles[st]}\n", "\n"])
            out.extend(by_status[st] if by_status[st] else ["* None\n"])

        out.extend(["\n", "## Records with non-standard statuses\n"])
        if non_standard:
            for st_key in sorted(non_standard):
                out.extend(["\n", f"### Status `{st_key}`\n", "\n"])
                out.extend(non_standard[st_key])
        else:
            out.extend(["\n", "* None\n"])
        return "".join(out)

    def generate_toc(self) -> Path:
        toc_path = self.records_dir / "index.md"
        toc_path.write_text(self.render_toc_content(), encoding="utf-8", newline="\n")
        return toc_path

    def check_adr_repo(self, check_no_proposed: bool = True) -> int:
        """Validate ADR filenames, ID uniqueness, metadata, title slugs, and proposed policy."""
        adr_dir = self.records_dir
        if not adr_dir.exists():
            raise AdrError(f"ADR directory does not exist: {adr_dir}")

        adr_files = sorted(p for p in adr_dir.glob("*.md") if p.name not in IGNORED_ADR_FILES)
        if not adr_files:
            raise AdrError(f"No ADR records found in {adr_dir}")

        seen_ids: dict[str, Path] = {}
        accepted_count = 0
        for path in adr_files:
            title, status, _, _ = parse_adr_metadata(path)
            expected_slug = slugify_title(title)
            if status == STATUS_PROPOSED:
                if check_no_proposed:
                    raise AdrError(
                        f"{path.name}: ADR has status 'proposed' (pass --allow-proposed on feature branches)."
                    )
                match_prop = PROPOSED_NAME_RE.match(path.name)
                if not match_prop or match_prop.group(1) != expected_slug:
                    raise AdrError(
                        f"{path.name}: Proposed ADR must be named 'XXXX-{expected_slug}.md'."
                    )
                continue

            match_id = WITH_ID_NAME_RE.match(path.name)
            if not match_id:
                raise AdrError(f"{path.name}: ADR filename must match 'NNNN-{expected_slug}.md'.")
            adr_id, file_slug = match_id.group(1), match_id.group(2)
            if adr_id in seen_ids:
                raise AdrError(
                    f"Duplicate ADR ID '{adr_id}': {seen_ids[adr_id].name} and {path.name}."
                )
            seen_ids[adr_id] = path
            if file_slug != expected_slug:
                raise AdrError(
                    f"{path.name}: Filename slug '{file_slug}' does not match H1 slug '{expected_slug}'."
                )
            if status == STATUS_ACCEPTED:
                accepted_count += 1
        return accepted_count


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyadr",
        description="Zero-CVE MIT Markdown Architectural Decision Record (MADR) CLI.",
    )
    parser.add_argument("--root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)

    cfg = sub.add_parser("config", help="Get or set .adr configuration.")
    cfg.add_argument("setting", nargs="?")
    cfg.add_argument("value", nargs="?")
    cfg.add_argument("-l", "--list", action="store_true")

    init_cmd = sub.add_parser("init", help="Initialize an ADR repository.")
    init_cmd.add_argument("-f", "--force", action="store_true")

    new_cmd = sub.add_parser("new", help="Create a new proposed ADR (XXXX-<slug>.md).")
    new_cmd.add_argument("title", nargs="+")

    prop_cmd = sub.add_parser("propose", help="Alias for `new` to propose a new ADR.")
    prop_cmd.add_argument("title", nargs="+")

    acc = sub.add_parser("accept", help="Accept a proposed ADR and assign the next ID.")
    acc.add_argument("file", nargs="?")
    acc.add_argument("--toc", action="store_true")

    rej = sub.add_parser("reject", help="Reject a proposed ADR and assign the next ID.")
    rej.add_argument("file", nargs="?")
    rej.add_argument("--toc", action="store_true")

    sub.add_parser("toc", help="Generate docs/adr/index.md table of contents.")

    chk = sub.add_parser("check-adr-repo", help="Verify ADR naming, IDs, format, and status.")
    chk.add_argument(
        "--allow-proposed",
        action="store_true",
        help="Allow XXXX-*.md records with status 'proposed' (e.g. on feature branches).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    core = AdrCore(Path(args.root).resolve())
    try:
        if args.command == "config":
            if args.list or args.value is None:
                print(core.print_config(args.setting))
            else:
                core.configure(args.setting, args.value)
                print(f"Configured '{args.setting}' to '{args.value}'.")
        elif args.command == "init":
            created = core.init_adr_repo(force=args.force)
            print(f"Initialized ADR repository with {len(created)} file(s).")
        elif args.command in {"new", "propose"}:
            path = core.new_adr(" ".join(args.title))
            print(f"Created proposed ADR: {path.name}")
        elif args.command == "accept":
            path = core.accept_or_reject(
                Path(args.file) if args.file else None, STATUS_ACCEPTED, toc=args.toc
            )
            print(f"Accepted ADR: {path.name}")
        elif args.command == "reject":
            path = core.accept_or_reject(
                Path(args.file) if args.file else None, STATUS_REJECTED, toc=args.toc
            )
            print(f"Rejected ADR: {path.name}")
        elif args.command == "toc":
            toc_path = core.generate_toc()
            print(f"Generated ADR index at {toc_path.name}.")
        elif args.command == "check-adr-repo":
            core.check_adr_repo(check_no_proposed=not args.allow_proposed)
            print("All checks passed.")
    except AdrError as exc:
        print(f"ADR validation error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
