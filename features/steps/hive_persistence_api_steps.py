"""Behave step definitions for hive_persistence_api."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from behave import given, then, when
from fastapi.testclient import TestClient

from nectr.contracts import BeeRole
from nectr.services import HiveServiceLayer


def _cleanup_repo(context: Any) -> None:
    repo = getattr(context, "repo", None)
    if repo is not None:
        repo.close()
    temp_dir = getattr(context, "temp_dir", None)
    if temp_dir is not None:
        temp_dir.cleanup()


@given("a SQLModel-backed HiveServiceLayer initialized via Alembic migrations")
def step_given_sqlmodel_service(context: Any) -> None:
    from nectr.services.api import create_app
    from nectr.services.persistence import SQLModelHiveRepository
    from nectr.services.telemetry import TelemetryAdapter

    temp_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_dir.name) / "bdd_hive.db"
    db_url = f"sqlite:///{db_path}"

    repo = SQLModelHiveRepository(database_url=db_url)
    telemetry = TelemetryAdapter(service_name="nectr-bdd")
    service = HiveServiceLayer(
        hive_id="HIVE_BDD",
        difficulty=1,
        accepted_status_peer_threshold=2,
        repository=repo,
        telemetry=telemetry,
    )
    service.bootstrap_sponsored_hive(
        seed_comb_amount=200.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    service.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.allocate_raw_pollen("queen_1", "learner_1", 25.0)

    context.temp_dir = temp_dir
    context.db_url = db_url
    context.repo = repo
    context.telemetry = telemetry
    context.service = service
    context.client = TestClient(create_app(service))


@when("a Certified Worker Bee settles a tutoring barter via the FastAPI endpoint")
def step_when_settle_via_api(context: Any) -> None:
    response = context.client.post(
        "/sessions/handshake",
        json={
            "session_id": "bdd_sess_1",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 10.0,
            "token_state": "RAW_POLLEN",
            "learner_attestation_score": 0.95,
        },
    )
    assert response.status_code == 200, response.text
    context.api_response = response


@then("the updated balances persist across repository reload with structured trace logs")
def step_then_persists_with_logs(context: Any) -> None:
    from nectr.services.persistence import SQLModelHiveRepository

    try:
        context.repo.close()
        reloaded_repo = SQLModelHiveRepository(database_url=context.db_url)
        try:
            reloaded = HiveServiceLayer.from_repository("HIVE_BDD", repository=reloaded_repo)
            assert reloaded.contracts.accounts["worker_1"].liquid_nectr_balance == 10.0
            assert reloaded.contracts.accounts["learner_1"].raw_pollen_balance == 15.0
            events = context.telemetry.get_recorded_events()
            spans = context.telemetry.get_finished_spans()
            assert any(e.get("hive_id") == "HIVE_BDD" for e in events)
            assert len(spans) >= 1
        finally:
            reloaded_repo.close()
    finally:
        temp_dir = getattr(context, "temp_dir", None)
        if temp_dir is not None:
            temp_dir.cleanup()


@when("a tutoring handshake fails with an invalid attestation score via the FastAPI endpoint")
def step_when_invalid_handshake_via_api(context: Any) -> None:
    response = context.client.post(
        "/sessions/handshake",
        json={
            "session_id": "bdd_sess_bad",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 10.0,
            "token_state": "RAW_POLLEN",
            "learner_attestation_score": 1.5,
        },
    )
    context.api_response = response


@then("the HTTP request is rejected and learner balances remain unchanged across repository reload")
def step_then_rollback_persists(context: Any) -> None:
    from nectr.services.persistence import SQLModelHiveRepository

    try:
        assert context.api_response.status_code == 400
        assert context.service.contracts.accounts["learner_1"].raw_pollen_balance == 25.0
        context.repo.close()
        reloaded_repo = SQLModelHiveRepository(database_url=context.db_url)
        try:
            reloaded = HiveServiceLayer.from_repository("HIVE_BDD", repository=reloaded_repo)
            assert reloaded.contracts.accounts["learner_1"].raw_pollen_balance == 25.0
            assert "bdd_sess_bad" not in reloaded.contracts.sessions
        finally:
            reloaded_repo.close()
    finally:
        _cleanup_repo(context)
