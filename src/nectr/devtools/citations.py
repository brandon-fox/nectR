"""Automated citation validation, plagiarism custody, and provenance lineage controls."""

from __future__ import annotations

import argparse
import sys
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import networkx as nx
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

MIN_PEER_REVIEWED_RATIO = 0.70

FORBIDDEN_SOURCE_DOMAINS: frozenset[str] = frozenset(
    {
        "grokipedia.com",
        "wikipedia.org",
        "reddit.com",
        "scribd.com",
        "youtube.com",
        "devpost.com",
        "plagiarism.repec.org",
        "docs.google.com",
        "medium.com",
        "blogspot.com",
        "trading212.com",
        "earninghustler.com",
        "collegehelpguide.com",
        "edushaale.com",
        "marcomsociety.org",
        "vistingo.com",
    }
)


class CitationGovernanceError(ValueError):
    """Raised when a reference or provenance lineage graph violates quality/custody rules."""


class SourceType(StrEnum):
    PEER_REVIEWED_JOURNAL = "peer-reviewed-journal"
    CONFERENCE_PROCEEDINGS = "conference-proceedings"
    ACADEMIC_BOOK = "academic-book"
    TECHNICAL_SPEC = "technical-spec"
    PREPRINT = "preprint"
    INSTITUTIONAL_REPORT = "institutional-report"
    INTERNAL_EXPERIMENT = "internal-experiment"
    SECONDARY_WEB = "secondary-web"


PEER_REVIEWED_TYPES: frozenset[SourceType] = frozenset(
    {SourceType.PEER_REVIEWED_JOURNAL, SourceType.CONFERENCE_PROCEEDINGS}
)


class ReferenceEntry(BaseModel):
    """Schema-validated citation with authorship custody and plagiarism screening state."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9_]+$")
    title: str = Field(min_length=4, max_length=220)
    authors: list[str] = Field(min_length=1)
    year: int = Field(ge=1900, le=2030)
    source_type: SourceType
    venue: str = ""
    doi: str | None = None
    url: str | None = None
    custody_agent: str = Field(min_length=3)
    plagiarism_screen: Literal["clean", "flagged", "retracted"] = "clean"
    status: Literal["verified", "quarantined"] = "verified"


class ReferenceRegistry(BaseModel):
    """Canonical bibliography stored in paper/references.yaml."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1, le=1)
    references: list[ReferenceEntry] = Field(default_factory=list)

    @field_validator("references")
    @classmethod
    def _unique_ids(cls, items: list[ReferenceEntry]) -> list[ReferenceEntry]:
        seen: set[str] = set()
        for item in items:
            if item.id in seen:
                raise ValueError(f"Duplicate reference ID '{item.id}'.")
            seen.add(item.id)
        return items


class LineageNode(BaseModel):
    """Node in the Source -> Theory -> Decision -> Code provenance DAG."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^(source|theory|decision|code):[A-Za-z0-9_.:-]+$")
    kind: Literal["source", "theory", "decision", "code"]
    label: str = Field(min_length=2, max_length=120)
    path: str
    test_path: str | None = None


class LineageEdge(BaseModel):
    """Directed intent edge explaining why an upstream artifact drives a downstream artifact."""

    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    intent: str = Field(min_length=3, max_length=120)


class LineageGraph(BaseModel):
    """Canonical provenance DAG stored in paper/lineage.yaml."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1, le=1)
    nodes: list[LineageNode] = Field(default_factory=list)
    edges: list[LineageEdge] = Field(default_factory=list)


def load_references(yaml_path: Path) -> ReferenceRegistry:
    if not yaml_path.exists():
        raise CitationGovernanceError(f"Missing citation registry: {yaml_path}")
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    return ReferenceRegistry.model_validate(raw)


def load_lineage(yaml_path: Path) -> LineageGraph:
    if not yaml_path.exists():
        raise CitationGovernanceError(f"Missing lineage graph: {yaml_path}")
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    return LineageGraph.model_validate(raw)


def _is_banned_host(url: str) -> str | None:
    host = urlparse(url).netloc.lower().split(":", 1)[0]
    for banned in FORBIDDEN_SOURCE_DOMAINS:
        if host == banned or host.endswith(f".{banned}"):
            return banned
    return None


def validate_references(registry: ReferenceRegistry) -> float:
    """Enforce banned-domain guards, DOI/URL requirements, and >=70% peer-reviewed floor."""
    if not registry.references:
        raise CitationGovernanceError("Reference registry cannot be empty.")

    external_count = 0
    peer_reviewed_count = 0

    for ref in registry.references:
        if ref.url:
            banned = _is_banned_host(ref.url)
            if banned:
                raise CitationGovernanceError(
                    f"Reference '{ref.id}' uses banned domain '{banned}' ({ref.url})."
                )
        if ref.source_type != SourceType.INTERNAL_EXPERIMENT:
            external_count += 1
            if not ref.doi and not ref.url:
                raise CitationGovernanceError(
                    f"External reference '{ref.id}' must provide a DOI or archival URL."
                )
            if ref.source_type in PEER_REVIEWED_TYPES:
                peer_reviewed_count += 1

    if external_count == 0:
        raise CitationGovernanceError("At least one external peer-reviewed reference is required.")

    ratio = peer_reviewed_count / external_count
    if ratio < MIN_PEER_REVIEWED_RATIO:
        raise CitationGovernanceError(
            f"External peer-reviewed ratio {ratio:.2%} is below minimum floor "
            f"{MIN_PEER_REVIEWED_RATIO:.0%} ({peer_reviewed_count}/{external_count})."
        )
    return ratio


def build_nx_graph(lineage: LineageGraph) -> nx.DiGraph[str]:
    """Build a directed acyclic provenance graph in NetworkX and verify acyclicity."""
    graph: nx.DiGraph[str] = nx.DiGraph()
    node_ids = {n.id for n in lineage.nodes}
    for node in lineage.nodes:
        graph.add_node(
            node.id,
            kind=node.kind,
            label=node.label,
            path=node.path,
            test_path=node.test_path,
        )
    for edge in lineage.edges:
        if edge.source not in node_ids:
            raise CitationGovernanceError(
                f"Lineage edge references unknown source '{edge.source}'."
            )
        if edge.target not in node_ids:
            raise CitationGovernanceError(
                f"Lineage edge references unknown target '{edge.target}'."
            )
        graph.add_edge(edge.source, edge.target, intent=edge.intent)
    if not nx.is_directed_acyclic_graph(graph):
        raise CitationGovernanceError("Lineage provenance graph contains a cycle.")
    return graph


def compute_impacted_downstream(lineage: LineageGraph, ref_id: str) -> list[str]:
    """Return all downstream node IDs impacted if ``ref_id`` is tainted or modified."""
    graph = build_nx_graph(lineage)
    source_node = f"source:{ref_id}"
    if source_node not in graph:
        return []
    return sorted(str(node) for node in nx.descendants(graph, source_node))


def validate_lineage_integrity(
    refs: ReferenceRegistry, lineage: LineageGraph, repo_root: Path
) -> nx.DiGraph[str]:
    """Verify source nodes match references.yaml and all linked repo files exist."""
    graph = build_nx_graph(lineage)
    ref_ids = {r.id for r in refs.references}
    for node in lineage.nodes:
        if node.kind == "source":
            raw_ref_id = node.id.split(":", 1)[1]
            if raw_ref_id not in ref_ids:
                raise CitationGovernanceError(
                    f"Lineage source node '{node.id}' missing from paper/references.yaml."
                )
            continue
        target = repo_root / node.path
        if not target.exists():
            raise CitationGovernanceError(
                f"Lineage node '{node.id}' points to missing path '{node.path}'."
            )
        if node.test_path and not (repo_root / node.test_path).exists():
            raise CitationGovernanceError(
                f"Lineage node '{node.id}' points to missing test_path '{node.test_path}'."
            )
    return graph


def render_provenance_report(
    refs: ReferenceRegistry,
    lineage: LineageGraph,
    repo_root: Path,
    allow_quarantined: bool = False,
) -> str:
    """Validate citations + lineage and render docs/theory/provenance_lineage.md."""
    ratio = validate_references(refs)
    validate_lineage_integrity(refs, lineage, repo_root)

    tainted = [
        r for r in refs.references if r.plagiarism_screen != "clean" or r.status != "verified"
    ]
    if tainted and not allow_quarantined:
        tainted_ids = ", ".join(r.id for r in tainted)
        impacted_all = sorted(
            {n for r in tainted for n in compute_impacted_downstream(lineage, r.id)}
        )
        raise CitationGovernanceError(
            f"quarantined/flagged references detected ({tainted_ids}); "
            f"impacted downstream artifacts: {impacted_all}"
        )

    external_count = sum(
        1 for r in refs.references if r.source_type != SourceType.INTERNAL_EXPERIMENT
    )
    peer_count = sum(1 for r in refs.references if r.source_type in PEER_REVIEWED_TYPES)

    lines: list[str] = [
        "<!-- AUTO-GENERATED by `nectr-citations render` from `paper/references.yaml` & `paper/lineage.yaml`. Do not edit manually. -->",
        "",
        "# Citation Quality & Provenance Chain-of-Custody",
        "",
        "This report links canonical primary literature through mathematical theory, architectural decisions, and production code/tests so source flaws trigger deterministic downstream rebuild flags.",
        "",
        "## Evidence Quality Scorecard",
        "",
        "| Metric | Observed Value | Required Threshold |",
        "| :--- | :---: | :---: |",
        f"| External References | `{external_count}` | `>= 1` |",
        f"| Peer-Reviewed Ratio | `{ratio:.1%}` (`{peer_count}/{external_count}`) | `>= 70.0%` |",
        f"| Quarantined / Flagged Sources | `{len(tainted)}` | `0` (strict mode) |",
        f"| Lineage Edges Tracked | `{len(lineage.edges)}` | DAG verified |",
        "",
        "## Lineage Graph (Sources → Theory → Decisions → Code)",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for node in lineage.nodes:
        safe_id = node.id.replace(":", "_").replace("-", "_")
        safe_label = node.label.replace('"', "'")
        lines.append(f'    {safe_id}["{safe_label}"]')
    for edge in lineage.edges:
        src_id = edge.source.replace(":", "_").replace("-", "_")
        dst_id = edge.target.replace(":", "_").replace("-", "_")
        safe_intent = edge.intent.replace('"', "'")
        lines.append(f'    {src_id} -->|"{safe_intent}"| {dst_id}')

    lines.extend(
        [
            "```",
            "",
            "## Downstream Quarantine & Rebuild Alerts",
            "",
        ]
    )
    if tainted:
        lines.append(
            "| Tainted Reference | Custody Status | Plagiarism Screen | Impacted Downstream Artifacts |"
        )
        lines.append("| :--- | :--- | :--- | :--- |")
        for ref in tainted:
            impacted = ", ".join(f"`{n}`" for n in compute_impacted_downstream(lineage, ref.id))
            lines.append(
                f"| **`{ref.id}`** | **REBUILD REQUIRED** (`{ref.status}`) | `{ref.plagiarism_screen}` | {impacted or '—'} |"
            )
    else:
        lines.append(
            "All canonical references passed plagiarism screening (`clean`) and custody checks (`verified`). No downstream rebuilds required."
        )

    lines.extend(
        [
            "",
            "## Chain-of-Custody Reference Ledger",
            "",
            "| ID | Year | Type | Custody Agent | Plagiarism Screen | Identifier |",
            "| :--- | :---: | :--- | :--- | :---: | :--- |",
        ]
    )
    for ref in refs.references:
        ident = ref.doi or ref.url or "internal"
        lines.append(
            f"| `{ref.id}` | {ref.year} | `{ref.source_type}` | `{ref.custody_agent}` | `{ref.plagiarism_screen}` | `{ident}` |"
        )
    lines.append("")
    return "\n".join(lines)


def check_all_citations(repo_root: Path) -> dict[str, Any]:
    """Validate paper/references.yaml, paper/lineage.yaml, and docs/theory/provenance_lineage.md."""
    refs = load_references(repo_root / "paper" / "references.yaml")
    lineage = load_lineage(repo_root / "paper" / "lineage.yaml")
    expected_md = render_provenance_report(refs, lineage, repo_root, allow_quarantined=False)
    report_path = repo_root / "docs" / "theory" / "provenance_lineage.md"
    if not report_path.exists():
        raise CitationGovernanceError(
            "Missing docs/theory/provenance_lineage.md (run `nectr-citations render`)."
        )
    actual_md = report_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if actual_md != expected_md.replace("\r\n", "\n"):
        raise CitationGovernanceError(
            "docs/theory/provenance_lineage.md is out of sync (run `nectr-citations render`)."
        )
    ratio = validate_references(refs)
    external_count = sum(
        1 for r in refs.references if r.source_type != SourceType.INTERNAL_EXPERIMENT
    )
    quarantined_count = sum(
        1 for r in refs.references if r.plagiarism_screen != "clean" or r.status != "verified"
    )
    return {
        "external_reference_count": external_count,
        "peer_reviewed_ratio": round(ratio, 4),
        "quarantined_count": quarantined_count,
        "lineage_edges": len(lineage.edges),
        "report_in_sync": True,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr-citations",
        description="Validate bibliography quality floors and provenance chain-of-custody.",
    )
    parser.add_argument("--root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "check", help="Validate references, lineage DAG, and rendered provenance report."
    )
    ren = sub.add_parser("render", help="Render docs/theory/provenance_lineage.md.")
    ren.add_argument(
        "--allow-quarantined",
        action="store_true",
        help="Allow rendering REBUILD REQUIRED alerts for quarantined sources.",
    )
    imp = sub.add_parser("impact", help="Show downstream artifacts impacted by a reference ID.")
    imp.add_argument("ref_id", help="Reference ID from paper/references.yaml.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "check":
            summary = check_all_citations(root)
            print(
                f"Citations & Provenance OK: {summary['external_reference_count']} external refs "
                f"({summary['peer_reviewed_ratio']:.1%} peer-reviewed), {summary['lineage_edges']} edges."
            )
            return 0
        if args.command == "render":
            refs = load_references(root / "paper" / "references.yaml")
            lineage = load_lineage(root / "paper" / "lineage.yaml")
            rendered = render_provenance_report(
                refs, lineage, root, allow_quarantined=args.allow_quarantined
            )
            out_path = root / "docs" / "theory" / "provenance_lineage.md"
            out_path.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"Rendered {out_path.relative_to(root).as_posix()}.")
            return 0
        if args.command == "impact":
            lineage = load_lineage(root / "paper" / "lineage.yaml")
            impacted = compute_impacted_downstream(lineage, args.ref_id)
            print("\n".join(impacted) if impacted else "No downstream impacts.")
            return 0
    except (CitationGovernanceError, ValidationError, ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Citation governance error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
