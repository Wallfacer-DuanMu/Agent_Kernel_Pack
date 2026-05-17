from __future__ import annotations

from pathlib import Path

from core.loader import PackLoader
from core.runtime import AgentRuntime
from core.state import AgentState


ROOT = Path(__file__).resolve().parents[1]


def test_default_pack_exposes_components() -> None:
    pack = PackLoader(ROOT).load_pack("default_pack")
    assert pack.workflow is not None
    assert pack.prompts
    assert callable(pack.output_renderer)
    assert isinstance(pack.policy_rules, list)


def test_default_pack_output_renderer() -> None:
    pack = PackLoader(ROOT).load_pack("default_pack")
    state = AgentState(session_id="s1", task="hello")
    assert pack.output_renderer is not None
    assert pack.output_renderer("done", state) == "done"


def test_runtime_uses_default_pack_by_default() -> None:
    runtime = AgentRuntime()
    assert runtime.loaded_pack is not None
    assert runtime.loaded_pack.name == "default_pack"
