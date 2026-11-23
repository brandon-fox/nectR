"""Strict TDD tests for the `nectr` CLI (`simulate` and `serve`)."""

from __future__ import annotations

import builtins
import json
import subprocess
import sys
import tomllib
import types
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_registers_nectr_script() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]
    assert scripts.get("nectr") == "nectr.cli:main"


def test_cli_simulate_outputs_deterministic_json(capsys: pytest.CaptureFixture[str]) -> None:
    from nectr.cli import main

    rc_first = main(["simulate"])
    out_first = capsys.readouterr().out
    rc_second = main(["simulate"])
    out_second = capsys.readouterr().out

    assert rc_first == 0
    assert rc_second == 0
    assert out_first == out_second

    parsed = json.loads(out_first)
    assert parsed["telemetry"]["hive_a_chain_valid"] is True
    assert parsed["telemetry"]["hive_a_blocks_mined"] == 5
    assert parsed["telemetry"]["pollinator_accepted_in_hive_b"] is True
    assert "hive_a_head_hash" in parsed["metadata"]


def test_cli_serve_builds_app_and_calls_uvicorn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    from nectr.cli import build_serve_app, main

    db_url = f"sqlite:///{(tmp_path / 'cli_serve.db').as_posix()}"

    app, repo = build_serve_app(hive_id="HIVE_CLI", database_url=db_url)
    try:
        client = TestClient(app)
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["hive_id"] == "HIVE_CLI"
        state = client.get("/hive/state")
        assert state.status_code == 200
        assert state.json()["hive_id"] == "HIVE_CLI"
    finally:
        repo.close()

    # Second open hydrates existing Hive cleanly via from_repository.
    app_reloaded, repo_reloaded = build_serve_app(hive_id="HIVE_CLI", database_url=db_url)
    try:
        health_reloaded = TestClient(app_reloaded).get("/health")
        assert health_reloaded.status_code == 200
        assert health_reloaded.json()["hive_id"] == "HIVE_CLI"
    finally:
        repo_reloaded.close()

    recorded: dict[str, Any] = {}
    stub_uvicorn = types.ModuleType("uvicorn")

    def _fake_run(served_app: Any, *, host: str, port: int) -> None:
        recorded["app"] = served_app
        recorded["host"] = host
        recorded["port"] = port

    stub_uvicorn.run = _fake_run  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "uvicorn", stub_uvicorn)

    rc = main(
        [
            "serve",
            "--host",
            "0.0.0.0",
            "--port",
            "9001",
            "--hive-id",
            "HIVE_CLI",
            "--database-url",
            db_url,
        ]
    )
    assert rc == 0
    assert recorded["host"] == "0.0.0.0"
    assert recorded["port"] == 9001
    assert TestClient(recorded["app"]).get("/health").status_code == 200


def test_cli_serve_missing_uvicorn_returns_nonzero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from nectr.cli import main

    real_import = builtins.__import__
    monkeypatch.delitem(sys.modules, "uvicorn", raising=False)

    def _blocking_import(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name == "uvicorn":
            raise ImportError("No module named 'uvicorn'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _blocking_import)

    rc = main(["serve"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "uvicorn" in err.lower()
    assert "api" in err.lower()


def test_cli_simulate_subprocess_smoke_byte_identical() -> None:
    exe_name = "nectr.exe" if sys.platform == "win32" else "nectr"
    nectr_exe = Path(sys.executable).parent / exe_name
    assert nectr_exe.is_file(), f"Expected installed console script at {nectr_exe}"

    run_1 = subprocess.run([str(nectr_exe), "simulate"], capture_output=True, check=True)
    run_2 = subprocess.run([str(nectr_exe), "simulate"], capture_output=True, check=True)
    run_mod = subprocess.run(
        [sys.executable, "-m", "nectr.cli", "simulate"], capture_output=True, check=True
    )

    assert len(run_1.stdout) > 0
    assert run_1.stdout == run_2.stdout
    assert run_1.stdout == run_mod.stdout

    payload = json.loads(run_1.stdout.decode("utf-8"))
    assert payload["telemetry"]["hive_a_chain_valid"] is True
    assert payload["telemetry"]["pollinator_accepted_in_hive_b"] is True
    assert "hive_a_head_hash" in payload["metadata"]
