"""Unit and integration tests for nectR SQLModel persistence, Alembic migrations, telemetry, and FastAPI."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nectr.contracts import BeeRole, ContractViolationError, SessionStatus, TokenState
from nectr.services import HiveServiceLayer


def test_backward_compatible_in_memory_hive_service_layer() -> None:
    service = HiveServiceLayer(
        hive_id="HIVE_MEM",
        difficulty=1,
        accepted_status_peer_threshold=2,
        repository=None,
        telemetry=None,
    )
    boot = service.bootstrap_sponsored_hive(
        seed_comb_amount=150.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    assert boot["genesis_comb"] == pytest.approx(150.0)
    assert service.blockchain.verify_chain() is True


def test_alembic_migrations_and_sqlmodel_repository_reload(tmp_path: Path) -> None:
    from nectr.services.persistence import SQLModelHiveRepository

    db_path = tmp_path / "hive_state.db"
    db_url = f"sqlite:///{db_path}"

    repo = SQLModelHiveRepository(database_url=db_url)
    repo.initialize()
    # Idempotent re-initialization
    repo.initialize()

    service = HiveServiceLayer(
        hive_id="HIVE_PERSIST",
        difficulty=1,
        accepted_status_peer_threshold=2,
        repository=repo,
    )
    service.bootstrap_sponsored_hive(
        seed_comb_amount=500.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    service.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.register_bee("learner_2", role=BeeRole.LEARNER_BEE)
    service.allocate_raw_pollen("queen_1", "learner_1", 30.0)
    service.allocate_raw_pollen("queen_1", "learner_2", 20.0)

    # Settled session
    service.execute_tutoring_handshake(
        session_id="sess_1",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=12.0,
        token_state=TokenState.RAW_POLLEN,
        learner_attestation_score=0.95,
    )
    # Open INTENT_ESCROWED session
    service.create_barter_escrow(
        session_id="sess_open",
        tutor_id="worker_1",
        learner_id="learner_2",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=8.0,
        token_state=TokenState.RAW_POLLEN,
    )
    service.mine_epoch_block()

    expected_comb = service.contracts.comb_reserve
    expected_worker_liquid = service.contracts.accounts["worker_1"].liquid_nectr_balance
    expected_queen_rj = service.contracts.accounts["queen_1"].royal_jelly_earned
    expected_blocks = len(service.blockchain.chain)
    repo.close()

    # Reload in a brand-new repository and service instance
    repo_reloaded = SQLModelHiveRepository(database_url=db_url)
    reloaded = HiveServiceLayer.from_repository(
        hive_id="HIVE_PERSIST",
        repository=repo_reloaded,
    )
    assert reloaded.contracts.comb_reserve == pytest.approx(expected_comb)
    assert reloaded.contracts.accounts["worker_1"].liquid_nectr_balance == pytest.approx(
        expected_worker_liquid
    )
    assert reloaded.contracts.accounts["queen_1"].royal_jelly_earned == pytest.approx(
        expected_queen_rj
    )
    assert reloaded.contracts.sessions["sess_open"].status == SessionStatus.INTENT_ESCROWED
    assert reloaded.current_epoch == 2
    assert len(reloaded.blockchain.chain) == expected_blocks
    assert reloaded.blockchain.verify_chain() is True
    assert reloaded.contracts.pairwise_counts[frozenset({"worker_1", "learner_1"})] == 1
    assert reloaded.contracts.subject_lineage[("learner_1", "CS-101")] == ["worker_1"]
    reloaded.contracts.assert_supply_conservation()
    # Also verify repository query helpers on reload
    assert repo_reloaded.get_account("HIVE_PERSIST", "worker_1") is not None
    assert repo_reloaded.get_account("HIVE_PERSIST", "missing") is None
    assert len(repo_reloaded.list_accounts("HIVE_PERSIST")) >= 4
    assert repo_reloaded.get_session("HIVE_PERSIST", "sess_open") is not None
    assert repo_reloaded.get_session("HIVE_PERSIST", "missing") is None
    assert len(repo_reloaded.list_sessions("HIVE_PERSIST")) == 2
    assert len(repo_reloaded.list_blocks("HIVE_PERSIST")) == expected_blocks
    repo_reloaded.close()


def test_from_repository_missing_hive_raises_key_error() -> None:
    from nectr.services.persistence import SQLModelHiveRepository

    repo = SQLModelHiveRepository(database_url="sqlite:///:memory:")
    repo.initialize()
    with pytest.raises(KeyError):
        HiveServiceLayer.from_repository(hive_id="DOES_NOT_EXIST", repository=repo)
    repo.close()


def test_atomic_rollback_on_contract_violation_error(tmp_path: Path) -> None:
    from nectr.services.persistence import SQLModelHiveRepository

    db_url = f"sqlite:///{tmp_path / 'rollback.db'}"
    repo = SQLModelHiveRepository(database_url=db_url)
    service = HiveServiceLayer(hive_id="HIVE_ROLLBACK", difficulty=1, repository=repo)
    service.bootstrap_sponsored_hive(
        seed_comb_amount=200.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    service.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.allocate_raw_pollen("queen_1", "learner_1", 25.0)

    # Step 1 (escrow) deducts 15.0, then step 2 (attestation=1.5) raises ContractViolationError
    mempool_before = len(service.blockchain.mempool)
    with pytest.raises(ContractViolationError):
        service.execute_tutoring_handshake(
            session_id="sess_fail",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=15.0,
            token_state=TokenState.RAW_POLLEN,
            learner_attestation_score=1.5,
        )

    # Both in-memory and DB state must remain unchanged
    assert service.contracts.accounts["learner_1"].raw_pollen_balance == pytest.approx(25.0)
    assert "sess_fail" not in service.contracts.sessions
    assert len(service.blockchain.mempool) == mempool_before

    reloaded = HiveServiceLayer.from_repository("HIVE_ROLLBACK", repository=repo)
    assert reloaded.contracts.accounts["learner_1"].raw_pollen_balance == pytest.approx(25.0)
    assert "sess_fail" not in reloaded.contracts.sessions
    repo.close()


def test_telemetry_adapter_binds_context_records_spans_and_redacts_secrets() -> None:
    from nectr.services.persistence import SQLModelHiveRepository
    from nectr.services.telemetry import TelemetryAdapter

    telemetry = TelemetryAdapter(service_name="nectr-test")
    repo = SQLModelHiveRepository(database_url="sqlite:///:memory:")
    service = HiveServiceLayer(
        hive_id="HIVE_TEL",
        difficulty=1,
        repository=repo,
        telemetry=telemetry,
    )
    service.bootstrap_sponsored_hive(
        seed_comb_amount=100.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    sensitive_fields = {
        "private_" + "key": "ed25519-sensitive-value",
        "api_" + "key": "example-key-value",
        "pem_blob": "-----BEGIN " + "PRIVATE KEY-----\nABC\n-----END " + "PRIVATE KEY-----",
    }
    telemetry.record_event(
        "custom_audit_check",
        hive_id="HIVE_TEL",
        epoch=1,
        tx_id="tx_001",
        token_state="RAW_POLLEN",
        **sensitive_fields,
    )

    events = telemetry.get_recorded_events()
    spans = telemetry.get_finished_spans()
    assert len(events) >= 2
    assert len(spans) >= 1

    custom = next(e for e in events if e.get("event") == "custom_audit_check")
    assert custom["hive_id"] == "HIVE_TEL"
    assert custom["epoch"] == 1
    assert custom["tx_id"] == "tx_001"
    assert custom["token_state"] == "RAW_POLLEN"
    assert custom["private_key"] == "[REDACTED]"
    assert custom["api_key"] == "[REDACTED]"
    assert custom["pem_blob"] == "[REDACTED]"
    assert len(telemetry.get_log_lines()) >= 2

    with (
        pytest.raises(RuntimeError, match="boom"),
        telemetry.span("failing_span", hive_id="HIVE_TEL", epoch=2, tx_id="tx_err"),
    ):
        raise RuntimeError("boom")
    repo.close()


def test_in_memory_repository_and_api_error_branches() -> None:
    from nectr.services.api import create_app
    from nectr.services.ports import InMemoryHiveRepository

    mem_repo = InMemoryHiveRepository()
    assert mem_repo.load_hive_snapshot("NONE") is None
    assert mem_repo.get_account("NONE", "b") is None
    assert mem_repo.list_accounts("NONE") == []
    assert mem_repo.get_session("NONE", "s") is None
    assert mem_repo.list_sessions("NONE") == []
    assert mem_repo.list_blocks("NONE") == []

    service = HiveServiceLayer(hive_id="HIVE_ERR", difficulty=1, repository=mem_repo)
    service.bootstrap_sponsored_hive(
        seed_comb_amount=100.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    assert mem_repo.get_account("HIVE_ERR", "worker_1") is not None
    assert len(mem_repo.list_accounts("HIVE_ERR")) >= 2
    assert len(mem_repo.list_blocks("HIVE_ERR")) == 2

    app = create_app(service)
    client = TestClient(app)
    assert (
        client.post(
            "/hive/bootstrap",
            json={"seed_comb_amount": -5.0, "queen_ids": ["q2"], "certified_workers": {}},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/pollen/allocate",
            json={"queen_id": "worker_1", "learner_id": "worker_1", "amount": 5.0},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/workers/certify",
            json={"queen_id": "worker_1", "worker_id": "worker_1", "subject_id": "BIO-101"},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/sessions/escrow",
            json={
                "session_id": "bad_e",
                "tutor_id": "worker_1",
                "learner_id": "worker_1",
                "subject_id": "CS-101",
                "duration_hours": 1.0,
                "amount": 5.0,
                "token_state": "LIQUID_NECTR",
            },
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/sessions/missing_s/settle",
            json={"learner_attestation_score": 0.9, "tutor_comprehension_hash": "h"},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/sessions/missing_s/dispute",
            json={"queen_id": "queen_1", "tutor_share_ratio": 0.5, "service_fee_rate": 0.1},
        ).status_code
        == 400
    )


def test_fastapi_hive_router_endpoints_and_error_rollback(tmp_path: Path) -> None:
    from nectr.services.api import FastAPIHiveRouter, create_app
    from nectr.services.persistence import SQLModelHiveRepository
    from nectr.services.telemetry import TelemetryAdapter

    db_url = f"sqlite:///{tmp_path / 'api.db'}"
    repo = SQLModelHiveRepository(database_url=db_url)
    telemetry = TelemetryAdapter(service_name="nectr-api-test")
    service = HiveServiceLayer(
        hive_id="HIVE_API",
        difficulty=1,
        repository=repo,
        telemetry=telemetry,
    )
    router_wrapper = FastAPIHiveRouter(service=service)
    assert router_wrapper.router is not None
    app = create_app(service=service)
    client = TestClient(app)

    assert client.get("/health").status_code == 200

    boot_res = client.post(
        "/hive/bootstrap",
        json={
            "seed_comb_amount": 250.0,
            "queen_ids": ["queen_1"],
            "certified_workers": {"worker_1": ["CS-101"]},
        },
    )
    assert boot_res.status_code == 200
    assert boot_res.json()["genesis_comb"] == pytest.approx(250.0)

    assert (
        client.post("/bees", json={"bee_id": "learner_1", "role": "LEARNER_BEE"}).status_code == 200
    )
    assert client.get("/bees/missing_bee").status_code == 404
    assert (
        client.post(
            "/pollen/allocate",
            json={"queen_id": "queen_1", "learner_id": "learner_1", "amount": 20.0},
        ).status_code
        == 200
    )

    hs_res = client.post(
        "/sessions/handshake",
        json={
            "session_id": "api_sess_1",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 10.0,
            "token_state": "RAW_POLLEN",
            "learner_attestation_score": 0.9,
        },
    )
    assert hs_res.status_code == 200
    assert hs_res.json()["amount"] == pytest.approx(10.0)

    # Invalid attestation must return 400 and roll back
    bad_hs = client.post(
        "/sessions/handshake",
        json={
            "session_id": "api_sess_bad",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 5.0,
            "token_state": "RAW_POLLEN",
            "learner_attestation_score": 1.5,
        },
    )
    assert bad_hs.status_code == 400
    assert client.get("/bees/learner_1").json()["raw_pollen_balance"] == pytest.approx(10.0)

    # Escrow + Settle via API + 404 on missing session
    assert client.get("/sessions/missing_sess").status_code == 404
    assert (
        client.post(
            "/workers/certify",
            json={"queen_id": "queen_1", "worker_id": "worker_1", "subject_id": "MATH-101"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/sessions/escrow",
            json={
                "session_id": "api_settle_sep",
                "tutor_id": "worker_1",
                "learner_id": "learner_1",
                "subject_id": "MATH-101",
                "duration_hours": 1.0,
                "amount": 5.0,
                "token_state": "RAW_POLLEN",
            },
        ).status_code
        == 200
    )
    assert client.get("/sessions/api_settle_sep").status_code == 200
    assert (
        client.post(
            "/sessions/api_settle_sep/settle",
            json={"learner_attestation_score": 0.9, "tutor_comprehension_hash": "hash_ok"},
        ).status_code
        == 200
    )

    # Escrow + Dispute via API
    assert (
        client.post(
            "/sessions/escrow",
            json={
                "session_id": "api_disp",
                "tutor_id": "worker_1",
                "learner_id": "learner_1",
                "subject_id": "CS-101",
                "duration_hours": 1.0,
                "amount": 5.0,
                "token_state": "RAW_POLLEN",
            },
        ).status_code
        == 200
    )
    disp_res = client.post(
        "/sessions/api_disp/dispute",
        json={"queen_id": "queen_1", "tutor_share_ratio": 0.5, "service_fee_rate": 0.1},
    )
    assert disp_res.status_code == 200
    assert disp_res.json()["fee_to_comb"] == pytest.approx(0.5)

    mine_res = client.post("/epochs/mine", json={"queen_dividend_beta": 0.05})
    assert mine_res.status_code == 200
    tel_res = client.get("/telemetry")
    assert tel_res.status_code == 200
    assert tel_res.json()["event_count"] >= 1
    state_res = client.get("/hive/state")
    assert state_res.status_code == 200
    assert state_res.json()["chain_valid"] is True
    repo.close()
