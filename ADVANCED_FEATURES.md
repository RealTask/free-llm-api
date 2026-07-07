# Free LLM API - Advanced Features Documentation

This document describes the advanced features added to the free-llm-api repository.

## 🚀 Overview

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

#### Chat

- `POST /api/v1/chat/` - Send chat message
- `POST /api/v1/chat/stream` - Stream chat response

#### Providers

- `GET /api/v1/providers/` - List all providers
- `GET /api/v1/providers/{provider}` - Get provider info

#### Models

- `GET /api/v1/models/` - List all models
- `GET /api/v1/models/{provider}/{model}` - Get model info

#### Health

- `GET /api/v1/health/` - Get health summary
- `GET /api/v1/health/{provider}` - Get provider health

#### Benchmark

- `POST /api/v1/benchmark/` - Run benchmark

#### Stats

- `GET /api/v1/stats/` - Get API statistics

#### Embeddings

- `POST /api/v1/embed/` - Generate embeddings

#### Images

- `POST /api/v1/image/` - Generate image

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
- ✅ **Rate Limiting** - Multiple algorithms
- ✅ **Retry Logic** - Exponential backoff
- ✅ **Circuit Breaker** - Fault tolerance
- ✅ **Analytics** - Usage tracking

This makes it suitable for production use in applications requiring reliable, scalable access to free AI providers.
