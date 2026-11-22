"""FastAPI driving adapter exposing HiveServiceLayer operations over HTTP."""

from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from nectr.contracts.engine import BeeRole, ContractViolationError, TokenState
from nectr.services.hive_service import HiveServiceLayer
from nectr.services.telemetry import TelemetryAdapter


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    status: str
    hive_id: str
    current_epoch: int


class HiveStateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    hive_id: str
    comb_reserve: float
    total_minted_supply: float
    current_epoch: int
    account_count: int
    session_count: int
    block_height: int
    chain_valid: bool


class BootstrapHiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    seed_comb_amount: float
    queen_ids: list[str] = Field(min_length=1)
    certified_workers: dict[str, list[str]] = Field(default_factory=dict)


class RegisterBeeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    bee_id: str
    role: BeeRole = BeeRole.LEARNER_BEE
    home_hive_id: str | None = None


class BeeAccountResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    bee_id: str
    home_hive_id: str
    role: str
    raw_pollen_balance: float
    liquid_nectr_balance: float
    certified_subjects: list[str]
    accepted_in_hives: list[str]
    distinct_peers_tutored_in_hive: list[str]
    royal_jelly_earned: float


class AllocatePollenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    queen_id: str
    learner_id: str
    amount: float


class CertifyWorkerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    queen_id: str
    worker_id: str
    subject_id: str
    certification_fee: float = 0.0


class TutoringHandshakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    session_id: str
    tutor_id: str
    learner_id: str
    subject_id: str
    duration_hours: float = Field(gt=0.0)
    amount: float
    token_state: TokenState = TokenState.LIQUID_NECTR
    learner_attestation_score: float = 0.95
    reciprocal_subject_id: str | None = None


class CreateEscrowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    session_id: str
    tutor_id: str
    learner_id: str
    subject_id: str
    duration_hours: float = Field(gt=0.0)
    amount: float
    token_state: TokenState = TokenState.LIQUID_NECTR
    reciprocal_subject_id: str | None = None


class SettleSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    learner_attestation_score: float
    tutor_comprehension_hash: str


class DisputeSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    queen_id: str
    tutor_share_ratio: float
    service_fee_rate: float = Field(default=0.10, ge=0.0, le=1.0)


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    session_id: str
    hive_id: str
    tutor_id: str
    learner_id: str
    subject_id: str
    duration_hours: float
    escrowed_amount: float
    token_state: str
    reciprocal_subject_id: str | None
    status: str
    learner_attestation_score: float
    tutor_comprehension_hash: str
    effective_weight: float


class MineEpochRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    queen_dividend_beta: float = Field(default=0.05, ge=0.0)


class MineEpochResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    height: int
    block_hash: str
    epoch: int
    gini_coefficient: float
    collusion_discounted_velocity: float


class TelemetrySummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    hive_id: str
    epoch: int
    active_bees: int
    total_directional_edges: int
    collusion_discounted_velocity: float
    gini_coefficient: float
    graph_state_hash: str
    event_count: int
    span_count: int


def create_hive_router(service: HiveServiceLayer) -> APIRouter:
    """Build a FastAPI APIRouter delegating all domain commands to HiveServiceLayer."""
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def get_health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            hive_id=service.hive_id,
            current_epoch=service.current_epoch,
        )

    @router.get("/hive/state", response_model=HiveStateResponse)
    def get_hive_state() -> HiveStateResponse:
        return HiveStateResponse(
            hive_id=service.hive_id,
            comb_reserve=service.contracts.comb_reserve,
            total_minted_supply=service.contracts.total_minted_supply,
            current_epoch=service.current_epoch,
            account_count=len(service.contracts.accounts),
            session_count=len(service.contracts.sessions),
            block_height=service.blockchain.chain[-1].header.height,
            chain_valid=service.blockchain.verify_chain(),
        )

    @router.post("/hive/bootstrap")
    def bootstrap_hive(payload: BootstrapHiveRequest) -> dict[str, Any]:
        try:
            return service.bootstrap_sponsored_hive(
                seed_comb_amount=payload.seed_comb_amount,
                queen_ids=payload.queen_ids,
                certified_workers=payload.certified_workers,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/bees", response_model=BeeAccountResponse)
    def register_bee(payload: RegisterBeeRequest) -> BeeAccountResponse:
        acct = service.register_bee(
            bee_id=payload.bee_id,
            role=payload.role,
            home_hive_id=payload.home_hive_id,
        )
        return BeeAccountResponse(
            **{k: v for k, v in acct.to_dict().items() if k in BeeAccountResponse.model_fields}
        )

    @router.get("/bees/{bee_id}", response_model=BeeAccountResponse)
    def get_bee(bee_id: str) -> BeeAccountResponse:
        acct = service.contracts.accounts.get(bee_id)
        if acct is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bee '{bee_id}' not found in Hive '{service.hive_id}'.",
            )
        return BeeAccountResponse(
            **{k: v for k, v in acct.to_dict().items() if k in BeeAccountResponse.model_fields}
        )

    @router.post("/pollen/allocate")
    def allocate_pollen(payload: AllocatePollenRequest) -> dict[str, Any]:
        try:
            return service.allocate_raw_pollen(
                queen_id=payload.queen_id,
                learner_id=payload.learner_id,
                amount=payload.amount,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/workers/certify")
    def certify_worker(payload: CertifyWorkerRequest) -> dict[str, Any]:
        try:
            return service.certify_worker_bee(
                queen_id=payload.queen_id,
                worker_id=payload.worker_id,
                subject_id=payload.subject_id,
                certification_fee=payload.certification_fee,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/sessions/handshake")
    def execute_handshake(payload: TutoringHandshakeRequest) -> dict[str, Any]:
        try:
            return service.execute_tutoring_handshake(
                session_id=payload.session_id,
                tutor_id=payload.tutor_id,
                learner_id=payload.learner_id,
                subject_id=payload.subject_id,
                duration_hours=payload.duration_hours,
                amount=payload.amount,
                token_state=payload.token_state,
                learner_attestation_score=payload.learner_attestation_score,
                reciprocal_subject_id=payload.reciprocal_subject_id,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/sessions/escrow", response_model=SessionResponse)
    def create_escrow(payload: CreateEscrowRequest) -> SessionResponse:
        try:
            sess = service.create_barter_escrow(
                session_id=payload.session_id,
                tutor_id=payload.tutor_id,
                learner_id=payload.learner_id,
                subject_id=payload.subject_id,
                duration_hours=payload.duration_hours,
                amount=payload.amount,
                token_state=payload.token_state,
                reciprocal_subject_id=payload.reciprocal_subject_id,
            )
            return SessionResponse(
                **{k: v for k, v in sess.to_dict().items() if k in SessionResponse.model_fields}
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.get("/sessions/{session_id}", response_model=SessionResponse)
    def get_session(session_id: str) -> SessionResponse:
        sess = service.contracts.sessions.get(session_id)
        if sess is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found.",
            )
        return SessionResponse(
            **{k: v for k, v in sess.to_dict().items() if k in SessionResponse.model_fields}
        )

    @router.post("/sessions/{session_id}/settle")
    def settle_session(session_id: str, payload: SettleSessionRequest) -> dict[str, Any]:
        try:
            return service.settle_session(
                session_id=session_id,
                learner_attestation_score=payload.learner_attestation_score,
                tutor_comprehension_hash=payload.tutor_comprehension_hash,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/sessions/{session_id}/dispute")
    def dispute_session(session_id: str, payload: DisputeSessionRequest) -> dict[str, Any]:
        try:
            return service.resolve_disputed_session(
                queen_id=payload.queen_id,
                session_id=session_id,
                tutor_share_ratio=payload.tutor_share_ratio,
                service_fee_rate=payload.service_fee_rate,
            )
        except ContractViolationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/epochs/mine", response_model=MineEpochResponse)
    def mine_epoch(payload: MineEpochRequest) -> MineEpochResponse:
        block = service.mine_epoch_block(queen_dividend_beta=payload.queen_dividend_beta)
        return MineEpochResponse(
            height=block.header.height,
            block_hash=block.block_hash,
            epoch=block.useful_compute_proof.epoch,
            gini_coefficient=block.useful_compute_proof.gini_coefficient,
            collusion_discounted_velocity=block.useful_compute_proof.collusion_discounted_velocity,
        )

    @router.get("/telemetry", response_model=TelemetrySummaryResponse)
    def get_telemetry() -> TelemetrySummaryResponse:
        proof = service.compute_useful_work_proof()
        event_count = 0
        span_count = 0
        if isinstance(service.telemetry, TelemetryAdapter):
            event_count = len(service.telemetry.get_recorded_events())
            span_count = len(service.telemetry.get_finished_spans())
        return TelemetrySummaryResponse(
            hive_id=service.hive_id,
            epoch=proof.epoch,
            active_bees=proof.active_bees,
            total_directional_edges=proof.total_directional_edges,
            collusion_discounted_velocity=proof.collusion_discounted_velocity,
            gini_coefficient=proof.gini_coefficient,
            graph_state_hash=proof.graph_state_hash,
            event_count=event_count,
            span_count=span_count,
        )

    return router


class FastAPIHiveRouter:
    """Object-oriented driving adapter wrapping the Hive FastAPI router."""

    def __init__(self, service: HiveServiceLayer) -> None:
        self.service = service
        self.router = create_hive_router(service)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def create_app(service: HiveServiceLayer) -> FastAPI:
    """Create a FastAPI application wired to a HiveServiceLayer instance."""
    app = FastAPI(title=f"nectR Hive API ({service.hive_id})", version="0.1.0")

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        safe_errors = jsonable_encoder(_json_safe_value(exc.errors()))
        return JSONResponse(status_code=422, content={"detail": safe_errors})

    app.include_router(FastAPIHiveRouter(service).router)
    return app
