from __future__ import annotations

from typing import Any


def render(result: Any, state: Any) -> str:
    if getattr(state, "error", None):
        return f"Error: {state.error}"
    if result is None:
        return ""
    return str(result)
