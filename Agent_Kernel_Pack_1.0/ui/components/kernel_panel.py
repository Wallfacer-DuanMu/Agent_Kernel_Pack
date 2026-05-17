from __future__ import annotations

import streamlit as st

from ui.adapters.kernel_view import KernelStatusBundle, get_kernel_status


STATUS_LABELS = {
    "Runtime": "active",
    "State": "ready",
    "Actions": "ready",
    "Capabilities": "ready",
    "Policy": "ready",
    "Context": "ready",
    "Tracing": "idle",
    "Recovery": "ready",
    "Loader": "active",
}


def _render_kv(label: str, value: object) -> None:
    st.markdown(f"**{label}:** {value if value not in (None, '') else 'not available'}")


def _render_json_selector(title: str, items: list[tuple[str, dict]], *, key: str) -> None:
    if not items:
        st.caption("not available")
        return
    labels = [label for label, _ in items]
    selected_label = st.selectbox(title, labels, key=key)
    selected_item = next(data for label, data in items if label == selected_label)
    st.json(selected_item)


def render_kernel_panel(selected_pack: str) -> None:
    st.subheader("Kernel Status")
    bundle: KernelStatusBundle = get_kernel_status(selected_pack)

    sections = [
        ("Runtime", bundle.runtime),
        ("State", bundle.state),
        ("Actions", bundle.actions),
        ("Capabilities", {"tools": bundle.capabilities}),
        ("Policy", bundle.policy),
        ("Context", bundle.context),
        ("Tracing", bundle.tracing),
        ("Recovery", bundle.recovery),
        ("Loader", bundle.loader),
    ]

    for name, data in sections:
        with st.expander(f"{name} · {STATUS_LABELS.get(name, 'ready')}", expanded=False):
            st.markdown(
                {
                    "Runtime": "Execution engine overview for the selected session.",
                    "State": "Current in-memory agent state snapshot.",
                    "Actions": "Supported action schemas and recent execution metadata.",
                    "Capabilities": "Registered tools and risk summaries.",
                    "Policy": "Kernel and pack policy overview.",
                    "Context": "Context builder inputs and preview.",
                    "Tracing": "Execution trace availability.",
                    "Recovery": "Fallback and recovery settings.",
                    "Loader": "Pack loading and manifest information.",
                }[name]
            )

            if name == "Runtime":
                for key in ["status", "max_steps", "current_step", "decision_provider", "loaded_pack"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
            elif name == "State":
                for key in ["session_id", "task", "finished", "error", "messages_count", "tool_results_count"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
                st.json(data.get("state_json", {}))
            elif name == "Actions":
                _render_json_selector(
                    "Action Schema",
                    [(schema.name, schema.schema) for schema in bundle.action_schemas],
                    key=f"action_schema_{selected_pack}",
                )
                recent_result = st.session_state.get("run_result") or {}
                recent_actions = recent_result.get("actions") or []
                if recent_actions:
                    st.markdown("**Current Step Action**")
                    st.json(recent_actions[-1])
                    st.markdown("**Action History**")
                    st.json(recent_actions)
                else:
                    st.caption("not available")
            elif name == "Capabilities":
                tool_items = [
                    (
                        tool.name,
                        {
                            "description": tool.description,
                            "risk_level": tool.risk_level,
                            "enabled": tool.enabled,
                            "args_schema": tool.args_schema,
                        },
                    )
                    for tool in bundle.capabilities
                ]
                _render_json_selector("Tool", tool_items, key=f"tool_detail_{selected_pack}")
            elif name == "Policy":
                st.markdown("**Kernel Policy**")
                for rule in data.get("rules", []):
                    st.write(f"- {rule.get('description', rule.get('name', 'rule'))}")
                st.markdown(f"**Effective Policy:** {data.get('effective_policy')}")
                st.caption("Policy decisions will appear in the execution panel after a run.")
            elif name == "Context":
                for key in ["builder_name", "included_sections", "includes_task", "includes_recent_messages", "includes_tool_results", "includes_pack_prompt", "includes_skill_hints"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
                st.code(str(data.get("preview", "")), language="text")
            elif name == "Tracing":
                for key in ["enabled", "trace_file_path", "events_count"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
            elif name == "Recovery":
                for key in ["mode", "retries", "last_error"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
            elif name == "Loader":
                for key in ["pack_source", "manifest_valid", "loaded_components"]:
                    _render_kv(key.replace("_", " ").title(), data.get(key))
                st.json(data.get("manifest", {}))
                st.button("Reload Pack", key=f"reload_pack_{selected_pack}")
