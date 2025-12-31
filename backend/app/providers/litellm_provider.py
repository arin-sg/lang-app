"""
LiteLLM Provider - Routes through LiteLLM proxy for multi-provider support.

This provider implements the LLMProvider interface and communicates with a
LiteLLM proxy server using OpenAI-compatible API. The proxy handles all
provider-specific logic (Ollama, OpenAI, Gemini, etc.).
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


class LiteLLMProvider(LLMProvider):
    """
    LiteLLM provider for unified multi-provider LLM access.

    Routes requests through LiteLLM proxy server which handles:
    - Provider-specific API translation
    - Fallback chains (automatic failover)
    - Load balancing across deployments
    - Cost tracking and rate limiting
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize LiteLLM provider.

        Args:
            base_url: LiteLLM proxy base URL (default from settings)
            default_model: Default model alias from litellm_config.yaml
            timeout: Request timeout in seconds (default from settings)
        """
        self.base_url = base_url or settings.litellm_base_url
        self.default_model = default_model or settings.litellm_extraction_model
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
        Generate text using LiteLLM proxy (OpenAI-compatible API).

        Args:
            prompt: The prompt to send
            model: Model alias (default: configured model)
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            LLMConnectionError: Cannot connect to LiteLLM proxy
            LLMTimeoutError: Request timed out
        """
        model = model or self.default_model

        # OpenAI-compatible message format
        messages = [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2000
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Extract content from OpenAI format
            return result["choices"][0]["message"]["content"]

        except httpx.ConnectError as e:
            raise LLMConnectionError(
                f"Cannot connect to LiteLLM proxy at {self.base_url}. "
                f"Make sure proxy is running: ./scripts/start_litellm.sh"
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                f"LiteLLM request timed out after {self.timeout}s: {str(e)}"
            )
        except Exception as e:
            raise LLMConnectionError(f"LiteLLM error: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response using LiteLLM proxy.

        Uses OpenAI's response_format to enforce JSON output. LiteLLM proxy
        translates this to provider-specific JSON modes.

        Args:
            prompt: The prompt to send
            model: Model alias (default: configured model)
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Parsed JSON dict

        Raises:
            LLMConnectionError: Cannot connect to LiteLLM proxy
            LLMTimeoutError: Request timed out
            LLMInvalidResponseError: Response is not valid JSON
        """
        model = model or self.default_model

        messages = [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2000,
            "response_format": {"type": "json_object"}  # Force JSON output
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Extract and parse JSON from response
            content = result["choices"][0]["message"]["content"]

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response if it's wrapped in text
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(content[start:end])
                    except json.JSONDecodeError:
                        pass

                raise LLMInvalidResponseError(
                    f"LiteLLM response is not valid JSON: {content[:200]}"
                )

        except httpx.ConnectError as e:
            raise LLMConnectionError(
                f"Cannot connect to LiteLLM proxy at {self.base_url}. "
                f"Make sure proxy is running: ./scripts/start_litellm.sh"
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                f"LiteLLM request timed out after {self.timeout}s: {str(e)}"
            )
        except (LLMConnectionError, LLMTimeoutError, LLMInvalidResponseError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise LLMConnectionError(f"LiteLLM error: {str(e)}")

    async def check_health(self) -> bool:
        """
        Check if LiteLLM proxy is running and accessible.

        Returns:
            True if proxy is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """
        List available models from LiteLLM proxy.

        Returns:
            List of model aliases configured in litellm_config.yaml
        """
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
        except Exception:
            return []

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_litellm_provider: Optional[LiteLLMProvider] = None


def get_litellm_provider() -> LiteLLMProvider:
    """
    Get the singleton LiteLLM provider instance.

    Returns:
        LiteLLMProvider instance
    """
    global _litellm_provider
    if _litellm_provider is None:
        _litellm_provider = LiteLLMProvider()
    return _litellm_provider
