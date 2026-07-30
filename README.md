# Free LLM API - Comprehensive Provider Collection

A curated collection of free LLM API providers with their capabilities, limitations, and best use cases based on 2026 research.

## 🎯 Overview

This repository provides a comprehensive catalog of free-tier and completely free AI model APIs across multiple categories:
- **Large Language Models (LLMs)**
- **Image Generation**
- **Embeddings**
- **Speech-to-Text/Text-to-Speech**
- **Multimodal models**

## 📊 Quick Recommendations by Use Case

| Use Case | Best Free API | Daily Limit | Notes |
|----------|---------------|-------------|-------|
| General LLM | Google AI Studio (Gemma 3) | 14,400 req | 30 req/min, Apache 2.0 models |
| Coding Agent | Groq (Llama 3.1 8B) | 14,400 req | 6,000 tokens/min |
| High Volume | Groq (Allam 2 7B) | 7,000 req | Best for bulk processing |
| Local Deployment | Stable Diffusion 3.5 | Unlimited | Hardware-limited only |
| Speech-to-Text | Groq (Whisper Large v3) | 2,000 req | Production-ready |
| Enterprise | Mistral La Plateforme | 1B tokens/mo | Requires phone verification |
| Multi-Model Access | OpenRouter | 50-1,000 req | 20+ free models |

## 🏆 Top Picks

- **🏆 Most Generous Free Tier**: Google AI Studio offers up to 14,400 requests/day for Gemma 3 models with 30 req/min
- **🎁 Best for Developers**: OpenRouter provides 20 req/min, 50 req/day baseline, extendable to 1,000 req/day with $10 lifetime credit
- **🚀 Highest Volume**: Groq offers 14,400 req/day for Llama 3.1 8B and 7,000 req/day for Allam 2 7B
- **💡 Open-Source Alternative**: Hugging Face Serverless Inference supports models <10GB with $0.10/month credits
- **🖼️ Free Image Generation**: Stable Diffusion 3.5 offers complete freedom for local deployment with no platform caps
- **🎤 Speech APIs**: Groq provides 2,000 req/day for Whisper Large v3 (STT)
- **🏢 Enterprise-Friendly**: Mistral La Plateforme offers 1M tokens/month free with phone verification

## 📁 Project Structure

```
free-llm-api/
├── free_llm_api/                    # Main package
│   ├── __init__.py                 # Exports all public APIs
│   └── api.py                      # Main FreeLLMAPI class
│
├── core/                           # Core functionality
│   ├── __init__.py
│   ├── models.py                   # Data models and types
│   ├── provider_registry.py        # Provider discovery and management
│   ├── streaming.py                # Async streaming support
│   ├── caching.py                  # Multi-level caching
│   └── orchestration.py            # Load balancing, fallback, routing
│
├── middleware/                     # Middleware components
│   ├── __init__.py
│   ├── rate_limiting.py            # Advanced rate limiting
│   └── retry.py                    # Retry logic
│
├── services/                       # Background services
│   ├── __init__.py
│   ├── health_monitor.py           # Health monitoring
│   └── benchmarking.py             # Benchmarking
│
├── cli/                            # Command-line interface
│   ├── __init__.py
│   ├── main.py                     # CLI main application
│   └── commands.py                 # CLI commands implementation
│
├── web/                            # FastAPI web server
│   ├── __init__.py
│   ├── app.py                      # FastAPI application
│   ├── routes.py                   # API route definitions
│   ├── static/                     # Static files (CSS, JS)
│   └── templates/                  # HTML templates
│
├── providers/                      # Provider implementations
│   ├── __init__.py
│   ├── base_provider.py            # Base provider class
│   ├── llm/                        # LLM providers
│   │   ├── __init__.py
│   │   ├── google_ai_studio.py     # Google AI Studio (Gemma)
│   │   ├── groq.py                 # Groq (Llama, Whisper)
│   │   ├── mistral.py              # Mistral La Plateforme
│   │   ├── openrouter.py           # OpenRouter (multi-model)
│   │   ├── cerebras.py             # Cerebras Cloud
│   │   ├── cohere.py               # Cohere Platform
│   │   ├── cloudflare.py           # Cloudflare Workers AI
│   │   ├── huggingface.py          # Hugging Face Inference
│   │   ├── nvidia.py               # NVIDIA NIM
│   │   ├── vercel.py               # Vercel AI SDK
│   │   └── github_models.py        # GitHub Models
│   ├── image/                      # Image generation providers
│   │   ├── __init__.py
│   │   ├── stable_diffusion.py     # Stable Diffusion 3.5
│   │   ├── flux.py                 # FLUX models
│   │   ├── google_gemini_image.py  # Gemini Image Generation
│   │   ├── adobe_firefly.py        # Adobe Firefly
│   │   ├── midjourney.py           # Midjourney (trial)
│   │   ├── gpt_image.py            # GPT Image (trial)
│   │   └── imagen.py               # Google Imagen
│   ├── speech/                     # Speech providers
│   │   ├── __init__.py
│   │   ├── groq_speech.py          # Groq Whisper STT
│   │   ├── google_tts.py           # Google TTS
│   │   └── whisper_local.py        # Local Whisper
│   └── embeddings/                 # Embedding providers
│       ├── __init__.py
│       ├── huggingface_embeddings.py
│       ├── cloudflare_embeddings.py
│       └── openrouter_embeddings.py
│
├── trial_credits/                  # Trial credit providers
│   ├── __init__.py
│   └── providers_with_credits.py
│
├── config/                         # Configuration
│   ├── __init__.py
│   ├── api_keys_template.py        # API keys template
│   └── settings.py                 # Settings management
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── helpers.py                  # Helper functions
│   ├── rate_limiter.py             # Rate limiting utilities
│   └── retry_logic.py              # Retry logic utilities
│
├── tests/                          # Tests
│   ├── __init__.py
│   └── test_providers.py           # Provider tests
│
├── examples/                       # Usage examples
│   ├── __init__.py
│   ├── basic_usage.py              # Basic usage examples
│   └── advanced_usage.py           # Advanced usage examples
│
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── LICENSE                         # MIT License
└── README.md                       # This file
```

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

1. Copy the template configuration:
```bash
cp config/api_keys_template.py config/api_keys.py
```

2. Edit `config/api_keys.py` with your API keys for various providers.

## 📖 Usage Examples

### Basic LLM Usage

```python
from providers.llm.groq import GroqProvider
from providers.llm.google_ai_studio import GoogleAIStudioProvider

# Initialize providers
groq = GroqProvider()
google = GoogleAIStudioProvider()

# Get responses
response = groq.chat("Llama 3.1 8B", "Hello, how are you?")
print(response)

response = google.chat("Gemma 3 27B Instruct", "Explain quantum computing")
print(response)
```

### Image Generation

```python
from providers.image.stable_diffusion import StableDiffusionProvider

sd = StableDiffusionProvider()
image = sd.generate("A beautiful sunset over mountains")
image.save("sunset.png")
```

### Speech-to-Text

```python
from providers.speech.groq_speech import GroqSpeechProvider

speech = GroqSpeechProvider()
transcription = speech.transcribe("audio.mp3")
print(transcription)
```

## 📊 Provider Details

See the individual provider files for detailed information about:
- Rate limits and quotas
- Available models
- Authentication requirements
- Best use cases
- Limitations and considerations

## ⚠️ Important Notes

- Free tiers may change without notice
- Some providers require phone number verification
- Data usage policies vary (some use data for training)
- Commercial usage rights differ by provider
- Rate limits are per-account, not per-API-key

## 🔍 Research Methodology

This collection is based on comprehensive research conducted in June 2026, consulting:
- Official provider documentation
- GitHub repositories
- API pricing pages
- Developer blogs and tutorials
- Tech news articles





## 📋 CLI Commands Reference

### Installation
```bash
pip install -e .
```

### Quick Start
```bash
# Interactive mode
free-llm --interactive
free-llm -i

# Simple chat
free-llm chat "What is AI?"
```

### Chat Commands
```bash
# Basic chat
free-llm chat "Your prompt here"

# With specific provider and model
free-llm chat "Tell me a story" --provider groq --model llama-3.1-8b-instant

# Stream responses
free-llm chat "Explain quantum computing" --stream

# With temperature
free-llm chat "Write a poem" --temperature 0.9

# With max tokens
free-llm chat "Summarize this article" --max-tokens 500
```

### Provider & Model Commands
```bash
# List all providers
free-llm list

# List all models
free-llm list models

# List models for a specific provider
free-llm list models groq
free-llm list models openrouter

# Get provider information
free-llm info groq

# Get model information
free-llm info groq llama-3.1-8b-instant
```

### Health & Status Commands
```bash
# Check all providers health
free-llm health

# Check specific provider health
free-llm health groq
free-llm health openrouter
```

### Benchmarking Commands
```bash
# Run benchmark on default provider
free-llm benchmark

# Benchmark specific provider
free-llm benchmark --provider groq

# Benchmark with specific type
free-llm benchmark --provider groq --type latency
free-llm benchmark --provider groq --type throughput
free-llm benchmark --provider groq --type comprehensive

# Benchmark specific model
free-llm benchmark --provider groq --model llama-3.1-8b-instant --type comprehensive
```

### Configuration Commands
```bash
# Show current configuration
free-llm config

# Set default provider
free-llm config set default_provider groq

# Set default model
free-llm config set default_model llama-3.1-8b-instant

# Enable/disable caching
free-llm config set enable_caching true
free-llm config set enable_caching false

# Enable/disable health monitoring
free-llm config set enable_health_monitoring true

# Set maximum retries
free-llm config set max_retries 3

# Set retry delay
free-llm config set retry_delay 2.0
```

### Statistics Commands
```bash
# Show API statistics
free-llm stats

# Show detailed statistics
free-llm stats --detailed
```

### Utility Commands
```bash
# Check version
free-llm --version
free-llm -v

# Show help
free-llm --help
free-llm -h
```

### Interactive Mode Commands
```
$ free-llm --interactive

Free LLM API - Interactive Mode
============================================================

Available commands:
  chat [prompt]           - Start a chat session
  list                   - List all providers and models
  list models            - List all available models
  list models [provider] - List models for a specific provider
  info [provider]        - Show provider information
  info [provider] [model] - Show model information
  health                 - Check provider health status
  health [provider]      - Check specific provider health
  benchmark              - Run performance benchmarks
  config                 - Show current configuration
  config set [key] [val] - Set configuration value
  stats                  - Show API usage statistics
  help                   - Show this help message
  exit                   - Exit interactive mode
  quit                   - Exit interactive mode

Examples:
  free-llm> chat "What is machine learning?"
  free-llm> chat "Write a story" --provider groq --stream
  free-llm> list
  free-llm> info groq
  free-llm> health
  free-llm> exit
```

## 🚀 Advanced Features

### Overview

The Free LLM API has been significantly enhanced with production-ready features including:

- **Advanced Provider Registry** - Dynamic loading and discovery of providers
- **Comprehensive Streaming** - Async streaming support for all providers
- **Multi-Level Caching** - Response, embedding, and image caching
- **Health Monitoring** - Automatic health checks and status tracking
- **Load Balancing** - Multiple strategies for request distribution
- **Auto-Fallback** - Automatic failover to backup providers
- **Benchmarking** - Performance testing and comparison
- **CLI Tool** - Command-line interface with interactive mode
- **FastAPI Web Server** - REST API for programmatic access
- **Advanced Rate Limiting** - Token bucket and sliding window algorithms

## 📁 New Package Structure

```
free-llm-api/
├── free_llm_api/                    # Main package
│   ├── __init__.py                 # Exports all public APIs
│   ├── api.py                      # Main FreeLLMAPI class
│   
├── core/                           # Core functionality
│   ├── __init__.py
│   ├── models.py                   # Data models and types
│   ├── provider_registry.py        # Provider discovery and management
│   ├── streaming.py                # Async streaming support
│   ├── caching.py                  # Multi-level caching
│   └── orchestration.py            # Load balancing, fallback, routing
│   
├── middleware/                     # Middleware components
│   ├── __init__.py
│   ├── rate_limiting.py            # Advanced rate limiting
│   ├── retry.py                    # Retry logic
│   ├── authentication.py           # API key management
│   ├── request_processing.py       # Request/response processing
│   └── circuit_breaker.py          # Circuit breaker pattern
│   
├── services/                       # Background services
│   ├── __init__.py
│   ├── health_monitor.py           # Health monitoring
│   ├── benchmarking.py             # Benchmarking
│   ├── analytics.py               # Usage analytics
│   └── background_tasks.py        # Task scheduling
│   
├── cli/                            # Command-line interface
│   ├── __init__.py
│   ├── main.py                     # CLI main application
│   └── commands.py                 # CLI commands
│   
├── web/                            # FastAPI web server
│   ├── __init__.py
│   ├── app.py                      # FastAPI application
│   └── routes.py                   # API route definitions
│   
└── providers/                      # Existing provider implementations
```

## 🎯 Main API Class

The `FreeLLMAPI` class provides a unified interface to all features:

### Basic Usage

```python
from free_llm_api import FreeLLMAPI

# Initialize
api = FreeLLMAPI()

# Simple chat with automatic provider selection
response = await api.chat("What is machine learning?")
print(response.content)

# With specific provider
response = await api.chat(
    "What is AI?",
    provider="groq",
    model="llama-3.1-8b-instant"
)

# Streaming
async for chunk in api.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)

# Embeddings
embedding = await api.embed("Hello world")

# Image generation
image = await api.generate_image("A beautiful sunset")
```

### Configuration

```python
from free_llm_api import FreeLLMAPI, FreeLLMAPIConfig

config = FreeLLMAPIConfig(
    default_provider="groq",
    default_model="llama-3.1-8b-instant",
    enable_caching=True,
    enable_health_monitoring=True,
    max_retries=3,
)

api = FreeLLMAPI(config)
await api.initialize()
```

## 🔄 Provider Orchestration

### Load Balancing

```python
from free_llm_api import LoadBalancer, LoadBalancingStrategy

# Create load balancer
balancer = LoadBalancer(strategy=LoadBalancingStrategy.ROUND_ROBIN)

# Available strategies:
# - ROUND_ROBIN: Distribute requests evenly
# - RANDOM: Random provider selection
# - LEAST_CONNECTIONS: Fewest active connections
# - LEAST_LATENCY: Fastest response times
# - WEIGHTED: Weighted distribution
# - PRIORITY: Priority-based selection

# Select provider
provider = await balancer.select_provider()
```

### Fallback Management

```python
from free_llm_api import FallbackManager

# Create fallback manager
fallback = FallbackManager(max_retries=3, exponential_backoff=True)

# Set fallback chain
fallback.set_fallback_chain(
    primary="groq",
    fallbacks=["openrouter", "mistral", "huggingface"]
)

# Execute with automatic fallback
result = await fallback.execute_with_fallback(
    provider_name="groq",
    method="chat",
    args=("llama-3.1-8b-instant", "What is AI?"),
    kwargs={}
)
```

### Routing Strategies

```python
from free_llm_api import RoutingStrategy, RoutingStrategy as RS

# Create routing strategy
router = RoutingStrategy(strategy=RS.COST_OPTIMIZED)

# Available strategies:
# - RANDOM: Random routing
# - COST_OPTIMIZED: Prefer cheaper/free providers
# - PERFORMANCE_OPTIMIZED: Prefer faster providers
# - CAPABILITY_BASED: Match required capabilities
# - GEOGRAPHIC: Geographic-based routing

# Route request
provider = await router.route_request(context, providers)
```

## 📡 Streaming Support

### Basic Streaming

```python
from free_llm_api import AsyncStreamingManager

manager = AsyncStreamingManager()

async for chunk in manager.stream(
    provider=groq_provider,
    model="llama-3.1-8b-instant",
    messages="Tell me a story"
):
    print(chunk.content, end="", flush=True)
```

### With Callbacks

```python
from free_llm_api import StreamingResponse

def on_chunk(chunk):
    print(f"Received chunk {chunk.chunk_id}: {chunk.content[:50]}...")

def on_complete(response: StreamingResponse):
    print(f"Streaming complete! Total chunks: {len(response.chunks)}")

def on_error(error):
    print(f"Error: {error}")

response = await manager.stream_with_callbacks(
    provider=groq_provider,
    model="llama-3.1-8b-instant",
    messages="Tell me a story",
    on_chunk=on_chunk,
    on_complete=on_complete,
    on_error=on_error
)
```

### Stream Aggregation

```python
from free_llm_api import StreamAggregator

aggregator = StreamAggregator()

# Aggregate multiple streams
streams = {
    "provider1": stream1,
    "provider2": stream2,
}

async for result in aggregator.aggregate_streams(streams, strategy="round_robin"):
    for name, chunk in result.items():
        print(f"{name}: {chunk.content}")
```

## 💾 Caching

### Response Caching

```python
from free_llm_api import ResponseCache, CacheConfig

# Configure cache
config = CacheConfig(
    enabled=True,
    cache_type="memory",  # memory, disk, redis
    response_ttl=3600.0,  # 1 hour
    max_response_size=100000,  # 100KB
)

cache = ResponseCache(config)

# Cache a response
await cache.set(
    provider="groq",
    model="llama-3.1-8b-instant",
    messages="What is AI?",
    response="AI stands for Artificial Intelligence..."
)

# Get cached response
cached = await cache.get(
    provider="groq",
    model="llama-3.1-8b-instant",
    messages="What is AI?"
)
```

### Embedding Caching

```python
from free_llm_api import EmbeddingCache

embedding_cache = EmbeddingCache(config)

# Cache embedding
await embedding_cache.set(
    provider="openrouter",
    model="text-embedding-ada-002",
    text="Hello world",
    embedding=[0.1, 0.2, 0.3, ...]
)

# Get cached embedding
embedding = await embedding_cache.get(
    provider="openrouter",
    model="text-embedding-ada-002",
    text="Hello world"
)
```

### Image Caching

```python
from free_llm_api import ImageCache

image_cache = ImageCache(config)

# Cache image
await image_cache.set(
    provider="stable_diffusion",
    model="stable-diffusion-3.5",
    prompt="A beautiful sunset",
    image_data=image_bytes
)

# Get cached image
image = await image_cache.get(
    provider="stable_diffusion",
    model="stable-diffusion-3.5",
    prompt="A beautiful sunset"
)
```

## 🏥 Health Monitoring

### Basic Usage

```python
from free_llm_api import HealthMonitor, HealthCheckConfig

# Configure health checks
config = HealthCheckConfig(
    check_interval=60.0,  # Check every 60 seconds
    timeout=30.0,
    max_retries=3,
    check_connectivity=True,
    check_latency=True,
    check_rate_limits=True,
)

monitor = HealthMonitor(config=config)
await monitor.initialize()
await monitor.start()

# Get health status
status = monitor.get_health_status("groq")
print(f"Status: {status.status}")
print(f"Response Time: {status.response_time}s")

# Get summary
summary = monitor.get_health_summary()
print(f"Available: {summary['available']}")
print(f"Degraded: {summary['degraded']}")
print(f"Unavailable: {summary['unavailable']}")

# Force check
await monitor.force_check("groq")

# Stop monitoring
await monitor.stop()
```

### Health Check Types

- `CONNECTIVITY` - Check if provider is reachable
- `LATENCY` - Measure response time
- `RATE_LIMIT` - Check rate limit status
- `AUTHENTICATION` - Verify authentication
- `MODEL_AVAILABILITY` - Check available models
- `FULL` - Run all checks

## 📊 Benchmarking

### Basic Benchmark

```python
from free_llm_api import BenchmarkRunner, BenchmarkConfig

# Configure benchmark
config = BenchmarkConfig(
    num_requests=10,
    warmup_requests=3,
    max_tokens=100,
    temperature=0.7,
    output_dir="benchmarks",
    output_format="json",
)

runner = BenchmarkRunner(config=config)
await runner.initialize()

# Run benchmark
results = await runner.run_benchmark(
    provider="groq",
    model="llama-3.1-8b-instant",
    benchmark_type="comprehensive"
)

# Display results
for key, result in results.items():
    print(f"{key}:")
    print(f"  Avg Latency: {result.avg_latency_ms:.2f}ms")
    print(f"  Requests/sec: {result.requests_per_second:.2f}")
    print(f"  Success Rate: {result.success_rate * 100:.1f}%")
```

### Benchmark Types

- `LATENCY` - Measure response latency
- `THROUGHPUT` - Measure requests per second
- `QUALITY` - Evaluate response quality (requires human evaluation)
- `COST` - Calculate cost metrics
- `COMPREHENSIVE` - Run all benchmarks

### Compare Providers

```python
# Compare multiple providers
results = await runner.compare_providers(
    providers=["groq", "openrouter", "mistral"],
    benchmark_type="latency"
)

# Display comparison
for provider, result in results.items():
    print(f"{provider}: {result.avg_latency_ms:.2f}ms avg latency")
```

## ⚡ Rate Limiting

### Advanced Rate Limiter

```python
from free_llm_api import AdvancedRateLimiter, RateLimitConfig

# Configure rate limits
config = RateLimitConfig(
    requests_per_minute=100,
    requests_per_hour=1000,
    tokens_per_minute=10000,
    burst_limit=50,
    concurrent_requests=10,
    wait_on_limit=True,
    max_wait_time=60.0,
)

limiter = AdvancedRateLimiter(config, name="global")

# Check if request is allowed
if limiter.check(tokens=10):
    # Make request
    pass

# Acquire permission
if limiter.acquire(tokens=10, wait=True):
    try:
        # Make request
        pass
    finally:
        limiter.release(tokens=10)

# Context manager
with limiter:
    # Request is allowed
    pass

# Async context manager
async with limiter:
    # Request is allowed
    pass
```

### Rate Limiter Types

- `AdvancedRateLimiter` - Combines multiple strategies
- `TokenBucketRateLimiter` - Token bucket algorithm
- `SlidingWindowRateLimiter` - Sliding window algorithm

## 🎨 CLI Tool

### Installation

```bash
pip install -e .
```

### Usage

```bash
# Interactive mode
free-llm --interactive
free-llm -i

# Chat
free-llm chat "What is AI?"
free-llm chat "Tell me a story" --provider groq --model llama-3.1-8b-instant
free-llm chat "Explain quantum computing" --stream

# List providers and models
free-llm list
free-llm list models
free-llm list models groq

# Get information
free-llm info groq
free-llm info groq llama-3.1-8b-instant

# Health checks
free-llm health
free-llm health groq

# Benchmarking
free-llm benchmark
free-llm benchmark --provider groq --type latency
free-llm benchmark --provider groq --model llama-3.1-8b-instant --type comprehensive

# Configuration
free-llm config
free-llm config set default_provider groq
free-llm config set enable_caching false

# Statistics
free-llm stats
```

### Interactive Mode

```
$ free-llm --interactive

Free LLM API - Interactive Mode
============================================================

Type 'help' for available commands, 'exit' to quit

free-llm> chat "What is AI?"

==================================================
Response from groq/llama-3.1-8b-instant
Latency: 123.45ms
==================================================

AI stands for Artificial Intelligence, which is the field...

==================================================

free-llm> list

==================================================
Available Providers
==================================================

groq                 [available   ] - 12 models
openrouter           [available   ] - 20 models
mistral              [available   ] - 5 models
...

Total: 15 providers
==================================================

free-llm> exit
Goodbye!
```

## 🌐 FastAPI Web Server

### Installation

```bash
pip install -e ".[all]"
```

### Running the Server

```bash
# Using uvicorn directly
uvicorn free_llm_api.web.app:app --reload

# Using the entry point
free-llm-server
```

### API Endpoints

#### Web UI Routes (HTML Pages)

- `GET /` - Home page
- `GET /dashboard` - Dashboard with statistics
- `GET /chat` - Chat interface
- `GET /providers` - Providers list and management
- `GET /models` - Models browser
- `GET /health` - Health status page
- `GET /benchmarks` - Benchmarking tools
- `GET /settings` - Configuration settings

#### Chat API

- `POST /api/v1/chat/` - Send chat message
  - Body: `{messages, model?, provider?, temperature?, max_tokens?, use_cache?, stream?}`
- `POST /api/v1/chat/stream` - Stream chat response (Server-Sent Events)
  - Body: `{messages, model?, provider?, temperature?, max_tokens?}`

#### Providers API

- `GET /api/v1/providers/` - List all providers
  - Query: `category?`, `status?`
- `GET /api/v1/providers/{provider}` - Get detailed provider information

#### Models API

- `GET /api/v1/models/` - List all models
  - Query: `provider?`, `category?`, `capability?`
- `GET /api/v1/models/{provider}/{model}` - Get detailed model information

#### Health API

- `GET /api/v1/health/` - Get health summary for all providers
- `GET /api/v1/health/{provider}` - Get health status for specific provider

#### Benchmark API

- `POST /api/v1/benchmark/` - Run benchmark
  - Query: `provider?`, `model?`, `type?` (latency|throughput|quality|cost|comprehensive)

#### Statistics API

- `GET /api/v1/stats/` - Get API statistics (cache, rate limiting, provider stats)

#### Embeddings API

- `POST /api/v1/embed/` - Generate embeddings
  - Body: `{text, model?, provider?, use_cache?}`

#### Image Generation API

- `POST /api/v1/image/` - Generate image from prompt
  - Body: `{prompt, model?, provider?, use_cache?}`

### Example Requests

```bash
# Chat
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"messages": "What is AI?", "provider": "groq"}'

# List providers
curl http://localhost:8000/api/v1/providers/

# Health check
curl http://localhost:8000/api/v1/health/

# Streaming chat
curl -N http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": "Tell me a story", "stream": true}'
```

## 🔧 Middleware Components

### Authentication

```python
from free_llm_api import APIKeyManager, APIKeyValidator

# Manage API keys
manager = APIKeyManager()
manager.add_key("user1", "sk-1234567890")
manager.remove_key("user1")

# Validate keys
validator = APIKeyValidator(manager)
is_valid = validator.validate("sk-1234567890")
```

### Circuit Breaker

```python
from free_llm_api import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    half_open_requests=3,
)

breaker = CircuitBreaker(config)

# Check if circuit is closed (allowing requests)
if breaker.allow_request():
    try:
        # Make request
        result = await make_request()
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
```

### Retry Logic

```python
from free_llm_api import AdvancedRetry, RetryConfig

config = RetryConfig(
    max_retries=3,
    delay=1.0,
    exponential_backoff=True,
    max_delay=10.0,
    retry_on=[Exception, ConnectionError, TimeoutError],
)

retry = AdvancedRetry(config)

# Retry a function
result = await retry.execute(async_function, args, kwargs)
```

## 📈 Analytics

```python
from free_llm_api import AnalyticsService

analytics = AnalyticsService()

# Record usage
analytics.record_request(
    provider="groq",
    model="llama-3.1-8b-instant",
    latency=123.45,
    tokens=50,
    success=True,
)

# Get usage statistics
usage = analytics.get_usage_stats()
print(f"Total requests: {usage.total_requests}")
print(f"Success rate: {usage.success_rate * 100:.1f}%")

# Get performance metrics
performance = analytics.get_performance_metrics()
print(f"Avg latency: {performance.avg_latency:.2f}ms")
```

## 🎯 Best Practices

### 1. Always Initialize

```python
api = FreeLLMAPI()
await api.initialize()  # Don't forget this!
```

### 2. Use Context Managers

```python
async with FreeLLMAPI() as api:
    response = await api.chat("Hello")
```

### 3. Handle Errors

```python
try:
    response = await api.chat("Hello")
    if not response.success:
        print(f"Error: {response.error}")
except Exception as e:
    print(f"Exception: {e}")
```

### 4. Use Caching Wisely

```python
# Cache responses that don't change often
response = await api.chat("What is AI?", use_cache=True)

# Don't cache unique requests
response = await api.chat("Current time?", use_cache=False)
```

### 5. Monitor Health

```python
# Check health before making requests
health = api.get_health_status("groq")
if health.get("status") == "available":
    response = await api.chat("Hello", provider="groq")
```

### 6. Use Streaming for Long Responses

```python
# For long responses, use streaming
async for chunk in api.stream("Write a long story"):
    print(chunk.content, end="")
```

## 🔍 Troubleshooting

### Common Issues

1. **Provider not found**
   - Make sure the provider name is correct
   - Check if the provider is available: `api.list_providers()`

2. **Authentication failed**
   - Set the API key in environment variables
   - Example: `export GROQ_API_KEY=your_key`

3. **Rate limit exceeded**
   - Check rate limits: `api.get_provider_info("groq")`
   - Use caching to reduce requests
   - Implement retry logic with backoff

4. **Connection errors**
   - Check your internet connection
   - Verify the provider's API is available
   - Check health status: `api.get_health_status("groq")`

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

api = FreeLLMAPI()
await api.initialize()
```

## 📚 API Reference

### FreeLLMAPI Class

#### Methods

- `chat(messages, model=None, provider=None, **kwargs)` - Send chat message
- `stream(messages, model=None, provider=None, **kwargs)` - Stream chat response
- `embed(text, model=None, provider=None, **kwargs)` - Generate embeddings
- `generate_image(prompt, model=None, provider=None, **kwargs)` - Generate image
- `list_providers(category=None, status=None)` - List providers
- `list_models(provider=None, category=None, capability=None)` - List models
- `get_provider_info(provider)` - Get provider information
- `get_model_info(provider, model)` - Get model information
- `get_health_status(provider=None)` - Get health status
- `run_benchmark(provider=None, model=None, benchmark_type="comprehensive")` - Run benchmark
- `get_stats()` - Get API statistics
- `search_providers(query, limit=10)` - Search providers
- `get_best_provider(task="general", min_context=None, streaming=False)` - Get best provider

#### Configuration

- `default_provider` - Default provider to use
- `default_model` - Default model to use
- `enable_caching` - Enable/disable caching
- `enable_health_monitoring` - Enable/disable health monitoring
- `enable_benchmarking` - Enable/disable benchmarking
- `max_retries` - Maximum number of retries
- `retry_delay` - Delay between retries
- `log_level` - Logging level

## 🎓 Examples

### Example 1: Simple Chat Application

```python
import asyncio
from free_llm_api import FreeLLMAPI

async def main():
    api = FreeLLMAPI()
    await api.initialize()
    
    while True:
        prompt = input("You: ")
        if prompt.lower() in ("exit", "quit"):
            break
        
        response = await api.chat(prompt)
        print(f"AI: {response.content}")

asyncio.run(main())
```

### Example 2: Multi-Provider Chat with Fallback

```python
import asyncio
from free_llm_api import FreeLLMAPI

async def chat_with_fallback(prompt):
    api = FreeLLMAPI()
    await api.initialize()
    
    # Try multiple providers
    providers = ["groq", "openrouter", "mistral"]
    
    for provider in providers:
        try:
            response = await api.chat(prompt, provider=provider)
            if response.success:
                return response
        except Exception as e:
            print(f"{provider} failed: {e}")
    
    raise Exception("All providers failed")

async def main():
    response = await chat_with_fallback("What is AI?")
    print(response.content)

asyncio.run(main())
```

### Example 3: Streaming with Progress

```python
import asyncio
from free_llm_api import FreeLLMAPI

async def stream_with_progress(prompt):
    api = FreeLLMAPI()
    await api.initialize()
    
    print("Generating response...")
    full_response = ""
    
    async for chunk in api.stream(prompt):
        full_response += chunk.content
        print(chunk.content, end="", flush=True)
    
    print(f"\n\nFull response ({len(full_response)} chars):")
    print(full_response)

asyncio.run(stream_with_progress("Write a detailed essay about AI"))
```

### Example 4: Batch Processing

```python
import asyncio
from free_llm_api import FreeLLMAPI

async def process_batch(prompts):
    api = FreeLLMAPI()
    await api.initialize()
    
    # Process prompts concurrently
    tasks = [api.chat(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    
    for prompt, result in zip(prompts, results):
        print(f"Prompt: {prompt[:50]}...")
        print(f"Response: {result.content[:100]}...")
        print(f"Provider: {result.provider}, Latency: {result.latency_ms:.2f}ms")
        print()

async def main():
    prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "What are the types of AI?",
        "How does deep learning work?",
    ]
    
    await process_batch(prompts)

asyncio.run(main())
```

### Example 5: Using the CLI

```bash
# Install
pip install -e .

# Chat
free-llm chat "What is AI?"

# List providers
free-llm list

# Get provider info
free-llm info groq

# Run benchmark
free-llm benchmark --provider groq --type latency

# Interactive mode
free-llm --interactive
```

### Example 6: FastAPI Server

```python
from fastapi import FastAPI
from free_llm_api import FreeLLMAPI

app = FastAPI()
api = FreeLLMAPI()

@app.on_event("startup")
async def startup():
    await api.initialize()

@app.post("/chat")
async def chat(prompt: str, provider: str = None):
    result = await api.chat(prompt, provider=provider)
    return {
        "content": result.content,
        "provider": result.provider,
        "model": result.model,
        "latency_ms": result.latency_ms,
    }

# Run with: uvicorn main:app --reload
```

## 📊 Performance Tips

1. **Use Caching** - Cache frequent requests to reduce API calls
2. **Batch Requests** - Process multiple requests concurrently
3. **Use Streaming** - For long responses, stream to reduce latency
4. **Monitor Health** - Check provider health before making requests
5. **Load Balance** - Distribute requests across multiple providers
6. **Implement Fallback** - Automatically failover to backup providers
7. **Rate Limit** - Respect provider rate limits to avoid bans
8. **Retry with Backoff** - Implement exponential backoff for retries

## 🔒 Security Considerations

1. **API Keys** - Never commit API keys to version control
2. **Environment Variables** - Store keys in environment variables
3. **Rate Limiting** - Implement rate limiting to prevent abuse
4. **Authentication** - Use API key validation for your endpoints
5. **HTTPS** - Always use HTTPS for web endpoints
6. **Input Validation** - Validate all user inputs
7. **Error Handling** - Don't expose sensitive information in errors
8. **Logging** - Be careful what you log (no sensitive data)

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e ".[all]"

CMD ["free-llm-server"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: free-llm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: free-llm-api
  template:
    metadata:
      labels:
        app: free-llm-api
    spec:
      containers:
      - name: free-llm-api
        image: your-image:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: groq
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openrouter
---
apiVersion: v1
kind: Service
metadata:
  name: free-llm-api
spec:
  selector:
    app: free-llm-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 🎉 Conclusion

The Free LLM API now provides a comprehensive, production-ready solution for accessing free LLM providers with advanced features including:

- ✅ **30+ Provider Integrations** - LLM, Image, Speech, Embeddings
- ✅ **Advanced Orchestration** - Load balancing, fallback, routing
- ✅ **Comprehensive Streaming** - Real-time responses
- ✅ **Multi-Level Caching** - Memory, disk, Redis support
- ✅ **Health Monitoring** - Automatic health checks
- ✅ **Benchmarking** - Performance testing
- ✅ **CLI Tool** - Interactive and non-interactive modes
- ✅ **FastAPI Web Server** - REST API with streaming
- ✅ **Premium Web UI & Dashboard** - Modern, minimalistic design with real-time analytics
- ✅ **Rate Limiting** - Multiple algorithms
- ✅ **Retry Logic** - Exponential backoff
- ✅ **Circuit Breaker** - Fault tolerance
- ✅ **Analytics** - Usage tracking

This makes it suitable for production use in applications requiring reliable, scalable access to free AI providers.

---

## 🌐 Premium Web UI & Dashboard

### Overview

The Free LLM API includes a premium, polished, professional web interface with a minimalistic design theme. The dashboard provides real-time monitoring, chat interface, provider management, and comprehensive analytics.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Landing page with feature overview |
| Dashboard | `/dashboard` | Real-time analytics and system overview |
| Chat | `/chat` | Interactive chat interface with streaming |
| Providers | `/providers` | Browse and manage API providers |
| Models | `/models` | Explore available models by category |
| Health | `/health` | Monitor provider health status |
| Benchmarks | `/benchmarks` | Performance comparison and metrics |
| Settings | `/settings` | Configure API keys and preferences |

### Running the Web Server

```bash
# Install dependencies
pip install -e ".[all]"

# Start the server
uvicorn free_llm_api.web.app:app --reload --host 0.0.0.0 --port 8000

# Or use the CLI entry point
free-llm-server
```

### Access the Dashboard

Once the server is running, open your browser and navigate to:

- **Home**: http://localhost:8000/
- **Dashboard**: http://localhost:8000/dashboard
- **Chat**: http://localhost:8000/chat
- **Providers**: http://localhost:8000/providers
- **Models**: http://localhost:8000/models
- **Health**: http://localhost:8000/health
- **Benchmarks**: http://localhost:8000/benchmarks
- **Settings**: http://localhost:8000/settings

### Design Features

- **Minimalistic Theme**: Clean, modern interface with focus on usability
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Live data refresh for health, stats, and benchmarks
- **Dark/Light Mode**: Automatic theme detection with manual toggle
- **Smooth Animations**: Polished transitions and micro-interactions
- **Professional Typography**: Optimized font stack for readability
- **Color Palette**: Carefully chosen colors for visual hierarchy
- **Card-based Layout**: Organized information in digestible chunks

### Dashboard Features

- **System Overview**: Quick stats on providers, models, and requests
- **Health Status Grid**: Visual indicators for all provider statuses
- **Performance Charts**: Latency, throughput, and success rate graphs
- **Recent Activity**: Log of recent API calls and their outcomes
- **Quick Actions**: Fast access to common operations

### Chat Interface

- **Streaming Responses**: Real-time token-by-token display
- **Provider Selection**: Choose from available providers and models
- **Conversation History**: Maintain context across multiple messages
- **Markdown Support**: Render formatted responses with code blocks
- **Copy/Paste**: Easy export of responses
- **Settings Panel**: Adjust temperature, max tokens, and more

### Provider Management

- **Status Indicators**: Green/yellow/red health status
- **Rate Limit Info**: Display current limits and usage
- **Model Browser**: Filter by category and capabilities
- **Detailed Info**: Click through for comprehensive provider details

### Benchmarking Tools

- **Latency Tests**: Measure response times across providers
- **Throughput Analysis**: Compare requests per second
- **Quality Metrics**: Evaluate response quality scores
- **Cost Comparison**: Analyze free tier value
- **Export Results**: Download benchmark data as CSV/JSON

---

## 📋 Complete Command Reference

### CLI Commands

```bash
# Installation
pip install -e .

# Interactive mode
free-llm --interactive
free-llm -i

# Chat commands
free-llm chat "Your prompt here"
free-llm chat "Tell me a story" --provider groq --model llama-3.1-8b-instant
free-llm chat "Explain quantum computing" --stream
free-llm chat "Write a poem" --temperature 0.9
free-llm chat "Summarize this article" --max-tokens 500

# List commands
free-llm list                      # List all providers
free-llm list models               # List all models
free-llm list models groq          # List models for specific provider

# Info commands
free-llm info groq                 # Provider information
free-llm info groq llama-3.1-8b-instant  # Model information

# Health commands
free-llm health                    # Check all providers
free-llm health groq               # Check specific provider

# Benchmark commands
free-llm benchmark                                    # Default benchmark
free-llm benchmark --provider groq                    # Specific provider
free-llm benchmark --provider groq --type latency     # Latency test
free-llm benchmark --provider groq --type throughput  # Throughput test
free-llm benchmark --provider groq --type comprehensive  # Full suite

# Configuration commands
free-llm config                              # Show configuration
free-llm config set default_provider groq    # Set default provider
free-llm config set default_model llama-3.1-8b-instant  # Set default model
free-llm config set enable_caching true      # Enable caching
free-llm config set enable_health_monitoring true  # Enable health checks
free-llm config set max_retries 3            # Set retry count
free-llm config set retry_delay 2.0          # Set retry delay

# Statistics commands
free-llm stats                  # Show API statistics
free-llm stats --detailed       # Detailed statistics

# Utility commands
free-llm --version              # Check version
free-llm --help                 # Show help
```

### Web Server Commands

```bash
# Install with all dependencies
pip install -e ".[all]"

# Start development server
uvicorn free_llm_api.web.app:app --reload

# Start production server
uvicorn free_llm_api.web.app:app --host 0.0.0.0 --port 8000 --workers 4

# Using CLI entry point
free-llm-server

# With custom host/port
free-llm-server --host 0.0.0.0 --port 8080
```

### API Endpoints

```bash
# Chat endpoints
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"messages": "What is AI?", "provider": "groq"}'

curl -N http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": "Tell me a story", "stream": true}'

# Provider endpoints
curl http://localhost:8000/api/v1/providers/
curl http://localhost:8000/api/v1/providers/groq

# Model endpoints
curl http://localhost:8000/api/v1/models/
curl http://localhost:8000/api/v1/models/groq/llama-3.1-8b-instant

# Health endpoints
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/groq

# Benchmark endpoint
curl -X POST "http://localhost:8000/api/v1/benchmark/?provider=groq&type=latency"

# Stats endpoint
curl http://localhost:8000/api/v1/stats/

# Embedding endpoint
curl -X POST http://localhost:8000/api/v1/embed/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "provider": "openrouter"}'

# Image generation endpoint
curl -X POST http://localhost:8000/api/v1/image/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset", "provider": "stable_diffusion"}'
```

### Docker Commands

```bash
# Build Docker image
docker build -t free-llm-api .

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e OPENROUTER_API_KEY=your_key \
  free-llm-api

# Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Kubernetes Commands

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services

# Scale deployment
kubectl scale deployment free-llm-api --replicas=5

# View logs
kubectl logs -f deployment/free-llm-api
```

## 📝 Contributing

Contributions are welcome! Please ensure:
1. All new providers are tested
2. Rate limits and quotas are verified
3. Documentation is updated
4. Follow the existing code structure

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- All the API providers for offering free tiers
- The open-source community for their contributions
- Researchers and developers who shared their findings

---

**Last Updated**: July 30, 2026
**Maintainer**: [RealTask](https://github.com/RealTask)
**Research Source**: Free AI Model APIs in 2026: Comprehensive Research Report
