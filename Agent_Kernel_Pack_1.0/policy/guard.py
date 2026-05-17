from __future__ import annotations

from dataclasses import dataclass, field

from capabilities.base import Tool
from core.state import AgentState
from policy.decisions import Decision, PolicyDecision
from policy.rules import default_rule


@dataclass
class PolicyGuard:
    auto_confirm: bool = False
    extra_rules: list[object] = field(default_factory=list)

    def check(self, tool: Tool, args: dict[str, object], state: AgentState) -> PolicyDecision:
        decision = default_rule(tool.name, args, tool.risk_level)
        if decision.decision == Decision.CONFIRM and self.auto_confirm:
            return PolicyDecision(Decision.ALLOW, reason=f"Auto-confirmed: {decision.reason}", risk_level=decision.risk_level)
        return decision
