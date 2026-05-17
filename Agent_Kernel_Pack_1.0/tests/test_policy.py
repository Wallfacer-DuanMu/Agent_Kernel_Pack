from capabilities.base import RiskLevel, Tool
from core.state import AgentState
from policy.decisions import Decision
from policy.guard import PolicyGuard


def test_policy_blocks_dangerous_command() -> None:
    guard = PolicyGuard()
    tool = Tool(name="run_command", description="run", risk_level=RiskLevel.high, handler=lambda args: None)
    decision = guard.check(tool, {"command": "rm -rf /"}, AgentState(session_id="s1", task="run rm -rf /"))
    assert decision.decision == Decision.DENY


def test_policy_allows_safe_file_tool() -> None:
    guard = PolicyGuard()
    tool = Tool(name="read_file", description="read", risk_level=RiskLevel.low, handler=lambda args: None)
    decision = guard.check(tool, {"path": "demo.txt"}, AgentState(session_id="s1", task="read demo.txt"))
    assert decision.decision == Decision.ALLOW
