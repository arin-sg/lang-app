"""
LLM Provider factory with task-based routing.

This module provides the factory function to get the appropriate LLM provider
based on the task type (extraction vs explanation). It handles provider
instantiation, caching, and configuration routing.
"""
from enum import Enum
from typing import Dict, Tuple, Optional

from app.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama import OllamaProvider


class LLMTask(str, Enum):
    """
    LLM task types for routing to appropriate providers.

    Different tasks may use different providers or models:
    - EXTRACTION: Extract learnable items from German text (complex, needs powerful model)
    - EXPLANATION: Lemmatize words, provide explanations (simpler, can use faster model)
    """
    EXTRACTION = "extraction"
    EXPLANATION = "explanation"


class ProviderType(str, Enum):
    """
    Supported LLM provider types.

    Unified Gateway:
    - LITELLM: LiteLLM proxy server (multi-provider gateway)

    Local providers (free, unlimited):
    - OLLAMA: Local Ollama server (default)
    - LM_STUDIO: LM Studio with OpenAI-compatible API

    Cloud providers (paid/rate-limited):
    - OPENAI: OpenAI GPT models
    - GEMINI: Google Gemini models
    """
    LITELLM = "litellm"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"
    GEMINI = "gemini"


# Provider cache: (task, provider_type) -> provider instance
# Ensures we reuse provider instances for efficiency
_provider_cache: Dict[Tuple[LLMTask, ProviderType], LLMProvider] = {}


def get_llm_provider(task: LLMTask) -> LLMProvider:
    """
    Get LLM provider for a specific task based on configuration.

    This is the main entry point for getting LLM providers. It routes to the
    appropriate provider based on environment configuration:
    - EXTRACTION_PROVIDER + corresponding model settings
    - EXPLANATION_PROVIDER + corresponding model settings

    Args:
        task: The task type (EXTRACTION or EXPLANATION)

    Returns:
        LLMProvider instance configured for the task

    Raises:
        ValueError: If task is unknown or provider type is unsupported

    Example:
        # Get provider for extraction
        provider = get_llm_provider(LLMTask.EXTRACTION)
        result = await provider.generate_json(prompt, system_prompt=system)

        # Get provider for explanation
        provider = get_llm_provider(LLMTask.EXPLANATION)
        response = await provider.generate(prompt)
    """
    # Get provider type from configuration
    # Note: Will be updated in Phase 4 when config.py is enhanced
    # For now, default to Ollama for all tasks
    if task == LLMTask.EXTRACTION:
        provider_type = _get_provider_type_from_config("extraction")
        model = _get_model_for_provider(provider_type, task)
    elif task == LLMTask.EXPLANATION:
        provider_type = _get_provider_type_from_config("explanation")
        model = _get_model_for_provider(provider_type, task)
    else:
        raise ValueError(f"Unknown task: {task}")

    # Check cache
    cache_key = (task, provider_type)
    if cache_key in _provider_cache:
        return _provider_cache[cache_key]

    # Create provider
    provider = _create_provider(provider_type, model, task)
    _provider_cache[cache_key] = provider
    return provider


def _get_provider_type_from_config(task_name: str) -> ProviderType:
    """
    Get provider type from configuration for a given task.

    Args:
        task_name: "extraction" or "explanation"

    Returns:
        ProviderType enum value

    Raises:
        ValueError: If provider type is not recognized
    """
    # Read from settings
    provider_str = getattr(settings, f"{task_name}_provider", "ollama")

    # Map string to enum
    provider_map = {
        "litellm": ProviderType.LITELLM,
        "ollama": ProviderType.OLLAMA,
        "lm_studio": ProviderType.LM_STUDIO,
        "openai": ProviderType.OPENAI,
        "gemini": ProviderType.GEMINI,
    }

    provider_type = provider_map.get(provider_str.lower())
    if provider_type is None:
        raise ValueError(
            f"Unknown provider '{provider_str}' for {task_name}. "
            f"Valid options: {', '.join(provider_map.keys())}"
        )

    return provider_type


def _get_model_for_provider(provider_type: ProviderType, task: LLMTask) -> str:
    """
    Get model name for a given provider and task.

    Args:
        provider_type: The provider type (LiteLLM, Ollama, LM Studio, OpenAI, Gemini)
        task: The task type (EXTRACTION or EXPLANATION)

    Returns:
        Model name/identifier string

    Example:
        - LiteLLM EXTRACTION -> "extraction-model" (from settings.litellm_extraction_model)
        - Ollama EXTRACTION -> "llama3.2" (from settings.ollama_extraction_model)
        - OpenAI EXTRACTION -> "gpt-4o-mini" (from settings.openai_extraction_model)
    """
    task_suffix = "extraction" if task == LLMTask.EXTRACTION else "explanation"

    if provider_type == ProviderType.LITELLM:
        return getattr(settings, f"litellm_{task_suffix}_model")
    elif provider_type == ProviderType.OLLAMA:
        return getattr(settings, f"ollama_{task_suffix}_model")
    elif provider_type == ProviderType.LM_STUDIO:
        # TODO (Phase 5): Will read from settings.lm_studio_{task_suffix}_model
        return "local-model"
    elif provider_type == ProviderType.OPENAI:
        # TODO (Phase 5): Will read from settings.openai_{task_suffix}_model
        return "gpt-4o-mini"
    elif provider_type == ProviderType.GEMINI:
        # TODO (Phase 5): Will read from settings.gemini_{task_suffix}_model
        return "gemini-1.5-flash"
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def _create_provider(
    provider_type: ProviderType,
    model: str,
    task: LLMTask
) -> LLMProvider:
    """
    Factory function to instantiate a provider.

    Args:
        provider_type: The provider type to create
        model: Default model for this provider instance
        task: The task this provider will be used for

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider_type is not supported
        ImportError: If required SDK is not installed (OpenAI, Gemini)
    """
    if provider_type == ProviderType.LITELLM:
        from app.providers.litellm_provider import LiteLLMProvider
        return LiteLLMProvider(
            base_url=settings.litellm_base_url,
            default_model=model,
            timeout=settings.extraction_timeout_seconds
        )
    elif provider_type == ProviderType.OLLAMA:
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            default_model=model,
            timeout=settings.extraction_timeout_seconds
        )
    elif provider_type == ProviderType.LM_STUDIO:
        # TODO (Phase 5): Implement LMStudioProvider
        raise NotImplementedError(
            "LM Studio provider not yet implemented. "
            "Will be available in Phase 5."
        )
    elif provider_type == ProviderType.OPENAI:
        # TODO (Phase 5): Implement OpenAIProvider
        raise NotImplementedError(
            "OpenAI provider not yet implemented. "
            "Will be available in Phase 5."
        )
    elif provider_type == ProviderType.GEMINI:
        # TODO (Phase 5): Implement GeminiProvider
        raise NotImplementedError(
            "Gemini provider not yet implemented. "
            "Will be available in Phase 5."
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")


def clear_provider_cache():
    """
    Clear the provider cache.

    Useful for testing or when configuration changes and providers need to be
    reinitialized. In production, providers are cached for the lifetime of the
    application.
    """
    global _provider_cache
    _provider_cache.clear()
