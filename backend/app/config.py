"""
Configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./data/lang_app.db"

    # Provider Selection
    extraction_provider: str = "ollama"
    explanation_provider: str = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_extraction_model: str = "llama3.2"
    ollama_explanation_model: str = "llama3.2"

    # LiteLLM
    litellm_base_url: str = "http://localhost:4000"
    litellm_extraction_model: str = "extraction-model"
    litellm_explanation_model: str = "explanation-model"

    # API
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # Extraction
    extraction_timeout_seconds: int = 60
    max_text_length: int = 500
    batch_size_sentences: int = 2
    max_items_per_type: int = 5
    enable_parallel_batching: bool = True

    # Verification
    use_llm_for_canonicalization: bool = False
    batch_canonicalization: bool = True
    enable_semantic_deduplication: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
