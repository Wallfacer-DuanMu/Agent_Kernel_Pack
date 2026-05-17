from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _coerce_event(event: Any) -> dict[str, Any]:
    if isinstance(event, dict):
        return event
    if is_dataclass(event):
        return asdict(event)
    return {"value": event}


def normalize_trace_events(events: list[Any] | None) -> list[dict[str, Any]]:
    if not events:
        return []
    normalized: list[dict[str, Any]] = []
    for event in events:
        item = _coerce_event(event)
        item.setdefault("trace_version", item.get("trace_version") or "legacy")
        item.setdefault("session_id", item.get("session_id") or "legacy-session")
        item.setdefault("run_id", item.get("run_id") or "legacy-run")
        item.setdefault("event_type", item.get("event_type") or "legacy_step")
        item.setdefault("status", item.get("status") or ("error" if item.get("error") else "success"))
        normalized.append(item)
    return normalized


def load_trace_file(path: str | Path) -> list[dict[str, Any]]:
    trace_path = Path(path)
    if not trace_path.exists() or trace_path.is_dir():
        return []

    events: list[dict[str, Any]] = []
    if trace_path.suffix.lower() == ".jsonl":
        for line in trace_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"raw": line})
        return normalize_trace_events(events)

    if trace_path.suffix.lower() == ".json":
        try:
            payload = json.loads(trace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if isinstance(payload, list):
            return normalize_trace_events(payload)
        if isinstance(payload, dict):
            return normalize_trace_events(payload.get("events") or payload.get("trace_events") or [])
    return []


def load_latest_trace(trace_dir: str | Path = "traces") -> tuple[list[dict[str, Any]], str]:
    directory = Path(trace_dir)
    if not directory.exists():
        return [], ""
    candidates = sorted(directory.glob("run_*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        candidates = sorted(directory.glob("session_*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        candidates = sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        return [], ""
    latest = candidates[0]
    return load_trace_file(latest), str(latest)


def load_latest_run(trace_dir: str | Path = "traces") -> tuple[list[dict[str, Any]], str]:
    return load_latest_trace(trace_dir)


def load_trace_events_for_run(run_id: str, trace_dir: str | Path = "traces") -> tuple[list[dict[str, Any]], str]:
    if not run_id:
        return [], ""
    path = Path(trace_dir) / f"run_{run_id}.jsonl"
    if not path.exists():
        return [], ""
    return load_trace_file(path), str(path)


def build_trace_timeline(events: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    timeline = []
    for event in normalize_trace_events(events):
        timeline.append(
            {
                "step": event.get("step", "?"),
                "action_type": event.get("action_type", "unknown"),
                "event_type": event.get("event_type", "legacy_step"),
                "tool_name": event.get("tool_name", ""),
                "policy_decision": event.get("policy_decision", ""),
                "status": event.get("status", "success"),
                "result_summary": event.get("result_summary", ""),
                "raw": event,
            }
        )
    return timeline


def get_empty_timeline() -> list[str]:
    return ["No runtime trace available yet."]
