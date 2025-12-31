"""
Unified exception hierarchy for LLM providers.

These exceptions provide consistent error handling across all LLM providers
(Ollama, LM Studio, OpenAI, Gemini). Each provider maps its specific errors
to these unified exception types.
"""


class LLMProviderError(Exception):
    """
    Base exception for all LLM provider errors.

    All provider-specific exceptions should inherit from this class to enable
    consistent error handling at the API layer.
    """
    pass


class LLMConnectionError(LLMProviderError):
    """
    Raised when cannot connect to LLM provider.

    Examples:
    - Ollama service not running (connection refused)
    - Network timeout connecting to cloud provider
    - Invalid base URL or hostname
    """
    pass


class LLMTimeoutError(LLMProviderError):
    """
    Raised when LLM request exceeds timeout limit.

    Examples:
    - Local model taking too long to generate (CPU inference)
    - Cloud provider API response timeout
    - Network latency exceeding configured timeout
    """
    pass


class LLMAuthenticationError(LLMProviderError):
    """
    Raised when authentication to LLM provider fails.

    Examples:
    - Invalid API key (OpenAI, Gemini)
    - Expired API key
    - Missing API key for cloud provider
    - Insufficient permissions

    Note: Not applicable to local providers (Ollama, LM Studio)
    """
    pass


class LLMRateLimitError(LLMProviderError):
    """
    Raised when LLM provider rate limit is exceeded.

    Examples:
    - OpenAI: Exceeded requests per minute (RPM) or tokens per day (TPD)
    - Gemini: Exceeded free tier quota (15 RPM)
    - Temporary throttling due to high load

    Note: Not applicable to local providers (Ollama, LM Studio)
    """
    pass


class LLMQuotaExceededError(LLMProviderError):
    """
    Raised when LLM provider quota is exhausted.

    Examples:
    - OpenAI: Account out of credits
    - Gemini: Monthly quota exceeded
    - Pay-as-you-go billing disabled

    Note: Not applicable to local providers (Ollama, LM Studio)
    """
    pass


class LLMModelNotFoundError(LLMProviderError):
    """
    Raised when requested model is not available from provider.

    Examples:
    - Ollama: Model not pulled locally (run `ollama pull <model>`)
    - LM Studio: Model not loaded in server
    - OpenAI: Invalid model name or deprecated model
    - Gemini: Model name typo or region restriction
    """
    pass


class LLMInvalidResponseError(LLMProviderError):
    """
    Raised when LLM provider returns unexpected or invalid response.

    Examples:
    - JSON generation returned non-JSON text
    - Empty response when content expected
    - Malformed response structure
    - Provider API schema changed
    """
    pass
