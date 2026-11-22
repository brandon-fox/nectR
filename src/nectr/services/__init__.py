"""Hive Service Layer (Owned by contracts-service-agent)."""

from nectr.services.api import FastAPIHiveRouter, create_app, create_hive_router
from nectr.services.hive_service import (
    CommandAuthorizationError,
    HiveServiceLayer,
    InvalidSignatureError,
    compute_gini_coefficient,
)
from nectr.services.persistence import SQLModelHiveRepository, run_migrations
from nectr.services.ports import (
    HiveRepositoryPort,
    HiveSnapshot,
    InMemoryHiveRepository,
    NoOpTelemetry,
    TelemetryPort,
)
from nectr.services.telemetry import TelemetryAdapter

__all__ = [
    "CommandAuthorizationError",
    "FastAPIHiveRouter",
    "HiveRepositoryPort",
    "HiveServiceLayer",
    "HiveSnapshot",
    "InMemoryHiveRepository",
    "InvalidSignatureError",
    "NoOpTelemetry",
    "SQLModelHiveRepository",
    "TelemetryAdapter",
    "TelemetryPort",
    "compute_gini_coefficient",
    "create_app",
    "create_hive_router",
    "run_migrations",
]
