"""Mutation-hardening tests for core HiveContractEngine smart contract invariants."""

from __future__ import annotations

import pytest

from nectr.contracts import (
    BeeRole,
    ContractViolationError,
    HiveContractEngine,
    SessionStatus,
    TokenState,
)


def _setup_basic_hive() -> HiveContractEngine:
    engine = HiveContractEngine(hive_id="HIVE_A", accepted_status_peer_threshold=2)
    engine.inject_sponsored_seed_comb(100.0)
    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    engine.register_bee("worker_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)
    engine.register_bee("learner_2", role=BeeRole.LEARNER_BEE)
    engine.certify_worker_bee("queen_1", "worker_1", "CS-101")
    return engine


def test_supply_conservation_and_cumulative_seed_pollen() -> None:
    engine = HiveContractEngine(hive_id="HIVE_S")
    with pytest.raises(ContractViolationError, match="positive"):
        engine.inject_sponsored_seed_comb(0.0)
    with pytest.raises(ContractViolationError, match="positive"):
        engine.inject_sponsored_seed_comb(-5.0)

    r1 = engine.inject_sponsored_seed_comb(40.0)
    r2 = engine.inject_sponsored_seed_comb(60.0)
    assert r1["comb_reserve"] == 40.0
    assert r2["comb_reserve"] == 100.0
    assert engine.total_minted_supply == 100.0

    engine.register_bee("queen_1", role=BeeRole.QUEEN)
    acct = engine.register_bee("bee_1", home_hive_id="HIVE_OTHER")
    assert acct.home_hive_id == "HIVE_OTHER"
    assert engine.register_bee("bee_1") is acct

    engine.allocate_raw_pollen_to_learner("queen_1", "bee_1", 10.0)
    alloc2 = engine.allocate_raw_pollen_to_learner("queen_1", "bee_1", 15.0)
    assert alloc2["amount"] == 15.0
    assert engine.accounts["bee_1"].raw_pollen_balance == 25.0
    assert engine.comb_reserve == 75.0

    with pytest.raises(ContractViolationError, match="Insufficient Comb"):
        engine.allocate_raw_pollen_to_learner("queen_1", "bee_1", 0.0)
    with pytest.raises(ContractViolationError, match="Insufficient Comb"):
        engine.allocate_raw_pollen_to_learner("queen_1", "bee_1", 75.1)

    # Tolerance boundary checks on assert_supply_conservation
    engine.accounts["bee_1"].raw_pollen_balance += 0.00005
    engine.assert_supply_conservation()
    engine.accounts["bee_1"].raw_pollen_balance += 0.0002
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        engine.assert_supply_conservation()


def test_queen_separation_of_powers_all_paths() -> None:
    engine = _setup_basic_hive()
    with pytest.raises(ContractViolationError, match="not registered"):
        engine.allocate_raw_pollen_to_learner("missing_queen", "learner_1", 5.0)
    with pytest.raises(ContractViolationError, match="does not hold QUEEN role"):
        engine.allocate_raw_pollen_to_learner("learner_1", "learner_2", 5.0)
    with pytest.raises(ContractViolationError, match="Queens cannot receive RAW_POLLEN"):
        engine.allocate_raw_pollen_to_learner("queen_1", "queen_1", 5.0)
    with pytest.raises(ContractViolationError, match="Queens cannot be certified"):
        engine.certify_worker_bee("queen_1", "queen_1", "CS-101")

    engine.accounts["queen_1"].liquid_nectr_balance = 10.0
    engine.total_minted_supply += 10.0
    target = HiveContractEngine(hive_id="HIVE_B")
    with pytest.raises(ContractViolationError, match="Queens are bound to their Hive"):
        engine.bridge_nectr_to_target_hive("queen_1", target, 5.0)


def test_certification_fee_and_dispute_fee_to_comb_invariants() -> None:
    engine = _setup_basic_hive()
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 40.0)

    # Worker needs LIQUID_NECTR to pay positive certification_fee
    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR"):
        engine.certify_worker_bee("queen_1", "worker_1", "MATH-201", certification_fee=5.0)

    # Earn LIQUID_NECTR by tutoring learner_1
    engine.create_service_barter_escrow(
        "s1", "worker_1", "learner_1", "CS-101", 1.0, 20.0, TokenState.RAW_POLLEN
    )
    engine.settle_co_signed_session("s1", 1.0, "h1")
    assert engine.accounts["worker_1"].liquid_nectr_balance == 20.0

    comb_before = engine.comb_reserve
    cert_res = engine.certify_worker_bee("queen_1", "worker_1", "MATH-201", certification_fee=4.0)
    assert cert_res["fee_to_comb"] == 4.0
    assert engine.accounts["worker_1"].liquid_nectr_balance == 16.0
    assert engine.comb_reserve == comb_before + 4.0
    assert "MATH-201" in engine.accounts["worker_1"].certified_subjects

    # Dispute on LIQUID_NECTR session with 0% and 100% tutor share bounds + cumulative balances
    engine.accounts["learner_2"].liquid_nectr_balance = 30.0
    engine.total_minted_supply += 30.0
    engine.create_service_barter_escrow(
        "d_liq", "worker_1", "learner_2", "CS-101", 1.0, 10.0, TokenState.LIQUID_NECTR
    )
    with pytest.raises(ContractViolationError, match="tutor_share_ratio"):
        engine.resolve_disputed_session("queen_1", "d_liq", tutor_share_ratio=-0.1)
    with pytest.raises(ContractViolationError, match="tutor_share_ratio"):
        engine.resolve_disputed_session("queen_1", "d_liq", tutor_share_ratio=1.1)

    res = engine.resolve_disputed_session(
        "queen_1", "d_liq", tutor_share_ratio=0.0, service_fee_rate=0.10
    )
    assert res["fee_to_comb"] == 1.0
    assert res["tutor_payout"] == 0.0
    assert res["learner_refund"] == 9.0
    assert engine.accounts["worker_1"].liquid_nectr_balance == 16.0
    assert engine.accounts["learner_2"].liquid_nectr_balance == 29.0
    assert engine.comb_reserve == comb_before + 5.0
    assert engine.sessions["d_liq"].status == SessionStatus.DISPUTED_TO_QUEEN

    with pytest.raises(ContractViolationError, match="Only escrowed sessions"):
        engine.resolve_disputed_session("queen_1", "d_liq", tutor_share_ratio=1.0)
    with pytest.raises(ContractViolationError, match="does not exist"):
        engine.resolve_disputed_session("queen_1", "missing", tutor_share_ratio=0.5)


def test_escrow_validation_lineage_and_collusion_boundaries() -> None:
    engine = _setup_basic_hive()
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 20.0)

    with pytest.raises(ContractViolationError, match="Self-tutoring"):
        engine.create_service_barter_escrow("bad1", "worker_1", "worker_1", "CS-101", 1.0, 5.0)
    with pytest.raises(ContractViolationError, match="negative"):
        engine.create_service_barter_escrow("bad2", "worker_1", "learner_1", "CS-101", 1.0, -1.0)
    with pytest.raises(ContractViolationError, match="reciprocal_subject_id"):
        engine.create_service_barter_escrow("bad3", "worker_1", "learner_1", "CS-101", 1.0, 0.0)
    with pytest.raises(ContractViolationError, match="certified subject"):
        engine.create_service_barter_escrow(
            "bad4", "worker_1", "learner_1", "BIOL-101", 1.0, 5.0, TokenState.RAW_POLLEN
        )
    with pytest.raises(ContractViolationError, match="Insufficient RAW_POLLEN"):
        engine.create_service_barter_escrow(
            "bad5", "worker_1", "learner_1", "CS-101", 1.0, 25.0, TokenState.RAW_POLLEN
        )
    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR"):
        engine.create_service_barter_escrow(
            "bad6", "worker_1", "learner_1", "CS-101", 1.0, 5.0, TokenState.LIQUID_NECTR
        )
    with pytest.raises(ContractViolationError, match="Invalid token state"):
        engine.create_service_barter_escrow(
            "bad7", "worker_1", "learner_1", "CS-101", 1.0, 5.0, TokenState.ROYAL_COMB_RESERVE
        )

    # Attestation boundaries & 0.6 lineage cutoff
    engine.create_service_barter_escrow(
        "low_att", "worker_1", "learner_1", "CS-101", 1.0, 5.0, TokenState.RAW_POLLEN
    )
    with pytest.raises(ContractViolationError, match="Attestation score"):
        engine.settle_co_signed_session("low_att", -0.01, "h")
    with pytest.raises(ContractViolationError, match="Attestation score"):
        engine.settle_co_signed_session("low_att", 1.01, "h")

    tx_low = engine.settle_co_signed_session("low_att", 0.59, "h")
    assert tx_low["effective_weight"] == pytest.approx(0.59)
    assert ("learner_1", "CS-101") not in engine.subject_lineage
    with pytest.raises(ContractViolationError, match="not in INTENT_ESCROWED"):
        engine.settle_co_signed_session("low_att", 0.9, "h")

    # Second session on same pair gets pairwise decay 1 / (1 + 1.5 * 1) = 0.4
    engine.create_service_barter_escrow(
        "pair2", "worker_1", "learner_1", "CS-101", 1.0, 5.0, TokenState.RAW_POLLEN
    )
    tx_pair2 = engine.settle_co_signed_session("pair2", 1.0, "h2")
    assert tx_pair2["effective_weight"] == pytest.approx(0.4)
    assert tx_pair2["fee_charged"] == 0.0

    # New peer learner_2 at exact 0.6 attestation grants lineage & downstream upstream boost
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_2", 10.0)
    engine.create_service_barter_escrow(
        "lin1", "worker_1", "learner_2", "CS-101", 1.0, 5.0, TokenState.RAW_POLLEN
    )
    engine.settle_co_signed_session("lin1", 0.6, "h3")
    assert engine.subject_lineage[("learner_2", "CS-101")] == ["worker_1"]

    eff_before = engine.tutor_effectiveness["worker_1"]
    engine.create_service_barter_escrow(
        "lin_down",
        "learner_2",
        "learner_1",
        "CS-101",
        1.0,
        0.0,
        reciprocal_subject_id="ART-101",
    )
    tx_down = engine.settle_co_signed_session("lin_down", 1.0, "h4")
    assert tx_down["effective_weight"] == pytest.approx(1.5)
    assert engine.tutor_effectiveness["worker_1"] == pytest.approx(eff_before + 0.25 * 1.5)


def test_cross_hive_accepted_status_and_bridge_clamps() -> None:
    hive_a = _setup_basic_hive()
    hive_b = HiveContractEngine(hive_id="HIVE_B", accepted_status_peer_threshold=2)
    hive_b.inject_sponsored_seed_comb(100.0)
    for idx in range(3):
        hive_b.register_bee(f"peer_{idx}", role=BeeRole.LEARNER_BEE)

    # Seed worker_1 in hive_a with 40 LIQUID_NECTR
    hive_a.allocate_raw_pollen_to_learner("queen_1", "learner_1", 40.0)
    hive_a.create_service_barter_escrow(
        "s_a", "worker_1", "learner_1", "CS-101", 1.0, 40.0, TokenState.RAW_POLLEN
    )
    hive_a.settle_co_signed_session("s_a", 1.0, "ha")

    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR"):
        hive_a.bridge_nectr_to_target_hive("worker_1", hive_b, 0.0)
    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR"):
        hive_a.bridge_nectr_to_target_hive("worker_1", hive_b, 41.0)

    # Tutor 1 distinct peer in hive_b (< threshold 2) -> still rejected
    hive_b.register_bee("worker_1", home_hive_id="HIVE_A")
    hive_b.create_service_barter_escrow(
        "sb1", "worker_1", "peer_0", "CS-101", 1.0, 0.0, reciprocal_subject_id="ENG-101"
    )
    hive_b.settle_co_signed_session("sb1", 0.8, "hb1")
    with pytest.raises(ContractViolationError, match="Accepted Status"):
        hive_a.bridge_nectr_to_target_hive("worker_1", hive_b, 10.0)

    # Second distinct peer grants Accepted Status
    hive_b.create_service_barter_escrow(
        "sb2", "worker_1", "peer_1", "CS-101", 1.0, 0.0, reciprocal_subject_id="ENG-102"
    )
    hive_b.settle_co_signed_session("sb2", 0.8, "hb2")
    assert "HIVE_B" in hive_b.accounts["worker_1"].accepted_in_hives

    # Test high FX clamp at 2.0
    hive_a.inject_sponsored_seed_comb(5000.0)
    comb_a_before = hive_a.comb_reserve
    supply_a_before = hive_a.total_minted_supply
    supply_b_before = hive_b.total_minted_supply

    res_hi = hive_a.bridge_nectr_to_target_hive("worker_1", hive_b, 10.0, bridge_toll_rate=0.05)
    assert res_hi["exchange_rate"] == 2.0
    assert res_hi["source_comb_toll"] == 0.5
    assert res_hi["received_in_target"] == 19.0
    assert hive_a.comb_reserve == pytest.approx(comb_a_before + 0.5)
    assert hive_a.total_minted_supply == pytest.approx(supply_a_before - 9.5)
    assert hive_b.total_minted_supply == pytest.approx(supply_b_before + 19.0)

    # Test low FX clamp at 0.5
    hive_b.inject_sponsored_seed_comb(100000.0)
    res_lo = hive_a.bridge_nectr_to_target_hive("worker_1", hive_b, 10.0, bridge_toll_rate=0.05)
    assert res_lo["exchange_rate"] == 0.5
    assert res_lo["received_in_target"] == 4.75
