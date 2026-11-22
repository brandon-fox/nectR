"""Hexagonal ports and lightweight default adapters for the nectR Hive Service Layer."""

from __future__ import annotations

import copy
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class HiveSnapshot:
    """Transport-agnostic snapshot of complete HiveServiceLayer state."""

    hive_id: str
    difficulty: int
    current_epoch: int
    contract_state: dict[str, Any]
    blocks: list[dict[str, Any]]
    mempool: list[dict[str, Any]]


@runtime_checkable
class HiveRepositoryPort(Protocol):
    """Persistence port for atomic Hive state storage and query operations."""

    def initialize(self) -> None:
        """Initialize storage schema or run migrations idempotently."""
        ...

    def transaction(self) -> AbstractContextManager[None]:
        """Execute mutations inside an atomic transaction that rolls back on exception."""
        ...

    def save_hive_snapshot(self, snapshot: HiveSnapshot) -> None:
        """Persist a full Hive snapshot within the active transaction or unit of work."""
        ...

    def load_hive_snapshot(self, hive_id: str) -> HiveSnapshot | None:
        """Load the latest persisted snapshot for a Hive, or None if not found."""
        ...

    def get_account(self, hive_id: str, bee_id: str) -> dict[str, Any] | None:
        """Fetch a serialized BeeAccount record by ID."""
        ...

    def list_accounts(self, hive_id: str) -> list[dict[str, Any]]:
        """List all serialized BeeAccount records for a Hive."""
        ...

    def get_session(self, hive_id: str, session_id: str) -> dict[str, Any] | None:
        """Fetch a serialized ServiceBarterSession record by ID."""
        ...

    def list_sessions(self, hive_id: str) -> list[dict[str, Any]]:
        """List all serialized ServiceBarterSession records for a Hive."""
        ...

    def list_blocks(self, hive_id: str) -> list[dict[str, Any]]:
        """List all serialized blockchain blocks for a Hive ordered by height."""
        ...


@runtime_checkable
class TelemetryPort(Protocol):
    """Observability port for structured logging and distributed tracing spans."""

    def record_event(
        self,
        event: str,
        *,
        hive_id: str,
        epoch: int | None = None,
        tx_id: str | None = None,
        **fields: Any,
    ) -> None:
        """Emit a structured event bound to Hive context without leaking secrets."""
        ...

    def span(
        self,
        name: str,
        *,
        hive_id: str,
        epoch: int | None = None,
        tx_id: str | None = None,
        **attributes: Any,
    ) -> AbstractContextManager[None]:
        """Open a tracing span bound to Hive context."""
        ...


class InMemoryHiveRepository:
    """Default zero-dependency repository keeping Hive state in memory with transactional rollback."""

    def __init__(self) -> None:
        self._snapshots: dict[str, HiveSnapshot] = {}
        self._tx_depth: int = 0

    def initialize(self) -> None:
        """No-op schema initialization for in-memory repository."""

    @contextmanager
    def transaction(self) -> Iterator[None]:
        backup = copy.deepcopy(self._snapshots)
        self._tx_depth += 1
        try:
            yield
        except BaseException:
            self._snapshots = backup
            raise
        finally:
            self._tx_depth -= 1

    def save_hive_snapshot(self, snapshot: HiveSnapshot) -> None:
        self._snapshots[snapshot.hive_id] = copy.deepcopy(snapshot)

    def load_hive_snapshot(self, hive_id: str) -> HiveSnapshot | None:
        snap = self._snapshots.get(hive_id)
        return copy.deepcopy(snap) if snap is not None else None

    def get_account(self, hive_id: str, bee_id: str) -> dict[str, Any] | None:
        snap = self._snapshots.get(hive_id)
        if snap is None:
            return None
        accounts: dict[str, dict[str, Any]] = snap.contract_state.get("accounts", {})
        acct = accounts.get(bee_id)
        return copy.deepcopy(acct) if acct is not None else None

    def list_accounts(self, hive_id: str) -> list[dict[str, Any]]:
        snap = self._snapshots.get(hive_id)
        if snap is None:
            return []
        accounts: dict[str, dict[str, Any]] = snap.contract_state.get("accounts", {})
        return [copy.deepcopy(accounts[k]) for k in sorted(accounts)]

    def get_session(self, hive_id: str, session_id: str) -> dict[str, Any] | None:
        snap = self._snapshots.get(hive_id)
        if snap is None:
            return None
        sessions: dict[str, dict[str, Any]] = snap.contract_state.get("sessions", {})
        sess = sessions.get(session_id)
        return copy.deepcopy(sess) if sess is not None else None

    def list_sessions(self, hive_id: str) -> list[dict[str, Any]]:
        snap = self._snapshots.get(hive_id)
        if snap is None:
            return []
        sessions: dict[str, dict[str, Any]] = snap.contract_state.get("sessions", {})
        return [copy.deepcopy(sessions[k]) for k in sorted(sessions)]

    def list_blocks(self, hive_id: str) -> list[dict[str, Any]]:
        snap = self._snapshots.get(hive_id)
        if snap is None:
            return []
        return copy.deepcopy(snap.blocks)


class NoOpTelemetry:
    """Default zero-noise telemetry adapter when no TelemetryAdapter is configured."""

    def record_event(
        self,
        event: str,
        *,
        hive_id: str,
        epoch: int | None = None,
        tx_id: str | None = None,
        **fields: Any,
    ) -> None:
        """Discard telemetry events cleanly."""

    @contextmanager
    def span(
        self,
        name: str,
        *,
        hive_id: str,
        epoch: int | None = None,
        tx_id: str | None = None,
        **attributes: Any,
    ) -> Iterator[None]:
        """No-op span context manager."""
        yield
