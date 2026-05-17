from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from core.runtime import AgentRuntime


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_runs_with_explicit_default_pack() -> None:
    runtime = AgentRuntime(pack_name_or_path="default_pack")
    result = runtime.run("hello")
    assert result


def test_main_accepts_pack_name() -> None:
    result = subprocess.run(
        [sys.executable, "main.py", "--pack", "default_pack", "hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Pack: default_pack" in result.stdout


def test_missing_pack_returns_clear_error() -> None:
    result = subprocess.run(
        [sys.executable, "main.py", "--pack", "not_exist_pack", "hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Pack load error" in result.stdout
