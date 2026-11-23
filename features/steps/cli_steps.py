"""Behave step definitions for the nectr CLI (`simulate` and `serve`)."""

from __future__ import annotations

import builtins
import io
import json
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from behave import given, then, when


@given("the nectr CLI application")
def step_given_cli_app(context: Any) -> None:
    context.cli_available = True


@given("the nectr CLI application and a temporary SQLite database path")
def step_given_cli_with_db(context: Any) -> None:
    tmp = tempfile.TemporaryDirectory()
    context._tmp = tmp
    context.db_path = Path(tmp.name) / "nectr_cli_bdd.db"


@given("the nectr CLI application without uvicorn installed")
def step_given_cli_without_uvicorn(context: Any) -> None:
    context.hide_uvicorn = True


@when('the user runs the CLI with arguments "{arg_str}"')
def step_when_run_cli_args(context: Any, arg_str: str) -> None:
    from nectr.cli import main

    argv = arg_str.split()
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    if getattr(context, "hide_uvicorn", False):
        real_import = builtins.__import__
        saved_uvicorn = sys.modules.pop("uvicorn", None)

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

        builtins.__import__ = _blocking_import  # type: ignore[assignment]
        try:
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                context.exit_code = main(argv)
        finally:
            builtins.__import__ = real_import
            if saved_uvicorn is not None:
                sys.modules["uvicorn"] = saved_uvicorn
    else:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            context.exit_code = main(argv)

    context.stdout = stdout_buf.getvalue()
    context.stderr = stderr_buf.getvalue()


@when("the user runs the CLI serve command with a stubbed ASGI server")
def step_when_run_cli_serve_stubbed(context: Any) -> None:
    from nectr.cli import main

    recorded: dict[str, Any] = {}
    stub_uvicorn = types.ModuleType("uvicorn")

    def _fake_run(app: Any, *, host: str, port: int) -> None:
        recorded["app"] = app
        recorded["host"] = host
        recorded["port"] = port

    stub_uvicorn.run = _fake_run  # type: ignore[attr-defined]
    saved_uvicorn = sys.modules.get("uvicorn")
    sys.modules["uvicorn"] = stub_uvicorn

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        db_url = f"sqlite:///{context.db_path.as_posix()}"
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            context.exit_code = main(
                [
                    "serve",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8123",
                    "--hive-id",
                    "HIVE_CLI_BDD",
                    "--database-url",
                    db_url,
                ]
            )
    finally:
        if saved_uvicorn is not None:
            sys.modules["uvicorn"] = saved_uvicorn
        else:
            sys.modules.pop("uvicorn", None)

    context.serve_recorded = recorded
    context.stdout = stdout_buf.getvalue()
    context.stderr = stderr_buf.getvalue()


@then("the CLI exits with status 0 and prints valid deterministic simulation JSON")
def step_then_simulate_output_valid(context: Any) -> None:
    assert context.exit_code == 0, context.stderr
    payload = json.loads(context.stdout)
    assert payload["telemetry"]["hive_a_chain_valid"] is True
    assert payload["telemetry"]["pollinator_accepted_in_hive_b"] is True
    assert "hive_a_head_hash" in payload["metadata"]


@then(
    "the CLI exits with status 0 and serves the Hive FastAPI app for the requested host, port, and hive id"
)
def step_then_serve_delegated(context: Any) -> None:
    from fastapi.testclient import TestClient

    assert context.exit_code == 0, context.stderr
    assert context.serve_recorded["host"] == "127.0.0.1"
    assert context.serve_recorded["port"] == 8123
    client = TestClient(context.serve_recorded["app"])
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["hive_id"] == "HIVE_CLI_BDD"


@then("the CLI exits with status 1 and prints an install hint for the api extra")
def step_then_missing_uvicorn_hint(context: Any) -> None:
    assert context.exit_code == 1
    assert "api" in context.stderr.lower()
    assert "uvicorn" in context.stderr.lower()


@given("the installed nectr console script")
def step_given_installed_nectr_script(context: Any) -> None:
    exe_name = "nectr.exe" if sys.platform == "win32" else "nectr"
    nectr_exe = Path(sys.executable).parent / exe_name
    assert nectr_exe.is_file(), f"Missing nectr console script at {nectr_exe}"
    context.nectr_exe = nectr_exe


@when('the user runs "nectr simulate" in two separate subprocesses')
def step_when_run_simulate_subprocesses(context: Any) -> None:
    context.sim_run_1 = subprocess.run(
        [str(context.nectr_exe), "simulate"], capture_output=True, check=True
    )
    context.sim_run_2 = subprocess.run(
        [str(context.nectr_exe), "simulate"], capture_output=True, check=True
    )


@then("both subprocess stdout byte streams are identical and parse as valid telemetry JSON")
def step_then_subprocesses_byte_identical(context: Any) -> None:
    assert len(context.sim_run_1.stdout) > 0
    assert context.sim_run_1.stdout == context.sim_run_2.stdout
    payload = json.loads(context.sim_run_1.stdout.decode("utf-8"))
    assert payload["telemetry"]["hive_a_chain_valid"] is True
    assert "hive_a_head_hash" in payload["metadata"]
