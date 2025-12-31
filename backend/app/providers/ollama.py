"""
Ollama LLM Provider implementation.

This module provides the OllamaProvider class that implements the LLMProvider
interface for local Ollama inference.
"""
import httpx
import json
from typing import Optional, Dict, Any, List

from app.config import settings
from app.providers.base import LLMProvider
from app.providers.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMInvalidResponseError,
)


class OllamaProvider(LLMProvider):
    """
    Ollama provider implementation for local LLM inference.

    This provider connects to a local Ollama server (default: http://localhost:11434)
    and supports any models pulled via `ollama pull <model>`.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama API base URL (default from settings)
            default_model: Default model to use (default from settings)
            timeout: Request timeout in seconds (default from settings)
        """
        self.base_url = base_url or settings.ollama_base_url
        self.default_model = default_model or settings.ollama_extraction_model
        self.timeout = timeout or settings.extraction_timeout_seconds
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: The prompt to send
            model: Model to use (default: configured model)
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate (default: 2000)

        Returns:
            Generated text response

        Raises:
            LLMConnectionError: Cannot connect to Ollama
            LLMTimeoutError: Request timed out
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens or 2000,
                "temperature": temperature,
                "top_p": 0.9
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except httpx.ConnectError as e:
            raise LLMConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: {str(e)}"
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                f"Ollama request timed out after {self.timeout}s: {str(e)}"
            )
        except Exception as e:
            raise LLMConnectionError(f"Ollama error: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Ollama.

        Uses Ollama's format="json" parameter to enforce JSON output.

        Args:
            prompt: The prompt to send
            model: Model to use (default: configured model)
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate (default: 2000)

        Returns:
            Parsed JSON dict

        Raises:
            LLMConnectionError: Cannot connect to Ollama
            LLMTimeoutError: Request timed out
            LLMInvalidResponseError: Response is not valid JSON
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",  # Enforce JSON output
            "options": {
                "num_predict": max_tokens or 2000,
                "temperature": temperature,
                "top_p": 0.9
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "")

            # Parse JSON from response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response if it's wrapped in text
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(response_text[start:end])
                    except json.JSONDecodeError:
                        pass

                raise LLMInvalidResponseError(
                    f"Ollama response is not valid JSON: {response_text[:200]}"
                )

        except httpx.ConnectError as e:
            raise LLMConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: {str(e)}"
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                f"Ollama request timed out after {self.timeout}s: {str(e)}"
            )
        except (LLMConnectionError, LLMTimeoutError, LLMInvalidResponseError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise LLMConnectionError(f"Ollama error: {str(e)}")

    async def check_health(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """
        List available models in Ollama.

        Returns:
            List of model names available locally
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model.get("name") for model in data.get("models", [])]
        except Exception:
            return []

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_ollama_provider: Optional[OllamaProvider] = None


def get_ollama_provider() -> OllamaProvider:
    """
    Get the singleton Ollama provider instance.

    This function maintains backward compatibility with the old get_ollama_client()
    pattern while using the new provider architecture.

    Returns:
        OllamaProvider instance
    """
    global _ollama_provider
    if _ollama_provider is None:
        _ollama_provider = OllamaProvider()
    return _ollama_provider
