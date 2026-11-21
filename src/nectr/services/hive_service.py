"""Hexagonal Hive Service Layer orchestrating contracts, PoUW-PoW mining, persistence, and telemetry."""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from nectr.chain.ledger import Block, HiveBlockchain, UsefulComputeProof, compute_sha256
from nectr.contracts.engine import (
    BeeAccount,
    BeeRole,
    HiveContractEngine,
    ServiceBarterSession,
    TokenState,
)
from nectr.services.ports import (
    HiveRepositoryPort,
    HiveSnapshot,
    InMemoryHiveRepository,
    NoOpTelemetry,
    TelemetryPort,
)


def compute_gini_coefficient(values: list[float]) -> float:
    """Compute the Gini coefficient of token wealth or effectiveness distribution in [0.0, 1.0]."""
    non_neg = sorted(v for v in values if v >= 0)
    n = len(non_neg)
    total = sum(non_neg)
    if n == 0 or total == 0:
        return 0.0
    weighted_sum = sum((i + 1) * val for i, val in enumerate(non_neg))
    return max(0.0, min(1.0, (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n))


class HiveServiceLayer:
    """Portfolio Service Layer connecting campus nodes, smart contracts, persistence, and PoUW-PoW chain."""

    def __init__(
        self,
        hive_id: str,
        difficulty: int = 2,
        accepted_status_peer_threshold: int = 3,
        repository: HiveRepositoryPort | None = None,
        telemetry: TelemetryPort | None = None,
    ) -> None:
        self.hive_id = hive_id
        self.repository: HiveRepositoryPort = (
            repository if repository is not None else InMemoryHiveRepository()
        )
        self.telemetry: TelemetryPort = telemetry if telemetry is not None else NoOpTelemetry()
        self.blockchain = HiveBlockchain(hive_id=hive_id, difficulty=difficulty)
        self.contracts = HiveContractEngine(
            hive_id=hive_id,
            accepted_status_peer_threshold=accepted_status_peer_threshold,
        )
        self.current_epoch: int = 0

        if repository is not None:
            self.repository.initialize()
            existing = self.repository.load_hive_snapshot(hive_id)
            if existing is not None:
                self._apply_snapshot(existing)

    @classmethod
    def from_repository(
        cls,
        hive_id: str,
        repository: HiveRepositoryPort,
        telemetry: TelemetryPort | None = None,
    ) -> HiveServiceLayer:
        """Hydrate an existing HiveServiceLayer strictly from persisted repository state."""
        repository.initialize()
        existing = repository.load_hive_snapshot(hive_id)
        if existing is None:
            raise KeyError(f"Hive '{hive_id}' not found in repository.")
        return cls(
            hive_id=hive_id,
            difficulty=existing.difficulty,
            accepted_status_peer_threshold=int(
                existing.contract_state["accepted_status_peer_threshold"]
            ),
            repository=repository,
            telemetry=telemetry,
        )

    def _apply_snapshot(self, snapshot: HiveSnapshot) -> None:
        self.contracts = HiveContractEngine.from_snapshot(snapshot.contract_state)
        self.current_epoch = snapshot.current_epoch
        self.blockchain = HiveBlockchain(hive_id=self.hive_id, difficulty=snapshot.difficulty)
        if snapshot.blocks:
            self.blockchain.chain = [Block.model_validate(b) for b in snapshot.blocks]
        self.blockchain.mempool = copy.deepcopy(snapshot.mempool)

    def _build_snapshot(self) -> HiveSnapshot:
        return HiveSnapshot(
            hive_id=self.hive_id,
            difficulty=self.blockchain.difficulty,
            current_epoch=self.current_epoch,
            contract_state=self.contracts.to_snapshot(),
            blocks=[b.model_dump(mode="json") for b in self.blockchain.chain],
            mempool=copy.deepcopy(self.blockchain.mempool),
        )

    @contextmanager
    def _atomic_mutation(
        self,
        op_name: str,
        *,
        tx_id: str | None = None,
    ) -> Iterator[None]:
        """Execute a mutating operation atomically across both DB and in-memory state."""
        contract_backup = self.contracts.to_snapshot()
        epoch_backup = self.current_epoch
        chain_len = len(self.blockchain.chain)
        mempool_backup = copy.deepcopy(self.blockchain.mempool)

        with (
            self.telemetry.span(
                op_name,
                hive_id=self.hive_id,
                epoch=self.current_epoch,
                tx_id=tx_id,
            ),
            self.repository.transaction(),
        ):
            try:
                yield
                self.repository.save_hive_snapshot(self._build_snapshot())
            except BaseException as exc:
                self.contracts = HiveContractEngine.from_snapshot(
                    contract_backup,
                    verify_invariants=False,
                )
                self.current_epoch = epoch_backup
                del self.blockchain.chain[chain_len:]
                self.blockchain.mempool[:] = mempool_backup
                self.telemetry.record_event(
                    f"{op_name}.rollback",
                    hive_id=self.hive_id,
                    epoch=self.current_epoch,
                    tx_id=tx_id,
                    error_type=type(exc).__name__,
                )
                raise
        self.telemetry.record_event(
            op_name,
            hive_id=self.hive_id,
            epoch=self.current_epoch,
            tx_id=tx_id,
            comb_reserve=self.contracts.comb_reserve,
        )

    def register_bee(
        self,
        bee_id: str,
        role: BeeRole = BeeRole.LEARNER_BEE,
        home_hive_id: str | None = None,
    ) -> BeeAccount:
        """Atomically register a Bee account and persist snapshot."""
        with self._atomic_mutation("register_bee", tx_id=bee_id):
            return self.contracts.register_bee(
                bee_id=bee_id,
                role=role,
                home_hive_id=home_hive_id,
            )

    def allocate_raw_pollen(
        self,
        queen_id: str,
        learner_id: str,
        amount: float,
    ) -> dict[str, Any]:
        """Atomically allocate RAW_POLLEN from the Comb to a Learner Bee."""
        with self._atomic_mutation("allocate_raw_pollen", tx_id=learner_id):
            tx = self.contracts.allocate_raw_pollen_to_learner(
                queen_id=queen_id,
                learner_id=learner_id,
                amount=amount,
            )
            self.blockchain.submit_transaction(tx)
            return tx

    def certify_worker_bee(
        self,
        queen_id: str,
        worker_id: str,
        subject_id: str,
        certification_fee: float = 0.0,
    ) -> dict[str, Any]:
        """Atomically certify a Worker Bee in a subject."""
        with self._atomic_mutation("certify_worker_bee", tx_id=worker_id):
            tx = self.contracts.certify_worker_bee(
                queen_id=queen_id,
                worker_id=worker_id,
                subject_id=subject_id,
                certification_fee=certification_fee,
            )
            self.blockchain.submit_transaction(tx)
            return tx

    def create_barter_escrow(
        self,
        session_id: str,
        tutor_id: str,
        learner_id: str,
        subject_id: str,
        duration_hours: float,
        amount: float,
        token_state: TokenState = TokenState.LIQUID_NECTR,
        reciprocal_subject_id: str | None = None,
    ) -> ServiceBarterSession:
        """Atomically create a DirectionalServiceBarterContract escrow session."""
        with self._atomic_mutation("create_barter_escrow", tx_id=session_id):
            return self.contracts.create_service_barter_escrow(
                session_id=session_id,
                tutor_id=tutor_id,
                learner_id=learner_id,
                subject_id=subject_id,
                duration_hours=duration_hours,
                amount=amount,
                token_state=token_state,
                reciprocal_subject_id=reciprocal_subject_id,
            )

    def settle_session(
        self,
        session_id: str,
        learner_attestation_score: float,
        tutor_comprehension_hash: str,
    ) -> dict[str, Any]:
        """Atomically settle an escrowed tutoring session and queue for PoUW-PoW block."""
        with self._atomic_mutation("settle_session", tx_id=session_id):
            tx = self.contracts.settle_co_signed_session(
                session_id=session_id,
                learner_attestation_score=learner_attestation_score,
                tutor_comprehension_hash=tutor_comprehension_hash,
            )
            self.blockchain.submit_transaction(tx)
            return tx

    def resolve_disputed_session(
        self,
        queen_id: str,
        session_id: str,
        tutor_share_ratio: float,
        service_fee_rate: float = 0.10,
    ) -> dict[str, Any]:
        """Atomically arbitrate a disputed session and route fees to Comb."""
        with self._atomic_mutation("resolve_disputed_session", tx_id=session_id):
            tx = self.contracts.resolve_disputed_session(
                queen_id=queen_id,
                session_id=session_id,
                tutor_share_ratio=tutor_share_ratio,
                service_fee_rate=service_fee_rate,
            )
            self.blockchain.submit_transaction(tx)
            return tx

    def bootstrap_sponsored_hive(
        self,
        seed_comb_amount: float,
        queen_ids: list[str],
        certified_workers: dict[str, list[str]],
    ) -> dict[str, Any]:
        """Phase 1 Genesis: Inject Seed Comb, appoint Teacher-Queens, and certify seed Worker Bees."""
        with self._atomic_mutation("bootstrap_sponsored_hive"):
            seed_tx = self.contracts.inject_sponsored_seed_comb(seed_comb_amount)
            self.blockchain.submit_transaction(seed_tx)

            for q_id in queen_ids:
                self.contracts.register_bee(q_id, role=BeeRole.QUEEN)

            lead_queen = queen_ids[0]
            for worker_id, subjects in certified_workers.items():
                self.contracts.register_bee(worker_id, role=BeeRole.LEARNER_BEE)
                for subj in subjects:
                    tx = self.contracts.certify_worker_bee(
                        queen_id=lead_queen,
                        worker_id=worker_id,
                        subject_id=subj,
                        certification_fee=0.0,
                    )
                    self.blockchain.submit_transaction(tx)

            block = self.mine_epoch_block()
            return {
                "hive_id": self.hive_id,
                "genesis_comb": self.contracts.comb_reserve,
                "queens": queen_ids,
                "certified_workers": list(certified_workers.keys()),
                "block_height": block.header.height,
                "block_hash": block.block_hash,
            }

    def execute_tutoring_handshake(
        self,
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
        """Execute a complete 2-way signed tutoring session atomically and queue for block inclusion."""
        with self._atomic_mutation("execute_tutoring_handshake", tx_id=session_id):
            self.contracts.create_service_barter_escrow(
                session_id=session_id,
                tutor_id=tutor_id,
                learner_id=learner_id,
                subject_id=subject_id,
                duration_hours=duration_hours,
                amount=amount,
                token_state=token_state,
                reciprocal_subject_id=reciprocal_subject_id,
            )
            comp_hash = compute_sha256(f"{session_id}:{tutor_id}:{learner_id}:{subject_id}")
            tx = self.contracts.settle_co_signed_session(
                session_id=session_id,
                learner_attestation_score=learner_attestation_score,
                tutor_comprehension_hash=comp_hash,
            )
            self.blockchain.submit_transaction(tx)
            return tx

    def compute_useful_work_proof(self) -> UsefulComputeProof:
        """Compute the PoUW Knowledge Graph, Collusion-Discounted Velocity, and Gini metrics."""
        non_queen_balances = [
            a.liquid_nectr_balance + a.raw_pollen_balance
            for a in self.contracts.accounts.values()
            if a.role != BeeRole.QUEEN
        ]
        gini = compute_gini_coefficient(non_queen_balances)
        velocity = sum(
            tx["amount"] * tx["effective_weight"] for tx in self.contracts.settled_tx_log
        )
        graph_snapshot = {
            "hive_id": self.hive_id,
            "epoch": self.current_epoch,
            "tutor_effectiveness": {
                k: round(v, 4) for k, v in sorted(self.contracts.tutor_effectiveness.items())
            },
            "comb_reserve": round(self.contracts.comb_reserve, 4),
        }
        return UsefulComputeProof(
            epoch=self.current_epoch,
            active_bees=len(self.contracts.accounts),
            total_directional_edges=len(self.contracts.settled_tx_log),
            collusion_discounted_velocity=round(velocity, 4),
            gini_coefficient=round(gini, 4),
            graph_state_hash=compute_sha256(json.dumps(graph_snapshot, sort_keys=True)),
        )

    def mine_epoch_block(self, queen_dividend_beta: float = 0.05) -> Block:
        """Mine a PoUW-PoW block and persist Queen Royal Jelly governance health credits."""
        with self._atomic_mutation("mine_epoch_block"):
            self.current_epoch += 1
            proof = self.compute_useful_work_proof()

            for acct in self.contracts.accounts.values():
                if acct.role == BeeRole.QUEEN:
                    acct.royal_jelly_earned = round(
                        queen_dividend_beta
                        * proof.collusion_discounted_velocity
                        * (1.0 - proof.gini_coefficient),
                        4,
                    )

            return self.blockchain.mine_block(useful_compute_proof=proof)
