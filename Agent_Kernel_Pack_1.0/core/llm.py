from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable
from urllib import error, request

from core.actions import Action, ActionType, parse_action
from core.llm_errors import LLMConfigurationError, LLMRequestError, LLMResponseError
from core.state import AgentState


class LLMProviderType:
    MOCK = "mock"
    OPENAI_COMPATIBLE = "openai_compatible"
    KIMI_COMPATIBLE = "kimi_compatible"
    QWEN_COMPATIBLE = "qwen_compatible"
    DEEPSEEK_COMPATIBLE = "deepseek_compatible"
    ZHIPU_COMPATIBLE = "zhipu_compatible"
    ANTHROPIC_COMPATIBLE = "anthropic_compatible"


@dataclass
class OpenAICompatibleEndpoint:
    base_url: str = ""
    path: str = "/chat/completions"

    def build_url(self) -> str:
        base = self.base_url.strip().rstrip("/")
        path = self.path.strip()
        if not base:
            return path
        if not path:
            return base
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        if base.endswith(path):
            return base
        return f"{base}{path}"


@dataclass
class LLMSettings:
    enabled: bool = False
    provider: str = LLMProviderType.OPENAI_COMPATIBLE
    api_base: str = ""
    api_path: str = "/chat/completions"
    api_key: str = ""
    model: str = ""
    system_prompt: str = ""
    temperature: float = 0.2
    timeout_seconds: int = 60
    max_tokens: int | None = None
    top_p: float | None = None
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0
    headers: dict[str, str] = field(default_factory=dict)
    extra_payload: dict[str, Any] = field(default_factory=dict)

    def normalized_provider(self) -> str:
        provider = (self.provider or LLMProviderType.OPENAI_COMPATIBLE).strip().lower()
        if not self.enabled:
            return LLMProviderType.MOCK
        if provider == LLMProviderType.MOCK:
            raise LLMConfigurationError("LLM mode is enabled but provider is mock; refusing to use local CLI/mock replies.")
        return provider

    def endpoint(self) -> OpenAICompatibleEndpoint:
        return OpenAICompatibleEndpoint(base_url=self.api_base, path=self.api_path)

    def validate(self) -> None:
        provider = self.normalized_provider()
        if not self.enabled:
            return
        missing = []
        if provider in (
            LLMProviderType.OPENAI_COMPATIBLE,
            LLMProviderType.KIMI_COMPATIBLE,
            LLMProviderType.QWEN_COMPATIBLE,
            LLMProviderType.DEEPSEEK_COMPATIBLE,
            LLMProviderType.ZHIPU_COMPATIBLE,
            LLMProviderType.ANTHROPIC_COMPATIBLE,
        ):
            if not self.api_base.strip():
                missing.append("API Base URL")
            if not self.api_key.strip():
                missing.append("API Key")
            if not self.model.strip():
                missing.append("Model")
        else:
            raise LLMConfigurationError(f"Unsupported LLM provider: {self.provider}")
        if missing:
            raise LLMConfigurationError(f"Missing LLM configuration: {', '.join(missing)}")


@runtime_checkable
class DecisionProvider(Protocol):
    def decide(self, context: str, state: AgentState) -> Action | dict[str, Any]:
        ...


class MockDecisionProvider:
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


class OpenAIChatClient:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self.settings.validate()

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.settings.endpoint().build_url()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.api_key}",
        }
        headers.update(self.settings.headers)

        last_http_code: int | None = None
        last_detail = ""

        for attempt in range(self.settings.max_retries + 1):
            req = request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                try:
                    return json.loads(body)
                except json.JSONDecodeError as exc:
                    raise LLMResponseError(f"Unexpected LLM response format: {body}") from exc
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                last_http_code = int(exc.code)
                last_detail = detail
                is_retryable = exc.code in (408, 409, 429, 500, 502, 503, 504)
                if is_retryable and attempt < self.settings.max_retries:
                    time.sleep(self.settings.retry_backoff_seconds * (2**attempt))
                    continue
                raise LLMRequestError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
            except error.URLError as exc:
                if attempt < self.settings.max_retries:
                    time.sleep(self.settings.retry_backoff_seconds * (2**attempt))
                    continue
                raise LLMRequestError(f"LLM request failed: {exc.reason}") from exc

        raise LLMRequestError(
            f"LLM request failed after retries. Last HTTP code: {last_http_code}, detail: {last_detail}"
        )

class OpenAICompatibleDecisionProvider:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self.client = OpenAIChatClient(settings)

    def decide(self, context: str, state: AgentState) -> dict[str, Any]:
        self.settings.validate()
        payload = {
            "model": self.settings.model,
            "temperature": self.settings.temperature,
            "messages": [
                {"role": "system", "content": self.settings.system_prompt.strip() or default_system_prompt()},
                {"role": "user", "content": build_user_prompt(context, state)},
            ],
        }
        if self.settings.max_tokens is not None:
            payload["max_tokens"] = self.settings.max_tokens
        if self.settings.top_p is not None:
            payload["top_p"] = self.settings.top_p
        payload.update(self.settings.extra_payload)
        raw = self.client.create_chat_completion(payload)
        text = extract_chat_message_content(raw)
        return parse_action_response(text, allow_plaintext_fallback=False)


def default_system_prompt() -> str:
    return (
        "You are the decision engine for an Agent Kernel runtime. "
        "Reply with exactly one JSON object and no extra prose. "
        "Allowed action types: respond, call_tool, request_approval, finish, fail. "
        "For call_tool you must provide tool_name and tool_args. "
        "For respond, finish, or fail you should provide content."
    )


def build_user_prompt(context: str, state: AgentState) -> str:
    return (
        "Decide the next action for the runtime.\n\n"
        f"Task: {state.task}\n"
        f"Current step: {state.current_step}\n"
        f"Max steps: {state.max_steps}\n\n"
        "Runtime context:\n"
        f"{context}\n\n"
        "Return JSON in this shape:\n"
        '{"type":"respond","content":"...","tool_name":"","tool_args":{},"reason":"..."}'
    )


def extract_chat_message_content(response_data: dict[str, Any]) -> str:
    try:
        choices = response_data["choices"]
        if not choices:
            raise KeyError("choices")
        message = choices[0].get("message") or {}
        if "content" in message and message["content"] is not None:
            return str(message["content"])
        if "text" in choices[0] and choices[0]["text"] is not None:
            return str(choices[0]["text"])
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMResponseError(f"Unexpected LLM response format: {response_data}") from exc
    raise LLMResponseError(f"Unexpected LLM response format: {response_data}")


def parse_action_response(raw_text: str, *, allow_plaintext_fallback: bool = True) -> dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        if allow_plaintext_fallback:
            return {"type": ActionType.respond.value, "content": raw_text.strip(), "reason": "LLM returned non-JSON output; treated as respond."}
        raise LLMResponseError(f"LLM returned non-JSON action payload: {raw_text.strip()}") from exc

    action = parse_action(parsed)
    result = asdict(action)
    if result["type"] == ActionType.respond.value and not result.get("content"):
        result["content"] = raw_text.strip()
    return result


def create_decision_provider(settings: LLMSettings | None) -> DecisionProvider:
    settings = settings or LLMSettings()
    provider = settings.normalized_provider()
    if provider == LLMProviderType.MOCK:
        return MockDecisionProvider()
    if provider in (
        LLMProviderType.OPENAI_COMPATIBLE,
        LLMProviderType.KIMI_COMPATIBLE,
        LLMProviderType.QWEN_COMPATIBLE,
        LLMProviderType.DEEPSEEK_COMPATIBLE,
        LLMProviderType.ZHIPU_COMPATIBLE,
        LLMProviderType.ANTHROPIC_COMPATIBLE,
    ):
        return OpenAICompatibleDecisionProvider(settings)
    raise LLMConfigurationError(f"Unsupported LLM provider: {settings.provider}")
