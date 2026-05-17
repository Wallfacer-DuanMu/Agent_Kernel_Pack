from __future__ import annotations

import json
from typing import Any

import streamlit as st


def validate_skill(skill: Any) -> tuple[bool, str]:
    if not isinstance(skill, dict):
        return False, "Skill must be a JSON object."

    name = str(skill.get("name", "")).strip()
    description = str(skill.get("description", "")).strip()
    steps = skill.get("steps")

    if not name:
        return False, "Skill name is required."
    if not description:
        return False, "Skill description is required."
    if not isinstance(steps, list) or not steps:
        return False, "Skill steps must be a non-empty list."

    recommended_tools = skill.get("recommended_tools")
    if recommended_tools is not None and not isinstance(recommended_tools, list):
        return False, "recommended_tools must be a list when provided."

    triggers = skill.get("triggers")
    if triggers is not None and not isinstance(triggers, list):
        return False, "triggers must be a list when provided."

    return True, "Skill is valid."


def _get_session_skills() -> list[dict[str, Any]]:
    if "imported_session_skills" not in st.session_state:
        st.session_state.imported_session_skills = []
    return st.session_state.imported_session_skills


def render_skill_importer() -> None:
    st.caption("Import a Skill JSON file for this session only. The skill is previewed in Pack Details and is not written back to the repository.")
    uploaded = st.file_uploader("Import Skill JSON", type=["json"], accept_multiple_files=False, key="skill_json_upload")

    if not uploaded:
        return

    try:
        payload = json.loads(uploaded.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        st.error("Invalid JSON file. Please upload a valid Skill JSON document.")
        return

    ok, message = validate_skill(payload)
    if not ok:
        st.error(message)
        return

    session_skills = _get_session_skills()
    existing_names = {skill.get("name") for skill in session_skills}
    if payload["name"] not in existing_names:
        session_skills.append(payload)
    st.success("Skill imported for the current session.")
