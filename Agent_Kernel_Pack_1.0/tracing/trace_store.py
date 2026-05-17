from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class TraceStore:
    trace_dir: Path = field(default_factory=lambda: Path("traces"))

    def _trace_path(self, event: dict[str, Any]) -> Path:
        run_id = event.get("run_id") or "unknown"
        session_id = event.get("session_id") or "unknown"
        return self.trace_dir / f"run_{run_id}.jsonl" if run_id != "unknown" else self.trace_dir / f"session_{session_id}.jsonl"

    def append(self, event: dict[str, Any]) -> Path:
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        trace_file = self._trace_path(event)
        event = {**event, "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat(), "trace_version": event.get("trace_version") or "v2"}
        with trace_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        return trace_file
