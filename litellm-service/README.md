# LiteLLM Proxy Service

Multi-provider LLM gateway for the German Language Learning App. This service provides a unified OpenAI-compatible API for accessing 100+ LLM providers (Ollama, OpenAI, Gemini, Claude, HuggingFace, and more).

## Architecture

```
Backend App (Port 8000)
    ↓ HTTP
LiteLLM Proxy (Port 4000) ← You are here
    ↓ Provider-specific APIs
[Ollama | OpenAI | Gemini | Claude | HuggingFace | ...]
```

**Why a Separate Service?**
- **Environment Isolation**: Avoids DATABASE_URL conflicts with the main backend
- **Independent Scaling**: Can run on different machines or containers
- **Provider Management**: Centralized configuration for all LLM providers
- **Fallback & Load Balancing**: Automatic failover between providers

## Prerequisites

- **Python 3.10+**
- **Ollama** (if using local models): [ollama.com/download](https://ollama.com/download)
- **Cloud API Keys** (optional): For OpenAI, Gemini, Claude, etc.

## Quick Start

### 1. Setup

```bash
# Navigate to service directory
cd litellm-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (Optional)

If using cloud providers, copy and edit `.env`:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

**For local-only usage (Ollama):** No `.env` needed!

### 3. Start Service

```bash
./start_litellm.sh
```

The service will start on **http://localhost:4000**

### 4. Verify

```bash
# Health check
curl http://localhost:4000/health

# List available models
curl http://localhost:4000/models
```

## Configuration

All configuration is in [litellm_config.yaml](litellm_config.yaml).

### Default Setup (Ollama)

The service is pre-configured to use local Ollama models:

```yaml
model_list:
  - model_name: extraction-model
    litellm_params:
      model: ollama/llama3.2
      api_base: http://localhost:11434
```

**Make sure Ollama is running:**
```bash
ollama serve  # Start Ollama server
ollama pull llama3.2  # Download model if needed
```

### Adding Cloud Providers

#### OpenAI (GPT)

```yaml
model_list:
  - model_name: extraction-model-openai
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
```

Set in `.env`:
```bash
OPENAI_API_KEY=sk-...
```

#### Google Gemini

```yaml
model_list:
  - model_name: explanation-model-gemini
    litellm_params:
      model: gemini/gemini-1.5-flash
      api_key: os.environ/GEMINI_API_KEY
```

Set in `.env`:
```bash
GEMINI_API_KEY=...
```

#### Anthropic Claude

```yaml
model_list:
  - model_name: extraction-model-claude
    litellm_params:
      model: anthropic/claude-3-5-haiku-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
```

Set in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

#### HuggingFace

```yaml
model_list:
  - model_name: explanation-model-hf
    litellm_params:
      model: huggingface/mistralai/Mistral-7B-Instruct-v0.3
      api_key: os.environ/HUGGINGFACE_API_KEY
```

Set in `.env`:
```bash
HUGGINGFACE_API_KEY=hf_...
```

#### LM Studio

```yaml
model_list:
  - model_name: extraction-model-lmstudio
    litellm_params:
      model: openai/local-model
      api_base: http://localhost:1234/v1
```

No API key needed - LM Studio runs locally.

### Advanced Configuration

#### Automatic Fallbacks

```yaml
router_settings:
  fallbacks:
    - extraction-model: ["extraction-model-openai"]  # Ollama → OpenAI
    - explanation-model: ["explanation-model-gemini"]  # Ollama → Gemini
```

If Ollama fails, LiteLLM automatically retries with the fallback provider.

#### Load Balancing

```yaml
router_settings:
  routing_strategy: simple-shuffle  # Options: simple-shuffle, least-busy, latency-based-routing
  num_retries: 2
  timeout: 60
  allowed_fails: 3  # Disable provider after 3 consecutive failures
```

#### Cost Tracking (Advanced)

Requires PostgreSQL or MySQL database:

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: postgresql://user:pass@localhost/litellm
```

Set in `.env`:
```bash
LITELLM_MASTER_KEY=sk-1234...
DATABASE_URL=postgresql://...
```

Then run Prisma migrations:
```bash
pip install prisma
prisma generate
prisma db push
```

## API Endpoints

The service provides an OpenAI-compatible API:

### POST /v1/chat/completions

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "extraction-model",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### GET /models

```bash
curl http://localhost:4000/models
```

### GET /health

```bash
curl http://localhost:4000/health
```

## Integration with Backend

The backend app connects to this service using the `LiteLLMProvider` class.

**Backend .env configuration:**
```bash
EXTRACTION_PROVIDER=litellm
EXPLANATION_PROVIDER=litellm
LITELLM_BASE_URL=http://localhost:4000
LITELLM_EXTRACTION_MODEL=extraction-model
LITELLM_EXPLANATION_MODEL=explanation-model
```

The backend will make HTTP requests to this service for all LLM operations.

## Troubleshooting

### Service won't start

**Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If not running:
```bash
ollama serve
```

**Check port 4000 is available:**
```bash
lsof -i :4000  # macOS/Linux
# Kill process if needed: kill -9 <PID>
```

### Models not found

**Pull Ollama model:**
```bash
ollama list  # Check installed models
ollama pull llama3.2  # Download if missing
```

**Verify model name in litellm_config.yaml:**
```yaml
model: ollama/llama3.2  # Must match ollama model name
```

### API key errors (cloud providers)

**Check environment variables:**
```bash
source venv/bin/activate
echo $OPENAI_API_KEY  # Should print your key
```

**Verify .env is loaded:**
```bash
set -a; source .env; set +a  # Load .env manually
./start_litellm.sh
```

### Timeout errors

**Increase timeout in litellm_config.yaml:**
```yaml
router_settings:
  timeout: 180  # Increase to 180 seconds for large models
```

**Or reduce model size:**
```yaml
model: ollama/llama3.2  # 3B model - faster
# Instead of: ollama/llama3.2:70b  # 70B model - slower
```

### Backend can't connect

**Verify service is running:**
```bash
curl http://localhost:4000/health
# Expected: {"status": "healthy"}
```

**Check backend .env:**
```bash
# In backend/.env
LITELLM_BASE_URL=http://localhost:4000  # Must match service port
```

## Provider Costs Reference

| Provider | Model | Cost (per 1M tokens) | Free Tier |
|----------|-------|----------------------|-----------|
| Ollama | llama3.2, mistral | $0 (local) | Unlimited |
| OpenAI | gpt-4o-mini | ~$0.15-0.60 | $5 credit (trial) |
| Gemini | gemini-1.5-flash | Free → $0.075 | 15 RPM, 1500 RPD |
| Claude | claude-3-5-haiku | ~$0.80-4.00 | $5 credit (trial) |
| HuggingFace | Various | Free → varies | Rate limited |

**Recommendation:** Start with Ollama (free, unlimited). Add cloud fallbacks only if needed.

## Development

### Logs

LiteLLM outputs logs to stdout. Increase verbosity:

```yaml
general_settings:
  set_verbose: true  # Detailed logs
  json_logs: true    # JSON format
```

### Testing Providers

```bash
# Test Ollama
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "extraction-model", "messages": [{"role": "user", "content": "Test"}]}'

# Test fallback
# Stop Ollama, request should failover to OpenAI automatically
```

### Update LiteLLM

```bash
source venv/bin/activate
pip install --upgrade litellm[proxy]
```

## Additional Resources

- **LiteLLM Documentation**: [docs.litellm.ai](https://docs.litellm.ai)
- **Supported Providers**: [docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers)
- **Configuration Reference**: [docs.litellm.ai/docs/proxy/configs](https://docs.litellm.ai/docs/proxy/configs)
- **Ollama Models**: [ollama.com/library](https://ollama.com/library)

## License

Part of the German Language Learning App project.
