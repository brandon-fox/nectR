"""Hexagonal Hive Service Layer orchestrating contracts, PoUW-PoW mining, persistence, and telemetry."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from pydantic import BaseModel

from nectr.chain.crypto import (
    CanonicalPayload,
    Ed25519Verifier,
    SignedTransaction,
    compute_sha256,
)
from nectr.chain.ledger import Block, HiveBlockchain, UsefulComputeProof
from nectr.contracts.engine import (
    BeeAccount,
    BeeRole,
    ContractViolationError,
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


class InvalidSignatureError(PermissionError):
    """Raised when a SignedTransaction fails cryptographic or key-registry verification (HTTP 401)."""


class CommandAuthorizationError(PermissionError):
    """Raised when an authenticated signer lacks actor or role authority for a command (HTTP 403)."""


def _serialize_tx_entry(entry: object) -> dict[str, Any]:
    """Normalize a SignedTransaction (or Mapping in unit helpers) to a JSON-safe dict."""
    if isinstance(entry, BaseModel):
        return entry.model_dump(mode="json")
    if isinstance(entry, Mapping):
        return copy.deepcopy(dict(entry))
    raise TypeError(f"Unsupported transaction entry type: {type(entry).__name__}")


def _deserialize_mempool_entry(item: Mapping[str, Any]) -> SignedTransaction:
    """Rehydrate a serialized mempool entry strictly into a SignedTransaction."""
    return SignedTransaction.model_validate(item)


def _require_valid_signed_tx(tx: object) -> tuple[SignedTransaction, str]:
    if not isinstance(tx, SignedTransaction):
        raise InvalidSignatureError("Command must be a SignedTransaction.")
    if not tx.verify_signature():
        raise InvalidSignatureError("Invalid Ed25519 signature on SignedTransaction.")
    if not isinstance(tx.signer_id, str) or not tx.signer_id.strip():
        raise InvalidSignatureError("SignedTransaction must include a non-empty signer_id.")
    return tx, tx.signer_id


def _require_positive_int_nonce(value: Any, label: str = "nonce") -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractViolationError(f"{label} must be a positive integer.")
    return value


def _validate_public_key_hex(public_key: object, bee_id: str) -> str:
    if not isinstance(public_key, str):
        raise ContractViolationError(f"Public key for '{bee_id}' must be a 64-char hex string.")
    try:
        verifier = Ed25519Verifier.from_public_hex(public_key)
    except (ValueError, TypeError) as exc:
        raise ContractViolationError(f"Invalid Ed25519 public key for '{bee_id}': {exc}") from exc
    return verifier.public_key_hex


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
        self.bee_public_keys: dict[str, str] = {}
        self.bee_nonces: dict[str, int] = {}

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
        self.bee_public_keys = dict(snapshot.bee_public_keys)
        self.bee_nonces = dict(snapshot.bee_nonces)
        self.blockchain = HiveBlockchain(hive_id=self.hive_id, difficulty=snapshot.difficulty)
        if snapshot.blocks:
            self.blockchain.chain = [Block.model_validate(b) for b in snapshot.blocks]
        self.blockchain.mempool.clear()
        self.blockchain.mempool.extend(
            _deserialize_mempool_entry(item) for item in snapshot.mempool
        )

    def _build_snapshot(self) -> HiveSnapshot:
        return HiveSnapshot(
            hive_id=self.hive_id,
            difficulty=self.blockchain.difficulty,
            current_epoch=self.current_epoch,
            contract_state=self.contracts.to_snapshot(),
            blocks=[b.model_dump(mode="json") for b in self.blockchain.chain],
            mempool=[_serialize_tx_entry(entry) for entry in self.blockchain.mempool],
            bee_public_keys=dict(self.bee_public_keys),
            bee_nonces=dict(self.bee_nonces),
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
        keys_backup = dict(self.bee_public_keys)
        nonces_backup = dict(self.bee_nonces)
        chain_len = len(self.blockchain.chain)
        mempool_backup = copy.deepcopy(self.blockchain.mempool)

        with self.telemetry.span(
            op_name,
            hive_id=self.hive_id,
            epoch=self.current_epoch,
            tx_id=tx_id,
        ):
            try:
                with self.repository.transaction():
                    yield
                    self.repository.save_hive_snapshot(self._build_snapshot())
            except BaseException as exc:
                self.contracts = HiveContractEngine.from_snapshot(
                    contract_backup,
                    verify_invariants=False,
                )
                self.current_epoch = epoch_backup
                self.bee_public_keys = keys_backup
                self.bee_nonces = nonces_backup
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

    def _verify_signed_command(
        self,
        signed_tx: SignedTransaction,
        *,
        expected_action: str,
        actor_id: str,
        require_queen: bool = False,
        allow_unregistered: bool = False,
    ) -> tuple[str, int]:
        tx, signer_id = _require_valid_signed_tx(signed_tx)
        payload = tx.payload

        if payload.get("action") != expected_action:
            raise ContractViolationError(
                f"Expected action '{expected_action}', got '{payload.get('action')}'."
            )
        if payload.get("hive_id") != self.hive_id:
            raise ContractViolationError(
                f"SignedTransaction hive_id '{payload.get('hive_id')}' does not match '{self.hive_id}'."
            )
        nonce = _require_positive_int_nonce(payload.get("nonce"))

        registered_pk = self.bee_public_keys.get(signer_id)
        if registered_pk is not None:
            if registered_pk != tx.signer_public_key:
                raise InvalidSignatureError(
                    f"Signer public key does not match registered key for '{signer_id}'."
                )
        elif not allow_unregistered:
            raise InvalidSignatureError(
                f"Signer '{signer_id}' has no registered public key in Hive '{self.hive_id}'."
            )

        if signer_id != actor_id:
            raise CommandAuthorizationError(
                f"Signer '{signer_id}' is not authorized to act as '{actor_id}'."
            )

        if require_queen:
            acct = self.contracts.accounts.get(signer_id)
            if acct is None:
                raise InvalidSignatureError(f"Signer '{signer_id}' is not registered.")
            if acct.role != BeeRole.QUEEN:
                raise CommandAuthorizationError(f"Account '{signer_id}' does not hold QUEEN role.")

        last_nonce = self.bee_nonces.get(signer_id, 0)
        if nonce <= last_nonce:
            raise ContractViolationError(
                f"Replayed or stale nonce {nonce} for '{signer_id}' (last accepted={last_nonce})."
            )
        return signer_id, nonce

    def register_bee(self, signed_tx: SignedTransaction) -> BeeAccount:
        """Atomically register a LEARNER_BEE account via self-signed SignedTransaction."""
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        bee_id = payload.get("bee_id")
        if not isinstance(bee_id, str) or not bee_id.strip():
            raise ContractViolationError("REGISTER_BEE payload must include a non-empty bee_id.")

        _, nonce = self._verify_signed_command(
            tx,
            expected_action="REGISTER_BEE",
            actor_id=bee_id,
            allow_unregistered=True,
        )
        raw_role = payload.get("role", BeeRole.LEARNER_BEE.value)
        try:
            requested_role = BeeRole(str(raw_role))
        except ValueError as exc:
            raise ContractViolationError(f"Invalid role '{raw_role}'.") from exc
        if requested_role != BeeRole.LEARNER_BEE:
            raise CommandAuthorizationError(
                "QUEEN and privileged roles cannot be self-assigned; "
                "self-signed register_bee only creates LEARNER_BEE."
            )

        home_hive_raw = payload.get("home_hive_id")
        home_hive_id = None if home_hive_raw is None else str(home_hive_raw)

        with self._atomic_mutation("register_bee", tx_id=bee_id):
            self.bee_public_keys[bee_id] = tx.signer_public_key
            self.bee_nonces[bee_id] = nonce
            acct = self.contracts.register_bee(
                bee_id=bee_id,
                role=BeeRole.LEARNER_BEE,
                home_hive_id=home_hive_id,
            )
            self.blockchain.submit_transaction(tx)
            return acct

    def allocate_raw_pollen(self, signed_tx: SignedTransaction) -> dict[str, Any]:
        """Atomically allocate RAW_POLLEN from the Comb to a Learner Bee."""
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        queen_id = str(payload.get("queen_id", ""))
        learner_id = str(payload.get("learner_id", ""))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="ALLOCATE_RAW_POLLEN",
            actor_id=queen_id,
            require_queen=True,
        )
        amount = float(payload["amount"])

        with self._atomic_mutation("allocate_raw_pollen", tx_id=learner_id):
            self.bee_nonces[queen_id] = nonce
            result = self.contracts.allocate_raw_pollen_to_learner(
                queen_id=queen_id,
                learner_id=learner_id,
                amount=amount,
            )
            self.blockchain.submit_transaction(tx)
            return result

    def certify_worker_bee(self, signed_tx: SignedTransaction) -> dict[str, Any]:
        """Atomically certify a Worker Bee in a subject."""
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        queen_id = str(payload.get("queen_id", ""))
        worker_id = str(payload.get("worker_id", ""))
        subject_id = str(payload.get("subject_id", ""))
        certification_fee = float(payload.get("certification_fee", 0.0))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="CERTIFY_WORKER_BEE",
            actor_id=queen_id,
            require_queen=True,
        )

        with self._atomic_mutation("certify_worker_bee", tx_id=worker_id):
            self.bee_nonces[queen_id] = nonce
            result = self.contracts.certify_worker_bee(
                queen_id=queen_id,
                worker_id=worker_id,
                subject_id=subject_id,
                certification_fee=certification_fee,
            )
            self.blockchain.submit_transaction(tx)
            return result

    def _apply_signed_escrow(self, signed_tx: SignedTransaction) -> ServiceBarterSession:
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        learner_id = str(payload.get("learner_id", ""))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="CREATE_BARTER_ESCROW",
            actor_id=learner_id,
        )
        session_id = str(payload["session_id"])
        tutor_id = str(payload["tutor_id"])
        subject_id = str(payload["subject_id"])
        duration_hours = float(payload["duration_hours"])
        amount = float(payload["amount"])
        token_state = TokenState(str(payload.get("token_state", TokenState.LIQUID_NECTR.value)))
        recip_raw = payload.get("reciprocal_subject_id")
        reciprocal_subject_id = None if recip_raw is None else str(recip_raw)

        self.bee_nonces[learner_id] = nonce
        session = self.contracts.create_service_barter_escrow(
            session_id=session_id,
            tutor_id=tutor_id,
            learner_id=learner_id,
            subject_id=subject_id,
            duration_hours=duration_hours,
            amount=amount,
            token_state=token_state,
            reciprocal_subject_id=reciprocal_subject_id,
        )
        self.blockchain.submit_transaction(tx)
        return session

    def create_barter_escrow(self, signed_tx: SignedTransaction) -> ServiceBarterSession:
        """Atomically create a DirectionalServiceBarterContract escrow session."""
        session_id = (
            str(signed_tx.payload.get("session_id", ""))
            if isinstance(signed_tx, SignedTransaction)
            else ""
        )
        with self._atomic_mutation("create_barter_escrow", tx_id=session_id):
            return self._apply_signed_escrow(signed_tx)

    def _apply_dual_signed_settlement(
        self,
        learner_tx: SignedTransaction,
        tutor_tx: SignedTransaction,
    ) -> dict[str, Any]:
        l_tx, learner_signer = _require_valid_signed_tx(learner_tx)
        t_tx, tutor_signer = _require_valid_signed_tx(tutor_tx)

        if CanonicalPayload.encode(l_tx.payload) != CanonicalPayload.encode(t_tx.payload):
            raise ContractViolationError(
                "Dual-signed settlement requires two identical-payload SignedTransactions."
            )

        payload = l_tx.payload
        if payload.get("action") != "SETTLE_SESSION":
            raise ContractViolationError(
                f"Expected action 'SETTLE_SESSION', got '{payload.get('action')}'."
            )
        if payload.get("hive_id") != self.hive_id:
            raise ContractViolationError(
                f"SignedTransaction hive_id '{payload.get('hive_id')}' does not match '{self.hive_id}'."
            )

        for sid, tx_obj in ((learner_signer, l_tx), (tutor_signer, t_tx)):
            registered_pk = self.bee_public_keys.get(sid)
            if registered_pk is None:
                raise InvalidSignatureError(
                    f"Signer '{sid}' has no registered public key in Hive '{self.hive_id}'."
                )
            if registered_pk != tx_obj.signer_public_key:
                raise InvalidSignatureError(
                    f"Signer public key does not match registered key for '{sid}'."
                )

        session_id = str(payload.get("session_id", ""))
        session = self.contracts._get_session(session_id)

        if learner_signer != session.learner_id:
            raise CommandAuthorizationError(
                f"Learner signature must come from '{session.learner_id}', got '{learner_signer}'."
            )
        if tutor_signer != session.tutor_id:
            raise CommandAuthorizationError(
                f"Tutor signature must come from '{session.tutor_id}', got '{tutor_signer}'."
            )

        learner_nonce = _require_positive_int_nonce(
            payload.get("learner_nonce", payload.get("nonce")), "learner_nonce"
        )
        tutor_nonce = _require_positive_int_nonce(
            payload.get("tutor_nonce", payload.get("nonce")), "tutor_nonce"
        )
        last_l = self.bee_nonces.get(learner_signer, 0)
        last_t = self.bee_nonces.get(tutor_signer, 0)
        if learner_nonce <= last_l:
            raise ContractViolationError(
                f"Replayed or stale learner nonce {learner_nonce} (last accepted={last_l})."
            )
        if tutor_nonce <= last_t:
            raise ContractViolationError(
                f"Replayed or stale tutor nonce {tutor_nonce} (last accepted={last_t})."
            )

        score = float(payload["learner_attestation_score"])
        comp_hash = str(payload["tutor_comprehension_hash"])

        self.bee_nonces[learner_signer] = learner_nonce
        self.bee_nonces[tutor_signer] = tutor_nonce
        tx_record = self.contracts.settle_co_signed_session(
            session_id=session_id,
            learner_attestation_score=score,
            tutor_comprehension_hash=comp_hash,
        )
        self.blockchain.submit_transaction(l_tx)
        self.blockchain.submit_transaction(t_tx)
        return tx_record

    def settle_session(
        self,
        learner_tx: SignedTransaction,
        tutor_tx: SignedTransaction,
    ) -> dict[str, Any]:
        """Atomically settle an escrowed tutoring session with identical learner+tutor signatures."""
        session_id = (
            str(learner_tx.payload.get("session_id", ""))
            if isinstance(learner_tx, SignedTransaction)
            else ""
        )
        with self._atomic_mutation("settle_session", tx_id=session_id):
            return self._apply_dual_signed_settlement(learner_tx, tutor_tx)

    def resolve_disputed_session(self, signed_tx: SignedTransaction) -> dict[str, Any]:
        """Atomically arbitrate a disputed session and route fees to Comb."""
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        queen_id = str(payload.get("queen_id", ""))
        session_id = str(payload.get("session_id", ""))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="RESOLVE_DISPUTED_SESSION",
            actor_id=queen_id,
            require_queen=True,
        )
        tutor_share_ratio = float(payload["tutor_share_ratio"])
        service_fee_rate = float(payload.get("service_fee_rate", 0.10))

        with self._atomic_mutation("resolve_disputed_session", tx_id=session_id):
            self.bee_nonces[queen_id] = nonce
            result = self.contracts.resolve_disputed_session(
                queen_id=queen_id,
                session_id=session_id,
                tutor_share_ratio=tutor_share_ratio,
                service_fee_rate=service_fee_rate,
            )
            self.blockchain.submit_transaction(tx)
            return result

    def bootstrap_sponsored_hive(self, signed_tx: SignedTransaction) -> dict[str, Any]:
        """Phase 1 Genesis: Inject Seed Comb, bind Queens/workers to public keys, and certify seed workers."""
        tx, lead_queen = _require_valid_signed_tx(signed_tx)
        payload = tx.payload

        if payload.get("action") != "BOOTSTRAP_HIVE":
            raise ContractViolationError(
                f"Expected action 'BOOTSTRAP_HIVE', got '{payload.get('action')}'."
            )
        if payload.get("hive_id") != self.hive_id:
            raise ContractViolationError(
                f"SignedTransaction hive_id '{payload.get('hive_id')}' does not match '{self.hive_id}'."
            )
        if self.contracts.accounts or self.bee_public_keys:
            raise ContractViolationError(f"Hive '{self.hive_id}' is already bootstrapped.")

        nonce = _require_positive_int_nonce(payload.get("nonce"))

        raw_queen_pks = payload.get("queen_public_keys")
        if not isinstance(raw_queen_pks, Mapping) or not raw_queen_pks:
            raise ContractViolationError("queen_public_keys must be a non-empty mapping.")
        queen_public_keys = {
            str(qid): _validate_public_key_hex(pk, str(qid)) for qid, pk in raw_queen_pks.items()
        }

        raw_workers = payload.get("certified_workers", {})
        if not isinstance(raw_workers, Mapping):
            raise ContractViolationError("certified_workers must be a mapping.")
        certified_workers: dict[str, list[str]] = {}
        for wid, subjects in raw_workers.items():
            if not isinstance(subjects, list):
                raise ContractViolationError(f"Subjects for worker '{wid}' must be a list.")
            certified_workers[str(wid)] = [str(s) for s in subjects]

        raw_worker_pks = payload.get("worker_public_keys", {})
        if not isinstance(raw_worker_pks, Mapping):
            raise ContractViolationError("worker_public_keys must be a mapping.")
        worker_public_keys = {
            str(wid): _validate_public_key_hex(pk, str(wid)) for wid, pk in raw_worker_pks.items()
        }

        overlap = set(queen_public_keys).intersection(worker_public_keys)
        if overlap:
            raise ContractViolationError(
                f"Accounts cannot be both Queen and Worker at bootstrap: {sorted(overlap)}"
            )
        missing_workers = set(certified_workers).difference(worker_public_keys)
        if missing_workers:
            raise ContractViolationError(
                f"Missing public keys for seed workers: {sorted(missing_workers)}"
            )

        if lead_queen not in queen_public_keys:
            raise CommandAuthorizationError(
                f"Bootstrap signer '{lead_queen}' must be listed in queen_public_keys."
            )
        declared_queen = payload.get("queen_id", lead_queen)
        if declared_queen != lead_queen:
            raise CommandAuthorizationError(
                f"Signer '{lead_queen}' does not match payload queen_id '{declared_queen}'."
            )
        if queen_public_keys[lead_queen] != tx.signer_public_key:
            raise InvalidSignatureError(
                f"Bootstrap signer public key does not match queen_public_keys['{lead_queen}']."
            )

        seed_comb_amount = float(payload["seed_comb_amount"])
        queen_dividend_beta = float(payload.get("queen_dividend_beta", 0.05))
        ts_raw = payload.get("timestamp")
        block_timestamp = None if ts_raw is None else float(ts_raw)
        if not math.isfinite(queen_dividend_beta) or queen_dividend_beta < 0.0:
            raise ContractViolationError(
                "queen_dividend_beta must be a finite non-negative number."
            )

        with self._atomic_mutation("bootstrap_sponsored_hive", tx_id=lead_queen):
            self.contracts.inject_sponsored_seed_comb(seed_comb_amount)

            for q_id, pk in queen_public_keys.items():
                self.bee_public_keys[q_id] = pk
                self.bee_nonces[q_id] = nonce if q_id == lead_queen else 0
                self.contracts.register_bee(q_id, role=BeeRole.QUEEN)

            for wid, pk in worker_public_keys.items():
                self.bee_public_keys[wid] = pk
                self.bee_nonces[wid] = 0
                self.contracts.register_bee(wid, role=BeeRole.LEARNER_BEE)

            for worker_id, subjects in certified_workers.items():
                for subj in subjects:
                    self.contracts.certify_worker_bee(
                        queen_id=lead_queen,
                        worker_id=worker_id,
                        subject_id=subj,
                        certification_fee=0.0,
                    )

            self.blockchain.submit_transaction(tx)
            block = self._mine_epoch_block_internal(
                queen_dividend_beta=queen_dividend_beta,
                timestamp=block_timestamp,
            )
            return {
                "hive_id": self.hive_id,
                "genesis_comb": self.contracts.comb_reserve,
                "queens": list(queen_public_keys.keys()),
                "certified_workers": list(certified_workers.keys()),
                "block_height": block.header.height,
                "block_hash": block.block_hash,
            }

    def execute_tutoring_handshake(
        self,
        escrow_tx: SignedTransaction,
        learner_settle_tx: SignedTransaction,
        tutor_settle_tx: SignedTransaction,
    ) -> dict[str, Any]:
        """Execute a complete signed escrow + dual-signed settlement atomically."""
        session_id = (
            str(escrow_tx.payload.get("session_id", ""))
            if isinstance(escrow_tx, SignedTransaction)
            else ""
        )
        with self._atomic_mutation("execute_tutoring_handshake", tx_id=session_id):
            escrow_session = self._apply_signed_escrow(escrow_tx)
            if isinstance(learner_settle_tx, SignedTransaction) and (
                learner_settle_tx.payload.get("session_id") != escrow_session.session_id
            ):
                raise ContractViolationError(
                    "Settlement session_id does not match escrow session_id."
                )
            return self._apply_dual_signed_settlement(learner_settle_tx, tutor_settle_tx)

    def bridge_nectr_to_target_hive(
        self,
        signed_tx: SignedTransaction,
        target_service: HiveServiceLayer,
    ) -> dict[str, Any]:
        """Execute a signed Guard-Bee-checked bridge transfer between two HiveServiceLayer instances."""
        if not isinstance(target_service, HiveServiceLayer):
            raise TypeError("target_service must be a HiveServiceLayer instance.")

        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        bee_id = str(payload.get("bee_id", ""))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="BRIDGE_NECTR",
            actor_id=bee_id,
        )
        target_hive_id = str(payload.get("target_hive_id", ""))
        if target_hive_id != target_service.hive_id:
            raise ContractViolationError(
                f"Target hive '{target_hive_id}' does not match '{target_service.hive_id}'."
            )

        target_pk = target_service.bee_public_keys.get(bee_id)
        if target_pk is not None and target_pk != tx.signer_public_key:
            raise InvalidSignatureError(
                f"Public key mismatch for '{bee_id}' in target Hive '{target_service.hive_id}'."
            )

        amount = float(payload["amount"])
        bridge_toll_rate = float(payload.get("bridge_toll_rate", 0.05))

        with (
            self._atomic_mutation("bridge_nectr_to_target_hive", tx_id=bee_id),
            target_service._atomic_mutation("receive_cross_hive_bridge", tx_id=bee_id),
        ):
            self.bee_nonces[bee_id] = nonce
            bridge_result = self.contracts.bridge_nectr_to_target_hive(
                bee_id=bee_id,
                target_hive=target_service.contracts,
                amount=amount,
                bridge_toll_rate=bridge_toll_rate,
            )
            self.blockchain.submit_transaction(tx)
            return bridge_result

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

    def _mine_epoch_block_internal(
        self,
        *,
        queen_dividend_beta: float = 0.05,
        timestamp: float | None = None,
    ) -> Block:
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

        return self.blockchain.mine_block(useful_compute_proof=proof, timestamp=timestamp)

    def mine_epoch_block(self, signed_tx: SignedTransaction) -> Block:
        """Mine a PoUW-PoW block via Queen-signed command and accrue Royal Jelly governance credits."""
        tx, _ = _require_valid_signed_tx(signed_tx)
        payload = tx.payload
        queen_id = str(payload.get("queen_id", ""))
        _, nonce = self._verify_signed_command(
            tx,
            expected_action="MINE_EPOCH_BLOCK",
            actor_id=queen_id,
            require_queen=True,
        )
        queen_dividend_beta = float(payload.get("queen_dividend_beta", 0.05))
        if not math.isfinite(queen_dividend_beta) or queen_dividend_beta < 0.0:
            raise ContractViolationError(
                "queen_dividend_beta must be a finite non-negative number."
            )
        ts_raw = payload.get("timestamp")
        timestamp = None if ts_raw is None else float(ts_raw)
        if timestamp is not None and not math.isfinite(timestamp):
            raise ContractViolationError("timestamp must be finite.")

        with self._atomic_mutation("mine_epoch_block", tx_id=queen_id):
            self.bee_nonces[queen_id] = nonce
            self.blockchain.submit_transaction(tx)
            return self._mine_epoch_block_internal(
                queen_dividend_beta=queen_dividend_beta,
                timestamp=timestamp,
            )
