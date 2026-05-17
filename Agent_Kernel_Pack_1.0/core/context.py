from __future__ import annotations

from core.state import AgentState


def build_context(state: AgentState) -> str:
    """Build a minimal text context from agent state."""

    lines = [
        f"Task: {state.task}",
        f"Step: {state.current_step}/{state.max_steps}",
    ]
    if state.messages:
        lines.append("Recent messages:")
        lines.extend(f"- {message}" for message in state.messages[-3:])
    if state.tool_results:
        lines.append("Recent tool results:")
        for result in state.tool_results[-3:]:
            lines.append(f"- {result.tool_name}: {result.result}")
    return "\n".join(lines)
