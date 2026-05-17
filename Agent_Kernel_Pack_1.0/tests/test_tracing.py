from pathlib import Path

from tracing.trace_store import TraceStore


def test_trace_store_writes_jsonl(tmp_path: Path) -> None:
    store = TraceStore(tmp_path)
    path = store.append({"session_id": "abc", "step": 1, "action_type": "respond"})
    assert path.exists()
    assert path.read_text(encoding="utf-8").strip()
