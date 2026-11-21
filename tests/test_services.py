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


# ---------------------------------------------------------------------------
# Iteration 2 RED Regression Tests: API, Rollback, Persistence & Telemetry
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True, reason="RED: BUG-2/3/4/5 API NaN/bounds and mine_epoch_block beta validation"
)
def test_api_and_service_reject_nan_inf_negative_duration_fee_and_beta() -> None:
    from nectr.services.api import create_app
    from nectr.services.ports import InMemoryHiveRepository

    repo = InMemoryHiveRepository()
    service = HiveServiceLayer(hive_id="HIVE_VAL", difficulty=1, repository=repo)
    service.bootstrap_sponsored_hive(
        seed_comb_amount=100.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    service.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.allocate_raw_pollen("queen_1", "learner_1", 20.0)
    app = create_app(service)
    client = TestClient(app)

    # BUG-5: NaN in JSON body must return 422
    nan_res = client.post(
        "/pollen/allocate",
        content='{"queen_id": "queen_1", "learner_id": "learner_1", "amount": NaN}',
        headers={"Content-Type": "application/json"},
    )
    assert nan_res.status_code == 422

    # BUG-3: duration_hours <= 0 must return 422
    for bad_dur in (0.0, -5.0):
        dur_res = client.post(
            "/sessions/escrow",
            json={
                "session_id": f"dur_{bad_dur}",
                "tutor_id": "worker_1",
                "learner_id": "learner_1",
                "subject_id": "CS-101",
                "duration_hours": bad_dur,
                "amount": 5.0,
                "token_state": "RAW_POLLEN",
            },
        )
        assert dur_res.status_code == 422

    hs_dur_res = client.post(
        "/sessions/handshake",
        json={
            "session_id": "hs_zero_dur",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 0.0,
            "amount": 5.0,
            "token_state": "RAW_POLLEN",
        },
    )
    assert hs_dur_res.status_code == 422

    # BUG-2: service_fee_rate out of [0, 1] must return 422
    esc_res = client.post(
        "/sessions/escrow",
        json={
            "session_id": "disp_bounds",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 5.0,
            "token_state": "RAW_POLLEN",
        },
    )
    assert esc_res.status_code == 200
    for bad_fee in (-0.1, 2.0):
        disp_res = client.post(
            "/sessions/disp_bounds/dispute",
            json={"queen_id": "queen_1", "tutor_share_ratio": 0.5, "service_fee_rate": bad_fee},
        )
        assert disp_res.status_code == 422

    # BUG-4: negative / non-finite queen_dividend_beta must be rejected
    mine_bad = client.post("/epochs/mine", json={"queen_dividend_beta": -1.0})
    assert mine_bad.status_code == 422
    for bad_beta in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ContractViolationError, match="queen_dividend_beta"):
            service.mine_epoch_block(queen_dividend_beta=bad_beta)


@pytest.mark.xfail(strict=True, reason="RED: R1 Medium commit-phase rollback ordering")
def test_commit_phase_failure_rolls_back_in_memory_state(tmp_path: Path) -> None:
    from collections.abc import Iterator
    from contextlib import contextmanager

    from nectr.services.persistence import SQLModelHiveRepository
    from nectr.services.telemetry import TelemetryAdapter

    class FailingCommitRepository(SQLModelHiveRepository):
        fail_next_commit: bool = False

        @contextmanager
        def transaction(self) -> Iterator[None]:
            with super().transaction():
                yield
                if self.fail_next_commit:
                    raise RuntimeError("simulated commit failure")

    db_url = f"sqlite:///{tmp_path / 'commit_fail.db'}"
    repo = FailingCommitRepository(database_url=db_url)
    telemetry = TelemetryAdapter(service_name="nectr-commit-rb")
    service = HiveServiceLayer(
        hive_id="HIVE_COMMIT_RB",
        difficulty=1,
        repository=repo,
        telemetry=telemetry,
    )
    service.bootstrap_sponsored_hive(
        seed_comb_amount=100.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )

    repo.fail_next_commit = True
    with pytest.raises(RuntimeError, match="simulated commit failure"):
        service.register_bee("bee_ghost")

    assert "bee_ghost" not in service.contracts.accounts
    assert repo.get_account("HIVE_COMMIT_RB", "bee_ghost") is None
    events = telemetry.get_recorded_events()
    assert any(e.get("event") == "register_bee.rollback" for e in events)
    repo.close()


@pytest.mark.xfail(
    strict=True, reason="RED: C1 #1 DB reload does not reject negative/duplicate pairwise_counts"
)
def test_repository_reload_rejects_corrupted_negative_or_duplicate_pairwise_counts(
    tmp_path: Path,
) -> None:
    from sqlalchemy import text

    from nectr.services.persistence import SQLModelHiveRepository

    db_url = f"sqlite:///{tmp_path / 'corrupt_pairs.db'}"
    repo = SQLModelHiveRepository(database_url=db_url)
    service = HiveServiceLayer(hive_id="HIVE_PAIR_DB", difficulty=1, repository=repo)
    service.bootstrap_sponsored_hive(
        seed_comb_amount=200.0,
        queen_ids=["queen_1"],
        certified_workers={"worker_1": ["CS-101"]},
    )
    service.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.allocate_raw_pollen("queen_1", "learner_1", 20.0)
    service.execute_tutoring_handshake(
        session_id="s_pair",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )

    with repo.engine.begin() as conn:
        conn.execute(
            text("UPDATE pairwise_counts SET tx_count = -1 WHERE hive_id = 'HIVE_PAIR_DB'")
        )
    with pytest.raises(ContractViolationError):
        HiveServiceLayer.from_repository("HIVE_PAIR_DB", repository=repo)

    with repo.engine.begin() as conn:
        conn.execute(text("UPDATE pairwise_counts SET tx_count = 1 WHERE hive_id = 'HIVE_PAIR_DB'"))
        conn.execute(
            text(
                "INSERT INTO pairwise_counts (hive_id, bee_a, bee_b, tx_count) "
                "VALUES ('HIVE_PAIR_DB', 'worker_1', 'learner_1', 99)"
            )
        )
    with pytest.raises(ContractViolationError, match="Duplicate pairwise_counts"):
        HiveServiceLayer.from_repository("HIVE_PAIR_DB", repository=repo)
    repo.close()


@pytest.mark.xfail(
    strict=True, reason="RED: MINOR-TEL-1/2 tuple/set sanitization and PEM exception scrubbing"
)
def test_telemetry_redacts_tuple_set_and_exception_pem() -> None:
    from nectr.services.telemetry import TelemetryAdapter, _sanitize_value

    telemetry = TelemetryAdapter(service_name="nectr-tel-harden")
    pem_blob = "-----BEGIN " + "PRIVATE KEY-----\nSECRET_BODY\n-----END " + "PRIVATE KEY-----"

    telemetry.record_event(
        "tuple_audit",
        hive_id="HIVE_TEL",
        epoch=1,
        tx_id="tx_t",
        nested=("safe", pem_blob),
    )
    events = telemetry.get_recorded_events()
    assert events[0]["nested"] == ["safe", "[REDACTED]"] or events[0]["nested"] == (
        "safe",
        "[REDACTED]",
    )
    assert "SECRET_BODY" not in "\n".join(telemetry.get_log_lines())

    sanitized_set = _sanitize_value("items", {"safe", pem_blob})
    assert isinstance(sanitized_set, set)
    assert "[REDACTED]" in sanitized_set
    assert pem_blob not in sanitized_set

    sanitized_fset = _sanitize_value("items", frozenset({"safe", pem_blob}))
    assert isinstance(sanitized_fset, frozenset)
    assert "[REDACTED]" in sanitized_fset

    with (
        pytest.raises(RuntimeError),
        telemetry.span("pem_exc_span", hive_id="HIVE_TEL", epoch=1, tx_id="tx_e"),
    ):
        raise RuntimeError(f"failed loading {pem_blob}")

    spans = telemetry.get_finished_spans()
    assert len(spans) == 1
    status_desc = spans[0].status.description or ""
    assert "SECRET_BODY" not in status_desc
    assert "PRIVATE KEY" not in status_desc
    for ev in spans[0].events:
        exc_msg = str(ev.attributes.get("exception.message", "")) if ev.attributes else ""
        assert "SECRET_BODY" not in exc_msg
        assert "PRIVATE KEY" not in exc_msg
