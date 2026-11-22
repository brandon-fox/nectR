"""Agent-Based Computational Economics (ACE) simulation runner for the 6 Persona Sub-Agents."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from nectr.chain import Ed25519Signer, SignedTransaction, compute_sha256
from nectr.contracts.engine import BeeRole, TokenState
from nectr.services.hive_service import HiveServiceLayer

_SIM_EPOCH_ORIGIN_TS: float = 1700000000.0
_SIM_EPOCH_STEP_SECONDS: float = 60.0


def _test_only_signer_for_bee(bee_id: str) -> Ed25519Signer:
    """Derive an Ed25519 keypair from sha256(bee_id) (TEST/SIMULATION ONLY; never use in production)."""
    return Ed25519Signer.from_seed(hashlib.sha256(bee_id.encode("utf-8")).digest())


class _SimSignerBook:
    """Test-only nonce and signature tracker for persona simulations."""

    def __init__(self) -> None:
        self._signers: dict[str, Ed25519Signer] = {}
        self._nonces: dict[tuple[str, str], int] = {}

    def signer(self, bee_id: str) -> Ed25519Signer:
        if bee_id not in self._signers:
            self._signers[bee_id] = _test_only_signer_for_bee(bee_id)
        return self._signers[bee_id]

    def public_key(self, bee_id: str) -> str:
        return self.signer(bee_id).public_key_hex

    def next_nonce(self, hive_id: str, bee_id: str) -> int:
        key = (hive_id, bee_id)
        val = self._nonces.get(key, 0) + 1
        self._nonces[key] = val
        return val

    def sign(self, hive_id: str, actor_id: str, payload: dict[str, Any]) -> SignedTransaction:
        return SignedTransaction.create(
            payload,
            signer=self.signer(actor_id),
            signer_id=actor_id,
        )


def _epoch_timestamp(epoch: int) -> float:
    return _SIM_EPOCH_ORIGIN_TS + epoch * _SIM_EPOCH_STEP_SECONDS


def _signed_handshake(
    book: _SimSignerBook,
    hive: HiveServiceLayer,
    *,
    session_id: str,
    tutor_id: str,
    learner_id: str,
    subject_id: str,
    duration_hours: float,
    amount: float,
    token_state: TokenState = TokenState.LIQUID_NECTR,
    learner_attestation_score: float = 0.95,
    reciprocal_subject_id: str | None = None,
) -> dict[str, Any]:
    hive_id = hive.hive_id
    escrow_tx = book.sign(
        hive_id,
        learner_id,
        {
            "action": "CREATE_BARTER_ESCROW",
            "hive_id": hive_id,
            "session_id": session_id,
            "tutor_id": tutor_id,
            "learner_id": learner_id,
            "subject_id": subject_id,
            "duration_hours": duration_hours,
            "amount": amount,
            "token_state": token_state.value,
            "reciprocal_subject_id": reciprocal_subject_id,
            "nonce": book.next_nonce(hive_id, learner_id),
        },
    )
    comp_hash = compute_sha256(f"{session_id}:{tutor_id}:{learner_id}:{subject_id}")
    settle_payload = {
        "action": "SETTLE_SESSION",
        "hive_id": hive_id,
        "session_id": session_id,
        "learner_attestation_score": learner_attestation_score,
        "tutor_comprehension_hash": comp_hash,
        "learner_nonce": book.next_nonce(hive_id, learner_id),
        "tutor_nonce": book.next_nonce(hive_id, tutor_id),
    }
    return hive.execute_tutoring_handshake(
        escrow_tx=escrow_tx,
        learner_settle_tx=book.sign(hive_id, learner_id, settle_payload),
        tutor_settle_tx=book.sign(hive_id, tutor_id, settle_payload),
    )


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
    book = _SimSignerBook()
    hive_a = HiveServiceLayer(hive_id="HIVE_ALPHA", difficulty=2, accepted_status_peer_threshold=2)
    hive_b = HiveServiceLayer(hive_id="HIVE_BETA", difficulty=2, accepted_status_peer_threshold=2)

    # 1. Phase 1 Sponsored Genesis for HIVE_ALPHA & HIVE_BETA
    hive_a.bootstrap_sponsored_hive(
        book.sign(
            "HIVE_ALPHA",
            "queen_faculty_1",
            {
                "action": "BOOTSTRAP_HIVE",
                "hive_id": "HIVE_ALPHA",
                "queen_id": "queen_faculty_1",
                "seed_comb_amount": 1000.0,
                "queen_public_keys": {"queen_faculty_1": book.public_key("queen_faculty_1")},
                "certified_workers": {
                    "worker_senior_1": ["CS-101", "CALC-101"],
                    "pollinator_bee_1": ["PHYS-201"],
                },
                "worker_public_keys": {
                    "worker_senior_1": book.public_key("worker_senior_1"),
                    "pollinator_bee_1": book.public_key("pollinator_bee_1"),
                },
                "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                "timestamp": _epoch_timestamp(1),
            },
        )
    )
    hive_b.bootstrap_sponsored_hive(
        book.sign(
            "HIVE_BETA",
            "queen_faculty_beta",
            {
                "action": "BOOTSTRAP_HIVE",
                "hive_id": "HIVE_BETA",
                "queen_id": "queen_faculty_beta",
                "seed_comb_amount": 800.0,
                "queen_public_keys": {"queen_faculty_beta": book.public_key("queen_faculty_beta")},
                "certified_workers": {"worker_beta_1": ["CHEM-101"]},
                "worker_public_keys": {"worker_beta_1": book.public_key("worker_beta_1")},
                "nonce": book.next_nonce("HIVE_BETA", "queen_faculty_beta"),
                "timestamp": _epoch_timestamp(1),
            },
        )
    )

    # 2. Register Freshman Foragers, Finals Panickers, and Sybil Colluder Ring in HIVE_ALPHA
    for freshman_id in ["freshman_1", "freshman_2", "panicker_1"]:
        hive_a.register_bee(
            book.sign(
                "HIVE_ALPHA",
                freshman_id,
                {
                    "action": "REGISTER_BEE",
                    "hive_id": "HIVE_ALPHA",
                    "bee_id": freshman_id,
                    "role": BeeRole.LEARNER_BEE.value,
                    "nonce": book.next_nonce("HIVE_ALPHA", freshman_id),
                },
            )
        )
        hive_a.allocate_raw_pollen(
            book.sign(
                "HIVE_ALPHA",
                "queen_faculty_1",
                {
                    "action": "ALLOCATE_RAW_POLLEN",
                    "hive_id": "HIVE_ALPHA",
                    "queen_id": "queen_faculty_1",
                    "learner_id": freshman_id,
                    "amount": 25.0,
                    "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                },
            )
        )

    for sybil_id in ["sybil_roommate_a", "sybil_roommate_b"]:
        hive_a.register_bee(
            book.sign(
                "HIVE_ALPHA",
                sybil_id,
                {
                    "action": "REGISTER_BEE",
                    "hive_id": "HIVE_ALPHA",
                    "bee_id": sybil_id,
                    "role": BeeRole.LEARNER_BEE.value,
                    "nonce": book.next_nonce("HIVE_ALPHA", sybil_id),
                },
            )
        )
        hive_a.allocate_raw_pollen(
            book.sign(
                "HIVE_ALPHA",
                "queen_faculty_1",
                {
                    "action": "ALLOCATE_RAW_POLLEN",
                    "hive_id": "HIVE_ALPHA",
                    "queen_id": "queen_faculty_1",
                    "learner_id": sybil_id,
                    "amount": 10.0,
                    "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                },
            )
        )

    # 3. Epoch 1: Freshmen spend RAW_POLLEN with Certified Workers (Refining into LIQUID_NECTR!)
    _signed_handshake(
        book,
        hive_a,
        session_id="sess_e1_1",
        tutor_id="worker_senior_1",
        learner_id="freshman_1",
        subject_id="CS-101",
        duration_hours=1.5,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    _signed_handshake(
        book,
        hive_a,
        session_id="sess_e1_2",
        tutor_id="worker_senior_1",
        learner_id="freshman_2",
        subject_id="CALC-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    _signed_handshake(
        book,
        hive_a,
        session_id="sess_e1_3",
        tutor_id="pollinator_bee_1",
        learner_id="panicker_1",
        subject_id="PHYS-201",
        duration_hours=2.0,
        amount=15.0,
        token_state=TokenState.RAW_POLLEN,
    )
    # Seed sybil_roommate_a with liquid nectR by spending raw pollen legitimately once
    _signed_handshake(
        book,
        hive_a,
        session_id="sess_e1_sybil_seed",
        tutor_id="worker_senior_1",
        learner_id="sybil_roommate_a",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=10.0,
        token_state=TokenState.RAW_POLLEN,
    )
    # freshman_1 learns CS-101 and then teaches freshman_2 (Downstream Learn-then-Teach Lineage!)
    _signed_handshake(
        book,
        hive_a,
        session_id="sess_e1_lineage",
        tutor_id="freshman_1",
        learner_id="freshman_2",
        subject_id="CS-101",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="SPAN-101",
    )
    hive_a.mine_epoch_block(
        book.sign(
            "HIVE_ALPHA",
            "queen_faculty_1",
            {
                "action": "MINE_EPOCH_BLOCK",
                "hive_id": "HIVE_ALPHA",
                "queen_id": "queen_faculty_1",
                "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                "timestamp": _epoch_timestamp(2),
            },
        )
    )

    # 4. Epoch 2: Sybil Roommate Ring attempts wash-trading back and forth 6 times
    _signed_handshake(
        book,
        hive_a,
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
        _signed_handshake(
            book,
            hive_a,
            session_id=f"sess_sybil_wash_{i}",
            tutor_id=tutor,
            learner_id=learner,
            subject_id="WASH-101",
            duration_hours=1.0,
            amount=5.0,
            token_state=TokenState.LIQUID_NECTR,
        )
    hive_a.mine_epoch_block(
        book.sign(
            "HIVE_ALPHA",
            "queen_faculty_1",
            {
                "action": "MINE_EPOCH_BLOCK",
                "hive_id": "HIVE_ALPHA",
                "queen_id": "queen_faculty_1",
                "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                "timestamp": _epoch_timestamp(3),
            },
        )
    )

    # 5. Epoch 3: Drifting Pollinator migrates from HIVE_ALPHA to HIVE_BETA
    for b_learner in ["beta_student_1", "beta_student_2"]:
        hive_b.register_bee(
            book.sign(
                "HIVE_BETA",
                b_learner,
                {
                    "action": "REGISTER_BEE",
                    "hive_id": "HIVE_BETA",
                    "bee_id": b_learner,
                    "role": BeeRole.LEARNER_BEE.value,
                    "nonce": book.next_nonce("HIVE_BETA", b_learner),
                },
            )
        )
    hive_b.register_bee(
        book.sign(
            "HIVE_BETA",
            "pollinator_bee_1",
            {
                "action": "REGISTER_BEE",
                "hive_id": "HIVE_BETA",
                "bee_id": "pollinator_bee_1",
                "home_hive_id": "HIVE_ALPHA",
                "nonce": book.next_nonce("HIVE_BETA", "pollinator_bee_1"),
            },
        )
    )

    _signed_handshake(
        book,
        hive_b,
        session_id="sess_beta_1",
        tutor_id="pollinator_bee_1",
        learner_id="beta_student_1",
        subject_id="PHYS-201",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="BIO-101",
    )
    _signed_handshake(
        book,
        hive_b,
        session_id="sess_beta_2",
        tutor_id="pollinator_bee_1",
        learner_id="beta_student_2",
        subject_id="PHYS-201",
        duration_hours=1.0,
        amount=0.0,
        reciprocal_subject_id="CHEM-101",
    )
    hive_b.mine_epoch_block(
        book.sign(
            "HIVE_BETA",
            "queen_faculty_beta",
            {
                "action": "MINE_EPOCH_BLOCK",
                "hive_id": "HIVE_BETA",
                "queen_id": "queen_faculty_beta",
                "nonce": book.next_nonce("HIVE_BETA", "queen_faculty_beta"),
                "timestamp": _epoch_timestamp(2),
            },
        )
    )

    # Signed cross-hive bridge HIVE_ALPHA -> HIVE_BETA
    bridge_tx = hive_a.bridge_nectr_to_target_hive(
        book.sign(
            "HIVE_ALPHA",
            "pollinator_bee_1",
            {
                "action": "BRIDGE_NECTR",
                "hive_id": "HIVE_ALPHA",
                "bee_id": "pollinator_bee_1",
                "target_hive_id": "HIVE_BETA",
                "amount": 10.0,
                "nonce": book.next_nonce("HIVE_ALPHA", "pollinator_bee_1"),
            },
        ),
        hive_b,
    )
    hive_a.mine_epoch_block(
        book.sign(
            "HIVE_ALPHA",
            "queen_faculty_1",
            {
                "action": "MINE_EPOCH_BLOCK",
                "hive_id": "HIVE_ALPHA",
                "queen_id": "queen_faculty_1",
                "nonce": book.next_nonce("HIVE_ALPHA", "queen_faculty_1"),
                "timestamp": _epoch_timestamp(4),
            },
        )
    )

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
    return telemetry, {
        "hive_a_bridge_tx": bridge_tx,
        "hive_a_head_hash": hive_a.blockchain.chain[-1].block_hash,
        "hive_b_head_hash": hive_b.blockchain.chain[-1].block_hash,
    }
