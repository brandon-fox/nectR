"""FastAPI driving adapter exposing HiveServiceLayer operations over HTTP."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from nectr.chain.crypto import SignedTransaction
from nectr.contracts.engine import ContractViolationError
from nectr.services.hive_service import (
    CommandAuthorizationError,
    HiveServiceLayer,
    InvalidSignatureError,
)
from nectr.services.telemetry import TelemetryAdapter

_T = TypeVar("_T")


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


class DualSignedSettleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    learner_tx: SignedTransaction
    tutor_tx: SignedTransaction


class SignedHandshakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    escrow_tx: SignedTransaction
    learner_settle_tx: SignedTransaction
    tutor_settle_tx: SignedTransaction


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


def _execute_command(fn: Callable[[], _T]) -> _T:
    try:
        return fn()
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except CommandAuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except (ContractViolationError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def create_hive_router(service: HiveServiceLayer) -> APIRouter:
    """Build a FastAPI APIRouter delegating all signed commands to HiveServiceLayer."""
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
    def bootstrap_hive(payload: SignedTransaction) -> dict[str, Any]:
        return _execute_command(lambda: service.bootstrap_sponsored_hive(payload))

    @router.post("/bees", response_model=BeeAccountResponse)
    def register_bee(payload: SignedTransaction) -> BeeAccountResponse:
        acct = _execute_command(lambda: service.register_bee(payload))
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
    def allocate_pollen(payload: SignedTransaction) -> dict[str, Any]:
        return _execute_command(lambda: service.allocate_raw_pollen(payload))

    @router.post("/workers/certify")
    def certify_worker(payload: SignedTransaction) -> dict[str, Any]:
        return _execute_command(lambda: service.certify_worker_bee(payload))

    @router.post("/sessions/handshake")
    def execute_handshake(payload: SignedHandshakeRequest) -> dict[str, Any]:
        return _execute_command(
            lambda: service.execute_tutoring_handshake(
                escrow_tx=payload.escrow_tx,
                learner_settle_tx=payload.learner_settle_tx,
                tutor_settle_tx=payload.tutor_settle_tx,
            )
        )

    @router.post("/sessions/escrow", response_model=SessionResponse)
    def create_escrow(payload: SignedTransaction) -> SessionResponse:
        sess = _execute_command(lambda: service.create_barter_escrow(payload))
        return SessionResponse(
            **{k: v for k, v in sess.to_dict().items() if k in SessionResponse.model_fields}
        )

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
    def settle_session(session_id: str, payload: DualSignedSettleRequest) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            if payload.learner_tx.payload.get("session_id") != session_id:
                raise ContractViolationError("Signed payload session_id does not match URL.")
            return service.settle_session(
                learner_tx=payload.learner_tx,
                tutor_tx=payload.tutor_tx,
            )

        return _execute_command(_run)

    @router.post("/sessions/{session_id}/dispute")
    def dispute_session(session_id: str, payload: SignedTransaction) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            if payload.payload.get("session_id") != session_id:
                raise ContractViolationError("Signed payload session_id does not match URL.")
            return service.resolve_disputed_session(payload)

        return _execute_command(_run)

    @router.post("/epochs/mine", response_model=MineEpochResponse)
    def mine_epoch(payload: SignedTransaction) -> MineEpochResponse:
        block = _execute_command(lambda: service.mine_epoch_block(payload))
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
