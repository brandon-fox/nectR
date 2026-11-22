"""Unit and invariant tests for nectR deterministic smart contracts."""

from __future__ import annotations

import json

import canonicaljson
import pytest

from nectr.contracts import (
    BeeAccount,
    BeeRole,
    ContractViolationError,
    HiveContractEngine,
    ServiceBarterSession,
    SessionStatus,
    TokenState,
)


def _setup_basic_hive(
    hive_id: str = "HIVE_UNIT",
    seed_comb: float = 500.0,
    accepted_threshold: int = 3,
) -> HiveContractEngine:
    engine = HiveContractEngine(
        hive_id=hive_id,
        accepted_status_peer_threshold=accepted_threshold,
    )
    engine.inject_sponsored_seed_comb(seed_comb)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("worker_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    engine.certify_worker_bee("queen_1", "worker_1", "CS-101")
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 50.0)
    return engine


# ---------------------------------------------------------------------------
# Coverage of all guard branches and uncovered lines in engine.py
# ---------------------------------------------------------------------------


def test_register_bee_is_idempotent() -> None:
    engine = HiveContractEngine(hive_id="HIVE_IDEMPOTENT")
    first = engine.register_bee("bee_1", role=BeeRole.LEARNER_BEE)
    second = engine.register_bee("bee_1", role=BeeRole.QUEEN)
    assert first is second
    assert second.role == BeeRole.LEARNER_BEE


@pytest.mark.parametrize("bad_amount", [0.0, -10.0])
def test_inject_seed_comb_rejects_non_positive(bad_amount: float) -> None:
    engine = HiveContractEngine(hive_id="HIVE_SEED")
    with pytest.raises(ContractViolationError, match="Seed Comb injection must be positive."):
        engine.inject_sponsored_seed_comb(bad_amount)


def test_allocate_raw_pollen_rejects_queen_recipient() -> None:
    engine = _setup_basic_hive()
    engine.register_bee("queen_2", role=BeeRole.QUEEN)
    with pytest.raises(ContractViolationError, match="Queens cannot receive RAW_POLLEN"):
        engine.allocate_raw_pollen_to_learner("queen_1", "queen_2", 10.0)


@pytest.mark.parametrize("bad_amount", [0.0, -1.0, 50.01])
def test_allocate_raw_pollen_rejects_non_positive_or_over_comb(bad_amount: float) -> None:
    engine = HiveContractEngine(hive_id="HIVE_COMB_LIMIT")
    engine.inject_sponsored_seed_comb(50.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    with pytest.raises(ContractViolationError, match="Insufficient Comb reserve"):
        engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", bad_amount)


def test_certify_worker_rejects_queen() -> None:
    engine = _setup_basic_hive()
    engine.register_bee("queen_2", role=BeeRole.QUEEN)
    with pytest.raises(ContractViolationError, match="Queens cannot be certified"):
        engine.certify_worker_bee("queen_1", "queen_2", "CS-101")


def test_certify_worker_fee_insufficient_liquid_nectr() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(
        ContractViolationError, match="Insufficient LIQUID_NECTR for certification fee."
    ):
        engine.certify_worker_bee("queen_1", "worker_1", "MATH-201", certification_fee=5.0)


def test_certify_worker_paid_fee_routes_to_comb_and_conserves_supply() -> None:
    engine = _setup_basic_hive(seed_comb=500.0)
    engine.create_service_barter_escrow(
        session_id="earn_liquid",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("earn_liquid", 1.0, "hash_ok")
    comb_before = engine.comb_reserve

    res = engine.certify_worker_bee("queen_1", "worker_1", "MATH-201", certification_fee=2.5)
    assert res["fee_to_comb"] == pytest.approx(2.5)
    assert engine.accounts["worker_1"].liquid_nectr_balance == pytest.approx(7.5)
    assert engine.comb_reserve == pytest.approx(comb_before + 2.5)
    assert "MATH-201" in engine.accounts["worker_1"].certified_subjects
    engine.assert_supply_conservation()


def test_escrow_rejects_self_tutoring() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="Self-tutoring is prohibited."):
        engine.create_service_barter_escrow(
            session_id="self_sess",
            tutor_id="worker_1",
            learner_id="worker_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.LIQUID_NECTR,
        )


def test_escrow_rejects_negative_amount() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="Escrow amount cannot be negative."):
        engine.create_service_barter_escrow(
            session_id="neg_sess",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=-0.5,
            token_state=TokenState.LIQUID_NECTR,
        )


@pytest.mark.parametrize("reciprocal", [None, ""])
def test_escrow_zero_nectr_requires_reciprocal_subject(reciprocal: str | None) -> None:
    engine = _setup_basic_hive()
    with pytest.raises(
        ContractViolationError, match="Zero-nectR sessions must specify a reciprocal_subject_id"
    ):
        engine.create_service_barter_escrow(
            session_id="zero_missing_rec",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.0,
            token_state=TokenState.LIQUID_NECTR,
            reciprocal_subject_id=reciprocal,
        )


def test_escrow_rejects_insufficient_raw_pollen() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="Insufficient RAW_POLLEN balance."):
        engine.create_service_barter_escrow(
            session_id="over_pollen",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=100.0,
            token_state=TokenState.RAW_POLLEN,
        )


def test_escrow_rejects_insufficient_liquid_nectr() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR balance."):
        engine.create_service_barter_escrow(
            session_id="over_liquid",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.LIQUID_NECTR,
        )


def test_escrow_rejects_invalid_token_state() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="Invalid token state for P2P escrow."):
        engine.create_service_barter_escrow(
            session_id="bad_state",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.ROYAL_COMB_RESERVE,
        )


def test_settle_rejects_non_escrowed_session() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s1",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("s1", 1.0, "hash_1")
    with pytest.raises(ContractViolationError, match="is not in INTENT_ESCROWED state."):
        engine.settle_co_signed_session("s1", 1.0, "hash_2")


@pytest.mark.parametrize("bad_score", [-0.01, 1.01])
def test_settle_rejects_out_of_bounds_attestation(bad_score: float) -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_bad_score",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    with pytest.raises(ContractViolationError, match=r"Attestation score must be in \[0.0, 1.0\]."):
        engine.settle_co_signed_session("s_bad_score", bad_score, "hash_1")


def test_dispute_rejects_non_escrowed_session() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_settled",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("s_settled", 0.9, "hash_1")
    with pytest.raises(ContractViolationError, match="Only escrowed sessions can be arbitrated."):
        engine.resolve_disputed_session("queen_1", "s_settled", tutor_share_ratio=0.5)


@pytest.mark.parametrize("bad_ratio", [-0.1, 1.1])
def test_dispute_rejects_invalid_tutor_share_ratio(bad_ratio: float) -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_bad_ratio",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    with pytest.raises(ContractViolationError, match="tutor_share_ratio must be between 0 and 1."):
        engine.resolve_disputed_session("queen_1", "s_bad_ratio", tutor_share_ratio=bad_ratio)


def test_dispute_liquid_nectr_refunds_learner_liquid_and_routes_fee_to_comb() -> None:
    engine = _setup_basic_hive()
    # Give learner_1 20.0 LIQUID_NECTR via tutoring worker_1
    engine.create_service_barter_escrow(
        session_id="s_seed_w",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("s_seed_w", 1.0, "h1")
    engine.create_service_barter_escrow(
        session_id="s_seed_l",
        tutor_id="learner_1",
        learner_id="worker_1",
        subject_id="ART-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.LIQUID_NECTR,
    )
    engine.settle_co_signed_session("s_seed_l", 1.0, "h2")

    # Now learner_1 escrows 20.0 LIQUID_NECTR with worker_1 and disputes
    engine.create_service_barter_escrow(
        session_id="s_liq_dispute",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.LIQUID_NECTR,
    )
    comb_before = engine.comb_reserve
    res = engine.resolve_disputed_session(
        queen_id="queen_1",
        session_id="s_liq_dispute",
        tutor_share_ratio=0.5,
        service_fee_rate=0.10,
    )
    assert res["fee_to_comb"] == pytest.approx(2.0)
    assert engine.comb_reserve == pytest.approx(comb_before + 2.0)
    assert engine.accounts["worker_1"].liquid_nectr_balance == pytest.approx(9.0)
    assert engine.accounts["learner_1"].liquid_nectr_balance == pytest.approx(9.0)
    engine.assert_supply_conservation()


def test_bridge_rejects_queen() -> None:
    source = _setup_basic_hive(hive_id="HIVE_SRC")
    target = _setup_basic_hive(hive_id="HIVE_DST")
    with pytest.raises(ContractViolationError, match="Queens are bound to their Hive"):
        source.bridge_nectr_to_target_hive("queen_1", target, 5.0)


@pytest.mark.parametrize("bad_amount", [0.0, -2.0, 999.0])
def test_bridge_rejects_non_positive_or_insufficient_balance(bad_amount: float) -> None:
    source = _setup_basic_hive(hive_id="HIVE_SRC")
    target = _setup_basic_hive(hive_id="HIVE_DST")
    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR in origin Hive"):
        source.bridge_nectr_to_target_hive("worker_1", target, bad_amount)


def test_bridge_rejects_without_accepted_status() -> None:
    source = _setup_basic_hive(hive_id="HIVE_SRC")
    target = _setup_basic_hive(hive_id="HIVE_DST", accepted_threshold=3)
    source.register_bee("visitor_worker", role=BeeRole.LEARNER_BEE)
    source.certify_worker_bee("queen_1", "visitor_worker", "CS-101")
    source.create_service_barter_escrow(
        session_id="earn",
        tutor_id="visitor_worker",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.RAW_POLLEN,
    )
    source.settle_co_signed_session("earn", 1.0, "h")

    target.register_bee("visitor_worker", home_hive_id="HIVE_SRC")
    for idx in range(2):
        peer = f"target_peer_{idx}"
        target.register_bee(peer, role=BeeRole.LEARNER_BEE)
        target.create_service_barter_escrow(
            session_id=f"t_{idx}",
            tutor_id="visitor_worker",
            learner_id=peer,
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.0,
            reciprocal_subject_id="ART-101",
        )
        target.settle_co_signed_session(f"t_{idx}", 0.9, f"ht_{idx}")

    with pytest.raises(ContractViolationError, match="Guard Bee Rejection"):
        source.bridge_nectr_to_target_hive("visitor_worker", target, 5.0)


def test_supply_conservation_detects_tampered_balance() -> None:
    engine = _setup_basic_hive()
    engine.comb_reserve += 1.0
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        engine.assert_supply_conservation()


def test_unregistered_bee_raises_contract_violation() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="is not registered in Hive"):
        engine.allocate_raw_pollen_to_learner("queen_1", "ghost_bee", 5.0)


def test_missing_session_raises_contract_violation() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="does not exist."):
        engine.settle_co_signed_session("missing_sess", 1.0, "h")
    with pytest.raises(ContractViolationError, match="does not exist."):
        engine.resolve_disputed_session("queen_1", "missing_sess", 0.5)


def test_non_queen_privileged_calls_rejected() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_open",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    for caller in ("worker_1", "learner_1"):
        with pytest.raises(ContractViolationError, match="does not hold QUEEN role."):
            engine.allocate_raw_pollen_to_learner(caller, "learner_1", 1.0)
        with pytest.raises(ContractViolationError, match="does not hold QUEEN role."):
            engine.certify_worker_bee(caller, "learner_1", "CS-101")
        with pytest.raises(ContractViolationError, match="does not hold QUEEN role."):
            engine.resolve_disputed_session(caller, "s_open", 0.5)


# ---------------------------------------------------------------------------
# Quantitative Invariants: Accepted Status, Collusion Decay, Lineage, FX Clamp
# ---------------------------------------------------------------------------


def test_accepted_status_requires_k_distinct_peers_with_attestation_threshold() -> None:
    engine = _setup_basic_hive(accepted_threshold=3)
    for i in range(4):
        engine.register_bee(f"peer_{i}", role=BeeRole.LEARNER_BEE)
    engine.register_bee("visitor_1", role=BeeRole.LEARNER_BEE, home_hive_id="HIVE_OTHER")

    # Repeated tutoring of same peer counts only once
    for rep in range(2):
        engine.create_service_barter_escrow(
            session_id=f"rep_{rep}",
            tutor_id="visitor_1",
            learner_id="peer_0",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.0,
            reciprocal_subject_id="HIST-101",
        )
        engine.settle_co_signed_session(f"rep_{rep}", 0.9, f"hr_{rep}")

    # Low attestation (< 0.6) does not advance distinct peers
    engine.create_service_barter_escrow(
        session_id="low_att",
        tutor_id="visitor_1",
        learner_id="peer_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="HIST-101",
    )
    engine.settle_co_signed_session("low_att", 0.59, "hl")
    assert len(engine.accounts["visitor_1"].distinct_peers_tutored_in_hive) == 1
    assert engine.hive_id not in engine.accounts["visitor_1"].accepted_in_hives

    # 2 more distinct peers with score >= 0.6 unlocks Accepted Status (K=3)
    for idx in (2, 3):
        engine.create_service_barter_escrow(
            session_id=f"good_{idx}",
            tutor_id="visitor_1",
            learner_id=f"peer_{idx}",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.0,
            reciprocal_subject_id="HIST-101",
        )
        engine.settle_co_signed_session(f"good_{idx}", 0.60, f"hg_{idx}")

    assert len(engine.accounts["visitor_1"].distinct_peers_tutored_in_hive) == 3
    assert engine.hive_id in engine.accounts["visitor_1"].accepted_in_hives


def test_pairwise_decay_alpha_and_symmetry() -> None:
    engine = _setup_basic_hive()
    engine.register_bee("bee_a", role=BeeRole.LEARNER_BEE)
    engine.register_bee("bee_b", role=BeeRole.LEARNER_BEE)

    # n=0: 1/(1 + 1.5*0) = 1.0 (A -> B)
    engine.create_service_barter_escrow(
        "ab_0", "bee_a", "bee_b", "S1", 1.0, 0.0, reciprocal_subject_id="S2"
    )
    tx0 = engine.settle_co_signed_session("ab_0", 1.0, "h0")
    assert tx0["effective_weight"] == pytest.approx(1.0)

    # n=1 symmetric (B -> A): 1/(1 + 1.5*1) = 0.4
    engine.create_service_barter_escrow(
        "ba_1", "bee_b", "bee_a", "S2", 1.0, 0.0, reciprocal_subject_id="S1"
    )
    tx1 = engine.settle_co_signed_session("ba_1", 1.0, "h1")
    assert tx1["effective_weight"] == pytest.approx(0.4)

    # n=2: 1/(1 + 1.5*2) = 0.25
    engine.create_service_barter_escrow(
        "ab_2", "bee_a", "bee_b", "S1", 1.0, 0.0, reciprocal_subject_id="S2"
    )
    tx2 = engine.settle_co_signed_session("ab_2", 1.0, "h2")
    assert tx2["effective_weight"] == pytest.approx(0.25)


def test_downstream_lineage_gamma_credits_upstream_tutor() -> None:
    engine = _setup_basic_hive()
    engine.register_bee("bee_a", role=BeeRole.LEARNER_BEE)
    engine.register_bee("bee_b", role=BeeRole.LEARNER_BEE)
    engine.register_bee("bee_c", role=BeeRole.LEARNER_BEE)

    engine.create_service_barter_escrow(
        "ab", "bee_a", "bee_b", "RUST-101", 1.0, 0.0, reciprocal_subject_id="PY-101"
    )
    engine.settle_co_signed_session("ab", 1.0, "h_ab")
    eff_a_before = engine.tutor_effectiveness["bee_a"]

    # B teaches C the same subject RUST-101 -> lineage bonus = 1 + 0.5 = 1.5
    engine.create_service_barter_escrow(
        "bc", "bee_b", "bee_c", "RUST-101", 1.0, 0.0, reciprocal_subject_id="GO-101"
    )
    tx_bc = engine.settle_co_signed_session("bc", 1.0, "h_bc")
    assert tx_bc["effective_weight"] == pytest.approx(1.5)
    assert engine.tutor_effectiveness["bee_a"] == pytest.approx(eff_a_before + 0.25 * 1.5)


def test_bridge_fx_clamp_bounds_and_zero_comb_floor() -> None:
    # Upper clamp 2.0x
    rich = _setup_basic_hive(hive_id="HIVE_RICH", seed_comb=2500.0, accepted_threshold=1)
    poor = _setup_basic_hive(hive_id="HIVE_POOR", seed_comb=50.0, accepted_threshold=1)
    rich.create_service_barter_escrow(
        "e1", "worker_1", "learner_1", "CS-101", 1.0, 20.0, TokenState.RAW_POLLEN
    )
    rich.settle_co_signed_session("e1", 1.0, "h")

    poor.register_bee("worker_1", home_hive_id="HIVE_RICH")
    poor.create_service_barter_escrow(
        "p1", "worker_1", "learner_1", "CS-101", 1.0, 0.0, reciprocal_subject_id="X"
    )
    poor.settle_co_signed_session("p1", 1.0, "hp")

    res_hi = rich.bridge_nectr_to_target_hive("worker_1", poor, 20.0, bridge_toll_rate=0.05)
    assert res_hi["exchange_rate"] == pytest.approx(2.0)
    assert res_hi["source_comb_toll"] == pytest.approx(1.0)
    assert res_hi["received_in_target"] == pytest.approx(38.0)
    rich.assert_supply_conservation()
    poor.assert_supply_conservation()

    # Lower clamp 0.5x + zero comb floor on source
    zero_src = HiveContractEngine(hive_id="HIVE_ZERO", accepted_status_peer_threshold=1)
    zero_src.inject_sponsored_seed_comb(20.0)
    zero_src.register_bee("queen_1", role=BeeRole.QUEEN)
    zero_src.register_bee("worker_1", role=BeeRole.LEARNER_BEE)
    zero_src.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    zero_src.certify_worker_bee("queen_1", "worker_1", "CS-101")
    zero_src.allocate_raw_pollen_to_learner("queen_1", "learner_1", 20.0)  # comb_reserve == 0.0!
    zero_src.create_service_barter_escrow(
        "z1", "worker_1", "learner_1", "CS-101", 1.0, 20.0, TokenState.RAW_POLLEN
    )
    zero_src.settle_co_signed_session("z1", 1.0, "hz")

    rich.register_bee("worker_1", home_hive_id="HIVE_ZERO")
    rich.accounts["worker_1"].accepted_in_hives.add("HIVE_RICH")
    res_lo = zero_src.bridge_nectr_to_target_hive("worker_1", rich, 20.0, bridge_toll_rate=0.05)
    assert res_lo["exchange_rate"] == pytest.approx(0.5)
    assert res_lo["source_comb_toll"] == pytest.approx(1.0)
    assert res_lo["received_in_target"] == pytest.approx(9.5)
    zero_src.assert_supply_conservation()
    rich.assert_supply_conservation()


# ---------------------------------------------------------------------------
# Phase 1 RED tests for pure snapshot/hydration helpers
# ---------------------------------------------------------------------------


def test_contract_engine_snapshot_round_trip_and_isolation() -> None:
    engine = _setup_basic_hive(hive_id="HIVE_SNAP", seed_comb=300.0, accepted_threshold=2)
    engine.register_bee("visitor:1", role=BeeRole.POLLINATOR_VISITOR, home_hive_id="HIVE_EXT")
    engine.accounts["queen_1"].royal_jelly_earned = 4.25

    # Settle one session (creates pairwise_counts, subject_lineage, tutor_effectiveness, settled_tx_log)
    engine.create_service_barter_escrow(
        session_id="sess_settled",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.5,
        amount=12.5,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("sess_settled", 0.92, "hash_settled")

    # Leave one session in INTENT_ESCROWED
    engine.create_service_barter_escrow(
        session_id="sess_escrow",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=7.5,
        token_state=TokenState.RAW_POLLEN,
    )

    # Disputed session
    engine.create_service_barter_escrow(
        session_id="sess_dispute",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.resolve_disputed_session("queen_1", "sess_dispute", tutor_share_ratio=0.5)

    snap = engine.to_snapshot()  # type: ignore[attr-defined]
    # Mutating snapshot copy must not mutate engine
    snap["accounts"]["worker_1"]["liquid_nectr_balance"] = 999999.0
    assert engine.accounts["worker_1"].liquid_nectr_balance != 999999.0

    fresh_snap = engine.to_snapshot()  # type: ignore[attr-defined]
    rehydrated = HiveContractEngine.from_snapshot(fresh_snap)  # type: ignore[attr-defined]

    assert json.dumps(rehydrated.to_snapshot(), sort_keys=True) == json.dumps(  # type: ignore[attr-defined]
        fresh_snap, sort_keys=True
    )
    assert canonicaljson.encode_canonical_json(
        rehydrated.to_snapshot()  # type: ignore[attr-defined]
    ) == canonicaljson.encode_canonical_json(fresh_snap)
    assert rehydrated.sessions["sess_escrow"].status == SessionStatus.INTENT_ESCROWED
    assert rehydrated.accounts["queen_1"].royal_jelly_earned == pytest.approx(4.25)

    # BeeAccount and ServiceBarterSession dict round-trips
    acct_dict = engine.accounts["worker_1"].to_dict()  # type: ignore[attr-defined]
    assert BeeAccount.from_dict(acct_dict) == engine.accounts["worker_1"]  # type: ignore[attr-defined]
    sess_dict = engine.sessions["sess_escrow"].to_dict()  # type: ignore[attr-defined]
    assert ServiceBarterSession.from_dict(sess_dict) == engine.sessions["sess_escrow"]  # type: ignore[attr-defined]


def test_contract_engine_from_snapshot_rejects_corrupted_supply_and_bad_pairs() -> None:
    engine = _setup_basic_hive(hive_id="HIVE_CORRUPT")
    snap = engine.to_snapshot()
    snap["comb_reserve"] = snap["comb_reserve"] + 42.0
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        HiveContractEngine.from_snapshot(snap)

    bad_pair_snap = engine.to_snapshot()
    bad_pair_snap["pairwise_counts"] = [{"pair": ["only_one"], "count": 1}]
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(bad_pair_snap)

    bad_ver = engine.to_snapshot()
    bad_ver["schema_version"] = 99
    with pytest.raises(ContractViolationError, match="Unsupported snapshot schema version"):
        HiveContractEngine.from_snapshot(bad_ver)

    bad_acct_key = engine.to_snapshot()
    bad_acct_key["accounts"]["wrong_key"] = bad_acct_key["accounts"].pop("worker_1")
    with pytest.raises(ContractViolationError, match="does not match bee_id"):
        HiveContractEngine.from_snapshot(bad_acct_key)

    engine.create_service_barter_escrow(
        session_id="sess_bad",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    bad_sess_key = engine.to_snapshot()
    bad_sess_key["sessions"]["wrong_sess"] = bad_sess_key["sessions"].pop("sess_bad")
    with pytest.raises(ContractViolationError, match="does not match session_id"):
        HiveContractEngine.from_snapshot(bad_sess_key)

    bad_sess_hive = engine.to_snapshot()
    bad_sess_hive["sessions"]["sess_bad"]["hive_id"] = "OTHER_HIVE"
    with pytest.raises(ContractViolationError, match="hive_id"):
        HiveContractEngine.from_snapshot(bad_sess_hive)

    with pytest.raises(ContractViolationError, match="Invalid BeeAccount snapshot"):
        BeeAccount.from_dict({"bee_id": "only_id"})

    with pytest.raises(ContractViolationError, match="Invalid ServiceBarterSession snapshot"):
        ServiceBarterSession.from_dict({"session_id": "only_id"})

    with pytest.raises(ContractViolationError, match="Invalid HiveContractEngine snapshot"):
        HiveContractEngine.from_snapshot({"schema_version": 1})


# ---------------------------------------------------------------------------
# Iteration 2 Regression Tests: Contract Validation Hardening
# ---------------------------------------------------------------------------


def test_escrow_rejects_duplicate_session_id() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="dup_sess",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("dup_sess", 1.0, "hash_1")
    with pytest.raises(ContractViolationError, match="already exists"):
        engine.create_service_barter_escrow(
            session_id="dup_sess",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.RAW_POLLEN,
        )


@pytest.mark.parametrize("bad_fee", [-0.1, 1.1, 2.0, float("nan"), float("inf")])
def test_dispute_rejects_out_of_bounds_service_fee_rate(bad_fee: float) -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_bad_fee",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    with pytest.raises(ContractViolationError, match="service_fee_rate"):
        engine.resolve_disputed_session(
            "queen_1", "s_bad_fee", tutor_share_ratio=0.5, service_fee_rate=bad_fee
        )


@pytest.mark.parametrize("bad_duration", [0.0, -1.0, float("nan"), float("inf")])
def test_escrow_rejects_non_positive_duration_hours(bad_duration: float) -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="duration_hours"):
        engine.create_service_barter_escrow(
            session_id="s_bad_dur",
            tutor_id="worker_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=bad_duration,
            amount=5.0,
            token_state=TokenState.RAW_POLLEN,
        )


def test_contract_methods_reject_non_finite_and_invalid_rates() -> None:
    engine = _setup_basic_hive()
    target = _setup_basic_hive(hive_id="HIVE_TARGET", accepted_threshold=1)
    target.register_bee("worker_1", home_hive_id="HIVE_UNIT")
    target.accounts["worker_1"].accepted_in_hives.add("HIVE_TARGET")

    for bad_num in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ContractViolationError):
            engine.inject_sponsored_seed_comb(bad_num)
        with pytest.raises(ContractViolationError):
            engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", bad_num)
        with pytest.raises(ContractViolationError):
            engine.certify_worker_bee("queen_1", "worker_1", "BIO-101", certification_fee=bad_num)
        with pytest.raises(ContractViolationError):
            engine.create_service_barter_escrow(
                session_id="s_nan",
                tutor_id="worker_1",
                learner_id="learner_1",
                subject_id="CS-101",
                duration_hours=1.0,
                amount=bad_num,
                token_state=TokenState.RAW_POLLEN,
            )
        with pytest.raises(ContractViolationError):
            engine.bridge_nectr_to_target_hive("worker_1", target, bad_num)

    with pytest.raises(ContractViolationError):
        engine.certify_worker_bee("queen_1", "worker_1", "BIO-101", certification_fee=-1.0)

    engine.create_service_barter_escrow(
        session_id="s_earn",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    engine.settle_co_signed_session("s_earn", 1.0, "h_earn")
    for bad_toll in (-0.1, 1.1, float("nan")):
        with pytest.raises(ContractViolationError):
            engine.bridge_nectr_to_target_hive("worker_1", target, 5.0, bridge_toll_rate=bad_toll)


def test_assert_supply_conservation_rejects_nan_inf_and_negative_balances() -> None:
    engine_nan = _setup_basic_hive(hive_id="HIVE_NAN")
    engine_nan.comb_reserve = float("nan")
    engine_nan.total_minted_supply = float("nan")
    with pytest.raises(ContractViolationError):
        engine_nan.assert_supply_conservation()

    engine_inf = _setup_basic_hive(hive_id="HIVE_INF")
    engine_inf.comb_reserve = float("inf")
    engine_inf.total_minted_supply = float("inf")
    with pytest.raises(ContractViolationError):
        engine_inf.assert_supply_conservation()

    engine_neg = _setup_basic_hive(hive_id="HIVE_NEG")
    engine_neg.accounts["learner_1"].raw_pollen_balance = -50.0
    engine_neg.comb_reserve += 100.0
    with pytest.raises(ContractViolationError):
        engine_neg.assert_supply_conservation()


def test_snapshot_hydration_rejects_corrupted_fields_and_bad_types() -> None:
    engine = _setup_basic_hive(hive_id="HIVE_SNAP_HARDEN")
    engine.create_service_barter_escrow(
        session_id="s1",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.RAW_POLLEN,
    )
    base_snap = engine.to_snapshot()

    neg_pair = json.loads(json.dumps(base_snap))
    neg_pair["pairwise_counts"] = [{"pair": ["worker_1", "learner_1"], "count": -1}]
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(neg_pair)

    dup_pair = json.loads(json.dumps(base_snap))
    dup_pair["pairwise_counts"] = [
        {"pair": ["worker_1", "learner_1"], "count": 1},
        {"pair": ["learner_1", "worker_1"], "count": 99},
    ]
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(dup_pair)

    nan_snap = json.loads(json.dumps(base_snap))
    nan_snap["comb_reserve"] = float("nan")
    nan_snap["total_minted_supply"] = float("nan")
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(nan_snap)

    neg_bal_snap = json.loads(json.dumps(base_snap))
    neg_bal_snap["accounts"]["learner_1"]["raw_pollen_balance"] = -50.0
    neg_bal_snap["comb_reserve"] += 95.0
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(neg_bal_snap)

    for bad_key, bad_val in (
        ("collusion_alpha", -1.0),
        ("lineage_gamma", -0.5),
        ("accepted_status_peer_threshold", 0),
    ):
        bad_cfg = json.loads(json.dumps(base_snap))
        bad_cfg[bad_key] = bad_val
        with pytest.raises(ContractViolationError):
            HiveContractEngine.from_snapshot(bad_cfg)

    bad_eff = json.loads(json.dumps(base_snap))
    bad_eff["tutor_effectiveness"] = {"worker_1": -1.0}
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(bad_eff)

    bad_accts_type = json.loads(json.dumps(base_snap))
    bad_accts_type["accounts"] = []
    with pytest.raises(ContractViolationError):
        HiveContractEngine.from_snapshot(bad_accts_type)

    acct_dict = engine.accounts["worker_1"].to_dict()
    bad_str_set = dict(acct_dict)
    bad_str_set["certified_subjects"] = "CS-101"
    with pytest.raises(ContractViolationError):
        BeeAccount.from_dict(bad_str_set)

    bad_rj = dict(acct_dict)
    bad_rj["royal_jelly_earned"] = -1.0
    with pytest.raises(ContractViolationError):
        BeeAccount.from_dict(bad_rj)

    sess_dict = engine.sessions["s1"].to_dict()
    for field_name, bad_val in (
        ("duration_hours", 0.0),
        ("escrowed_amount", -1.0),
        ("learner_attestation_score", 1.5),
        ("effective_weight", -0.1),
    ):
        bad_sess = dict(sess_dict)
        bad_sess[field_name] = bad_val
        with pytest.raises(ContractViolationError):
            ServiceBarterSession.from_dict(bad_sess)


# ---------------------------------------------------------------------------
# Review Findings Strict RED Regression Tests (CA1)
# ---------------------------------------------------------------------------


def test_repeated_fractional_disputes_conserve_supply_with_exact_equality() -> None:
    engine = HiveContractEngine(hive_id="HIVE_EXACT_SUPPLY")
    engine.inject_sponsored_seed_comb(10_000.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("tutor_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    engine.certify_worker_bee("queen_1", "tutor_1", "CS-101")

    for idx in range(500):
        engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 0.1234567)
        sess_id = f"frac_sess_{idx}"
        engine.create_service_barter_escrow(
            session_id=sess_id,
            tutor_id="tutor_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.1234567,
            token_state=TokenState.RAW_POLLEN,
        )
        engine.resolve_disputed_session(
            queen_id="queen_1",
            session_id=sess_id,
            tutor_share_ratio=1.0 / 3.0,
            service_fee_rate=0.10,
        )

    total_pollen = sum(a.raw_pollen_balance for a in engine.accounts.values())
    total_liquid = sum(a.liquid_nectr_balance for a in engine.accounts.values())
    total_escrow = sum(
        s.escrowed_amount
        for s in engine.sessions.values()
        if s.status == SessionStatus.INTENT_ESCROWED
    )
    assert (
        engine.comb_reserve + total_pollen + total_liquid + total_escrow
        == engine.total_minted_supply
    )


def test_micro_unit_conservation_holds_exact_integer_equality_for_any_iteration_count() -> None:
    engine = HiveContractEngine(hive_id="HIVE_MICRO_504")
    engine.inject_sponsored_seed_comb(10_000.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("tutor_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    engine.certify_worker_bee("queen_1", "tutor_1", "CS-101")

    for idx in range(504):
        engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 0.1234567)
        sess_id = f"micro_sess_{idx}"
        engine.create_service_barter_escrow(
            session_id=sess_id,
            tutor_id="tutor_1",
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.1234567,
            token_state=TokenState.RAW_POLLEN,
        )
        engine.resolve_disputed_session(
            queen_id="queen_1",
            session_id=sess_id,
            tutor_share_ratio=1.0 / 3.0,
            service_fee_rate=0.10,
        )

    pollen_units = sum(a.raw_pollen_units for a in engine.accounts.values())
    liquid_units = sum(a.liquid_nectr_units for a in engine.accounts.values())
    escrow_units = sum(
        s.escrowed_units
        for s in engine.sessions.values()
        if s.status == SessionStatus.INTENT_ESCROWED
    )
    assert (
        engine.comb_reserve_units + pollen_units + liquid_units + escrow_units
        == engine.total_minted_supply_units
    )


def test_micro_unit_helpers_and_snapshot_mismatch_guards() -> None:
    from decimal import Decimal

    from nectr.contracts import from_micro_units, to_micro_units

    assert to_micro_units(Decimal("1.5")) == 1_500_000
    assert to_micro_units(2) == 2_000_000
    assert from_micro_units(1_500_000) == 1.5

    for bad_val in (True, Decimal("-0.1"), Decimal("NaN"), -1, "bad"):
        with pytest.raises(ContractViolationError):
            to_micro_units(bad_val)  # type: ignore[arg-type]

    engine = _setup_basic_hive(hive_id="HIVE_MISMATCH")
    snap = engine.to_snapshot()
    snap["comb_reserve_units"] = snap["comb_reserve_units"] + 1
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        HiveContractEngine.from_snapshot(snap)

    # Sub-micro-unit positive values (< 0.5e-6) round to 0 and are rejected for positive-only ops
    with pytest.raises(ContractViolationError, match="Seed Comb injection must be positive"):
        engine.inject_sponsored_seed_comb(1e-8)
    with pytest.raises(ContractViolationError, match="Insufficient Comb reserve"):
        engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 1e-8)

    # Non-finite session balance via property setter triggers assert_supply_conservation failure
    engine.create_service_barter_escrow(
        "s_nan_prop", "worker_1", "learner_1", "CS-101", 1.0, 5.0, TokenState.RAW_POLLEN
    )
    engine.sessions["s_nan_prop"].escrowed_amount = float("nan")
    with pytest.raises(ContractViolationError, match="Non-finite session balance"):
        engine.assert_supply_conservation()
    engine.sessions["s_nan_prop"].escrowed_amount = 5.0
    engine.assert_supply_conservation()

    engine.accounts["learner_1"].raw_pollen_balance = float("inf")
    with pytest.raises(ContractViolationError, match="Non-finite account balance"):
        engine.assert_supply_conservation()


def test_legacy_float_only_snapshot_reconciles_bounded_drift_and_rejects_excess() -> None:
    engine = _setup_basic_hive(hive_id="HIVE_LEGACY_SNAP", seed_comb=10_000.0)
    legacy = json.loads(json.dumps(engine.to_snapshot()))
    # Strip *_units keys to simulate a pre-CA2 float-only snapshot with 9e-5 tolerated drift
    for key in ("comb_reserve_units", "total_minted_supply_units"):
        legacy.pop(key, None)
    for acct in legacy["accounts"].values():
        for key in ("raw_pollen_units", "liquid_nectr_units", "royal_jelly_units"):
            acct.pop(key, None)
    for sess in legacy["sessions"].values():
        sess.pop("escrowed_units", None)

    legacy["accounts"]["worker_1"]["liquid_nectr_balance"] += 0.000090
    rehydrated = HiveContractEngine.from_snapshot(legacy)
    rehydrated.assert_supply_conservation()
    assert rehydrated.total_minted_supply_units == 10_000_000_000

    # Drift > 100 micro-units (1e-4) must still be rejected
    legacy["accounts"]["worker_1"]["liquid_nectr_balance"] += 0.000020  # total +110 micro-units
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        HiveContractEngine.from_snapshot(legacy)


def test_large_balance_above_2_pow_53_micro_units_round_trips_losslessly() -> None:
    engine = HiveContractEngine(hive_id="HIVE_LARGE")
    engine.inject_sponsored_seed_comb(1e10)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 0.000001)

    assert engine.comb_reserve_units == 9_999_999_999_999_999
    snap = engine.to_snapshot()
    rehydrated = HiveContractEngine.from_snapshot(snap)
    assert rehydrated.comb_reserve_units == 9_999_999_999_999_999
    assert rehydrated.accounts["learner_1"].raw_pollen_units == 1
    assert rehydrated.total_minted_supply_units == 10_000_000_000_000_000
    rehydrated.assert_supply_conservation()


@pytest.mark.xfail(strict=True, reason="review finding 4; fixed by CA4")
def test_bridge_rejects_foreign_mover_registered_in_target_without_home_hive_id() -> None:
    hive_a = HiveContractEngine(hive_id="HIVE_A")
    hive_b = HiveContractEngine(hive_id="HIVE_B")

    hive_a.inject_sponsored_seed_comb(500.0)
    hive_b.inject_sponsored_seed_comb(500.0)

    hive_a.register_bee("queen_a", role=BeeRole.QUEEN)
    hive_a.register_bee("learner_a", role=BeeRole.LEARNER_BEE)
    hive_a.register_bee("mover", role=BeeRole.LEARNER_BEE)
    hive_a.certify_worker_bee("queen_a", "mover", "CS-101")
    hive_a.allocate_raw_pollen_to_learner("queen_a", "learner_a", 50.0)
    hive_a.create_service_barter_escrow(
        session_id="earn_in_a",
        tutor_id="mover",
        learner_id="learner_a",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=50.0,
        token_state=TokenState.RAW_POLLEN,
    )
    hive_a.settle_co_signed_session("earn_in_a", 1.0, "hash_earn_a")
    assert hive_a.accounts["mover"].liquid_nectr_balance == 50.0

    # Register "mover" in HIVE_B without home_hive_id and without tutoring anyone there
    hive_b.register_bee("mover", role=BeeRole.LEARNER_BEE)

    with pytest.raises(ContractViolationError, match="Guard Bee Rejection"):
        hive_a.bridge_nectr_to_target_hive("mover", hive_b, 20.0)


@pytest.mark.xfail(strict=True, reason="review finding 5a; fixed by CA3")
def test_queen_cannot_resolve_undisputed_escrow_at_full_fee() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(
        session_id="s_undisputed",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=20.0,
        token_state=TokenState.RAW_POLLEN,
    )
    comb_before = engine.comb_reserve
    with pytest.raises(ContractViolationError):
        engine.resolve_disputed_session(
            queen_id="queen_1",
            session_id="s_undisputed",
            tutor_share_ratio=0.5,
            service_fee_rate=1.0,
        )
    assert engine.sessions["s_undisputed"].status == SessionStatus.INTENT_ESCROWED
    assert engine.sessions["s_undisputed"].escrowed_amount == 20.0
    assert engine.comb_reserve == comb_before


@pytest.mark.xfail(strict=True, reason="review finding 5b; fixed by CA3")
def test_learner_cancels_expired_escrow_and_recovers_original_token_state() -> None:
    engine = _setup_basic_hive()
    engine.create_service_barter_escrow(  # type: ignore[call-arg]
        session_id="s_expired",
        tutor_id="worker_1",
        learner_id="learner_1",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=15.0,
        token_state=TokenState.RAW_POLLEN,
        created_at_epoch=0,
        expiry_epochs=5,
    )
    assert engine.accounts["learner_1"].raw_pollen_balance == 35.0

    engine.cancel_expired_escrow(  # type: ignore[attr-defined]
        session_id="s_expired",
        learner_id="learner_1",
        current_epoch=6,
    )
    assert engine.accounts["learner_1"].raw_pollen_balance == 50.0
    assert engine.accounts["learner_1"].liquid_nectr_balance == 0.0
    assert engine.sessions["s_expired"].status != SessionStatus.INTENT_ESCROWED
    engine.assert_supply_conservation()
