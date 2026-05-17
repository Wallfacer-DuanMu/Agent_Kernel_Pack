from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from capabilities.file_tools import LIST_DIR_TOOL, READ_FILE_TOOL
from capabilities.search_tools import SEARCH_TEXT_TOOL
from capabilities.shell_tools import RUN_COMMAND_TOOL
from core.context import build_context
from core.loader import PackLoader
from core.state import AgentState


@dataclass(frozen=True)
class KernelActionSchema:
    name: str
    schema: dict[str, Any]


@dataclass(frozen=True)
class KernelToolSummary:
    name: str
    description: str
    risk_level: str
    enabled: bool
    args_schema: dict[str, Any]


@dataclass(frozen=True)
class KernelSection:
    name: str
    status: str
    description: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KernelStatusBundle:
    runtime: dict[str, Any]
    state: dict[str, Any]
    actions: dict[str, Any]
    capabilities: list[KernelToolSummary]
    policy: dict[str, Any]
    context: dict[str, Any]
    tracing: dict[str, Any]
    recovery: dict[str, Any]
    loader: dict[str, Any]
    action_schemas: list[KernelActionSchema]


ACTION_SCHEMAS = [
    KernelActionSchema("respond", {"type": "respond", "content": "string"}),
    KernelActionSchema(
        "call_tool",
        {"type": "call_tool", "tool_name": "string", "tool_args": "object", "reason": "string"},
    ),
    KernelActionSchema("request_approval", {"type": "request_approval", "reason": "string"}),
    KernelActionSchema("finish", {"type": "finish", "summary": "string"}),
    KernelActionSchema("fail", {"type": "fail", "error": "string"}),
]


DEFAULT_STATE = AgentState(session_id="ui-preview", task="", max_steps=3)


def _default_pack_name() -> str:
    try:
        loader = PackLoader()
        return loader.load_pack("default_pack").name
    except Exception:
        return "default_pack"


def _tool_summaries() -> list[KernelToolSummary]:
    tools = [READ_FILE_TOOL, LIST_DIR_TOOL, SEARCH_TEXT_TOOL, RUN_COMMAND_TOOL]
    return [
        KernelToolSummary(
            name=tool.name,
            description=tool.description,
            risk_level=getattr(tool.risk_level, "value", str(tool.risk_level)),
            enabled=True,
            args_schema=tool.args_schema or {},
        )
        for tool in tools
    ]


def _policy_rules() -> list[dict[str, str]]:
    rules = []
    try:
        from policy.rules import DEFAULT_RULES

        rules = list(DEFAULT_RULES)
    except Exception:
        rules = []
    if not rules:
        return [
            {"name": "read-only allow", "description": "read-only tools: allow"},
            {"name": "shell inspect risk", "description": "shell command: inspect risk"},
            {"name": "destructive confirm block", "description": "destructive command: confirm/block"},
            {"name": "unknown deny", "description": "unknown tool: deny"},
        ]
    return [{"name": getattr(rule, "name", "rule"), "description": getattr(rule, "description", "")} for rule in rules]


def _trace_summary() -> dict[str, Any]:
    trace_dir = Path("traces")
    files = list(trace_dir.glob("*")) if trace_dir.is_dir() else []
    latest = max(files, key=lambda path: path.stat().st_mtime) if files else None
    return {
        "enabled": True,
        "trace_file_path": str(latest) if latest else "",
        "events_count": len(files),
    }


def get_kernel_status(selected_pack: str = "default_pack") -> KernelStatusBundle:
    loader = PackLoader()
    try:
        loaded_pack = loader.load_pack(selected_pack)
        pack_name = loaded_pack.name
        pack_description = loaded_pack.description or "Loaded pack summary available."
        workflow = loaded_pack.workflow
    except Exception:
        pack_name = _default_pack_name()
        pack_description = "Pack loader is available for the selected pack."
        workflow = None

    state = DEFAULT_STATE
    context_text = build_context(state)
    tools = _tool_summaries()
    policy_rules = _policy_rules()

    runtime = {
        "status": "idle",
        "max_steps": state.max_steps,
        "current_step": state.current_step,
        "decision_provider": "kernel-default",
        "loaded_pack": pack_name,
    }
    state_info = {
        "session_id": state.session_id,
        "task": state.task,
        "finished": state.finished,
        "error": state.error,
        "messages_count": len(state.messages),
        "tool_results_count": len(state.tool_results),
        "state_json": {
            "session_id": state.session_id,
            "task": state.task,
            "current_step": state.current_step,
            "max_steps": state.max_steps,
            "messages": state.messages,
            "tool_results": [result.__dict__ for result in state.tool_results],
            "finished": state.finished,
            "error": state.error,
        },
    }
    actions = {
        "supported": ACTION_SCHEMAS,
        "current_step_action": None,
        "history": [],
    }
    context = {
        "builder_name": "core.context.build_context",
        "included_sections": ["task", "recent_messages", "tool_results"],
        "includes_task": True,
        "includes_recent_messages": bool(state.messages),
        "includes_tool_results": bool(state.tool_results),
        "includes_pack_prompt": bool(pack_description),
        "includes_skill_hints": False,
        "preview": context_text,
    }
    tracing = _trace_summary()
    recovery = {"mode": "basic", "retries": 0, "last_error": state.error or ""}
    loader_info = {
        "pack_source": selected_pack,
        "manifest_valid": True,
        "loaded_components": ["workflow", "policy", "tools", "output", "prompts"],
        "manifest": loaded_pack.__dict__ if 'loaded_pack' in locals() and loaded_pack else {},
    }

    return KernelStatusBundle(
        runtime=runtime,
        state=state_info,
        actions=actions,
        capabilities=tools,
        policy={"rules": policy_rules, "effective_policy": "Kernel Policy + Pack Policy"},
        context=context,
        tracing=tracing,
        recovery=recovery,
        loader=loader_info,
        action_schemas=ACTION_SCHEMAS,
    )
