from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.actions import ActionType, parse_action
from core.context import build_context
from core.llm import LLMSettings
from core.loader import PackLoader
from core.runtime import AgentRuntime
from core.state import AgentState
from ui.adapters.trace_view import build_trace_timeline, normalize_trace_events


def _action_to_dict(action: object | None) -> dict[str, Any] | None:
    if action is None:
        return None
    if isinstance(action, dict):
        return action
    if hasattr(action, "__dict__"):
        return dict(action.__dict__)
    return {"value": action}


def _state_to_dict(state: AgentState | None) -> dict[str, Any]:
    if state is None:
        return {}
    return {
        "session_id": state.session_id,
        "run_id": state.run_id,
        "task": state.task,
        "current_step": state.current_step,
        "max_steps": state.max_steps,
        "messages": list(state.messages),
        "tool_results": [
            {"tool_name": result.tool_name, "result": result.result, "step": result.step}
            for result in state.tool_results
        ],
        "finished": state.finished,
        "error": state.error,
        "created_at": state.created_at,
        "steps": [asdict(step) for step in state.steps],
    }


def _skill_hint_text(session_skills: list[dict[str, Any]] | None) -> str:
    skills = session_skills or []
    if not skills:
        return ""
    lines = ["Skill Hints:"]
    for skill in skills:
        name = str(skill.get("name", "skill")).strip() or "skill"
        description = str(skill.get("description", "")).strip()
        lines.append(f"- {name}: {description}")
    return "\n".join(lines)


def _policy_decision_to_dict(step: dict[str, Any], policy_source: str) -> dict[str, Any]:
    action_type = step.get("action_type", "")
    return {
        "action": action_type,
        "tool": step.get("tool_name", ""),
        "decision": step.get("policy_decision") or ("allow" if action_type == ActionType.respond.value else ""),
        "reason": step.get("result_summary") or step.get("error") or "",
        "risk_level": "unknown",
        "source": policy_source,
    }


def run_task(
    task: str,
    pack_name: str,
    max_steps: int,
    trace_enabled: bool,
    session_skills: list[dict[str, Any]] | None = None,
    llm_settings: LLMSettings | None = None,
) -> dict[str, Any]:
    task = task.strip()
    trace_dir = Path("traces") if trace_enabled else Path("traces_disabled")
    runtime = None
    status = "finished"
    error = None
    output = ""
    actions: list[dict[str, Any]] = []
    policy_decisions: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []
    skill_hint_text = _skill_hint_text(session_skills)

    try:
        runtime = AgentRuntime(max_steps=max_steps, trace_dir=trace_dir, pack_name_or_path=pack_name, llm_settings=llm_settings)
        run_result = runtime.run(task)
        output = run_result.get("output", "")
        status = run_result.get("status", status)
        error = run_result.get("error")
    except Exception as exc:
        status = "error"
        error = str(exc)
        output = error
        run_result = {"trace_events": [], "trace_file": "", "state": runtime.last_state if runtime is not None else None}

    state = (runtime.last_state if runtime is not None else None) or AgentState(session_id="ui-session", run_id="ui-run", task=task, max_steps=max_steps)

    try:
        loaded_pack = PackLoader().load_pack(pack_name)
    except Exception:
        loaded_pack = None

    for step in state.steps:
        step_dict = asdict(step)
        actions.append(step_dict)
        policy_decisions.append(
            _policy_decision_to_dict(step_dict, "pack" if loaded_pack and getattr(loaded_pack, "policy_rules", None) else "kernel")
        )
        if step.tool_name:
            tool_calls.append(
                {
                    "tool_name": step.tool_name,
                    "args": step.tool_args,
                    "risk_level": "unknown",
                    "result": step.result,
                    "error": step.error,
                }
            )

    if not actions and task and not error and runtime is not None and not (llm_settings and llm_settings.enabled):
        preview_context = build_context(state)
        try:
            parsed = parse_action(runtime.decision_provider.decide(preview_context, state))
        except Exception:
            parsed = None
        if parsed is not None:
            action_dict = _action_to_dict(parsed)
            if action_dict is not None:
                actions.append(action_dict)
            if parsed.type == ActionType.call_tool:
                tool_calls.append(
                    {"tool_name": parsed.tool_name, "args": parsed.tool_args, "risk_level": "unknown", "result": None, "error": None}
                )

    trace_events = normalize_trace_events(run_result.get("trace_events") or [])
    current_run_id = run_result.get("run_id", state.run_id)
    if current_run_id:
        trace_events = [event for event in trace_events if event.get("run_id") == current_run_id]
    trace_file = run_result.get("trace_file", "")
    trace_timeline = build_trace_timeline(trace_events or actions)
    context_preview = build_context(state)
    if skill_hint_text:
        context_preview = f"{context_preview}\n\n{skill_hint_text}" if context_preview else skill_hint_text

    llm_mode = "llm" if llm_settings and llm_settings.enabled else "mock"
    provider_name = type(runtime.decision_provider).__name__ if runtime is not None else "not initialized"

    return {
        "status": status,
        "output": output,
        "state": _state_to_dict(state),
        "actions": actions,
        "action_history": trace_timeline,
        "tool_calls": tool_calls,
        "policy_decisions": policy_decisions,
        "context_preview": context_preview,
        "trace_events": trace_events,
        "trace_file": trace_file,
        "error": error,
        "pack": getattr(loaded_pack, "__dict__", None),
        "session_id": run_result.get("session_id", state.session_id),
        "run_id": run_result.get("run_id", state.run_id),
        "skill_hints": skill_hint_text,
        "llm_mode": run_result.get("llm_mode", llm_mode),
        "llm_model": run_result.get("llm_model", llm_settings.model if llm_settings and llm_settings.enabled else ""),
        "llm_provider": run_result.get("llm_provider", getattr(llm_settings, "provider", "mock")),
        "llm_requests": run_result.get("llm_requests", []),
        "llm_responses": run_result.get("llm_responses", []),
        "decision_provider": provider_name,
    }
