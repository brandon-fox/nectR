"""Structured observability adapter using structlog and OpenTelemetry SDK."""

from __future__ import annotations

import copy
import io
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TextIO, cast

import structlog
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode
from structlog.typing import EventDict, FilteringBoundLogger, WrappedLogger

_SENSITIVE_KEY_EXACT = frozenset(
    {
        "private_key",
        "secret",
        "secret_key",
        "password",
        "passwd",
        "api_key",
        "auth_token",
        "access_token",
        "refresh_token",
        "bearer_token",
        "signing_key",
        "mnemonic",
        "email",
        "ssn",
    }
)
_SENSITIVE_KEY_FRAGMENTS = (
    "private_key",
    "secret",
    "password",
    "api_key",
    "auth_token",
    "signing_key",
    "mnemonic",
)
_PEM_MARKERS = ("PRIVATE KEY-----", "OPENSSH PRIVATE KEY", "RSA PRIVATE KEY")


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    if lowered in _SENSITIVE_KEY_EXACT:
        return True
    return any(fragment in lowered for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _sanitize_value(key: str, value: Any) -> Any:
    if _is_sensitive_key(key):
        return "[REDACTED]"
    if isinstance(value, str) and any(marker in value for marker in _PEM_MARKERS):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _sanitize_value(str(k), v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(key, item) for item in value]
    return value


def redact_sensitive_fields(
    _logger: WrappedLogger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Structlog processor that redacts secret/PII keys and PEM blobs."""
    sanitized: EventDict = {}
    for key, val in event_dict.items():
        sanitized[key] = _sanitize_value(str(key), val)
    return sanitized


class TelemetryAdapter:
    """TelemetryPort implementation combining structlog and opentelemetry-sdk."""

    def __init__(
        self,
        service_name: str = "nectr-hive-service",
        *,
        stream: TextIO | None = None,
        span_exporter: InMemorySpanExporter | None = None,
    ) -> None:
        self.service_name = service_name
        self._stream: TextIO = stream if stream is not None else io.StringIO()
        self._recorded_events: list[dict[str, Any]] = []
        self._exporter = span_exporter if span_exporter is not None else InMemorySpanExporter()
        self._provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        self._provider.add_span_processor(SimpleSpanProcessor(self._exporter))
        self._tracer = self._provider.get_tracer("nectr.services.telemetry")

        def _capture_processor(
            _logger: WrappedLogger,
            _method_name: str,
            event_dict: EventDict,
        ) -> EventDict:
            self._recorded_events.append(copy.deepcopy(dict(event_dict)))
            return event_dict

        raw_logger = structlog.wrap_logger(
            structlog.PrintLogger(file=self._stream),
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                redact_sensitive_fields,
                _capture_processor,
                structlog.processors.JSONRenderer(sort_keys=True),
            ],
        )
        self._logger: FilteringBoundLogger = cast(FilteringBoundLogger, raw_logger)

    def record_event(
        self,
        event: str,
        *,
        hive_id: str,
        epoch: int | None = None,
        tx_id: str | None = None,
        **fields: Any,
    ) -> None:
        """Emit a structured JSON log event bound to Hive context."""
        payload: dict[str, Any] = {"hive_id": hive_id}
        if epoch is not None:
            payload["epoch"] = epoch
        if tx_id is not None:
            payload["tx_id"] = tx_id
        for key, value in fields.items():
            payload[key] = _sanitize_value(key, value)
        self._logger.info(event, **payload)

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
        """Open an OpenTelemetry span bound to Hive context."""
        with self._tracer.start_as_current_span(name) as otel_span:
            otel_span.set_attribute("nectr.hive_id", hive_id)
            if epoch is not None:
                otel_span.set_attribute("nectr.epoch", epoch)
            if tx_id is not None:
                otel_span.set_attribute("nectr.tx_id", tx_id)
            for key, value in attributes.items():
                sanitized = _sanitize_value(key, value)
                if isinstance(sanitized, (str, bool, int, float)):
                    otel_span.set_attribute(f"nectr.{key}", sanitized)
            try:
                yield
            except BaseException as exc:
                otel_span.record_exception(exc)
                otel_span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise

    def get_recorded_events(self) -> list[dict[str, Any]]:
        """Return deep copies of captured structured log events."""
        return copy.deepcopy(self._recorded_events)

    def get_finished_spans(self) -> tuple[ReadableSpan, ...]:
        """Return finished OpenTelemetry spans from the in-memory exporter."""
        return self._exporter.get_finished_spans()

    def get_log_lines(self) -> list[str]:
        """Return rendered JSON log lines if using an in-memory StringIO stream."""
        if isinstance(self._stream, io.StringIO):
            content = self._stream.getvalue().strip()
            return content.splitlines() if content else []
        return []
