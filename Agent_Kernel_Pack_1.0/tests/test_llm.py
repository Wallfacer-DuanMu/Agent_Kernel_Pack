from __future__ import annotations

import json

import pytest

from core.actions import ActionType
from core.llm import LLMProviderType, LLMSettings, OpenAICompatibleDecisionProvider, create_decision_provider, extract_chat_message_content, parse_action_response
from core.llm_errors import LLMConfigurationError, LLMRequestError, LLMResponseError
from core.llm_config import load_llm_config, save_llm_config
from core.runtime import AgentRuntime
from core.state import AgentState


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_llm_settings_validate_requires_required_fields() -> None:
    settings = LLMSettings(enabled=True)
    with pytest.raises(LLMConfigurationError):
        settings.validate()


def test_llm_settings_rejects_mock_provider_when_enabled() -> None:
    settings = LLMSettings(enabled=True, provider=LLMProviderType.MOCK)
    with pytest.raises(LLMConfigurationError):
        settings.validate()


def test_llm_config_round_trip_supports_new_fields(tmp_path) -> None:
    path = tmp_path / "llm.json"
    settings = LLMSettings(
        enabled=True,
        provider=LLMProviderType.OPENAI_COMPATIBLE,
        api_base="https://example.com/v1",
        api_path="/v1/chat/completions",
        api_key="secret",
        model="demo",
        timeout_seconds=42,
        headers={"X-Test": "1"},
    )
    save_llm_config(settings, path)
    loaded = load_llm_config(path)
    assert loaded.provider == LLMProviderType.OPENAI_COMPATIBLE
    assert loaded.api_path == "/v1/chat/completions"
    assert loaded.timeout_seconds == 42
    assert loaded.headers == {"X-Test": "1"}


def test_create_decision_provider_uses_mock_when_disabled() -> None:
    provider = create_decision_provider(LLMSettings(enabled=False))
    assert provider.__class__.__name__ == "MockDecisionProvider"


def test_provider_endpoint_builds_url_with_override() -> None:
    settings = LLMSettings(enabled=True, api_base="https://example.com/v1/", api_path="/custom/path", api_key="k", model="m")
    assert settings.endpoint().build_url() == "https://example.com/v1/custom/path"


def test_llm_provider_parses_json_action(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = LLMSettings(enabled=True, api_base="https://example.com/v1", api_key="test-key", model="demo-model")
    provider = OpenAICompatibleDecisionProvider(settings)

    def fake_urlopen(request_obj, timeout=0):
        assert request_obj.full_url == "https://example.com/v1/chat/completions"
        body = json.loads(request_obj.data.decode("utf-8"))
        assert body["model"] == "demo-model"
        return _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "type": "respond",
                                    "content": "hello from llm",
                                    "reason": "unit test",
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("core.llm.request.urlopen", fake_urlopen)
    action = provider.decide("context", AgentState(session_id="test-session", task="hello"))
    assert action["type"] == ActionType.respond.value
    assert action["content"] == "hello from llm"


def test_llm_provider_non_json_raises_protocol_error(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = LLMSettings(enabled=True, api_base="https://example.com/v1", api_key="test-key", model="demo-model")
    provider = OpenAICompatibleDecisionProvider(settings)

    def fake_urlopen(request_obj, timeout=0):
        return _FakeResponse({"choices": [{"message": {"content": "plain text reply"}}]})

    monkeypatch.setattr("core.llm.request.urlopen", fake_urlopen)
    with pytest.raises(LLMResponseError):
        provider.decide("context", AgentState(session_id="test-session", task="hello"))


def test_action_parser_non_json_fallback() -> None:
    action = parse_action_response("hello world")
    assert action["type"] == ActionType.respond.value
    assert action["content"] == "hello world"


def test_action_parser_non_json_can_be_forbidden() -> None:
    with pytest.raises(LLMResponseError):
        parse_action_response("hello world", allow_plaintext_fallback=False)


def test_runtime_uses_mock_provider_when_llm_disabled() -> None:
    runtime = AgentRuntime(llm_settings=LLMSettings(enabled=False))
    result = runtime.run("echo hello")
    assert result["output"]


def test_runtime_uses_real_provider_when_llm_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = LLMSettings(enabled=True, api_base="https://example.com/v1", api_key="test-key", model="demo-model")

    def fake_urlopen(request_obj, timeout=0):
        return _FakeResponse({"choices": [{"message": {"content": json.dumps({"type": "respond", "content": "ok"})}}]})

    monkeypatch.setattr("core.llm.request.urlopen", fake_urlopen)
    runtime = AgentRuntime(llm_settings=settings)
    result = runtime.run("hello")
    assert result["output"] == "ok"
    assert result["status"] == "finished"


def test_runtime_rejects_unknown_provider() -> None:
    with pytest.raises(LLMConfigurationError):
        AgentRuntime(llm_settings=LLMSettings(enabled=True, provider="unknown", api_base="x", api_key="y", model="z"))


def test_runtime_answers_identity_questions_explicitly() -> None:
    runtime = AgentRuntime(llm_settings=LLMSettings(enabled=True, provider=LLMProviderType.OPENAI_COMPATIBLE, api_base="https://example.com/v1", api_key="test-key", model="demo-model"))
    result = runtime.run("你是什么大模型？")
    assert "provider=" in result["output"]
    assert result["status"] == "finished"
    assert result["trace_events"][0].get("special_case") == "identity_question"
