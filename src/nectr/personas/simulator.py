"""Agent-Based Computational Economics (ACE) simulation runner for the 6 Persona Sub-Agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nectr.contracts.engine import BeeRole, TokenState
from nectr.services.hive_service import HiveServiceLayer


@dataclass
class SimulationTelemetry:
    """Empirical metrics produced by running the 6 Persona Sub-Agents on the private blockchain."""

    hive_a_blocks_mined: int
    hive_a_chain_valid: bool
    hive_a_comb_reserve: float
    honest_worker_effectiveness: float
    sybil_colluder_effectiveness: float
    collusion_attenuation_ratio: float
    pollinator_accepted_in_hive_b: bool
    pollinator_bridged_nectr: float
    queen_royal_jelly_score: float


def run_multi_hive_persona_simulation() -> tuple[SimulationTelemetry, dict[str, Any]]:
    """Run a deterministic multi-epoch simulation of all 6 Persona Sub-Agents across HIVE_ALPHA and HIVE_BETA."""
    hive_a = HiveServiceLayer(hive_id="HIVE_ALPHA", difficulty=2, accepted_status_peer_threshold=2)
    hive_b = HiveServiceLayer(hive_id="HIVE_BETA", difficulty=2, accepted_status_peer_threshold=2)

    # 1. Phase 1 Sponsored Genesis for HIVE_ALPHA & HIVE_BETA
    hive_a.bootstrap_sponsored_hive(
        seed_comb_amount=1000.0,
        queen_ids=["queen_faculty_1"],
        certified_workers={
            "worker_senior_1": ["CS-101", "CALC-101"],
            "pollinator_bee_1": ["PHYS-201"],
        },
    )
    hive_b.bootstrap_sponsored_hive(
        seed_comb_amount=800.0,
        queen_ids=["queen_faculty_beta"],
        certified_workers={"worker_beta_1": ["CHEM-101"]},
    )

    # 2. Register Freshman Foragers, Finals Panickers, and Sybil Colluder Ring in HIVE_ALPHA
    for freshman_id in ["freshman_1", "freshman_2", "panicker_1"]:
        hive_a.contracts.register_bee(freshman_id, role=BeeRole.LEARNER_BEE)
        hive_a.contracts.allocate_raw_pollen_to_learner("queen_faculty_1", freshman_id, 25.0)

    for sybil_id in ["sybil_roommate_a", "sybil_roommate_b"]:
        hive_a.contracts.register_bee(sybil_id, role=BeeRole.LEARNER_BEE)
        hive_a.contracts.allocate_raw_pollen_to_learner("queen_faculty_1", sybil_id, 10.0)

    # 3. Epoch 1: Freshmen spend RAW_POLLEN with Certified Workers (Refining into LIQUID_NECTR!)
    hive_a.execute_tutoring_handshake(
        session_id="sess_e1_1",
        tutor_id="worker_senior_1",
        learner_id="freshman_1",
        subject_id="CS-101",
        duration_hours=1.5,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    hive_a.execute_tutoring_handshake(
        session_id="sess_e1_2",
        tutor_id="worker_senior_1",
        learner_id="freshman_2",
        subject_id="CALC-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    hive_a.execute_tutoring_handshake(
        session_id="sess_e1_3",
        tutor_id="pollinator_bee_1",
        learner_id="panicker_1",
        subject_id="PHYS-201",
        duration_hours=2.0,
        amount=15.0,
        token_state=TokenState.RAW_POLLEN,
    )
    # Seed sybil_roommate_a with liquid nectR by spending raw pollen legitimately once
    hive_a.execute_tutoring_handshake(
        session_id="sess_e1_sybil_seed",
        tutor_id="worker_senior_1",
        learner_id="sybil_roommate_a",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    # freshman_1 learns CS-101 and then teaches freshman_2 (Downstream Learn-then-Teach Lineage!)
    hive_a.execute_tutoring_handshake(
        session_id="sess_e1_lineage",
        tutor_id="freshman_1",
        learner_id="freshman_2",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="SPAN-101",
    )
    hive_a.mine_epoch_block()

    # 4. Epoch 2: Sybil Roommate Ring attempts wash-trading back and forth 6 times
    # First give sybil_roommate_a some liquid nectR via a session with worker_senior_1
    hive_a.execute_tutoring_handshake(
        session_id="sess_e2_prep",
        tutor_id="sybil_roommate_a",
        learner_id="worker_senior_1",
        subject_id="MUSIC-101",
        duration_hours=1.0,
        amount=5.0,
        token_state=TokenState.LIQUID_NECTR,
    )
    for i in range(6):
        tutor = "sybil_roommate_b" if i % 2 == 0 else "sybil_roommate_a"
        learner = "sybil_roommate_a" if i % 2 == 0 else "sybil_roommate_b"
        hive_a.execute_tutoring_handshake(
            session_id=f"sess_sybil_wash_{i}",
            tutor_id=tutor,
            learner_id=learner,
            subject_id="WASH-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.LIQUID_NECTR,
        )
    hive_a.mine_epoch_block()

    # 5. Epoch 3: Drifting Pollinator migrates from HIVE_ALPHA to HIVE_BETA
    # Earns Accepted Status in HIVE_BETA by tutoring 2 distinct local Bees in HIVE_BETA
    for b_learner in ["beta_student_1", "beta_student_2"]:
        hive_b.contracts.register_bee(b_learner, role=BeeRole.LEARNER_BEE)
    hive_b.contracts.register_bee("pollinator_bee_1", home_hive_id="HIVE_ALPHA")

    hive_b.execute_tutoring_handshake(
        session_id="sess_beta_1",
        tutor_id="pollinator_bee_1",
        learner_id="beta_student_1",
        subject_id="PHYS-201",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="BIO-101",
    )
    hive_b.execute_tutoring_handshake(
        session_id="sess_beta_2",
        tutor_id="pollinator_bee_1",
        learner_id="beta_student_2",
        subject_id="PHYS-201",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="CHEM-101",
    )
    hive_b.mine_epoch_block()

    # Now pollinator_bee_1 has Accepted Status in HIVE_BETA and bridges 10 LIQUID_NECTR from HIVE_ALPHA -> HIVE_BETA
    bridge_tx = hive_a.contracts.bridge_nectr_to_target_hive(
        bee_id="pollinator_bee_1",
        target_hive=hive_b.contracts,
        amount=10.0,
    )
    hive_a.blockchain.submit_transaction(bridge_tx)
    hive_a.mine_epoch_block()

    honest_eff = hive_a.contracts.tutor_effectiveness.get("worker_senior_1", 0.0)
    sybil_b_eff = hive_a.contracts.tutor_effectiveness.get("sybil_roommate_b", 0.0)
    queen_rj = hive_a.contracts.accounts["queen_faculty_1"].royal_jelly_earned

    telemetry = SimulationTelemetry(
        hive_a_blocks_mined=len(hive_a.blockchain.chain),
        hive_a_chain_valid=hive_a.blockchain.verify_chain(),
        hive_a_comb_reserve=hive_a.contracts.comb_reserve,
        honest_worker_effectiveness=round(honest_eff, 4),
        sybil_colluder_effectiveness=round(sybil_b_eff, 4),
        collusion_attenuation_ratio=round(honest_eff / max(sybil_b_eff, 1e-6), 4),
        pollinator_accepted_in_hive_b="HIVE_BETA"
        in hive_b.contracts.accounts["pollinator_bee_1"].accepted_in_hives,
        pollinator_bridged_nectr=bridge_tx["received_in_target"],
        queen_royal_jelly_score=queen_rj,
    )
    return telemetry, {"hive_a_bridge_tx": bridge_tx}
