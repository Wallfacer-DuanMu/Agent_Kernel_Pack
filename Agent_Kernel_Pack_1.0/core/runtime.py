from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from capabilities.registry import CapabilityRegistry
from core.actions import Action, ActionType, parse_action
from core.config import VERSION
from core.context import build_context
from core.llm import LLMSettings, create_decision_provider, extract_chat_message_content
from core.llm_config import load_llm_config
from core.loader import LoadedPack, PackLoader, PackLoaderError
from core.state import AgentState, StepRecord, ToolResult
from policy.decisions import Decision, PolicyDecision
from policy.guard import PolicyGuard
from tracing.logger import TraceLogger
from tracing.trace_store import TraceStore


class DecisionProvider(Protocol):
    """Decision provider protocol."""

    def decide(self, context: str, state: AgentState) -> Action | dict:
        ...


@dataclass
class MockDecisionProvider:
    """Very small rule-based provider for local runtime checks."""

    def decide(self, context: str, state: AgentState) -> Action:
        task = state.task.strip()
        if task.startswith("list "):
            return Action(type=ActionType.call_tool, tool_name="list_dir", tool_args={"path": task[5:].strip()})
        if task.startswith("read "):
            return Action(type=ActionType.call_tool, tool_name="read_file", tool_args={"path": task[5:].strip()})
        if task.startswith("search ") and " in " in task:
            query, path = task[7:].split(" in ", 1)
            return Action(type=ActionType.call_tool, tool_name="search_text", tool_args={"query": query.strip(), "path": path.strip()})
        if task.startswith("run "):
            return Action(type=ActionType.call_tool, tool_name="run_command", tool_args={"command": task[4:].strip()})
        if task.startswith("echo "):
            return Action(type=ActionType.respond, content=task[5:])
        if "finish" in task:
            return Action(type=ActionType.finish, content="Task finished.")
        if state.current_step >= state.max_steps - 1:
            return Action(type=ActionType.finish, content="Reached max steps.")
        return Action(type=ActionType.respond, content=f"Processed: {task or context}")


class AgentRuntime:
    """Minimal runtime loop for the experimental kernel."""

    def __init__(
        self,
        decision_provider: DecisionProvider | None = None,
        max_steps: int = 3,
        auto_confirm: bool = False,
        trace_dir: str | Path = "traces",
        loaded_pack: LoadedPack | None = None,
        pack_name_or_path: str | None = None,
        llm_settings: LLMSettings | None = None,
    ) -> None:
        self.llm_settings = llm_settings if llm_settings is not None else load_llm_config()
        if decision_provider is not None:
            self.decision_provider = decision_provider
        else:
            self.decision_provider = create_decision_provider(self.llm_settings)
        self.max_steps = max_steps
        self.registry = CapabilityRegistry()
        self.guard = PolicyGuard(auto_confirm=auto_confirm)
        self.trace_logger = TraceLogger(TraceStore(Path(trace_dir)))
        self.pack_loader = PackLoader()
        self.loaded_pack = loaded_pack
        self.last_state: AgentState | None = None
        self.last_result: str = ""
        self.last_trace_file: str = ""
        self.last_run_result: dict[str, Any] | None = None
        if self.loaded_pack is None:
            pack_ref = pack_name_or_path or "default_pack"
            self.loaded_pack = self.pack_loader.load_pack(pack_ref)
        if self.loaded_pack.register_tools is not None:
            self.loaded_pack.register_tools(self.registry)
        else:
            from packs.default_pack.tools import register_tools
            register_tools(self.registry)
        if self.loaded_pack.policy_rules:
            self.guard.extra_rules = list(self.loaded_pack.policy_rules)
        self.output_renderer = self.loaded_pack.output_renderer
        self.prompts = self.loaded_pack.prompts

    def _tool_summary(self, value: object) -> str:
        text = str(value)
        return text if len(text) <= 200 else text[:200] + "..."

    def _is_identity_question(self, task: str) -> bool:
        normalized = task.strip().lower()
        keywords = ["你是什么模型", "你是什么大模型", "what model are you", "who are you", "你是谁", "你用的什么模型"]
        return any(keyword in normalized for keyword in keywords)

    def _identity_answer(self) -> str:
        if self.llm_settings.enabled:
            provider = self.llm_settings.provider or "unknown"
            model = self.llm_settings.model or "unknown"
            return f"我是 Agent Kernel 当前启用的 LLM 决策器，provider={provider}，model={model}。"
        return "我是 Agent Kernel 的本地 Mock/规则决策器。"

    def run(self, task: str, session_id: str | None = None, run_id: str | None = None) -> dict[str, Any]:
        session_id = session_id or f"session-{uuid4().hex[:8]}"
        run_id = run_id or f"run-{uuid4().hex[:12]}"
        state = AgentState(session_id=session_id, run_id=run_id, task=task, max_steps=self.max_steps)
        result = ""
        last_trace_path: Path | None = None
        trace_events: list[dict[str, Any]] = []
        llm_request_log: list[dict[str, Any]] = []
        llm_response_log: list[dict[str, Any]] = []

        self.trace_logger.start_run({"trace_version": "v2", "session_id": session_id, "run_id": run_id, "task": task, "step": -1, "status": "success", "result_summary": "run started"})

        while state.current_step < state.max_steps and not state.finished:
            if self._is_identity_question(task):
                result = self._identity_answer()
                state.messages.append(result)
                state.finished = True
                action = Action(type=ActionType.respond, content=result)
                step_record = StepRecord(step=state.current_step, action_type=action.type.value, content=action.content, reason=action.reason, tool_name=action.tool_name, tool_args=action.tool_args)
                event = {
                    "trace_version": "v2",
                    "session_id": state.session_id,
                    "run_id": state.run_id,
                    "task": state.task,
                    "step": state.current_step,
                    "event_type": "responded",
                    "action_type": action.type.value,
                    "status": "success",
                    "tool_name": "",
                    "tool_args_summary": "{}",
                    "policy_decision": "",
                    "result_summary": self._tool_summary(result),
                    "error": state.error,
                    "special_case": "identity_question",
                }
                last_trace_path = self.trace_logger.log(event)
                trace_events.append(event)
                state.steps.append(step_record)
                break

            context = build_context(state)
            if self.prompts:
                if self.llm_settings.enabled:
                    context = f"{context}\n\nPack prompt (do not override the JSON action protocol):\n{self.prompts}"
                else:
                    context = f"{self.prompts}\n\n{context}"
            llm_request_log.append(
                {
                    "step": state.current_step,
                    "provider": type(self.decision_provider).__name__,
                    "task": state.task,
                    "context_preview": self._tool_summary(context),
                }
            )
            decision_raw = self.decision_provider.decide(context, state)
            llm_response_log.append(
                {
                    "step": state.current_step,
                    "provider": type(self.decision_provider).__name__,
                    "raw_response": decision_raw if isinstance(decision_raw, dict) else getattr(decision_raw, "__dict__", str(decision_raw)),
                }
            )
            action = parse_action(decision_raw)
            step_record = StepRecord(step=state.current_step, action_type=action.type.value, content=action.content, reason=action.reason, tool_name=action.tool_name, tool_args=action.tool_args)

            event_type = "action_selected"
            status = "success"
            policy_decision = ""

            if action.type == ActionType.respond:
                state.messages.append(action.content)
                result = action.content
                state.finished = True
                event_type = "responded"
            elif action.type == ActionType.finish:
                state.finished = True
                result = action.content or "Finished."
                event_type = "run_finished"
            elif action.type == ActionType.call_tool:
                event_type = "tool_called"
                try:
                    tool = self.registry.get(action.tool_name)
                    decision = self.guard.check(tool, action.tool_args, state)
                    policy_decision = decision.decision.value
                    step_record.policy_decision = decision.decision.value
                    if decision.decision == Decision.DENY:
                        result = decision.reason
                        state.error = decision.reason
                        state.finished = True
                        status = "error"
                    elif decision.decision == Decision.CONFIRM:
                        result = decision.reason
                        state.finished = True
                        status = "confirm_required"
                    else:
                        tool_result = self.registry.execute(action.tool_name, action.tool_args)
                        state.tool_results.append(ToolResult(tool_name=action.tool_name, result=tool_result, step=state.current_step))
                        result = self._tool_summary(tool_result)
                        step_record.result = result
                        state.finished = True
                except Exception as exc:
                    state.error = str(exc)
                    step_record.error = state.error
                    result = state.error
                    state.finished = True
                    status = "error"
            elif action.type == ActionType.request_approval:
                result = "Approval requested."
                state.finished = True
                status = "confirm_required"
            else:
                state.error = action.content or "Runtime failed."
                result = state.error
                state.finished = True
                status = "error"

            event = {
                "trace_version": "v2",
                "session_id": state.session_id,
                "run_id": state.run_id,
                "task": state.task,
                "step": state.current_step,
                "event_type": event_type,
                "action_type": action.type.value,
                "status": status,
                "tool_name": action.tool_name,
                "tool_args_summary": self._tool_summary(action.tool_args),
                "policy_decision": policy_decision,
                "result_summary": self._tool_summary(result),
                "error": state.error,
            }
            last_trace_path = self.trace_logger.log(event)
            trace_events.append(event)
            state.steps.append(step_record)
            state.current_step += 1

        self.trace_logger.finish_run({"trace_version": "v2", "session_id": state.session_id, "run_id": state.run_id, "task": state.task, "step": state.current_step, "status": "success" if not state.error else "error", "result_summary": self._tool_summary(result), "error": state.error})
        self.last_state = state
        self.last_result = result
        self.last_trace_file = str(last_trace_path) if last_trace_path else ""
        run_result = {
            "session_id": state.session_id,
            "run_id": state.run_id,
            "task": task,
            "status": "error" if state.error else "finished",
            "output": self.output_renderer(result, state) if self.output_renderer is not None else result,
            "error": state.error,
            "trace_file": self.last_trace_file,
            "trace_events": trace_events,
            "final_state": state,
            "actions": [step.__dict__ for step in state.steps],
            "llm_requests": llm_request_log,
            "llm_responses": llm_response_log,
            "llm_mode": "llm" if self.llm_settings.enabled else "mock",
            "llm_provider": getattr(self.llm_settings, "provider", "mock"),
            "llm_model": getattr(self.llm_settings, "model", ""),
        }
        self.last_run_result = run_result
        return run_result
