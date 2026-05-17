from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class StepRecord:
    """A single runtime step record."""

    step: int
    action_type: str
    content: str = ""
    reason: str = ""
    tool_name: str = ""
    tool_args: dict[str, Any] = field(default_factory=dict)
    policy_decision: str = ""
    result: str = ""
    error: str = ""
    event_type: str = "step_recorded"
    status: str = "success"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ToolResult:
    """Minimal result record for a tool execution."""

    tool_name: str
    result: Any
    step: int | None = None


@dataclass
class AgentState:
    """Lightweight state container for the agent runtime."""

    session_id: str
    task: str
    run_id: str = field(default_factory=lambda: f"run-{uuid4().hex[:12]}")
    current_step: int = 0
    max_steps: int = 3
    messages: list[str] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    finished: bool = False
    error: str | None = None
    steps: list[StepRecord] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
