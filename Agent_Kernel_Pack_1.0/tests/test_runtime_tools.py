from pathlib import Path

from core.runtime import AgentRuntime


def test_runtime_list_dir_creates_trace(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("hello keyword", encoding="utf-8")
    runtime = AgentRuntime(trace_dir=tmp_path / "traces")
    result = runtime.run(f"list {tmp_path}")
    assert result
    assert any((tmp_path / "traces").glob("*.jsonl"))
