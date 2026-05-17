from __future__ import annotations

import streamlit as st

from ui.adapters.pack_view import PackSummary, get_pack_summary


def _render_json_selector(title: str, items: list[tuple[str, dict]], *, key: str) -> None:
    if not items:
        st.caption("not available")
        return
    labels = [label for label, _ in items]
    selected_label = st.selectbox(title, labels, key=key)
    selected_item = next(data for label, data in items if label == selected_label)
    st.json(selected_item)


def render_pack_panel(pack_name: str) -> None:
    st.subheader("Pack Details")
    summary: PackSummary = get_pack_summary(pack_name)
    imported_skills = st.session_state.get("imported_session_skills", [])

    with st.expander("Manifest · ready", expanded=False):
        st.markdown(f"**Name:** {summary.manifest.get('name', summary.name)}")
        st.markdown(f"**Version:** {summary.manifest.get('version', 'not available')}")
        st.markdown(f"**Kernel Compatibility:** {summary.manifest.get('kernel_version', 'not available')}")
        st.markdown(f"**Description:** {summary.description}")
        entry = summary.manifest.get("entry", {}) if isinstance(summary.manifest.get("entry", {}), dict) else {}
        st.markdown(f"**Entry:** {entry}")
        st.json(summary.manifest or {})

    with st.expander("Workflow · ready"):
        st.markdown(f"**Workflow name:** {summary.workflow.get('name', 'not available')}")
        st.markdown(f"**Stages:** {summary.workflow.get('stages', [])}")
        st.markdown(f"**Allowed tools:** {summary.workflow.get('allowed_tools', [])}")
        st.markdown(f"**Completion conditions:** {summary.workflow.get('completion_conditions', [])}")

    with st.expander("Policy · ready"):
        st.markdown("**Effective Policy = Kernel Policy + Pack Policy**")
        for rule in summary.policy.get("rules", []):
            st.write(f"- {rule.get('description', rule.get('name', 'rule'))}")

    with st.expander("Tools · ready"):
        if summary.tools:
            _render_json_selector(
                "Tool",
                [
                    (
                        tool.get("name", "tool"),
                        {
                            "name": tool.get("name", ""),
                            "source": tool.get("source", "pack"),
                            "risk_level": tool.get("risk_level", "unknown"),
                            "args_schema": tool.get("args_schema", {}),
                        },
                    )
                    for tool in summary.tools
                ],
                key=f"pack_tool_detail_{pack_name}",
            )
        else:
            st.caption("not available")

    with st.expander("Prompts · ready"):
        st.markdown(f"**System prompt:** {summary.prompts.get('system_prompt', 'not available')}")
        st.markdown(f"**Task prompt template:** {summary.prompts.get('task_prompt_template', 'not available')}")
        st.markdown(f"**Skill hint prompt:** {summary.prompts.get('skill_hint_prompt', 'not available')}")

    with st.expander("Output · ready"):
        st.markdown(f"**Renderer name:** {summary.output.get('renderer_name', 'not available')}")
        st.markdown(f"**Format:** {summary.output.get('format', 'not available')}")
        st.markdown(f"**Sections:** {summary.output.get('sections', [])}")
        st.markdown(f"**Recent preview:** {summary.output.get('preview', '') or 'not available'}")

    with st.expander("Skills · ready"):
        st.markdown("**Built-in Pack Skills**")
        if summary.skills:
            _render_json_selector("Built-in Skill", [(skill.get("name", "skill"), skill) for skill in summary.skills], key=f"pack_skill_detail_{pack_name}")
        else:
            st.caption("not available")

        st.markdown("**Imported Session Skills**")
        if imported_skills:
            _render_json_selector(
                "Imported Skill",
                [(skill.get("name", "skill"), skill) for skill in imported_skills],
                key=f"imported_pack_skill_detail_{pack_name}",
            )
        else:
            st.caption("not available")
