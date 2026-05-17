from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui.adapters.kernel_view import get_kernel_status
from ui.adapters.pack_view import get_pack_summary, list_available_packs
from ui.adapters.runtime_view import run_task


def test_get_kernel_status_returns_bundle() -> None:
    bundle = get_kernel_status("default_pack")
    assert isinstance(bundle.runtime, dict)
    assert isinstance(bundle.state, dict)
    assert isinstance(bundle.capabilities, list)
    assert bundle.runtime["status"] == "idle"


def test_list_available_packs_contains_default_pack() -> None:
    packs = list_available_packs()
    assert "default_pack" in packs


def test_get_pack_summary_default_pack() -> None:
    summary = get_pack_summary("default_pack")
    assert summary.name == "default_pack"
    assert isinstance(summary.manifest, dict)


def test_run_task_returns_structured_result() -> None:
    result = run_task("hello agent", "default_pack", max_steps=3, trace_enabled=False)
    assert isinstance(result, dict)
    assert "status" in result
    assert "output" in result
    assert isinstance(result.get("state"), dict)
