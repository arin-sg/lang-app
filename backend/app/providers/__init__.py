"""
LLM Provider abstraction layer.

This package provides a unified interface for interacting with different LLM providers:
- Multi-provider gateway: LiteLLM (recommended for production)
- Local providers: Ollama, LM Studio
- Cloud providers: OpenAI, Gemini

Usage:
    from app.providers.factory import get_llm_provider, LLMTask
    from app.providers.base import LLMProvider
    from app.providers.exceptions import LLMConnectionError, LLMTimeoutError

    # Get provider for extraction task (routing based on config)
    provider = get_llm_provider(LLMTask.EXTRACTION)

    # Generate text
    response = await provider.generate("Translate to German: Hello")

    # Generate structured JSON
    result = await provider.generate_json(
        prompt="Extract items from this text",
        system_prompt="You are a linguist"
    )

Configuration (via .env):
    EXTRACTION_PROVIDER=litellm  # or ollama, openai, gemini
    LITELLM_BASE_URL=http://localhost:4000
    LITELLM_EXTRACTION_MODEL=extraction-model
"""

from app.providers.base import LLMProvider
from app.providers.exceptions import (
    LLMProviderError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMQuotaExceededError,
    LLMModelNotFoundError,
    LLMInvalidResponseError,
)
from app.providers.factory import (
    get_llm_provider,
    LLMTask,
    ProviderType,
    clear_provider_cache,
)

__all__ = [
    # Base class
    "LLMProvider",
    # Exceptions
    "LLMProviderError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMQuotaExceededError",
    "LLMModelNotFoundError",
    "LLMInvalidResponseError",
    # Factory
    "get_llm_provider",
    "LLMTask",
    "ProviderType",
    "clear_provider_cache",
]
