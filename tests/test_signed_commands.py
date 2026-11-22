"""Strict TDD tests for CB1 signed commands, key registry, and authority binding."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from nectr.chain import Block, Ed25519Signer, HiveBlockchain, SignedTransaction, UsefulComputeProof
from nectr.contracts import BeeRole, ContractViolationError, TokenState
from nectr.personas import run_multi_hive_persona_simulation
from nectr.services import HiveServiceLayer
from nectr.services.api import create_app
from nectr.services.persistence import SQLModelHiveRepository


def _test_signer(label: str) -> Ed25519Signer:
    return Ed25519Signer.from_seed(hashlib.sha256(f"test:{label}".encode()).digest())


def _bootstrap_signed_hive(
    service: HiveServiceLayer,
    *,
    seed_comb_amount: float = 300.0,
    queen_id: str = "queen_1",
    certified_workers: dict[str, list[str]] | None = None,
) -> dict[str, Ed25519Signer]:
    workers = {"worker_1": ["CS-101"]} if certified_workers is None else certified_workers
    signers: dict[str, Ed25519Signer] = {queen_id: _test_signer(f"{service.hive_id}:{queen_id}")}
    worker_pks: dict[str, str] = {}
    for wid in workers:
        ws = _test_signer(f"{service.hive_id}:{wid}")
        signers[wid] = ws
        worker_pks[wid] = ws.public_key_hex

    boot_tx = SignedTransaction.create(
        {
            "action": "BOOTSTRAP_HIVE",
            "hive_id": service.hive_id,
            "queen_id": queen_id,
            "seed_comb_amount": seed_comb_amount,
            "queen_public_keys": {queen_id: signers[queen_id].public_key_hex},
            "certified_workers": workers,
            "worker_public_keys": worker_pks,
            "nonce": 1,
        },
        signer=signers[queen_id],
        signer_id=queen_id,
    )
    service.bootstrap_sponsored_hive(boot_tx)
    return signers


def test_bee_keys_migration_0003_and_snapshot_roundtrip(tmp_path: Path) -> None:
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    import nectr.services.persistence as persistence_mod

    db_url = f"sqlite:///{tmp_path / 'keys_0003.db'}"
    repo = SQLModelHiveRepository(database_url=db_url)
    repo.initialize()

    inspector = inspect(repo.engine)
    assert "bee_keys" in inspector.get_table_names()

    service = HiveServiceLayer(hive_id="HIVE_KEYS", difficulty=1, repository=repo)
    signers = _bootstrap_signed_hive(service)
    learner_signer = _test_signer("HIVE_KEYS:learner_1")
    reg_tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": "HIVE_KEYS",
            "bee_id": "learner_1",
            "role": BeeRole.LEARNER_BEE.value,
            "nonce": 1,
        },
        signer=learner_signer,
        signer_id="learner_1",
    )
    service.register_bee(reg_tx)

    alloc_tx = SignedTransaction.create(
        {
            "action": "ALLOCATE_RAW_POLLEN",
            "hive_id": "HIVE_KEYS",
            "queen_id": "queen_1",
            "learner_id": "learner_1",
            "amount": 25.0,
            "nonce": 2,
        },
        signer=signers["queen_1"],
        signer_id="queen_1",
    )
    service.allocate_raw_pollen(alloc_tx)

    snapshot = service._build_snapshot()
    assert snapshot.bee_public_keys["queen_1"] == signers["queen_1"].public_key_hex
    assert snapshot.bee_public_keys["worker_1"] == signers["worker_1"].public_key_hex
    assert snapshot.bee_public_keys["learner_1"] == learner_signer.public_key_hex
    assert snapshot.bee_nonces["queen_1"] == 2
    assert snapshot.bee_nonces["learner_1"] == 1
    repo.close()

    reloaded_repo = SQLModelHiveRepository(database_url=db_url)
    reloaded = HiveServiceLayer.from_repository("HIVE_KEYS", repository=reloaded_repo)
    assert reloaded.bee_public_keys == snapshot.bee_public_keys
    assert reloaded.bee_nonces == snapshot.bee_nonces

    # Stale nonce after reload must still be rejected
    with pytest.raises(ContractViolationError, match="nonce"):
        reloaded.allocate_raw_pollen(alloc_tx)

    # Verify Alembic downgrade removes bee_keys cleanly
    migrations_dir = Path(persistence_mod.__file__).resolve().parent / "migrations"
    cfg = Config()
    cfg.set_main_option("script_location", str(migrations_dir).replace("%", "%%"))
    cfg.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))
    with reloaded_repo.engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.downgrade(cfg, "0002_micro_unit_accounting")
    assert "bee_keys" not in inspect(reloaded_repo.engine).get_table_names()
    reloaded_repo.close()


def test_self_signed_register_bee_creates_learner_only_and_rejects_key_hijack() -> None:
    service = HiveServiceLayer(hive_id="HIVE_REG", difficulty=1)
    _bootstrap_signed_hive(service)

    alice_signer = _test_signer("alice")
    eve_signer = _test_signer("eve")

    # Self-assigning QUEEN or CERTIFIED_WORKER_BEE is rejected
    for forbidden_role in (BeeRole.QUEEN, BeeRole.CERTIFIED_WORKER_BEE, BeeRole.POLLINATOR_VISITOR):
        esc_tx = SignedTransaction.create(
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_REG",
                "bee_id": "alice",
                "role": forbidden_role.value,
                "nonce": 1,
            },
            signer=alice_signer,
            signer_id="alice",
        )
        with pytest.raises(PermissionError):
            service.register_bee(esc_tx)
        assert "alice" not in service.contracts.accounts

    # Signer mismatch (eve tries to register alice) is rejected
    mismatched_tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": "HIVE_REG",
            "bee_id": "alice",
            "role": BeeRole.LEARNER_BEE.value,
            "nonce": 1,
        },
        signer=eve_signer,
        signer_id="eve",
    )
    with pytest.raises(PermissionError):
        service.register_bee(mismatched_tx)

    # Valid self-signed LEARNER_BEE succeeds
    ok_tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": "HIVE_REG",
            "bee_id": "alice",
            "role": BeeRole.LEARNER_BEE.value,
            "nonce": 1,
        },
        signer=alice_signer,
        signer_id="alice",
    )
    acct = service.register_bee(ok_tx)
    assert acct.role == BeeRole.LEARNER_BEE
    assert service.bee_public_keys["alice"] == alice_signer.public_key_hex

    # Re-registering alice with eve's key is rejected
    hijack_tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": "HIVE_REG",
            "bee_id": "alice",
            "role": BeeRole.LEARNER_BEE.value,
            "nonce": 2,
        },
        signer=eve_signer,
        signer_id="alice",
    )
    with pytest.raises(PermissionError):
        service.register_bee(hijack_tx)


def test_dual_signed_settlement_requires_two_identical_payloads_from_learner_and_tutor() -> None:
    service = HiveServiceLayer(hive_id="HIVE_DUAL", difficulty=1)
    signers = _bootstrap_signed_hive(service)
    learner_signer = _test_signer("HIVE_DUAL:learner_1")
    signers["learner_1"] = learner_signer

    service.register_bee(
        SignedTransaction.create(
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_DUAL",
                "bee_id": "learner_1",
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
                "hive_id": "HIVE_DUAL",
                "queen_id": "queen_1",
                "learner_id": "learner_1",
                "amount": 20.0,
                "nonce": 2,
            },
            signer=signers["queen_1"],
            signer_id="queen_1",
        )
    )
    service.create_barter_escrow(
        SignedTransaction.create(
            {
                "action": "CREATE_BARTER_ESCROW",
                "hive_id": "HIVE_DUAL",
                "session_id": "s_dual",
                "tutor_id": "worker_1",
                "learner_id": "learner_1",
                "subject_id": "CS-101",
                "duration_hours": 1.0,
                "amount": 10.0,
                "token_state": TokenState.RAW_POLLEN.value,
                "nonce": 2,
            },
            signer=learner_signer,
            signer_id="learner_1",
        )
    )

    settle_payload_a = {
        "action": "SETTLE_SESSION",
        "hive_id": "HIVE_DUAL",
        "session_id": "s_dual",
        "learner_attestation_score": 0.9,
        "tutor_comprehension_hash": "hash_ok",
        "learner_nonce": 3,
        "tutor_nonce": 1,
    }
    settle_payload_b = {
        **settle_payload_a,
        "learner_attestation_score": 0.5,
    }
    learner_tx = SignedTransaction.create(
        settle_payload_a, signer=learner_signer, signer_id="learner_1"
    )
    tutor_tx_mismatch = SignedTransaction.create(
        settle_payload_b, signer=signers["worker_1"], signer_id="worker_1"
    )
    with pytest.raises(ContractViolationError, match="identical"):
        service.settle_session(learner_tx, tutor_tx_mismatch)

    # Duplicate learner signature posing as tutor must be rejected
    tutor_spoof = SignedTransaction.create(
        settle_payload_a, signer=learner_signer, signer_id="learner_1"
    )
    with pytest.raises(PermissionError):
        service.settle_session(learner_tx, tutor_spoof)

    # Valid dual-signed settlement succeeds
    tutor_tx = SignedTransaction.create(
        settle_payload_a, signer=signers["worker_1"], signer_id="worker_1"
    )
    res = service.settle_session(learner_tx, tutor_tx)
    assert res["amount"] == pytest.approx(10.0)
    assert service.bee_nonces["learner_1"] == 3
    assert service.bee_nonces["worker_1"] == 1


def test_signed_bridge_between_two_service_layers_and_atomic_rollback(tmp_path: Path) -> None:
    repo_a = SQLModelHiveRepository(database_url=f"sqlite:///{tmp_path / 'a.db'}")
    repo_b = SQLModelHiveRepository(database_url=f"sqlite:///{tmp_path / 'b.db'}")
    hive_a = HiveServiceLayer(
        hive_id="HIVE_A", difficulty=1, accepted_status_peer_threshold=1, repository=repo_a
    )
    hive_b = HiveServiceLayer(
        hive_id="HIVE_B", difficulty=1, accepted_status_peer_threshold=1, repository=repo_b
    )

    signers_a = _bootstrap_signed_hive(
        hive_a, queen_id="queen_a", certified_workers={"pollinator_1": ["CS-101"]}
    )
    _bootstrap_signed_hive(hive_b, queen_id="queen_b", certified_workers={})
    learner_a = _test_signer("learner_a")
    learner_b = _test_signer("learner_b")
    pol_signer = signers_a["pollinator_1"]

    hive_a.register_bee(
        SignedTransaction.create(
            {"action": "REGISTER_BEE", "hive_id": "HIVE_A", "bee_id": "learner_a", "nonce": 1},
            signer=learner_a,
            signer_id="learner_a",
        )
    )
    hive_a.allocate_raw_pollen(
        SignedTransaction.create(
            {
                "action": "ALLOCATE_RAW_POLLEN",
                "hive_id": "HIVE_A",
                "queen_id": "queen_a",
                "learner_id": "learner_a",
                "amount": 20.0,
                "nonce": 2,
            },
            signer=signers_a["queen_a"],
            signer_id="queen_a",
        )
    )
    esc = SignedTransaction.create(
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": "HIVE_A",
            "session_id": "s_a1",
            "tutor_id": "pollinator_1",
            "learner_id": "learner_a",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 20.0,
            "token_state": TokenState.RAW_POLLEN.value,
            "nonce": 2,
        },
        signer=learner_a,
        signer_id="learner_a",
    )
    s_payload = {
        "action": "SETTLE_SESSION",
        "hive_id": "HIVE_A",
        "session_id": "s_a1",
        "learner_attestation_score": 0.95,
        "tutor_comprehension_hash": "h1",
        "learner_nonce": 3,
        "tutor_nonce": 1,
    }
    hive_a.execute_tutoring_handshake(
        esc,
        SignedTransaction.create(s_payload, signer=learner_a, signer_id="learner_a"),
        SignedTransaction.create(s_payload, signer=pol_signer, signer_id="pollinator_1"),
    )

    # Register pollinator_1 and learner_b in HIVE_B and earn Accepted Status
    hive_b.register_bee(
        SignedTransaction.create(
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_B",
                "bee_id": "pollinator_1",
                "home_hive_id": "HIVE_A",
                "nonce": 1,
            },
            signer=pol_signer,
            signer_id="pollinator_1",
        )
    )
    hive_b.register_bee(
        SignedTransaction.create(
            {"action": "REGISTER_BEE", "hive_id": "HIVE_B", "bee_id": "learner_b", "nonce": 1},
            signer=learner_b,
            signer_id="learner_b",
        )
    )
    esc_b = SignedTransaction.create(
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": "HIVE_B",
            "session_id": "s_b1",
            "tutor_id": "pollinator_1",
            "learner_id": "learner_b",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 0.0,
            "token_state": TokenState.LIQUID_NECTR.value,
            "reciprocal_subject_id": "BIO-101",
            "nonce": 2,
        },
        signer=learner_b,
        signer_id="learner_b",
    )
    sb_payload = {
        "action": "SETTLE_SESSION",
        "hive_id": "HIVE_B",
        "session_id": "s_b1",
        "learner_attestation_score": 0.95,
        "tutor_comprehension_hash": "h2",
        "learner_nonce": 3,
        "tutor_nonce": 2,
    }
    hive_b.execute_tutoring_handshake(
        esc_b,
        SignedTransaction.create(sb_payload, signer=learner_b, signer_id="learner_b"),
        SignedTransaction.create(sb_payload, signer=pol_signer, signer_id="pollinator_1"),
    )

    # Signed bridge executes atomically across both HiveServiceLayers
    bridge_tx = SignedTransaction.create(
        {
            "action": "BRIDGE_NECTR",
            "hive_id": "HIVE_A",
            "bee_id": "pollinator_1",
            "target_hive_id": "HIVE_B",
            "amount": 10.0,
            "bridge_toll_rate": 0.05,
            "nonce": 2,
        },
        signer=pol_signer,
        signer_id="pollinator_1",
    )
    res = hive_a.bridge_nectr_to_target_hive(bridge_tx, hive_b)
    assert res["received_in_target"] > 0.0
    assert hive_a.contracts.accounts["pollinator_1"].liquid_nectr_balance == pytest.approx(10.0)
    assert hive_b.contracts.accounts["pollinator_1"].liquid_nectr_balance == pytest.approx(
        res["received_in_target"]
    )

    repo_a.close()
    repo_b.close()


def test_blockchain_rejects_dicts_in_submit_transaction_and_block_transactions() -> None:
    chain = HiveBlockchain(hive_id="HIVE_STRICT_CHAIN", difficulty=1)
    with pytest.raises(TypeError):
        chain.submit_transaction(cast(Any, {"action": "UNSIGNED_DICT"}))
    assert chain.mempool == []

    signer = _test_signer("chain_bee")
    tx = SignedTransaction.create(
        {"action": "OK", "nonce": 1}, signer=signer, signer_id="chain_bee"
    )
    chain.submit_transaction(tx)
    block = chain.mine_block(
        useful_compute_proof=UsefulComputeProof(
            epoch=1,
            active_bees=1,
            total_directional_edges=0,
            collusion_discounted_velocity=0.0,
            gini_coefficient=0.0,
            graph_state_hash="0" * 64,
        ),
        timestamp=1700000010.0,
    )
    assert all(isinstance(item, SignedTransaction) for item in block.transactions)
    assert chain.verify_chain() is True

    # Manually injecting a dict into Block.transactions must fail verify_chain()
    cast(list[Any], block.transactions).append({"injected": True})
    assert chain.verify_chain() is False
    assert isinstance(Block.model_validate(block.model_dump(mode="json")), Block)


def test_api_enforces_401_bad_sig_and_403_wrong_actor_or_role() -> None:
    service = HiveServiceLayer(hive_id="HIVE_API_AUTH", difficulty=1)
    signers = _bootstrap_signed_hive(service)
    learner_signer = _test_signer("HIVE_API_AUTH:learner_1")
    service.register_bee(
        SignedTransaction.create(
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_API_AUTH",
                "bee_id": "learner_1",
                "nonce": 1,
            },
            signer=learner_signer,
            signer_id="learner_1",
        )
    )
    client = TestClient(create_app(service))

    # 401 on bad signature
    bad_sig_tx = SignedTransaction(
        payload={
            "action": "ALLOCATE_RAW_POLLEN",
            "hive_id": "HIVE_API_AUTH",
            "queen_id": "queen_1",
            "learner_id": "learner_1",
            "amount": 10.0,
            "nonce": 2,
        },
        signer_public_key=signers["queen_1"].public_key_hex,
        signature="ab" * 64,
        signer_id="queen_1",
    )
    assert (
        client.post("/pollen/allocate", json=bad_sig_tx.model_dump(mode="json")).status_code == 401
    )

    # 403 on wrong role (learner signs allocate_raw_pollen)
    wrong_role_tx = SignedTransaction.create(
        {
            "action": "ALLOCATE_RAW_POLLEN",
            "hive_id": "HIVE_API_AUTH",
            "queen_id": "learner_1",
            "learner_id": "learner_1",
            "amount": 10.0,
            "nonce": 2,
        },
        signer=learner_signer,
        signer_id="learner_1",
    )
    assert (
        client.post("/pollen/allocate", json=wrong_role_tx.model_dump(mode="json")).status_code
        == 403
    )

    # 403 on wrong actor (worker_1 signs escrow claiming learner_id=learner_1)
    wrong_actor_tx = SignedTransaction.create(
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": "HIVE_API_AUTH",
            "session_id": "s_bad_actor",
            "tutor_id": "worker_1",
            "learner_id": "learner_1",
            "subject_id": "CS-101",
            "duration_hours": 1.0,
            "amount": 5.0,
            "token_state": TokenState.RAW_POLLEN.value,
            "nonce": 1,
        },
        signer=signers["worker_1"],
        signer_id="worker_1",
    )
    assert (
        client.post("/sessions/escrow", json=wrong_actor_tx.model_dump(mode="json")).status_code
        == 403
    )


def test_simulator_is_deterministic_with_epoch_timestamps_and_bee_id_keys() -> None:
    telemetry_a, extra_a = run_multi_hive_persona_simulation()
    telemetry_b, extra_b = run_multi_hive_persona_simulation()

    assert telemetry_a == telemetry_b
    assert extra_a == extra_b
    assert telemetry_a.hive_a_chain_valid is True
    assert telemetry_a.pollinator_accepted_in_hive_b is True
    assert telemetry_a.pollinator_bridged_nectr > 0
