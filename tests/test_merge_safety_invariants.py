"""Adversarial chain/contract boundary tests and Hypothesis stateful property-based invariants."""

from __future__ import annotations

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from nectr.chain.ledger import (
    Block,
    BlockHeader,
    HiveBlockchain,
    UsefulComputeProof,
    compute_merkle_root,
    compute_sha256,
)
from nectr.contracts.engine import (
    BeeRole,
    ContractViolationError,
    HiveContractEngine,
    TokenState,
)
from nectr.services.hive_service import HiveServiceLayer, compute_gini_coefficient


def test_blockchain_merkle_and_all_four_tamper_detection_paths() -> None:
    """Verify empty/odd/even Merkle roots and all 4 PoUW-PoW tamper rejection checks."""
    empty_root = compute_merkle_root([])
    one_root = compute_merkle_root([{"tx": 1}])
    two_root = compute_merkle_root([{"tx": 1}, {"tx": 2}])
    two_reordered = compute_merkle_root([{"tx": 2}, {"tx": 1}])
    three_root = compute_merkle_root([{"tx": 1}, {"tx": 2}, {"tx": 3}])

    assert len({empty_root, one_root, two_root, two_reordered, three_root}) == 5

    chain = HiveBlockchain(hive_id="HIVE_SEC", difficulty=1)
    proof = UsefulComputeProof(
        epoch=1,
        active_bees=2,
        total_directional_edges=1,
        collusion_discounted_velocity=10.0,
        gini_coefficient=0.2,
        graph_state_hash=compute_sha256("epoch-1"),
    )
    chain.submit_transaction({"session_id": "s1", "amount": 10.0})
    mined = chain.mine_block(proof, timestamp=1700000100.0)
    assert chain.verify_chain() is True

    # 1. Forged header failing PoW difficulty prefix
    bad_pow_chain = HiveBlockchain(hive_id="HIVE_SEC", difficulty=4)
    bad_pow_chain.chain.append(mined)
    assert bad_pow_chain.verify_chain() is False

    # 2. Mutated transaction list invalidating Merkle root
    tampered_tx_chain = HiveBlockchain(hive_id="HIVE_SEC", difficulty=1)
    tampered_tx_chain.submit_transaction({"session_id": "s1", "amount": 10.0})
    blk_tx = tampered_tx_chain.mine_block(proof, timestamp=1700000100.0)
    blk_tx.transactions.append({"injected": True})
    assert tampered_tx_chain.verify_chain() is False

    # 3. Swapped UsefulComputeProof invalidating knowledge_graph_root
    tampered_kg_chain = HiveBlockchain(hive_id="HIVE_SEC", difficulty=1)
    tampered_kg_chain.submit_transaction({"session_id": "s1", "amount": 10.0})
    blk_kg = tampered_kg_chain.mine_block(proof, timestamp=1700000100.0)
    forged_proof = UsefulComputeProof(
        epoch=99,
        active_bees=99,
        total_directional_edges=99,
        collusion_discounted_velocity=999.0,
        gini_coefficient=0.0,
        graph_state_hash=compute_sha256("forged"),
    )
    tampered_kg_chain.chain[-1] = Block(
        header=blk_kg.header,
        useful_compute_proof=forged_proof,
        transactions=blk_kg.transactions,
    )
    assert tampered_kg_chain.verify_chain() is False

    # 4. Broken prev_hash link between block 0 and block 1
    broken_link_chain = HiveBlockchain(hive_id="HIVE_SEC", difficulty=1)
    unlinked_header = broken_link_chain._mine_header(
        height=1,
        prev_hash="f" * 64,
        merkle_root=compute_merkle_root([]),
        knowledge_graph_root=proof.to_commitment_hash(),
        timestamp=1700000200.0,
    )
    assert isinstance(unlinked_header, BlockHeader)
    broken_link_chain.chain.append(
        Block(header=unlinked_header, useful_compute_proof=proof, transactions=[])
    )
    assert broken_link_chain.verify_chain() is False


def test_contract_engine_adversarial_and_boundary_guards() -> None:
    """Exercise every smart contract invariant guard and supply conservation check."""
    engine = HiveContractEngine(hive_id="HIVE_GUARD", accepted_status_peer_threshold=2)

    with pytest.raises(ContractViolationError, match="Seed Comb injection must be positive"):
        engine.inject_sponsored_seed_comb(0.0)

    engine.inject_sponsored_seed_comb(100.0)
    q = engine.register_bee("queen_1", role=BeeRole.QUEEN)
    # Idempotent registration returns existing account
    assert engine.register_bee("queen_1", role=BeeRole.LEARNER_BEE) is q

    w = engine.register_bee("worker_1", role=BeeRole.LEARNER_BEE)
    l1 = engine.register_bee("learner_1", role=BeeRole.LEARNER_BEE)

    with pytest.raises(ContractViolationError, match="not registered"):
        engine.allocate_raw_pollen_to_learner("queen_1", "ghost", 5.0)

    with pytest.raises(ContractViolationError, match="does not hold QUEEN role"):
        engine.allocate_raw_pollen_to_learner("learner_1", "worker_1", 5.0)

    with pytest.raises(ContractViolationError, match="Queens cannot receive RAW_POLLEN"):
        engine.allocate_raw_pollen_to_learner("queen_1", "queen_1", 5.0)

    with pytest.raises(ContractViolationError, match="Insufficient Comb reserve"):
        engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 500.0)

    with pytest.raises(ContractViolationError, match="Queens cannot be certified"):
        engine.certify_worker_bee("queen_1", "queen_1", "CS-101")

    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR for certification"):
        engine.certify_worker_bee("queen_1", "worker_1", "CS-101", certification_fee=5.0)

    engine.certify_worker_bee("queen_1", "worker_1", "CS-101", certification_fee=0.0)
    engine.allocate_raw_pollen_to_learner("queen_1", "learner_1", 30.0)

    # Settle one valid session so worker_1 earns LIQUID_NECTR, then pay certification fee -> Comb
    engine.create_service_barter_escrow(
        "s_seed", "worker_1", "learner_1", "CS-101", 1.0, 15.0, TokenState.RAW_POLLEN
    )
    engine.settle_co_signed_session("s_seed", 0.9, "hash_seed")
    cert_tx = engine.certify_worker_bee("queen_1", "worker_1", "MATH-201", certification_fee=5.0)
    assert cert_tx["fee_to_comb"] == 5.0
    assert w.liquid_nectr_balance == 10.0

    # Escrow rejections
    with pytest.raises(ContractViolationError, match="Self-tutoring is prohibited"):
        engine.create_service_barter_escrow("s_self", "worker_1", "worker_1", "CS-101", 1.0, 1.0)

    with pytest.raises(ContractViolationError, match="Escrow amount cannot be negative"):
        engine.create_service_barter_escrow("s_neg", "worker_1", "learner_1", "CS-101", 1.0, -1.0)

    with pytest.raises(ContractViolationError, match="reciprocal_subject_id"):
        engine.create_service_barter_escrow("s_zero", "worker_1", "learner_1", "CS-101", 1.0, 0.0)

    with pytest.raises(ContractViolationError, match="Insufficient RAW_POLLEN"):
        engine.create_service_barter_escrow(
            "s_pollen_over", "worker_1", "learner_1", "CS-101", 1.0, 999.0, TokenState.RAW_POLLEN
        )

    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR"):
        engine.create_service_barter_escrow(
            "s_liq_over", "learner_1", "worker_1", "CS-101", 1.0, 999.0, TokenState.LIQUID_NECTR
        )

    with pytest.raises(ContractViolationError, match="Invalid token state"):
        engine.create_service_barter_escrow(
            "s_comb_state",
            "worker_1",
            "learner_1",
            "CS-101",
            1.0,
            1.0,
            TokenState.ROYAL_COMB_RESERVE,
        )

    # Settlement & replay rejections
    with pytest.raises(ContractViolationError, match="does not exist"):
        engine.settle_co_signed_session("missing_sess", 0.8, "h")

    with pytest.raises(ContractViolationError, match="not in INTENT_ESCROWED"):
        engine.settle_co_signed_session("s_seed", 0.8, "h")

    engine.create_service_barter_escrow(
        "s_liq_dispute", "learner_1", "worker_1", "ART-101", 1.0, 10.0, TokenState.LIQUID_NECTR
    )
    with pytest.raises(ContractViolationError, match="Attestation score must be in"):
        engine.settle_co_signed_session("s_liq_dispute", 1.5, "bad_score")

    # Dispute rejections + LIQUID_NECTR refund path
    with pytest.raises(ContractViolationError, match="Only escrowed sessions can be arbitrated"):
        engine.resolve_disputed_session("queen_1", "s_seed", 0.5)

    with pytest.raises(ContractViolationError, match="tutor_share_ratio must be between 0 and 1"):
        engine.resolve_disputed_session("queen_1", "s_liq_dispute", -0.1)

    dispute_res = engine.resolve_disputed_session("queen_1", "s_liq_dispute", 0.5, 0.10)
    assert dispute_res["learner_refund"] == 4.5
    assert w.liquid_nectr_balance == 4.5
    assert l1.liquid_nectr_balance == 4.5

    # Cross-Hive bridge rejections
    target = HiveContractEngine(hive_id="HIVE_TARGET", accepted_status_peer_threshold=1)
    target.inject_sponsored_seed_comb(50.0)

    with pytest.raises(ContractViolationError, match="Queens are bound to their Hive"):
        engine.bridge_nectr_to_target_hive("queen_1", target, 1.0)

    with pytest.raises(ContractViolationError, match="Insufficient LIQUID_NECTR in origin Hive"):
        engine.bridge_nectr_to_target_hive("worker_1", target, 0.0)

    with pytest.raises(ContractViolationError, match="Guard Bee Rejection"):
        engine.bridge_nectr_to_target_hive("worker_1", target, 2.0)

    # Supply conservation tamper detection
    w.liquid_nectr_balance += 1000.0
    with pytest.raises(ContractViolationError, match="Supply conservation invariant violated"):
        engine.assert_supply_conservation()


def test_gini_coefficient_boundary_cases() -> None:
    assert compute_gini_coefficient([]) == 0.0
    assert compute_gini_coefficient([0.0, 0.0, 0.0]) == 0.0
    assert compute_gini_coefficient([-5.0]) == 0.0
    assert compute_gini_coefficient([10.0, 10.0, 10.0]) == 0.0
    skewed = compute_gini_coefficient([0.0, 0.0, 0.0, 100.0])
    assert 0.70 <= skewed <= 1.0


class HiveEconomyStateMachine(RuleBasedStateMachine):
    """Stateful Hypothesis fuzzer verifying protocol invariants across randomized multi-hive operations."""

    def __init__(self) -> None:
        super().__init__()
        self.hive_a = HiveServiceLayer(
            hive_id="FUZZ_A", difficulty=1, accepted_status_peer_threshold=2
        )
        self.hive_b = HiveServiceLayer(
            hive_id="FUZZ_B", difficulty=1, accepted_status_peer_threshold=1
        )
        self.seq = 0
        self.bridged_bees: set[str] = set()

    @initialize()
    def bootstrap_hives(self) -> None:
        self.hive_a.bootstrap_sponsored_hive(
            seed_comb_amount=500.0,
            queen_ids=["queen_a"],
            certified_workers={"worker_1": ["CS-101"], "worker_2": ["MATH-101"]},
        )
        self.hive_b.bootstrap_sponsored_hive(
            seed_comb_amount=300.0,
            queen_ids=["queen_b"],
            certified_workers={"worker_b": ["BIO-101"]},
        )
        for lid in ("learner_1", "learner_2", "learner_3"):
            self.hive_a.contracts.register_bee(lid, role=BeeRole.LEARNER_BEE)
            self.hive_b.contracts.register_bee(lid, role=BeeRole.LEARNER_BEE)

    @rule(
        learner=st.sampled_from(["learner_1", "learner_2", "learner_3"]),
        amount=st.floats(min_value=1.0, max_value=25.0, allow_nan=False, allow_infinity=False),
    )
    def allocate_pollen(self, learner: str, amount: float) -> None:
        rounded = round(amount, 2)
        if rounded <= self.hive_a.contracts.comb_reserve:
            self.hive_a.contracts.allocate_raw_pollen_to_learner("queen_a", learner, rounded)

    @rule(
        worker=st.sampled_from(["worker_1", "worker_2"]),
        learner=st.sampled_from(["learner_1", "learner_2", "learner_3"]),
        amount=st.floats(min_value=1.0, max_value=15.0, allow_nan=False, allow_infinity=False),
        score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    )
    def settle_pollen_session(self, worker: str, learner: str, amount: float, score: float) -> None:
        rounded = round(amount, 2)
        subj = "CS-101" if worker == "worker_1" else "MATH-101"
        acct = self.hive_a.contracts.accounts[learner]
        if acct.raw_pollen_balance >= rounded:
            self.seq += 1
            self.hive_a.execute_tutoring_handshake(
                session_id=f"fuzz_p_{self.seq}",
                tutor_id=worker,
                learner_id=learner,
                subject_id=subj,
                duration_hours=1.0,
                amount=rounded,
                token_state=TokenState.RAW_POLLEN,
                learner_attestation_score=round(score, 2),
            )

    @rule(
        tutor=st.sampled_from(["worker_1", "worker_2", "learner_1"]),
        learner=st.sampled_from(["worker_1", "worker_2", "learner_2"]),
        amount=st.floats(min_value=0.5, max_value=10.0, allow_nan=False, allow_infinity=False),
        disputed=st.booleans(),
        share=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    )
    def liquid_barter_or_dispute(
        self,
        tutor: str,
        learner: str,
        amount: float,
        disputed: bool,
        share: float,
    ) -> None:
        if tutor == learner:
            return
        rounded = round(amount, 2)
        learner_acct = self.hive_a.contracts.accounts[learner]
        if learner_acct.liquid_nectr_balance < rounded:
            return
        self.seq += 1
        sid = f"fuzz_l_{self.seq}"
        self.hive_a.contracts.create_service_barter_escrow(
            session_id=sid,
            tutor_id=tutor,
            learner_id=learner,
            subject_id="PEER-101",
            duration_hours=1.0,
            amount=rounded,
            token_state=TokenState.LIQUID_NECTR,
        )
        if disputed:
            self.hive_a.contracts.resolve_disputed_session("queen_a", sid, round(share, 2))
        else:
            self.hive_a.contracts.settle_co_signed_session(sid, 0.9, f"hash_{sid}")

    @rule(worker=st.sampled_from(["worker_1", "worker_2"]))
    def earn_acceptance_and_bridge(self, worker: str) -> None:
        self.hive_b.contracts.register_bee(worker, home_hive_id="FUZZ_A")
        self.seq += 1
        self.hive_b.execute_tutoring_handshake(
            session_id=f"fuzz_b_{self.seq}",
            tutor_id=worker,
            learner_id="learner_1",
            subject_id="CS-101",
            duration_hours=1.0,
            amount=0.0,
            reciprocal_subject_id="BIO-101",
            learner_attestation_score=0.95,
        )
        src_acct = self.hive_a.contracts.accounts[worker]
        if src_acct.liquid_nectr_balance >= 2.0:
            self.hive_a.contracts.bridge_nectr_to_target_hive(
                bee_id=worker,
                target_hive=self.hive_b.contracts,
                amount=2.0,
            )
            self.bridged_bees.add(worker)

    @rule()
    def mine_epoch(self) -> None:
        self.hive_a.mine_epoch_block()
        self.hive_b.mine_epoch_block()

    @invariant()
    def all_protocol_invariants_hold(self) -> None:
        # 1. Exact supply conservation in both Hives
        self.hive_a.contracts.assert_supply_conservation()
        self.hive_b.contracts.assert_supply_conservation()

        # 2. Non-negative balances & Queen zero-currency separation of powers
        for hive in (self.hive_a, self.hive_b):
            assert hive.contracts.comb_reserve >= 0.0
            for acct in hive.contracts.accounts.values():
                assert acct.raw_pollen_balance >= -1e-9
                assert acct.liquid_nectr_balance >= -1e-9
                if acct.role == BeeRole.QUEEN:
                    assert acct.raw_pollen_balance == 0.0
                    assert acct.liquid_nectr_balance == 0.0
            for tx in hive.contracts.settled_tx_log:
                assert hive.contracts.accounts[tx["tutor_id"]].role != BeeRole.QUEEN

        # 3. Guard Bee Acceptance prerequisite for any bridged Bee
        for bee_id in self.bridged_bees:
            assert "FUZZ_B" in self.hive_b.contracts.accounts[bee_id].accepted_in_hives

        # 4. PoUW-PoW cryptographic chain integrity & bounded Gini
        assert self.hive_a.blockchain.verify_chain() is True
        assert self.hive_b.blockchain.verify_chain() is True
        proof_a = self.hive_a.compute_useful_work_proof()
        assert 0.0 <= proof_a.gini_coefficient <= 1.0


TestHiveEconomyStateful = HiveEconomyStateMachine.TestCase
TestHiveEconomyStateful.settings = settings(max_examples=35, stateful_step_count=20, deadline=None)
