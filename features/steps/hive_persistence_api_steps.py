"""Behave step definitions for hive_persistence_api."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Any

from behave import given, then, when
from fastapi.testclient import TestClient

from nectr.chain import Ed25519Signer, SignedTransaction, compute_sha256
from nectr.contracts import BeeRole
from nectr.services import HiveServiceLayer


def _bdd_signer(bee_id: str) -> Ed25519Signer:
    return Ed25519Signer.from_seed(hashlib.sha256(f"bdd_persist:{bee_id}".encode()).digest())


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
    queen_signer = _bdd_signer("queen_1")
    worker_signer = _bdd_signer("worker_1")
    learner_signer = _bdd_signer("learner_1")

    service.bootstrap_sponsored_hive(
        SignedTransaction.create(
            {
                "action": "BOOTSTRAP_HIVE",
                "hive_id": "HIVE_BDD",
                "queen_id": "queen_1",
                "seed_comb_amount": 200.0,
                "queen_public_keys": {"queen_1": queen_signer.public_key_hex},
                "certified_workers": {"worker_1": ["CS-101"]},
                "worker_public_keys": {"worker_1": worker_signer.public_key_hex},
                "nonce": 1,
            },
            signer=queen_signer,
            signer_id="queen_1",
        )
    )
    service.register_bee(
        SignedTransaction.create(
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_BDD",
                "bee_id": "learner_1",
                "role": BeeRole.LEARNER_BEE.value,
                "nonce": 1,
            },
            signer=learner_signer,
            signer_id="learner_1",
        )
    )
    service.allocate_raw_pollen(
        SignedTransaction.create(
            {
                "action": "ALLOCATE_RAW_POLLEN",
                "hive_id": "HIVE_BDD",
                "queen_id": "queen_1",
                "learner_id": "learner_1",
                "amount": 25.0,
                "nonce": 2,
            },
            signer=queen_signer,
            signer_id="queen_1",
        )
    )

    context.temp_dir = temp_dir
    context.db_url = db_url
    context.repo = repo
    context.telemetry = telemetry
    context.service = service
    context.worker_signer = worker_signer
    context.learner_signer = learner_signer
    context.client = TestClient(create_app(service))


@when("a Certified Worker Bee settles a tutoring barter via the FastAPI endpoint")
def step_when_settle_via_api(context: Any) -> None:
    escrow_tx = SignedTransaction.create(
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": "HIVE_BDD",
            "session_id": "bdd_sess_1",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 10.0,
            "token_state": "RAW_POLLEN",
            "nonce": 2,
        },
        signer=context.learner_signer,
        signer_id="learner_1",
    )
    settle_payload = {
        "action": "SETTLE_SESSION",
        "hive_id": "HIVE_BDD",
        "session_id": "bdd_sess_1",
        "learner_attestation_score": 0.95,
        "tutor_comprehension_hash": compute_sha256("bdd_sess_1:worker_1:learner_1:CS-101"),
        "learner_nonce": 3,
        "tutor_nonce": 1,
    }
    response = context.client.post(
        "/sessions/handshake",
        json={
            "escrow_tx": escrow_tx.model_dump(mode="json"),
            "learner_settle_tx": SignedTransaction.create(
                settle_payload, signer=context.learner_signer, signer_id="learner_1"
            ).model_dump(mode="json"),
            "tutor_settle_tx": SignedTransaction.create(
                settle_payload, signer=context.worker_signer, signer_id="worker_1"
            ).model_dump(mode="json"),
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
    escrow_tx = SignedTransaction.create(
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": "HIVE_BDD",
            "session_id": "bdd_sess_bad",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 10.0,
            "token_state": "RAW_POLLEN",
            "nonce": 2,
        },
        signer=context.learner_signer,
        signer_id="learner_1",
    )
    settle_payload = {
        "action": "SETTLE_SESSION",
        "hive_id": "HIVE_BDD",
        "session_id": "bdd_sess_bad",
        "learner_attestation_score": 1.5,
        "tutor_comprehension_hash": compute_sha256("bdd_sess_bad:worker_1:learner_1:CS-101"),
        "learner_nonce": 3,
        "tutor_nonce": 1,
    }
    response = context.client.post(
        "/sessions/handshake",
        json={
            "escrow_tx": escrow_tx.model_dump(mode="json"),
            "learner_settle_tx": SignedTransaction.create(
                settle_payload, signer=context.learner_signer, signer_id="learner_1"
            ).model_dump(mode="json"),
            "tutor_settle_tx": SignedTransaction.create(
                settle_payload, signer=context.worker_signer, signer_id="worker_1"
            ).model_dump(mode="json"),
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
