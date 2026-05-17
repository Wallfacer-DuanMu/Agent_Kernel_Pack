from capabilities.base import RiskLevel, Tool
from capabilities.registry import CapabilityError, CapabilityRegistry


def test_registry_register_and_list() -> None:
    registry = CapabilityRegistry()
    registry.register(Tool(name="demo", description="demo", risk_level=RiskLevel.low, handler=lambda args: "ok"))
    assert registry.list_tools() == ["demo"]


def test_registry_missing_tool_raises() -> None:
    registry = CapabilityRegistry()
    try:
        registry.get("missing")
    except CapabilityError as exc:
        assert "Tool not found" in str(exc)
