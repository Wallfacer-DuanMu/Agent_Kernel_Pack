from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    respond = "respond"
    call_tool = "call_tool"
    request_approval = "request_approval"
    finish = "finish"
    fail = "fail"


@dataclass
class Action:
    """Unified action emitted by the decision provider."""

    type: ActionType
    content: str = ""
    tool_name: str = ""
    tool_args: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


def parse_action(value: Action | dict[str, Any]) -> Action:
    """Parse a dictionary-like action into an Action instance."""

    if isinstance(value, Action):
        return value
    action_type = ActionType(value.get("type", ActionType.respond.value))
    return Action(
        type=action_type,
        content=value.get("content", ""),
        tool_name=value.get("tool_name", ""),
        tool_args=dict(value.get("tool_args", {})),
        reason=value.get("reason", ""),
    )
