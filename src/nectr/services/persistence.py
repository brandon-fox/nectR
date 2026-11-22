"""SQLModel persistence adapter and programmatic Alembic migration runner."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from sqlalchemy import BigInteger, Engine, delete, event
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, col, create_engine, select

from nectr.contracts.engine import from_micro_units, to_micro_units
from nectr.services.ports import HiveSnapshot


class HiveStateRecord(SQLModel, table=True):
    """Top-level persisted Hive configuration, reserves, and epoch state."""

    __tablename__ = "hive_states"

    hive_id: str = Field(primary_key=True)
    difficulty: int
    collusion_alpha: float
    lineage_gamma: float
    accepted_status_peer_threshold: int
    comb_reserve: float
    total_minted_supply: float
    comb_reserve_units: int = Field(default=0, sa_type=BigInteger)
    total_minted_supply_units: int = Field(default=0, sa_type=BigInteger)
    current_epoch: int
    mempool_json: str = Field(default="[]")


class BeeAccountRecord(SQLModel, table=True):
    """Persisted BeeAccount state scoped to a Hive."""

    __tablename__ = "bee_accounts"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    bee_id: str = Field(primary_key=True)
    home_hive_id: str
    role: str
    raw_pollen_balance: float
    liquid_nectr_balance: float
    raw_pollen_units: int = Field(default=0, sa_type=BigInteger)
    liquid_nectr_units: int = Field(default=0, sa_type=BigInteger)
    certified_subjects_json: str
    accepted_in_hives_json: str
    distinct_peers_tutored_json: str
    royal_jelly_earned: float
    royal_jelly_units: int = Field(default=0, sa_type=BigInteger)


class BeeKeyRecord(SQLModel, table=True):
    """Persisted Ed25519 public key and monotonic nonce per Bee in a Hive."""

    __tablename__ = "bee_keys"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    bee_id: str = Field(primary_key=True)
    public_key: str
    last_nonce: int = Field(default=0, sa_type=BigInteger)


class ServiceBarterSessionRecord(SQLModel, table=True):
    """Persisted DirectionalServiceBarterContract session state."""

    __tablename__ = "service_barter_sessions"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    session_id: str = Field(primary_key=True)
    tutor_id: str
    learner_id: str
    subject_id: str
    duration_hours: float
    escrowed_amount: float
    escrowed_units: int = Field(default=0, sa_type=BigInteger)
    token_state: str
    reciprocal_subject_id: str | None = None
    status: str
    learner_attestation_score: float
    tutor_comprehension_hash: str
    effective_weight: float


class PairwiseCountRecord(SQLModel, table=True):
    """Persisted symmetric pairwise interaction counts for anti-collusion decay."""

    __tablename__ = "pairwise_counts"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    bee_a: str = Field(primary_key=True)
    bee_b: str = Field(primary_key=True)
    tx_count: int


class SubjectLineageRecord(SQLModel, table=True):
    """Persisted directional subject learning lineage."""

    __tablename__ = "subject_lineage"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    learner_id: str = Field(primary_key=True)
    subject_id: str = Field(primary_key=True)
    tutors_json: str


class TutorEffectivenessRecord(SQLModel, table=True):
    """Persisted cumulative collusion-discounted tutor effectiveness."""

    __tablename__ = "tutor_effectiveness"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    tutor_id: str = Field(primary_key=True)
    effectiveness: float


class SettledTxRecord(SQLModel, table=True):
    """Persisted ordered log of settled contract transactions."""

    __tablename__ = "settled_tx_logs"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    seq_index: int = Field(primary_key=True)
    session_id: str
    tx_json: str


class BlockRecord(SQLModel, table=True):
    """Persisted PoUW-PoW blockchain blocks for a Hive."""

    __tablename__ = "hive_blocks"

    hive_id: str = Field(primary_key=True, foreign_key="hive_states.hive_id")
    height: int = Field(primary_key=True)
    block_hash: str
    prev_hash: str
    merkle_root: str
    knowledge_graph_root: str
    timestamp: float
    block_json: str


def run_migrations(engine: Engine) -> None:
    """Run programmatic Alembic migrations to head using an active engine connection."""
    migrations_dir = Path(__file__).resolve().parent / "migrations"
    cfg = Config()
    cfg.set_main_option("script_location", str(migrations_dir).replace("%", "%%"))
    cfg.set_main_option(
        "sqlalchemy.url",
        engine.url.render_as_string(hide_password=False).replace("%", "%%"),
    )
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")


class SQLModelHiveRepository:
    """SQLModel + Alembic implementation of HiveRepositoryPort."""

    def __init__(self, database_url: str, *, auto_migrate: bool = True) -> None:
        self.database_url = database_url
        self._auto_migrate = auto_migrate
        self._initialized = False
        self._session_var: ContextVar[Session | None] = ContextVar(
            f"nectr_sqlmodel_session_{id(self)}",
            default=None,
        )

        is_sqlite = database_url.startswith("sqlite")
        is_memory = is_sqlite and (
            database_url == "sqlite:///:memory:" or ":memory:" in database_url
        )
        connect_args: dict[str, Any] = {"check_same_thread": False} if is_sqlite else {}
        if is_memory:
            self.engine = create_engine(
                database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(database_url, connect_args=connect_args)

        if is_sqlite:

            @event.listens_for(self.engine, "connect")
            def _configure_sqlite(dbapi_connection: Any, _connection_record: Any) -> None:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                if not is_memory:
                    cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()

    def initialize(self) -> None:
        """Apply Alembic migrations idempotently."""
        if self._auto_migrate:
            run_migrations(self.engine)
        else:
            SQLModel.metadata.create_all(self.engine)
        self._initialized = True

    def close(self) -> None:
        """Dispose the underlying SQLAlchemy engine and release file handles."""
        self.engine.dispose()

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Run operations in an atomic SQLAlchemy transaction (or nested savepoint)."""
        self._ensure_initialized()
        active = self._session_var.get()
        if active is not None:
            with active.begin_nested():
                yield
            return

        with Session(self.engine, expire_on_commit=False) as session:
            token = self._session_var.set(session)
            try:
                yield
                session.commit()
            except BaseException:
                session.rollback()
                raise
            finally:
                self._session_var.reset(token)

    def _run_with_session(self, fn: Any) -> Any:
        self._ensure_initialized()
        active = self._session_var.get()
        if active is not None:
            return fn(active)
        with Session(self.engine, expire_on_commit=False) as session:
            return fn(session)

    def save_hive_snapshot(self, snapshot: HiveSnapshot) -> None:
        """Persist full Hive snapshot atomically within the current or a new transaction."""
        active = self._session_var.get()
        if active is None:
            with self.transaction():
                self.save_hive_snapshot(snapshot)
            return

        contract = snapshot.contract_state
        hive_id = snapshot.hive_id
        existing = active.get(HiveStateRecord, hive_id)
        mempool_json = json.dumps(snapshot.mempool, sort_keys=True)
        comb_units = int(
            contract.get("comb_reserve_units", to_micro_units(float(contract["comb_reserve"])))
        )
        supply_units = int(
            contract.get(
                "total_minted_supply_units",
                to_micro_units(float(contract["total_minted_supply"])),
            )
        )
        if existing is None:
            active.add(
                HiveStateRecord(
                    hive_id=hive_id,
                    difficulty=snapshot.difficulty,
                    collusion_alpha=float(contract["collusion_alpha"]),
                    lineage_gamma=float(contract["lineage_gamma"]),
                    accepted_status_peer_threshold=int(contract["accepted_status_peer_threshold"]),
                    comb_reserve=from_micro_units(comb_units),
                    total_minted_supply=from_micro_units(supply_units),
                    comb_reserve_units=comb_units,
                    total_minted_supply_units=supply_units,
                    current_epoch=snapshot.current_epoch,
                    mempool_json=mempool_json,
                )
            )
        else:
            existing.difficulty = snapshot.difficulty
            existing.collusion_alpha = float(contract["collusion_alpha"])
            existing.lineage_gamma = float(contract["lineage_gamma"])
            existing.accepted_status_peer_threshold = int(
                contract["accepted_status_peer_threshold"]
            )
            existing.comb_reserve = from_micro_units(comb_units)
            existing.total_minted_supply = from_micro_units(supply_units)
            existing.comb_reserve_units = comb_units
            existing.total_minted_supply_units = supply_units
            existing.current_epoch = snapshot.current_epoch
            existing.mempool_json = mempool_json
        active.flush()

        for model in (
            BlockRecord,
            SettledTxRecord,
            TutorEffectivenessRecord,
            SubjectLineageRecord,
            PairwiseCountRecord,
            ServiceBarterSessionRecord,
            BeeKeyRecord,
            BeeAccountRecord,
        ):
            active.exec(delete(model).where(col(model.hive_id) == hive_id))
        active.flush()

        for bee_id, public_key in sorted(snapshot.bee_public_keys.items()):
            active.add(
                BeeKeyRecord(
                    hive_id=hive_id,
                    bee_id=bee_id,
                    public_key=public_key,
                    last_nonce=int(snapshot.bee_nonces.get(bee_id, 0)),
                )
            )

        for acct in contract["accounts"].values():
            pollen_units = int(
                acct.get("raw_pollen_units", to_micro_units(float(acct["raw_pollen_balance"])))
            )
            liquid_units = int(
                acct.get("liquid_nectr_units", to_micro_units(float(acct["liquid_nectr_balance"])))
            )
            rj_units = int(
                acct.get("royal_jelly_units", to_micro_units(float(acct["royal_jelly_earned"])))
            )
            active.add(
                BeeAccountRecord(
                    hive_id=hive_id,
                    bee_id=acct["bee_id"],
                    home_hive_id=acct["home_hive_id"],
                    role=acct["role"],
                    raw_pollen_balance=from_micro_units(pollen_units),
                    liquid_nectr_balance=from_micro_units(liquid_units),
                    raw_pollen_units=pollen_units,
                    liquid_nectr_units=liquid_units,
                    certified_subjects_json=json.dumps(acct["certified_subjects"]),
                    accepted_in_hives_json=json.dumps(acct["accepted_in_hives"]),
                    distinct_peers_tutored_json=json.dumps(acct["distinct_peers_tutored_in_hive"]),
                    royal_jelly_earned=from_micro_units(rj_units),
                    royal_jelly_units=rj_units,
                )
            )

        for sess in contract["sessions"].values():
            escrowed_units = int(
                sess.get("escrowed_units", to_micro_units(float(sess["escrowed_amount"])))
            )
            active.add(
                ServiceBarterSessionRecord(
                    hive_id=hive_id,
                    session_id=sess["session_id"],
                    tutor_id=sess["tutor_id"],
                    learner_id=sess["learner_id"],
                    subject_id=sess["subject_id"],
                    duration_hours=float(sess["duration_hours"]),
                    escrowed_amount=from_micro_units(escrowed_units),
                    escrowed_units=escrowed_units,
                    token_state=sess["token_state"],
                    reciprocal_subject_id=sess["reciprocal_subject_id"],
                    status=sess["status"],
                    learner_attestation_score=float(sess["learner_attestation_score"]),
                    tutor_comprehension_hash=sess["tutor_comprehension_hash"],
                    effective_weight=float(sess["effective_weight"]),
                )
            )

        for pair_entry in contract["pairwise_counts"]:
            bee_a, bee_b = pair_entry["pair"]
            active.add(
                PairwiseCountRecord(
                    hive_id=hive_id,
                    bee_a=bee_a,
                    bee_b=bee_b,
                    tx_count=int(pair_entry["count"]),
                )
            )

        for lineage_entry in contract["subject_lineage"]:
            active.add(
                SubjectLineageRecord(
                    hive_id=hive_id,
                    learner_id=lineage_entry["learner_id"],
                    subject_id=lineage_entry["subject_id"],
                    tutors_json=json.dumps(lineage_entry["tutors"]),
                )
            )

        for tutor_id, effectiveness in contract["tutor_effectiveness"].items():
            active.add(
                TutorEffectivenessRecord(
                    hive_id=hive_id,
                    tutor_id=tutor_id,
                    effectiveness=float(effectiveness),
                )
            )

        for idx, tx in enumerate(contract["settled_tx_log"]):
            active.add(
                SettledTxRecord(
                    hive_id=hive_id,
                    seq_index=idx,
                    session_id=str(tx.get("session_id", "")),
                    tx_json=json.dumps(tx, sort_keys=True),
                )
            )

        for block in snapshot.blocks:
            header = block["header"]
            active.add(
                BlockRecord(
                    hive_id=hive_id,
                    height=int(header["height"]),
                    block_hash=str(block.get("block_hash", "")),
                    prev_hash=str(header["prev_hash"]),
                    merkle_root=str(header["merkle_root"]),
                    knowledge_graph_root=str(header["knowledge_graph_root"]),
                    timestamp=float(header["timestamp"]),
                    block_json=json.dumps(block, sort_keys=True),
                )
            )
        active.flush()

    def load_hive_snapshot(self, hive_id: str) -> HiveSnapshot | None:
        """Load the full Hive snapshot from SQLite/SQLModel storage."""

        def _load(session: Session) -> HiveSnapshot | None:
            hive_row = session.get(HiveStateRecord, hive_id)
            if hive_row is None:
                return None

            account_rows = session.exec(
                select(BeeAccountRecord)
                .where(col(BeeAccountRecord.hive_id) == hive_id)
                .order_by(col(BeeAccountRecord.bee_id))
            ).all()
            session_rows = session.exec(
                select(ServiceBarterSessionRecord)
                .where(col(ServiceBarterSessionRecord.hive_id) == hive_id)
                .order_by(col(ServiceBarterSessionRecord.session_id))
            ).all()
            pair_rows = session.exec(
                select(PairwiseCountRecord)
                .where(col(PairwiseCountRecord.hive_id) == hive_id)
                .order_by(col(PairwiseCountRecord.bee_a), col(PairwiseCountRecord.bee_b))
            ).all()
            lineage_rows = session.exec(
                select(SubjectLineageRecord)
                .where(col(SubjectLineageRecord.hive_id) == hive_id)
                .order_by(
                    col(SubjectLineageRecord.learner_id),
                    col(SubjectLineageRecord.subject_id),
                )
            ).all()
            eff_rows = session.exec(
                select(TutorEffectivenessRecord)
                .where(col(TutorEffectivenessRecord.hive_id) == hive_id)
                .order_by(col(TutorEffectivenessRecord.tutor_id))
            ).all()
            tx_rows = session.exec(
                select(SettledTxRecord)
                .where(col(SettledTxRecord.hive_id) == hive_id)
                .order_by(col(SettledTxRecord.seq_index))
            ).all()
            block_rows = session.exec(
                select(BlockRecord)
                .where(col(BlockRecord.hive_id) == hive_id)
                .order_by(col(BlockRecord.height))
            ).all()
            key_rows = session.exec(
                select(BeeKeyRecord)
                .where(col(BeeKeyRecord.hive_id) == hive_id)
                .order_by(col(BeeKeyRecord.bee_id))
            ).all()

            accounts = {row.bee_id: _account_row_to_dict(row) for row in account_rows}
            sessions = {row.session_id: _session_row_to_dict(row) for row in session_rows}
            contract_state: dict[str, Any] = {
                "schema_version": 1,
                "hive_id": hive_row.hive_id,
                "collusion_alpha": hive_row.collusion_alpha,
                "lineage_gamma": hive_row.lineage_gamma,
                "accepted_status_peer_threshold": hive_row.accepted_status_peer_threshold,
                "comb_reserve": from_micro_units(hive_row.comb_reserve_units),
                "comb_reserve_units": hive_row.comb_reserve_units,
                "total_minted_supply": from_micro_units(hive_row.total_minted_supply_units),
                "total_minted_supply_units": hive_row.total_minted_supply_units,
                "accounts": accounts,
                "sessions": sessions,
                "pairwise_counts": [
                    {"pair": [row.bee_a, row.bee_b], "count": row.tx_count} for row in pair_rows
                ],
                "subject_lineage": [
                    {
                        "learner_id": row.learner_id,
                        "subject_id": row.subject_id,
                        "tutors": json.loads(row.tutors_json),
                    }
                    for row in lineage_rows
                ],
                "tutor_effectiveness": {row.tutor_id: row.effectiveness for row in eff_rows},
                "settled_tx_log": [json.loads(row.tx_json) for row in tx_rows],
            }
            blocks = [json.loads(row.block_json) for row in block_rows]
            mempool: list[dict[str, Any]] = json.loads(hive_row.mempool_json)
            bee_public_keys = {row.bee_id: row.public_key for row in key_rows}
            bee_nonces = {row.bee_id: row.last_nonce for row in key_rows}
            return HiveSnapshot(
                hive_id=hive_row.hive_id,
                difficulty=hive_row.difficulty,
                current_epoch=hive_row.current_epoch,
                contract_state=contract_state,
                blocks=blocks,
                mempool=mempool,
                bee_public_keys=bee_public_keys,
                bee_nonces=bee_nonces,
            )

        res: HiveSnapshot | None = self._run_with_session(_load)
        return res

    def get_account(self, hive_id: str, bee_id: str) -> dict[str, Any] | None:
        """Fetch a single BeeAccount dict from persistence."""

        def _get(session: Session) -> dict[str, Any] | None:
            row = session.get(BeeAccountRecord, (hive_id, bee_id))
            return None if row is None else _account_row_to_dict(row)

        res: dict[str, Any] | None = self._run_with_session(_get)
        return res

    def list_accounts(self, hive_id: str) -> list[dict[str, Any]]:
        """List all BeeAccount dicts for a Hive."""

        def _list(session: Session) -> list[dict[str, Any]]:
            rows = session.exec(
                select(BeeAccountRecord)
                .where(col(BeeAccountRecord.hive_id) == hive_id)
                .order_by(col(BeeAccountRecord.bee_id))
            ).all()
            return [_account_row_to_dict(row) for row in rows]

        res: list[dict[str, Any]] = self._run_with_session(_list)
        return res

    def get_session(self, hive_id: str, session_id: str) -> dict[str, Any] | None:
        """Fetch a single ServiceBarterSession dict from persistence."""

        def _get(session: Session) -> dict[str, Any] | None:
            row = session.get(ServiceBarterSessionRecord, (hive_id, session_id))
            return None if row is None else _session_row_to_dict(row)

        res: dict[str, Any] | None = self._run_with_session(_get)
        return res

    def list_sessions(self, hive_id: str) -> list[dict[str, Any]]:
        """List all ServiceBarterSession dicts for a Hive."""

        def _list(session: Session) -> list[dict[str, Any]]:
            rows = session.exec(
                select(ServiceBarterSessionRecord)
                .where(col(ServiceBarterSessionRecord.hive_id) == hive_id)
                .order_by(col(ServiceBarterSessionRecord.session_id))
            ).all()
            return [_session_row_to_dict(row) for row in rows]

        res: list[dict[str, Any]] = self._run_with_session(_list)
        return res

    def list_blocks(self, hive_id: str) -> list[dict[str, Any]]:
        """List all persisted blockchain blocks ordered by height."""

        def _list(session: Session) -> list[dict[str, Any]]:
            rows = session.exec(
                select(BlockRecord)
                .where(col(BlockRecord.hive_id) == hive_id)
                .order_by(col(BlockRecord.height))
            ).all()
            return [json.loads(row.block_json) for row in rows]

        res: list[dict[str, Any]] = self._run_with_session(_list)
        return res


def _account_row_to_dict(row: BeeAccountRecord) -> dict[str, Any]:
    return {
        "bee_id": row.bee_id,
        "home_hive_id": row.home_hive_id,
        "role": row.role,
        "raw_pollen_balance": from_micro_units(row.raw_pollen_units),
        "raw_pollen_units": row.raw_pollen_units,
        "liquid_nectr_balance": from_micro_units(row.liquid_nectr_units),
        "liquid_nectr_units": row.liquid_nectr_units,
        "certified_subjects": json.loads(row.certified_subjects_json),
        "accepted_in_hives": json.loads(row.accepted_in_hives_json),
        "distinct_peers_tutored_in_hive": json.loads(row.distinct_peers_tutored_json),
        "royal_jelly_earned": from_micro_units(row.royal_jelly_units),
        "royal_jelly_units": row.royal_jelly_units,
    }


def _session_row_to_dict(row: ServiceBarterSessionRecord) -> dict[str, Any]:
    return {
        "session_id": row.session_id,
        "hive_id": row.hive_id,
        "tutor_id": row.tutor_id,
        "learner_id": row.learner_id,
        "subject_id": row.subject_id,
        "duration_hours": row.duration_hours,
        "escrowed_amount": from_micro_units(row.escrowed_units),
        "escrowed_units": row.escrowed_units,
        "token_state": row.token_state,
        "reciprocal_subject_id": row.reciprocal_subject_id,
        "status": row.status,
        "learner_attestation_score": row.learner_attestation_score,
        "tutor_comprehension_hash": row.tutor_comprehension_hash,
        "effective_weight": row.effective_weight,
    }
