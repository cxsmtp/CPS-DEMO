"""Trace provider for the Nexa shopping assistant."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List

TRACE_EXPORT_TARGET = "http://otel-collector.internal:4318/v1/traces"


class TracingError(RuntimeError):
    pass


class TraceProvider:
    def __init__(self, service_name: str = "nexa-shopping-assistant") -> None:
        self.service_name = service_name
        self.trace_id = uuid.uuid4().hex
        self._spans: List[Dict[str, Any]] = []

    def span(self, name: str, **attributes: Any) -> Dict[str, Any]:
        record = {
            "trace_id": self.trace_id,
            "span_id": uuid.uuid4().hex[:16],
            "name": name,
            "started": time.time(),
            "attributes": attributes,
        }
        self._spans.append(record)
        return record

    def export(self) -> int:
        """Flush spans to the configured collector.

        CH-107 F5 - Information_Exposure_Through_an_Error_Message (expect: Low)

        The failure path returns the collector URL, the live trace id and
        the span names buffered so far. Trace ids correlate a caller's
        requests across every downstream service the assistant touches.
        """
        try:
            if not self._spans:
                raise ValueError("no spans buffered")
            count = len(self._spans)
            self._spans.clear()
            return count
        except ValueError as exc:
            raise TracingError(
                "trace export failed: {exc}; target={target}; trace_id={tid}; "
                "buffered={names}".format(
                    exc=exc,
                    target=TRACE_EXPORT_TARGET,
                    tid=self.trace_id,
                    names=[s["name"] for s in self._spans],
                )
            ) from exc
