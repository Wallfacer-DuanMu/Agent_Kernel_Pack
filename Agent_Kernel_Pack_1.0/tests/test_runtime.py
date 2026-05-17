from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from core.runtime import AgentRuntime
from core.state import AgentState


ROOT = Path(__file__).resolve().parents[1]


def test_agent_state_defaults() -> None:
    state = AgentState(session_id="s1", task="hello")
    assert state.current_step == 0
    assert state.max_steps == 3
    assert state.finished is False
    assert state.error is None


def test_runtime_run_returns_non_empty_result() -> None:
    runtime = AgentRuntime()
    result = runtime.run("hello")
    assert result


def test_main_runs_with_task() -> None:
    result = subprocess.run(
        [sys.executable, "main.py", "hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip()
