from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ToolProtocol(Protocol):
    name: str
    description: str
    args_schema: dict[str, Any]
    risk_level: RiskLevel

    def execute(self, args: dict[str, Any]) -> Any:
        ...


@dataclass
class Tool:
    name: str
    description: str
    args_schema: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.low
    handler: Callable[[dict[str, Any]], Any] | None = None

    def execute(self, args: dict[str, Any]) -> Any:
        if self.handler is None:
            raise NotImplementedError(f"Tool {self.name} has no handler")
        return self.handler(args)
