"""Comprehensive unit & game-theory invariant tests for nectR PoUW-PoW chain, contracts, and personas."""

import pytest

from nectr import __version__
from nectr.contracts import (
    BeeRole,
    ContractViolationError,
    HiveContractEngine,
    TokenState,
)
from nectr.personas import PersonaArchetype, run_multi_hive_persona_simulation
from nectr.services import HiveServiceLayer


def test_workspace_enums_and_version() -> None:
    assert __version__ == "0.1.0"
    assert TokenState.RAW_POLLEN == "RAW_POLLEN"
    assert TokenState.LIQUID_NECTR == "LIQUID_NECTR"
    assert TokenState.ROYAL_COMB_RESERVE == "ROYAL_COMB_RESERVE"
    assert BeeRole.QUEEN == "QUEEN"
    assert len(list(PersonaArchetype)) == 6


def test_queen_separation_of_powers_enforced() -> None:
    """Queens cannot tutor for nectR or be certified as Worker Bees."""
    engine = HiveContractEngine(hive_id="HIVE_TEST")
    engine.inject_sponsored_seed_comb(500.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("student_1", role=BeeRole.LEARNER_BEE)
    engine.allocate_raw_pollen_to_learner("queen_1", "student_1", 20.0)

    with pytest.raises(ContractViolationError, match="Queen Separation of Powers Violation"):
        engine.create_service_barter_escrow(
            session_id="illegal_queen_tutor",
            tutor_id="queen_1",
            learner_id="student_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.RAW_POLLEN,
        )


def test_raw_pollen_restricted_to_certified_workers_and_refines_to_liquid() -> None:
    """RAW_POLLEN cannot be sent to uncertified roommates; refines into LIQUID_NECTR with Certified Workers."""
    engine = HiveContractEngine(hive_id="HIVE_TEST")
    engine.inject_sponsored_seed_comb(500.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("worker_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("freshman_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("roommate_1", role=BeeRole.LEARNER_BEE)

    engine.certify_worker_bee("queen_1", "worker_1", "CALC-101")
    engine.allocate_raw_pollen_to_learner("queen_1", "freshman_1", 15.0)

    # Attempting to spend RAW_POLLEN with an uncertified roommate fails
    with pytest.raises(ContractViolationError, match="RAW_POLLEN can only be spent"):
        engine.create_service_barter_escrow(
            session_id="bad_pollen_spend",
            tutor_id="roommate_1",
            learner_id="freshman_1",
            subject_id="CALC-101",
            duration_hours=1.0,
            amount=10.0,
            token_state=TokenState.RAW_POLLEN,
        )

    # Spending RAW_POLLEN with Certified Worker succeeds and refines into LIQUID_NECTR
    engine.create_service_barter_escrow(
        session_id="good_pollen_spend",
        tutor_id="worker_1",
        learner_id="freshman_1",
        subject_id="CALC-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("good_pollen_spend", 1.0, "hash_ok")
    assert engine.accounts["worker_1"].liquid_nectr_balance == 10.0
    assert engine.accounts["freshman_1"].raw_pollen_balance == 5.0


def test_dispute_routes_fee_to_comb_and_conserves_supply() -> None:
    """Only Queen dispute resolution charges a fee, routing 100% of the fee into the Comb."""
    import hashlib

    from nectr.chain import Ed25519Signer, SignedTransaction

    queen_signer = Ed25519Signer.from_seed(hashlib.sha256(b"inv:queen_1").digest())
    worker_signer = Ed25519Signer.from_seed(hashlib.sha256(b"inv:worker_1").digest())
    service = HiveServiceLayer(hive_id="HIVE_DISPUTE")
    service.bootstrap_sponsored_hive(
        SignedTransaction.create(
            {
                "action": "BOOTSTRAP_HIVE",
                "hive_id": "HIVE_DISPUTE",
                "queen_id": "queen_1",
                "seed_comb_amount": 200.0,
                "queen_public_keys": {"queen_1": queen_signer.public_key_hex},
                "certified_workers": {"worker_1": ["PHYS-101"]},
                "worker_public_keys": {"worker_1": worker_signer.public_key_hex},
                "nonce": 1,
            },
            signer=queen_signer,
            signer_id="queen_1",
        )
    )
    service.contracts.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    service.contracts.allocate_raw_pollen_to_learner("queen_1", "learner_1", 20.0)

    # Comb is now 180.0
    service.contracts.create_service_barter_escrow(
        session_id="disputed_sess",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="PHYS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.RAW_POLLEN,
    )
    res = service.contracts.resolve_disputed_session(
        queen_id="queen_1",
        session_id="disputed_sess",
        tutor_share_ratio=0.5,
        service_fee_rate=0.10,
    )
    assert res["fee_to_comb"] == 2.0
    assert service.contracts.comb_reserve == 182.0
    assert service.contracts.accounts["worker_1"].liquid_nectr_balance == 9.0
    assert service.contracts.accounts["learner_1"].raw_pollen_balance == 9.0


def test_cross_hive_guard_bee_rejection_and_persona_simulation() -> None:
    """Verify full multi-hive simulation, PoUW-PoW chain integrity, collusion decay, and Accepted Status bridging."""
    telemetry, _ = run_multi_hive_persona_simulation()
    assert telemetry.hive_a_chain_valid is True
    assert telemetry.hive_a_blocks_mined >= 4
    assert telemetry.pollinator_accepted_in_hive_b is True
    assert telemetry.pollinator_bridged_nectr > 0
    # Honest worker effectiveness with downstream lineage is higher than repeated Sybil loop per-tx weight
    assert telemetry.honest_worker_effectiveness > telemetry.sybil_colluder_effectiveness
    assert telemetry.queen_royal_jelly_score > 0
