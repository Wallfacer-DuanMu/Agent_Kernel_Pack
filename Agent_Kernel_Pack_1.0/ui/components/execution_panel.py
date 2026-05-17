from __future__ import annotations

import streamlit as st

from core.llm import LLMSettings
from ui.adapters.runtime_view import run_task
from ui.adapters.trace_view import build_trace_timeline


def _render_empty(message: str) -> None:
    st.caption(message)


def _render_summary_cards(result: dict) -> None:
    cols = st.columns(5)
    summary_items = [
        ("status", result.get("status") or "idle"),
        ("mode", result.get("llm_mode") or "mock"),
        ("tools", len(result.get("tool_calls") or [])),
        ("trace", len(result.get("trace_events") or [])),
        ("run id", result.get("run_id") or "not available"),
    ]
    for col, (label, value) in zip(cols, summary_items, strict=False):
        with col:
            st.metric(label, value)




def _build_llm_settings_from_session() -> LLMSettings:
    return LLMSettings(
        enabled=bool(st.session_state.get("llm_enabled", False)),
        provider=str(st.session_state.get("llm_provider", "openai_compatible")).strip() or "openai_compatible",
        api_base=str(st.session_state.get("llm_api_base", "")).strip(),
        api_path=str(st.session_state.get("llm_api_path", "/chat/completions")).strip() or "/chat/completions",
        api_key=str(st.session_state.get("llm_api_key", "")).strip(),
        model=str(st.session_state.get("llm_model", "")).strip(),
        system_prompt=str(st.session_state.get("llm_system_prompt", "")).strip(),
        temperature=float(st.session_state.get("llm_temperature", 0.2)),
        timeout_seconds=int(st.session_state.get("llm_timeout_seconds", 60)),
    )



def render_execution_panel(selected_pack: str) -> None:
    st.subheader("Task / Execution")

    if "run_result" not in st.session_state:
        st.session_state.run_result = None
    if "current_run_id" not in st.session_state:
        st.session_state.current_run_id = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_task" not in st.session_state:
        st.session_state.pending_task = ""
    if "chat_processing" not in st.session_state:
        st.session_state.chat_processing = False

    reset_clicked = st.button("Reset Session", key="reset_task_button")
    if reset_clicked:
        for key in ["run_result", "current_run_id", "chat_history", "pending_task", "chat_processing"]:
            st.session_state.pop(key, None)
        st.rerun()

    result = st.session_state.get("run_result") or {}
    _render_summary_cards(result)
    tabs = st.tabs(["Output", "LLM Calls", "Trace Timeline", "Tool Calls", "Policy Decisions", "Context", "State"])

    with tabs[0]:
        st.markdown("### Agent Output")
        if result.get("llm_mode") == "llm":
            model_name = result.get("llm_model") or "not configured"
            provider_name = result.get("decision_provider") or "unknown"
            st.caption(f"LLM mode enabled · model: {model_name} · provider: {provider_name}")
        else:
            st.caption("Mock mode enabled · local rule-based execution for testing.")

        for message in st.session_state.get("chat_history", []):
            with st.chat_message(message.get("role", "assistant")):
                st.markdown(message.get("content", ""))

        prompt = st.chat_input("输入任务并发送给 Agent")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.pending_task = prompt
            st.session_state.chat_processing = True
            st.rerun()

        if st.session_state.get("chat_processing") and st.session_state.get("pending_task"):
            task = str(st.session_state.get("pending_task", "")).strip()
            with st.chat_message("assistant"):
                with st.spinner("模型思考中..."):
                    st.session_state.run_result = run_task(
                        task=task,
                        pack_name=selected_pack,
                        max_steps=int(st.session_state.get("max_steps", 3)),
                        trace_enabled=bool(st.session_state.get("trace_enabled", True)),
                        session_skills=st.session_state.get("imported_session_skills", []),
                        llm_settings=_build_llm_settings_from_session(),
                    )
                st.session_state.current_run_id = st.session_state.run_result.get("run_id", "")
                assistant_text = str(st.session_state.run_result.get("output") or "")
                if st.session_state.run_result.get("error"):
                    assistant_text = f"执行失败：{st.session_state.run_result['error']}"
                if not assistant_text:
                    assistant_text = "(无输出)"
                st.markdown(assistant_text)

            st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
            st.session_state.pending_task = ""
            st.session_state.chat_processing = False

        if not st.session_state.get("chat_history"):
            _render_empty("发送一条消息开始对话。")

    with tabs[1]:
        st.markdown("### LLM Calls")
        if result.get("llm_mode") == "llm":
            st.caption(
                f"Provider: {result.get('llm_provider') or 'unknown'} · Model: {result.get('llm_model') or 'unknown'} · Run ID: {result.get('run_id') or 'unknown'}"
            )
        llm_requests = result.get("llm_requests") or []
        llm_responses = result.get("llm_responses") or []
        if not llm_requests and not llm_responses:
            _render_empty("No LLM call evidence available yet.")
        else:
            request_cols = st.columns(2)
            with request_cols[0]:
                st.markdown("#### Requests")
                for idx, item in enumerate(llm_requests, start=1):
                    st.markdown(f"**Request {idx}**")
                    st.json(item)
            with request_cols[1]:
                st.markdown("#### Responses")
                for idx, item in enumerate(llm_responses, start=1):
                    st.markdown(f"**Response {idx}**")
                    st.json(item)

    with tabs[2]:
        st.markdown("### Execution Trace")
        if st.session_state.get("current_run_id"):
            st.caption(f"Current Run ID: {st.session_state.current_run_id}")
        timeline = build_trace_timeline(result.get("trace_events") or result.get("actions") or [])
        if not timeline:
            _render_empty("No trace events yet. Run a task to generate trace.")
        for event in timeline:
            st.markdown(
                f"**Step {event.get('step', '?')}** · `{event.get('event_type', 'unknown')}` · `{event.get('action_type', 'unknown')}` · `{event.get('status', 'unknown')}`"
            )
            st.markdown(f"- Tool: {event.get('tool_name') or 'not available'}")
            st.markdown(f"- Policy decision: {event.get('policy_decision') or 'not available'}")
            st.markdown(f"- Result summary: {event.get('result_summary') or 'not available'}")
            st.json(event.get("raw") or event)

    with tabs[3]:
        st.markdown("### Tool Calls")
        tool_calls = result.get("tool_calls") or []
        if not tool_calls:
            _render_empty("No tool calls recorded.")
        for idx, call in enumerate(tool_calls, start=1):
            st.markdown(f"**Tool Call {idx}**")
            st.json(call)

    with tabs[4]:
        st.markdown("### Policy Decisions")
        decisions = result.get("policy_decisions") or []
        if not decisions:
            _render_empty("No policy decisions recorded yet.")
        for idx, decision in enumerate(decisions, start=1):
            st.markdown(f"**Decision {idx}**")
            st.json(decision)

    with tabs[5]:
        st.markdown("### Context")
        context_preview = result.get("context_preview") or ""
        if context_preview:
            st.code(context_preview, language="text")
        else:
            _render_empty("No context available yet.")

    with tabs[6]:
        st.markdown("### Raw State")
        st.json(result.get("state") or {})
