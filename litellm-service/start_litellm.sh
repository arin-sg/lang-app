#!/bin/bash
# Start LiteLLM proxy for German language learning app

cd "$(dirname "$0")"

echo "============================================"
echo "  LiteLLM Proxy Server"
echo "  German Language Learning App"
echo "============================================"
echo ""
echo "Starting LiteLLM proxy on port 4000..."
echo "Config: litellm_config.yaml"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

# Start LiteLLM with clean environment (no DATABASE_URL)
# Only pass PATH and HOME to avoid DATABASE_URL from .env file
# LiteLLM will read API keys from environment or litellm_config.yaml
env -i \
  PATH="$PATH" \
  HOME="$HOME" \
  OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
  ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  HUGGINGFACE_API_KEY="${HUGGINGFACE_API_KEY:-}" \
  ./venv/bin/litellm --config litellm_config.yaml --port 4000
