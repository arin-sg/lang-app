"""
Ollama Client - Wrapper for interacting with local Ollama LLM.
"""
import httpx
import json
from typing import Optional, Dict, Any
from app.config import settings


class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama."""
    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama request times out."""
    pass


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama API base URL (default from settings)
            timeout: Request timeout in seconds (default from settings)
        """
        self.base_url = base_url or settings.ollama_base_url
        self.timeout = timeout or settings.extraction_timeout_seconds
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: The prompt to send
            model: Model to use (default: extraction model from settings)
            system_prompt: Optional system prompt
            format: Optional response format (e.g., "json")

        Returns:
            Generated text response

        Raises:
            OllamaConnectionError: Cannot connect to Ollama
            OllamaTimeoutError: Request timed out
        """
        model = model or settings.ollama_extraction_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 2000,  # Limit output tokens for faster response
                "temperature": 0.3,   # Lower temperature for more focused output
                "top_p": 0.9
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        if format:
            payload["format"] = format

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except httpx.ConnectError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: {str(e)}"
            )
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(
                f"Ollama request timed out after {self.timeout}s: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Ollama.

        Args:
            prompt: The prompt to send
            model: Model to use
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dict

        Raises:
            OllamaConnectionError: Cannot connect to Ollama
            OllamaTimeoutError: Request timed out
            json.JSONDecodeError: Response is not valid JSON
        """
        response_text = await self.generate(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            format="json"
        )

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
            raise json.JSONDecodeError(
                f"Ollama response is not valid JSON: {response_text[:200]}",
                response_text,
                0
            )

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

    async def list_models(self) -> list:
        """
        List available models in Ollama.

        Returns:
            List of model names
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
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get the singleton Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
