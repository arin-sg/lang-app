"""
Abstract base class for LLM providers.

This module defines the LLMProvider interface that all provider implementations
must follow (Ollama, LM Studio, OpenAI, Gemini, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    All LLM providers (Ollama, LM Studio, OpenAI, Gemini) must implement
    this interface to ensure consistent behavior across the application.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion from prompt.

        Args:
            prompt: The user prompt to send to the LLM
            model: Optional model override (uses default if not specified)
            system_prompt: Optional system prompt for context
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate (provider-specific default if None)

        Returns:
            Generated text response

        Raises:
            LLMConnectionError: Cannot connect to provider
            LLMTimeoutError: Request timed out
            LLMAuthenticationError: Authentication failed (invalid API key)
            LLMRateLimitError: Rate limit exceeded
        """
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from prompt.

        This method enforces JSON format output. The implementation may use
        provider-specific JSON modes (e.g., Ollama format="json", OpenAI
        response_format, Gemini generation_config).

        Args:
            prompt: The user prompt to send to the LLM
            model: Optional model override (uses default if not specified)
            system_prompt: Optional system prompt for context
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate (provider-specific default if None)

        Returns:
            Parsed JSON dictionary

        Raises:
            LLMConnectionError: Cannot connect to provider
            LLMTimeoutError: Request timed out
            LLMAuthenticationError: Authentication failed (invalid API key)
            LLMRateLimitError: Rate limit exceeded
            json.JSONDecodeError: Response is not valid JSON
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if the provider is accessible and healthy.

        This method should verify:
        - Provider service is running
        - Network connectivity
        - Authentication is valid (for cloud providers)

        Returns:
            True if provider is healthy and accessible, False otherwise
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        List available models from the provider.

        Returns:
            List of model names/identifiers available from this provider.
            Returns empty list if provider is not accessible.
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Close provider connections and cleanup resources.

        This method should close HTTP clients, release connections, and
        perform any necessary cleanup. Should be called when shutting down.
        """
        pass
