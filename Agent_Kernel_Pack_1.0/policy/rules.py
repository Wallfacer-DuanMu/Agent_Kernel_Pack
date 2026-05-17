from __future__ import annotations

from capabilities.base import RiskLevel
from policy.decisions import Decision, PolicyDecision

DANGEROUS_PATTERNS = [
    "rm -rf",
    "del /s",
    "format",
    "sudo",
    "chmod 777",
    "curl",
    "Invoke-WebRequest",
    "| sh",
    "| iex",
]


def default_rule(tool_name: str, args: dict[str, object], risk_level: RiskLevel) -> PolicyDecision:
    if risk_level == RiskLevel.low:
        return PolicyDecision(Decision.ALLOW, reason="Low-risk tool allowed", risk_level=risk_level.value)

    if tool_name != "run_command":
        return PolicyDecision(Decision.ALLOW, reason="Non-shell tool allowed", risk_level=risk_level.value)

    command = str(args.get("command", "")).lower()
    if any(pattern.lower() in command for pattern in DANGEROUS_PATTERNS):
        return PolicyDecision(Decision.DENY, reason="Dangerous command blocked", risk_level=risk_level.value)

    if command:
        return PolicyDecision(Decision.CONFIRM, reason="Shell command requires confirmation", risk_level=risk_level.value)

    return PolicyDecision(Decision.DENY, reason="Missing command", risk_level=risk_level.value)
