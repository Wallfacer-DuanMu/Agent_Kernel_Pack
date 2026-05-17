from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONFIRM = "confirm"


@dataclass
class PolicyDecision:
    decision: Decision
    reason: str = ""
    risk_level: str = "low"
