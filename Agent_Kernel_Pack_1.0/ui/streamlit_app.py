from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.llm_config import clear_llm_config, load_llm_config, save_llm_config
from core.llm import LLMSettings, LLMProviderType
from ui.adapters.pack_view import list_available_packs
from ui.components.execution_panel import render_execution_panel
from ui.components.kernel_panel import render_kernel_panel
from ui.components.pack_panel import render_pack_panel
from ui.components.skill_importer import render_skill_importer


PROVIDER_OPTIONS = [
    LLMProviderType.OPENAI_COMPATIBLE,
    LLMProviderType.KIMI_COMPATIBLE,
    LLMProviderType.QWEN_COMPATIBLE,
    LLMProviderType.DEEPSEEK_COMPATIBLE,
    LLMProviderType.ZHIPU_COMPATIBLE,
    LLMProviderType.ANTHROPIC_COMPATIBLE,
]

PROVIDER_PRESETS = {
    LLMProviderType.OPENAI_COMPATIBLE: {"api_base": "https://api.openai.com/v1", "api_path": "/chat/completions", "model": "gpt-4o-mini"},
    LLMProviderType.KIMI_COMPATIBLE: {"api_base": "https://api.moonshot.cn/v1", "api_path": "/chat/completions", "model": "moonshot-v1-8k"},
    LLMProviderType.QWEN_COMPATIBLE: {"api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_path": "/chat/completions", "model": "qwen-plus"},
    LLMProviderType.DEEPSEEK_COMPATIBLE: {"api_base": "https://api.deepseek.com/v1", "api_path": "/chat/completions", "model": "deepseek-chat"},
    LLMProviderType.ZHIPU_COMPATIBLE: {"api_base": "https://open.bigmodel.cn/api/paas/v4", "api_path": "/chat/completions", "model": "glm-4-plus"},
    LLMProviderType.ANTHROPIC_COMPATIBLE: {"api_base": "https://api.anthropic.com/v1", "api_path": "/messages", "model": "claude-3-5-sonnet-20241022"},
}


st.set_page_config(page_title="Agent Kernel Console", layout="wide")
st.title("Agent Kernel Console")
st.caption("Kernel + Pack => Runtime Execution")

if "selected_pack" not in st.session_state:
    st.session_state.selected_pack = "default_pack"
if "max_steps" not in st.session_state:
    st.session_state.max_steps = 3
if "trace_enabled" not in st.session_state:
    st.session_state.trace_enabled = True
if "task_input" not in st.session_state:
    st.session_state.task_input = ""
if "imported_session_skills" not in st.session_state:
    st.session_state.imported_session_skills = []
if "llm_config_loaded" not in st.session_state:
    st.session_state.llm_config_loaded = False
if not st.session_state.llm_config_loaded:
    persisted = load_llm_config()
    st.session_state.llm_enabled = persisted.enabled
    st.session_state.llm_api_base = persisted.api_base
    st.session_state.llm_api_key = persisted.api_key
    st.session_state.llm_model = persisted.model
    st.session_state.llm_system_prompt = persisted.system_prompt
    st.session_state.llm_provider = persisted.provider
    st.session_state.llm_api_path = persisted.api_path
    st.session_state.llm_timeout_seconds = persisted.timeout_seconds
    st.session_state.llm_temperature = persisted.temperature
    st.session_state.llm_config_loaded = True
if "llm_enabled" not in st.session_state:
    st.session_state.llm_enabled = False
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = LLMProviderType.OPENAI_COMPATIBLE
if "llm_api_base" not in st.session_state:
    st.session_state.llm_api_base = ""
if "llm_api_path" not in st.session_state:
    st.session_state.llm_api_path = "/chat/completions"
if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""
if "llm_model" not in st.session_state:
    st.session_state.llm_model = ""
if "llm_system_prompt" not in st.session_state:
    st.session_state.llm_system_prompt = ""
if "llm_temperature" not in st.session_state:
    st.session_state.llm_temperature = 0.2
if "llm_timeout_seconds" not in st.session_state:
    st.session_state.llm_timeout_seconds = 60

packs = list_available_packs()
if st.session_state.selected_pack not in packs:
    st.session_state.selected_pack = packs[0]

header_left, header_mid, header_right = st.columns([1.1, 1.2, 1])
with header_left:
    st.session_state.selected_pack = st.selectbox("Pack", packs, index=packs.index(st.session_state.selected_pack))
with header_mid:
    st.session_state.max_steps = st.number_input("Max Steps", min_value=1, max_value=50, value=int(st.session_state.max_steps))
with header_right:
    st.session_state.trace_enabled = st.toggle("Trace Enabled", value=st.session_state.trace_enabled)
    st.caption("Use the center panel to run or reset tasks.")

with st.sidebar:
    st.subheader("LLM")
    st.session_state.llm_enabled = st.toggle(
        "Enable LLM mode",
        value=st.session_state.llm_enabled,
        help="Turn on to use a provider-backed model runtime. Turn off to keep the local mock runtime for demos and tests.",
    )
    st.caption("Mock mode keeps the project runnable without any API key.")
    if st.session_state.llm_enabled:
        previous_provider = st.session_state.llm_provider
        st.selectbox(
            "Provider",
            PROVIDER_OPTIONS,
            key="llm_provider",
            help="Choose a provider, then edit base URL/path/model if you use a proxy or custom endpoint.",
        )
        if st.session_state.llm_provider != previous_provider:
            preset = PROVIDER_PRESETS.get(st.session_state.llm_provider, {})
            st.session_state.llm_api_base = preset.get("api_base", st.session_state.llm_api_base)
            st.session_state.llm_api_path = preset.get("api_path", st.session_state.llm_api_path)
            st.session_state.llm_model = preset.get("model", st.session_state.llm_model)

        st.text_input(
            "API Base URL",
            key="llm_api_base",
            placeholder="https://api.openai.com/v1",
            help="Use provider base URL (preset applied when provider changes).",
        )
        st.text_input(
            "API Path",
            key="llm_api_path",
            placeholder="/chat/completions",
            help="Leave as Chat Completions for OpenAI and Kimi style providers, or override for a gateway.",
        )
        st.text_input("API Key", key="llm_api_key", type="password")
        st.text_input("Model", key="llm_model", placeholder="gpt-4o-mini / qwen-plus / deepseek-chat / glm-4-plus")
        st.text_area(
            "System Prompt (optional)",
            key="llm_system_prompt",
            placeholder="You are the decision engine for Agent Kernel...",
            height=120,
        )
        st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(st.session_state.llm_temperature), step=0.1, key="llm_temperature")
        st.number_input("Timeout Seconds", min_value=1, max_value=600, value=int(st.session_state.llm_timeout_seconds), key="llm_timeout_seconds")
        save_col, clear_col = st.columns(2)
        with save_col:
            save_clicked = st.button("Save", use_container_width=True)
        with clear_col:
            clear_clicked = st.button("Clear", use_container_width=True)
        if save_clicked:
            save_llm_config(
                LLMSettings(
                    enabled=bool(st.session_state.llm_enabled),
                    provider=str(st.session_state.llm_provider),
                    api_base=str(st.session_state.llm_api_base).strip(),
                    api_path=str(st.session_state.llm_api_path).strip() or "/chat/completions",
                    api_key=str(st.session_state.llm_api_key).strip(),
                    model=str(st.session_state.llm_model).strip(),
                    system_prompt=str(st.session_state.llm_system_prompt).strip(),
                    temperature=float(st.session_state.llm_temperature),
                    timeout_seconds=int(st.session_state.llm_timeout_seconds),
                )
            )
            st.success("LLM configuration saved.")
        if clear_clicked:
            clear_llm_config()
            for key, value in {
                "llm_enabled": False,
                "llm_provider": LLMProviderType.OPENAI_COMPATIBLE,
                "llm_api_base": "",
                "llm_api_path": "/chat/completions",
                "llm_api_key": "",
                "llm_model": "",
                "llm_system_prompt": "",
                "llm_temperature": 0.2,
                "llm_timeout_seconds": 60,
            }.items():
                st.session_state[key] = value
            st.success("LLM configuration cleared.")
        st.info("LLM mode sends the runtime context to the configured API and expects a JSON action response.")
    else:
        st.caption("LLM mode is off. The app will use the built-in mock decision provider for safe local testing.")

render_skill_importer()

left, middle, right = st.columns([1, 1.4, 1.1])
with left:
    render_kernel_panel(st.session_state.selected_pack)
with middle:
    render_execution_panel(st.session_state.selected_pack)
with right:
    render_pack_panel(st.session_state.selected_pack)
