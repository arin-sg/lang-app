"""
Ollama Client - Compatibility shim for backward compatibility.

DEPRECATED: This module is maintained for backward compatibility only.
New code should use app.providers.ollama.OllamaProvider directly.

This module now imports from the new provider architecture (app.providers.ollama)
to maintain compatibility with existing code while enabling the new multi-provider
system.
"""
from typing import Optional

# Import from new provider architecture
from app.providers.ollama import OllamaProvider, get_ollama_provider
from app.providers.exceptions import (
    LLMConnectionError as OllamaConnectionError,
    LLMTimeoutError as OllamaTimeoutError,
)

# Export for backward compatibility
OllamaClient = OllamaProvider


def get_ollama_client() -> OllamaProvider:
    """
    Get the singleton Ollama client instance.

    DEPRECATED: Use app.providers.factory.get_llm_provider() instead.

    This function is maintained for backward compatibility. It returns an
    OllamaProvider instance that implements the same interface as the old
    OllamaClient.

    Returns:
        OllamaProvider instance (compatible with old OllamaClient interface)
    """
    return get_ollama_provider()


__all__ = [
    "OllamaClient",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "get_ollama_client",
]
