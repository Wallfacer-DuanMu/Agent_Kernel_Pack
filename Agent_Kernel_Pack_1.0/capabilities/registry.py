from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from capabilities.base import Tool


class CapabilityError(RuntimeError):
    pass


@dataclass
class CapabilityRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        if tool.name in self.tools:
            raise CapabilityError(f"Tool already registered: {tool.name}")
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self.tools[name]
        except KeyError as exc:
            raise CapabilityError(f"Tool not found: {name}") from exc

    def list_tools(self) -> list[str]:
        return sorted(self.tools)

    def execute(self, name: str, args: dict[str, Any]) -> Any:
        tool = self.get(name)
        return tool.execute(args)
