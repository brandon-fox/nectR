"""The 5 Core Deterministic Smart Contracts for the nectR Hive State Machine."""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class TokenState(StrEnum):
    """Three biomimetic states of nectR currency inside a Hive."""

    RAW_POLLEN = "RAW_POLLEN"
    LIQUID_NECTR = "LIQUID_NECTR"
    ROYAL_COMB_RESERVE = "ROYAL_COMB_RESERVE"


class BeeRole(StrEnum):
    """Strict separation-of-powers roles inside a Hive."""

    LEARNER_BEE = "LEARNER_BEE"
    CERTIFIED_WORKER_BEE = "CERTIFIED_WORKER_BEE"
    POLLINATOR_VISITOR = "POLLINATOR_VISITOR"
    QUEEN = "QUEEN"


class SessionStatus(StrEnum):
    """Lifecycle states of a DirectionalServiceBarterContract session."""

    INTENT_ESCROWED = "INTENT_ESCROWED"
    SESSION_CO_SIGNED = "SESSION_CO_SIGNED"
    SETTLED = "SETTLED"
    DISPUTED_TO_QUEEN = "DISPUTED_TO_QUEEN"


class ContractViolationError(ValueError):
    """Raised when a transaction violates a nectR smart contract or game-theory invariant."""


def _require_finite_non_negative(value: float, label: str) -> float:
    if not math.isfinite(value) or value < 0:
        raise ContractViolationError(f"{label} must be a finite non-negative number.")
    return value


def _require_str_collection(value: Any, label: str) -> set[str]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        raise ContractViolationError(
            f"Invalid BeeAccount snapshot: '{label}' must be a collection."
        )
    return {str(item) for item in value}


@dataclass
class BeeAccount:
    """On-chain account state for a Bee or Queen inside a specific Hive."""

    bee_id: str
    home_hive_id: str
    role: BeeRole = BeeRole.LEARNER_BEE
    raw_pollen_balance: float = 0.0
    liquid_nectr_balance: float = 0.0
    certified_subjects: set[str] = field(default_factory=set)
    accepted_in_hives: set[str] = field(default_factory=set)
    distinct_peers_tutored_in_hive: set[str] = field(default_factory=set)
    royal_jelly_earned: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize account state into canonical JSON-safe primitives."""
        return {
            "bee_id": self.bee_id,
            "home_hive_id": self.home_hive_id,
            "role": self.role.value,
            "raw_pollen_balance": float(self.raw_pollen_balance),
            "liquid_nectr_balance": float(self.liquid_nectr_balance),
            "certified_subjects": sorted(self.certified_subjects),
            "accepted_in_hives": sorted(self.accepted_in_hives),
            "distinct_peers_tutored_in_hive": sorted(self.distinct_peers_tutored_in_hive),
            "royal_jelly_earned": float(self.royal_jelly_earned),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BeeAccount:
        """Hydrate a BeeAccount from serialized primitives."""
        try:
            return cls(
                bee_id=str(data["bee_id"]),
                home_hive_id=str(data["home_hive_id"]),
                role=BeeRole(str(data["role"])),
                raw_pollen_balance=_require_finite_non_negative(
                    float(data["raw_pollen_balance"]), "raw_pollen_balance"
                ),
                liquid_nectr_balance=_require_finite_non_negative(
                    float(data["liquid_nectr_balance"]), "liquid_nectr_balance"
                ),
                certified_subjects=_require_str_collection(
                    data["certified_subjects"], "certified_subjects"
                ),
                accepted_in_hives=_require_str_collection(
                    data["accepted_in_hives"], "accepted_in_hives"
                ),
                distinct_peers_tutored_in_hive=_require_str_collection(
                    data["distinct_peers_tutored_in_hive"],
                    "distinct_peers_tutored_in_hive",
                ),
                royal_jelly_earned=_require_finite_non_negative(
                    float(data["royal_jelly_earned"]), "royal_jelly_earned"
                ),
            )
        except ContractViolationError:
            raise
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise ContractViolationError(f"Invalid BeeAccount snapshot: {exc}") from exc


@dataclass
class ServiceBarterSession:
    """Directional Proof-of-Service & Barter Escrow Contract instance."""

    session_id: str
    hive_id: str
    tutor_id: str
    learner_id: str
    subject_id: str
    duration_hours: float
    escrowed_amount: float
    token_state: TokenState
    reciprocal_subject_id: str | None = None
    status: SessionStatus = SessionStatus.INTENT_ESCROWED
    learner_attestation_score: float = 0.0
    tutor_comprehension_hash: str = ""
    effective_weight: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize session state into canonical JSON-safe primitives."""
        return {
            "session_id": self.session_id,
            "hive_id": self.hive_id,
            "tutor_id": self.tutor_id,
            "learner_id": self.learner_id,
            "subject_id": self.subject_id,
            "duration_hours": float(self.duration_hours),
            "escrowed_amount": float(self.escrowed_amount),
            "token_state": self.token_state.value,
            "reciprocal_subject_id": self.reciprocal_subject_id,
            "status": self.status.value,
            "learner_attestation_score": float(self.learner_attestation_score),
            "tutor_comprehension_hash": self.tutor_comprehension_hash,
            "effective_weight": float(self.effective_weight),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ServiceBarterSession:
        """Hydrate a ServiceBarterSession from serialized primitives."""
        try:
            rec = data.get("reciprocal_subject_id")
            duration_hours = float(data["duration_hours"])
            if not math.isfinite(duration_hours) or duration_hours <= 0:
                raise ContractViolationError("Session duration_hours must be finite and positive.")
            attestation_score = float(data["learner_attestation_score"])
            if not math.isfinite(attestation_score) or not (0.0 <= attestation_score <= 1.0):
                raise ContractViolationError("Attestation score must be in [0.0, 1.0].")
            return cls(
                session_id=str(data["session_id"]),
                hive_id=str(data["hive_id"]),
                tutor_id=str(data["tutor_id"]),
                learner_id=str(data["learner_id"]),
                subject_id=str(data["subject_id"]),
                duration_hours=duration_hours,
                escrowed_amount=_require_finite_non_negative(
                    float(data["escrowed_amount"]), "escrowed_amount"
                ),
                token_state=TokenState(str(data["token_state"])),
                reciprocal_subject_id=None if rec is None else str(rec),
                status=SessionStatus(str(data["status"])),
                learner_attestation_score=attestation_score,
                tutor_comprehension_hash=str(data["tutor_comprehension_hash"]),
                effective_weight=_require_finite_non_negative(
                    float(data["effective_weight"]), "effective_weight"
                ),
            )
        except ContractViolationError:
            raise
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise ContractViolationError(f"Invalid ServiceBarterSession snapshot: {exc}") from exc


class HiveContractEngine:
    """Executes the 5 core nectR smart contracts deterministically for a single Hive."""

    def __init__(
        self,
        hive_id: str,
        collusion_alpha: float = 1.5,
        lineage_gamma: float = 0.5,
        accepted_status_peer_threshold: int = 3,
    ) -> None:
        self.hive_id = hive_id
        self.collusion_alpha = collusion_alpha
        self.lineage_gamma = lineage_gamma
        self.accepted_status_peer_threshold = accepted_status_peer_threshold

        self.comb_reserve: float = 0.0
        self.total_minted_supply: float = 0.0
        self.accounts: dict[str, BeeAccount] = {}
        self.sessions: dict[str, ServiceBarterSession] = {}

        # Knowledge graph & anti-collusion state:
        # pairwise_counts[frozenset({u, v})] -> total closed-loop exchanges
        self.pairwise_counts: dict[frozenset[str], int] = {}
        # subject_learners[(learner_id, subject_id)] -> list of tutors who taught them
        self.subject_lineage: dict[tuple[str, str], list[str]] = {}
        # tutor_effectiveness[tutor_id] -> cumulative collusion-discounted effectiveness
        self.tutor_effectiveness: dict[str, float] = {}
        self.settled_tx_log: list[dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # 1. TokenStateAndCombContract & Genesis Injection
    # -------------------------------------------------------------------------
    def register_bee(
        self,
        bee_id: str,
        role: BeeRole = BeeRole.LEARNER_BEE,
        home_hive_id: str | None = None,
    ) -> BeeAccount:
        origin = self.hive_id if home_hive_id is None else home_hive_id
        if bee_id in self.accounts:
            return self.accounts[bee_id]
        acct = BeeAccount(
            bee_id=bee_id,
            home_hive_id=origin,
            role=role,
            accepted_in_hives={origin},
        )
        self.accounts[bee_id] = acct
        return acct

    def inject_sponsored_seed_comb(self, amount: float) -> dict[str, Any]:
        """School sponsor injects initial fixed Seed Comb into the Hive."""
        if not math.isfinite(amount) or amount <= 0:
            raise ContractViolationError("Seed Comb injection must be positive.")
        self.comb_reserve += amount
        self.total_minted_supply += amount
        return {
            "contract": "TokenStateAndCombContract",
            "action": "INJECT_SEED_COMB",
            "hive_id": self.hive_id,
            "amount": amount,
            "comb_reserve": self.comb_reserve,
        }

    def allocate_raw_pollen_to_learner(
        self,
        queen_id: str,
        learner_id: str,
        amount: float,
    ) -> dict[str, Any]:
        """Issue restricted RAW_POLLEN from the Comb to a Learner Bee."""
        self._require_queen(queen_id)
        learner = self._get_account(learner_id)
        if learner.role == BeeRole.QUEEN:
            raise ContractViolationError("Queens cannot receive RAW_POLLEN learner vouchers.")
        if not math.isfinite(amount) or amount <= 0 or amount > self.comb_reserve:
            raise ContractViolationError("Insufficient Comb reserve for RAW_POLLEN draw.")
        self.comb_reserve -= amount
        learner.raw_pollen_balance += amount
        self.assert_supply_conservation()
        return {
            "contract": "TokenStateAndCombContract",
            "action": "ALLOCATE_RAW_POLLEN",
            "queen_id": queen_id,
            "learner_id": learner_id,
            "amount": amount,
        }

    # -------------------------------------------------------------------------
    # 2. QueenGovernanceAndCertificationContract (Separation of Powers)
    # -------------------------------------------------------------------------
    def certify_worker_bee(
        self,
        queen_id: str,
        worker_id: str,
        subject_id: str,
        certification_fee: float = 0.0,
    ) -> dict[str, Any]:
        """Queen accredits a student as a Certified Worker Bee in a subject. Fee -> Comb."""
        self._require_queen(queen_id)
        worker = self._get_account(worker_id)
        if worker.role == BeeRole.QUEEN:
            raise ContractViolationError("Queens cannot be certified as Worker Tutors.")
        _require_finite_non_negative(certification_fee, "certification_fee")
        if certification_fee > 0:
            if worker.liquid_nectr_balance < certification_fee:
                raise ContractViolationError("Insufficient LIQUID_NECTR for certification fee.")
            worker.liquid_nectr_balance -= certification_fee
            self.comb_reserve += certification_fee
        worker.role = BeeRole.CERTIFIED_WORKER_BEE
        worker.certified_subjects.add(subject_id)
        self.assert_supply_conservation()
        return {
            "contract": "QueenGovernanceContract",
            "action": "CERTIFY_WORKER_BEE",
            "queen_id": queen_id,
            "worker_id": worker_id,
            "subject_id": subject_id,
            "fee_to_comb": certification_fee,
        }

    # -------------------------------------------------------------------------
    # 3. DirectionalServiceBarterContract & 4. KnowledgeGraphAndPolicingContract
    # -------------------------------------------------------------------------
    def create_service_barter_escrow(
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
        """Step 1: Lock funds (or 0-nectR mutual skill obligation) into directional service escrow."""
        if session_id in self.sessions:
            raise ContractViolationError(f"Session '{session_id}' already exists.")
        if not math.isfinite(duration_hours) or duration_hours <= 0:
            raise ContractViolationError("Session duration_hours must be positive and finite.")
        if tutor_id == learner_id:
            raise ContractViolationError("Self-tutoring is prohibited.")
        tutor = self._get_account(tutor_id)
        learner = self._get_account(learner_id)

        # Strict Separation of Powers: Queens can NEVER generate money from tutoring
        if tutor.role == BeeRole.QUEEN:
            raise ContractViolationError(
                "Queen Separation of Powers Violation: Queens cannot tutor or earn nectR from tutoring."
            )

        if not math.isfinite(amount) or amount < 0:
            raise ContractViolationError("Escrow amount cannot be negative.")

        if amount == 0 and not reciprocal_subject_id:
            raise ContractViolationError(
                "Zero-nectR sessions must specify a reciprocal_subject_id for direct skill barter."
            )

        if token_state == TokenState.RAW_POLLEN:
            if (
                tutor.role != BeeRole.CERTIFIED_WORKER_BEE
                or subject_id not in tutor.certified_subjects
            ):
                raise ContractViolationError(
                    "RAW_POLLEN can only be spent with a Queen-Certified Worker Bee in their certified subject."
                )
            if learner.raw_pollen_balance < amount:
                raise ContractViolationError("Insufficient RAW_POLLEN balance.")
            learner.raw_pollen_balance -= amount
        elif token_state == TokenState.LIQUID_NECTR:
            if learner.liquid_nectr_balance < amount:
                raise ContractViolationError("Insufficient LIQUID_NECTR balance.")
            learner.liquid_nectr_balance -= amount
        else:
            raise ContractViolationError("Invalid token state for P2P escrow.")

        session = ServiceBarterSession(
            session_id=session_id,
            hive_id=self.hive_id,
            tutor_id=tutor_id,
            learner_id=learner_id,
            subject_id=subject_id,
            duration_hours=duration_hours,
            escrowed_amount=amount,
            token_state=token_state,
            reciprocal_subject_id=reciprocal_subject_id,
            status=SessionStatus.INTENT_ESCROWED,
        )
        self.sessions[session_id] = session
        self.assert_supply_conservation()
        return session

    def settle_co_signed_session(
        self,
        session_id: str,
        learner_attestation_score: float,
        tutor_comprehension_hash: str,
    ) -> dict[str, Any]:
        """Step 2 & 3: Both Bees co-sign session completion -> 0-fee P2P settlement & Knowledge Graph update."""
        session = self._get_session(session_id)
        if session.status != SessionStatus.INTENT_ESCROWED:
            raise ContractViolationError(f"Session {session_id} is not in INTENT_ESCROWED state.")
        if not math.isfinite(learner_attestation_score) or not (
            0.0 <= learner_attestation_score <= 1.0
        ):
            raise ContractViolationError("Attestation score must be in [0.0, 1.0].")

        tutor = self._get_account(session.tutor_id)
        learner = self._get_account(session.learner_id)

        # Trophallaxis refinement: RAW_POLLEN refines into LIQUID_NECTR upon verified tutoring!
        # And 0% protocol fee is charged on normal P2P settlement.
        tutor.liquid_nectr_balance += session.escrowed_amount

        # Pairwise Anti-Collusion Decay & Downstream Lineage Calculation
        pair_key = frozenset({tutor.bee_id, learner.bee_id})
        prior_pair_txs = self.pairwise_counts.get(pair_key, 0)
        decay_factor = 1.0 / (1.0 + self.collusion_alpha * prior_pair_txs)

        # Check if Tutor previously learned this subject from an upstream tutor (Learn-then-Teach Lineage)
        upstream_tutors = self.subject_lineage.get((tutor.bee_id, session.subject_id), [])
        lineage_bonus = 1.0 + (self.lineage_gamma if upstream_tutors else 0.0)

        effective_weight = learner_attestation_score * decay_factor * lineage_bonus
        self.pairwise_counts[pair_key] = prior_pair_txs + 1

        # Record directional knowledge edge & credit upstream tutors for effective downstream teaching
        if prior_pair_txs == 0 and learner_attestation_score >= 0.6:
            self.subject_lineage.setdefault((learner.bee_id, session.subject_id), []).append(
                tutor.bee_id
            )
            tutor.distinct_peers_tutored_in_hive.add(learner.bee_id)
            for upstream_id in upstream_tutors:
                self.tutor_effectiveness[upstream_id] = (
                    self.tutor_effectiveness.get(upstream_id, 0.0) + 0.25 * effective_weight
                )

        self.tutor_effectiveness[tutor.bee_id] = (
            self.tutor_effectiveness.get(tutor.bee_id, 0.0) + effective_weight
        )

        # Guard Bee Foreign Acceptance check: unlock Accepted Status if threshold met
        if len(tutor.distinct_peers_tutored_in_hive) >= self.accepted_status_peer_threshold:
            tutor.accepted_in_hives.add(self.hive_id)

        session.learner_attestation_score = learner_attestation_score
        session.tutor_comprehension_hash = tutor_comprehension_hash
        session.effective_weight = effective_weight
        session.status = SessionStatus.SETTLED

        self.assert_supply_conservation()
        tx_record = {
            "contract": "DirectionalServiceBarterContract",
            "action": "SETTLE_SESSION",
            "session_id": session_id,
            "tutor_id": tutor.bee_id,
            "learner_id": learner.bee_id,
            "subject_id": session.subject_id,
            "amount": session.escrowed_amount,
            "refined_from": str(session.token_state),
            "effective_weight": round(effective_weight, 4),
            "pairwise_loop_count": self.pairwise_counts[pair_key],
            "fee_charged": 0.0,
        }
        self.settled_tx_log.append(tx_record)
        return tx_record

    def resolve_disputed_session(
        self,
        queen_id: str,
        session_id: str,
        tutor_share_ratio: float,
        service_fee_rate: float = 0.10,
    ) -> dict[str, Any]:
        """Step 3b: Queen arbitrates a dispute. Service fee is deducted and routed 100% to the Comb."""
        self._require_queen(queen_id)
        session = self._get_session(session_id)
        if session.status != SessionStatus.INTENT_ESCROWED:
            raise ContractViolationError("Only escrowed sessions can be arbitrated.")
        if not math.isfinite(tutor_share_ratio) or not (0.0 <= tutor_share_ratio <= 1.0):
            raise ContractViolationError("tutor_share_ratio must be between 0 and 1.")
        if not math.isfinite(service_fee_rate) or not (0.0 <= service_fee_rate <= 1.0):
            raise ContractViolationError("service_fee_rate must be between 0 and 1.")

        tutor = self._get_account(session.tutor_id)
        learner = self._get_account(session.learner_id)

        fee_to_comb = round(session.escrowed_amount * service_fee_rate, 6)
        distributable = session.escrowed_amount - fee_to_comb
        tutor_payout = round(distributable * tutor_share_ratio, 6)
        learner_refund = round(distributable - tutor_payout, 6)

        self.comb_reserve += fee_to_comb
        tutor.liquid_nectr_balance += tutor_payout
        if session.token_state == TokenState.RAW_POLLEN:
            learner.raw_pollen_balance += learner_refund
        else:
            learner.liquid_nectr_balance += learner_refund

        session.status = SessionStatus.DISPUTED_TO_QUEEN
        self.assert_supply_conservation()
        return {
            "contract": "QueenGovernanceContract",
            "action": "RESOLVE_DISPUTE",
            "queen_id": queen_id,
            "session_id": session_id,
            "fee_to_comb": fee_to_comb,
            "tutor_payout": tutor_payout,
            "learner_refund": learner_refund,
        }

    # -------------------------------------------------------------------------
    # 5. GuardBeeCrossHiveBridgeContract
    # -------------------------------------------------------------------------
    def bridge_nectr_to_target_hive(
        self,
        bee_id: str,
        target_hive: HiveContractEngine,
        amount: float,
        bridge_toll_rate: float = 0.05,
    ) -> dict[str, Any]:
        """Bridge LIQUID_NECTR from home Hive to target Hive ONLY after earning Accepted Status in target Hive."""
        source_acct = self._get_account(bee_id)
        if source_acct.role == BeeRole.QUEEN:
            raise ContractViolationError(
                "Queens are bound to their Hive and cannot bridge tutoring currency."
            )
        if not math.isfinite(amount) or amount <= 0 or source_acct.liquid_nectr_balance < amount:
            raise ContractViolationError("Insufficient LIQUID_NECTR in origin Hive to bridge.")
        if not math.isfinite(bridge_toll_rate) or not (0.0 <= bridge_toll_rate <= 1.0):
            raise ContractViolationError("bridge_toll_rate must be between 0 and 1.")

        target_acct = target_hive.register_bee(bee_id, home_hive_id=source_acct.home_hive_id)
        if target_hive.hive_id not in target_acct.accepted_in_hives:
            raise ContractViolationError(
                f"Guard Bee Rejection: Bee '{bee_id}' has not reached Accepted Status in '{target_hive.hive_id}'."
            )

        # Comb-to-Comb dynamic exchange rate based on Comb per active Bee health ratio
        source_health = max(self.comb_reserve / max(len(self.accounts), 1), 1.0)
        target_health = max(target_hive.comb_reserve / max(len(target_hive.accounts), 1), 1.0)
        exchange_rate = min(max(source_health / target_health, 0.5), 2.0)

        source_toll = round(amount * bridge_toll_rate, 6)
        net_out = amount - source_toll

        # Burn/Lock in source Hive and send toll to source Comb
        source_acct.liquid_nectr_balance -= amount
        self.comb_reserve += source_toll
        self.total_minted_supply -= net_out
        self.assert_supply_conservation()

        # Mint equivalent in target Hive backed by cross-comb liquidity
        minted_in_target = round(net_out * exchange_rate, 6)
        target_acct.liquid_nectr_balance += minted_in_target
        target_hive.total_minted_supply += minted_in_target
        target_hive.assert_supply_conservation()

        return {
            "contract": "GuardBeeCrossHiveBridgeContract",
            "action": "CROSS_HIVE_BRIDGE",
            "bee_id": bee_id,
            "from_hive": self.hive_id,
            "to_hive": target_hive.hive_id,
            "amount_bridged": amount,
            "source_comb_toll": source_toll,
            "exchange_rate": round(exchange_rate, 4),
            "received_in_target": minted_in_target,
        }

    # -------------------------------------------------------------------------
    # Invariant Verification
    # -------------------------------------------------------------------------
    def assert_supply_conservation(self) -> None:
        """Assert that TotalSupply == CombReserve + Sum(RawPollen) + Sum(LiquidNectR) + Sum(Escrow)."""
        _require_finite_non_negative(self.comb_reserve, "comb_reserve")
        _require_finite_non_negative(self.total_minted_supply, "total_minted_supply")
        for acct in self.accounts.values():
            _require_finite_non_negative(acct.raw_pollen_balance, "raw_pollen_balance")
            _require_finite_non_negative(acct.liquid_nectr_balance, "liquid_nectr_balance")
            _require_finite_non_negative(acct.royal_jelly_earned, "royal_jelly_earned")
        for sess in self.sessions.values():
            _require_finite_non_negative(sess.escrowed_amount, "escrowed_amount")

        total_pollen = sum(a.raw_pollen_balance for a in self.accounts.values())
        total_liquid = sum(a.liquid_nectr_balance for a in self.accounts.values())
        total_escrow = sum(
            s.escrowed_amount
            for s in self.sessions.values()
            if s.status == SessionStatus.INTENT_ESCROWED
        )
        accounted = round(self.comb_reserve + total_pollen + total_liquid + total_escrow, 5)
        expected = round(self.total_minted_supply, 5)
        if (
            not math.isfinite(accounted)
            or not math.isfinite(expected)
            or abs(accounted - expected) > 1e-4
        ):
            raise ContractViolationError(
                f"Supply conservation invariant violated: accounted={accounted} != expected={expected}"
            )

    def _get_account(self, bee_id: str) -> BeeAccount:
        if bee_id not in self.accounts:
            raise ContractViolationError(
                f"Bee '{bee_id}' is not registered in Hive '{self.hive_id}'."
            )
        return self.accounts[bee_id]

    def _get_session(self, session_id: str) -> ServiceBarterSession:
        if session_id not in self.sessions:
            raise ContractViolationError(f"Session '{session_id}' does not exist.")
        return self.sessions[session_id]

    def _require_queen(self, queen_id: str) -> BeeAccount:
        acct = self._get_account(queen_id)
        if acct.role != BeeRole.QUEEN:
            raise ContractViolationError(f"Account '{queen_id}' does not hold QUEEN role.")
        return acct

    # -------------------------------------------------------------------------
    # Pure Deterministic Snapshot / Hydration
    # -------------------------------------------------------------------------
    def to_snapshot(self) -> dict[str, Any]:
        """Export full contract state as canonical JSON-safe stdlib primitives."""
        return {
            "schema_version": 1,
            "hive_id": self.hive_id,
            "collusion_alpha": float(self.collusion_alpha),
            "lineage_gamma": float(self.lineage_gamma),
            "accepted_status_peer_threshold": int(self.accepted_status_peer_threshold),
            "comb_reserve": float(self.comb_reserve),
            "total_minted_supply": float(self.total_minted_supply),
            "accounts": {bee_id: acct.to_dict() for bee_id, acct in sorted(self.accounts.items())},
            "sessions": {
                session_id: sess.to_dict() for session_id, sess in sorted(self.sessions.items())
            },
            "pairwise_counts": [
                {"pair": pair_list, "count": int(count)}
                for pair_list, count in sorted(
                    ((sorted(pair), count) for pair, count in self.pairwise_counts.items()),
                    key=lambda item: item[0],
                )
            ],
            "subject_lineage": [
                {"learner_id": learner_id, "subject_id": subject_id, "tutors": list(tutors)}
                for (learner_id, subject_id), tutors in sorted(
                    self.subject_lineage.items(),
                    key=lambda item: item[0],
                )
            ],
            "tutor_effectiveness": {
                k: float(v) for k, v in sorted(self.tutor_effectiveness.items())
            },
            "settled_tx_log": copy.deepcopy(self.settled_tx_log),
        }

    @classmethod
    def from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
        *,
        verify_invariants: bool = True,
    ) -> HiveContractEngine:
        """Hydrate a HiveContractEngine from a snapshot dictionary."""
        try:
            schema_version = snapshot.get("schema_version", 1)
            if schema_version != 1:
                raise ContractViolationError(
                    f"Unsupported snapshot schema version: {schema_version}"
                )
            collusion_alpha = _require_finite_non_negative(
                float(snapshot["collusion_alpha"]), "collusion_alpha"
            )
            lineage_gamma = _require_finite_non_negative(
                float(snapshot["lineage_gamma"]), "lineage_gamma"
            )
            accepted_threshold = int(snapshot["accepted_status_peer_threshold"])
            if accepted_threshold < 1:
                raise ContractViolationError("accepted_status_peer_threshold must be >= 1.")
            engine = cls(
                hive_id=str(snapshot["hive_id"]),
                collusion_alpha=collusion_alpha,
                lineage_gamma=lineage_gamma,
                accepted_status_peer_threshold=accepted_threshold,
            )
            engine.comb_reserve = _require_finite_non_negative(
                float(snapshot["comb_reserve"]), "comb_reserve"
            )
            engine.total_minted_supply = _require_finite_non_negative(
                float(snapshot["total_minted_supply"]), "total_minted_supply"
            )

            raw_accounts = snapshot["accounts"]
            for key, raw_acct in raw_accounts.items():
                acct = BeeAccount.from_dict(raw_acct)
                if acct.bee_id != str(key):
                    raise ContractViolationError(
                        f"Account key '{key}' does not match bee_id '{acct.bee_id}'."
                    )
                engine.accounts[acct.bee_id] = acct

            raw_sessions = snapshot["sessions"]
            for key, raw_sess in raw_sessions.items():
                sess = ServiceBarterSession.from_dict(raw_sess)
                if sess.session_id != str(key):
                    raise ContractViolationError(
                        f"Session key '{key}' does not match session_id '{sess.session_id}'."
                    )
                if sess.hive_id != engine.hive_id:
                    raise ContractViolationError(
                        f"Session '{sess.session_id}' hive_id '{sess.hive_id}' != '{engine.hive_id}'."
                    )
                engine.sessions[sess.session_id] = sess

            for entry in snapshot["pairwise_counts"]:
                pair = [str(x) for x in entry["pair"]]
                count = int(entry["count"])
                if len(pair) != 2 or pair[0] == pair[1] or count < 0:
                    raise ContractViolationError(f"Invalid pairwise_counts entry: {entry!r}")
                pair_key = frozenset(pair)
                if pair_key in engine.pairwise_counts:
                    raise ContractViolationError(
                        f"Duplicate pairwise_counts entry for pair {sorted(pair_key)!r}."
                    )
                engine.pairwise_counts[pair_key] = count

            for lineage_entry in snapshot["subject_lineage"]:
                lineage_key = (str(lineage_entry["learner_id"]), str(lineage_entry["subject_id"]))
                engine.subject_lineage[lineage_key] = [str(t) for t in lineage_entry["tutors"]]

            engine.tutor_effectiveness = {
                str(k): _require_finite_non_negative(float(v), f"tutor_effectiveness[{k}]")
                for k, v in snapshot["tutor_effectiveness"].items()
            }
            engine.settled_tx_log = copy.deepcopy(list(snapshot["settled_tx_log"]))
        except ContractViolationError:
            raise
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise ContractViolationError(f"Invalid HiveContractEngine snapshot: {exc}") from exc

        if verify_invariants:
            engine.assert_supply_conservation()
        return engine
