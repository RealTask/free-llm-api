"""
Free LLM API - Advanced Edition

A comprehensive, production-ready library for accessing free LLM API providers.

This package provides:
- Unified interface to 30+ free AI providers
- Advanced orchestration with load balancing and fallback
- Comprehensive streaming support
- Multi-level caching
- Health monitoring and benchmarking
- CLI and web server interfaces
- Rate limiting and retry logic

Example usage:
    from free_llm_api import FreeLLMAPI
    
    # Initialize
    api = FreeLLMAPI()
    
    # Chat with automatic provider selection
    response = await api.chat("What is machine learning?")
    
    # Use specific provider
    response = await api.chat("What is AI?", provider="groq", model="llama-3.1-8b-instant")
    
    # Streaming
    async for chunk in api.stream("Tell me a story"):
        print(chunk, end="", flush=True)
"""

from core import (
    ProviderRegistry,
    ProviderDiscovery,
    StreamingResponse,
    AsyncStreamingManager,
    ResponseCache,
    EmbeddingCache,
    ImageCache,
    CacheConfig,
    ProviderOrchestrator,
    LoadBalancer,
    FallbackManager,
    RoutingStrategyManager as RoutingStrategy,
)
from middleware import (
    AdvancedRateLimiter,
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
    RateLimitConfig,
    AdvancedRetry,
    RetryConfig,
    APIKeyManager,
    APIKeyValidator,
    TokenManager,
    RequestProcessor,
    ResponseProcessor,
    ErrorHandler,
    CircuitBreaker,
)
from services import (
    HealthMonitor,
    HealthCheckResult,
    HealthCheckConfig,
    BenchmarkRunner,
    BenchmarkConfig,
    BenchmarkResult,
    AnalyticsService,
    UsageAnalytics,
    PerformanceAnalytics,
    BackgroundTaskManager,
    ScheduledTask,
)

# Main API class
from .api import FreeLLMAPI

__all__ = [
    # Core
    "ProviderRegistry",
    "ProviderDiscovery",
    "StreamingResponse",
    "AsyncStreamingManager",
    "ResponseCache",
    "EmbeddingCache",
    "ImageCache",
    "CacheConfig",
    "ProviderOrchestrator",
    "LoadBalancer",
    "FallbackManager",
    "RoutingStrategy",
    
    # Middleware
    "AdvancedRateLimiter",
    "TokenBucketRateLimiter",
    "SlidingWindowRateLimiter",
    "RateLimitConfig",
    "AdvancedRetry",
    "RetryConfig",
    "APIKeyManager",
    "APIKeyValidator",
    "TokenManager",
    "RequestProcessor",
    "ResponseProcessor",
    "ErrorHandler",
    "CircuitBreaker",
    
    # Services
    "HealthMonitor",
    "HealthCheckResult",
    "HealthCheckConfig",
    "BenchmarkRunner",
    "BenchmarkConfig",
    "BenchmarkResult",
    "AnalyticsService",
    "UsageAnalytics",
    "PerformanceAnalytics",
    "BackgroundTaskManager",
    "ScheduledTask",
    
    # Main API
    "FreeLLMAPI",
]

# Version
__version__ = "2.0.0"
__author__ = "realtast"
__description__ = "Advanced Free LLM API - Production-ready AI provider library"
