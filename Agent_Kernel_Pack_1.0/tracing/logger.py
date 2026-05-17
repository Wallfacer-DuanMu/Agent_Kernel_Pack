from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tracing.trace_store import TraceStore


@dataclass
class TraceLogger:
    store: TraceStore

    def log(self, event: dict[str, Any]):
        return self.store.append(event)

    def start_run(self, event: dict[str, Any]):
        return self.log({**event, "event_type": "run_started"})

    def finish_run(self, event: dict[str, Any]):
        return self.log({**event, "event_type": "run_finished"})
