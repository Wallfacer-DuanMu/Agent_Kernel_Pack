from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.llm import LLMSettings, LLMProviderType


CONFIG_PATH = Path(".agent_kernel_llm.json")


@dataclass
class StoredLLMConfig:
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
    headers: dict[str, str] = field(default_factory=dict)
    extra_payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "StoredLLMConfig":
        return cls(
            enabled=settings.enabled,
            provider=settings.provider,
            api_base=settings.api_base,
            api_path=settings.api_path,
            api_key=settings.api_key,
            model=settings.model,
            system_prompt=settings.system_prompt,
            temperature=settings.temperature,
            timeout_seconds=settings.timeout_seconds,
            max_tokens=settings.max_tokens,
            top_p=settings.top_p,
            headers=settings.headers,
            extra_payload=settings.extra_payload,
        )

    def to_settings(self) -> LLMSettings:
        return LLMSettings(
            enabled=self.enabled,
            provider=self.provider,
            api_base=self.api_base,
            api_path=self.api_path,
            api_key=self.api_key,
            model=self.model,
            system_prompt=self.system_prompt,
            temperature=self.temperature,
            timeout_seconds=self.timeout_seconds,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            headers=self.headers,
            extra_payload=self.extra_payload,
        )


def _normalize_legacy_payload(data: dict[str, Any]) -> dict[str, Any]:
    if "provider" not in data:
        data["provider"] = LLMProviderType.OPENAI_COMPATIBLE if data.get("enabled") else LLMProviderType.MOCK
    if "api_path" not in data:
        data["api_path"] = "/chat/completions"
    if "timeout_seconds" not in data:
        data["timeout_seconds"] = 60
    if "headers" not in data:
        data["headers"] = {}
    if "extra_payload" not in data:
        data["extra_payload"] = {}
    return data


def load_llm_config(path: Path = CONFIG_PATH) -> LLMSettings:
    if not path.exists():
        return LLMSettings()
    data = _normalize_legacy_payload(json.loads(path.read_text(encoding="utf-8")))
    return StoredLLMConfig(**data).to_settings()


def save_llm_config(settings: LLMSettings, path: Path = CONFIG_PATH) -> None:
    path.write_text(json.dumps(asdict(StoredLLMConfig.from_settings(settings)), ensure_ascii=False, indent=2), encoding="utf-8")


def clear_llm_config(path: Path = CONFIG_PATH) -> None:
    if path.exists():
        path.unlink()
