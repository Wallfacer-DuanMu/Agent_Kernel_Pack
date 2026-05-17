from __future__ import annotations


class LLMError(RuntimeError):
    """Base class for LLM integration errors."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM configuration is incomplete or invalid."""


class LLMRequestError(LLMError):
    """Raised when an HTTP request to a model provider fails."""


class LLMResponseError(LLMError):
    """Raised when a provider response cannot be parsed."""
