"""Top-level command-line interface for running nectR simulations and serving a Hive node."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

    from nectr.services.persistence import SQLModelHiveRepository


def build_serve_app(
    *,
    hive_id: str = "HIVE_ALPHA",
    database_url: str = "sqlite:///nectr.db",
    difficulty: int = 2,
) -> tuple[FastAPI, SQLModelHiveRepository]:
    """Initialize or hydrate a HiveServiceLayer backed by SQLite and build its FastAPI app."""
    from nectr.services.api import create_app
    from nectr.services.hive_service import HiveServiceLayer
    from nectr.services.persistence import SQLModelHiveRepository

    repo = SQLModelHiveRepository(database_url=database_url)
    try:
        repo.initialize()
        if repo.load_hive_snapshot(hive_id) is not None:
            service = HiveServiceLayer.from_repository(hive_id=hive_id, repository=repo)
        else:
            service = HiveServiceLayer(
                hive_id=hive_id,
                difficulty=difficulty,
                repository=repo,
            )
        app = create_app(service)
    except Exception:
        repo.close()
        raise
    return app, repo


def _cmd_simulate() -> int:
    from nectr.personas.simulator import run_multi_hive_persona_simulation

    telemetry, metadata = run_multi_hive_persona_simulation()
    payload = {
        "telemetry": asdict(telemetry),
        "metadata": metadata,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _cmd_serve(
    *,
    host: str,
    port: int,
    hive_id: str,
    database_url: str,
    difficulty: int,
) -> int:
    try:
        import uvicorn
    except ImportError:
        print(
            "uvicorn is required for `nectr serve`. Install the api extra: "
            "uv sync --extra api (or pip install 'nectr[api]').",
            file=sys.stderr,
        )
        return 1

    app, repo = build_serve_app(
        hive_id=hive_id,
        database_url=database_url,
        difficulty=difficulty,
    )
    try:
        uvicorn.run(app, host=host, port=port)
    finally:
        repo.close()
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nectr",
        description="nectR peer-tutoring credit economy simulation and Hive node CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "simulate",
        help="Run the deterministic multi-hive 6-persona simulation and print JSON telemetry.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the FastAPI Hive node server (requires the optional 'api' extra).",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host address (default: 127.0.0.1).",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind TCP port (default: 8000).",
    )
    serve_parser.add_argument(
        "--hive-id",
        default="HIVE_ALPHA",
        help="Hive identifier to initialize or load (default: HIVE_ALPHA).",
    )
    serve_parser.add_argument(
        "--database-url",
        default="sqlite:///nectr.db",
        help="SQLAlchemy database URL for Hive persistence (default: sqlite:///nectr.db).",
    )
    serve_parser.add_argument(
        "--difficulty",
        type=int,
        default=2,
        help="PoW difficulty when initializing a new Hive (default: 2).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for the ``nectr`` console script."""
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "simulate":
        return _cmd_simulate()
    if args.command == "serve":
        return _cmd_serve(
            host=str(args.host),
            port=int(args.port),
            hive_id=str(args.hive_id),
            database_url=str(args.database_url),
            difficulty=int(args.difficulty),
        )
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
