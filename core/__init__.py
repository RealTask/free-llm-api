"""
Core Package

Advanced core functionality for the free LLM API providers.
Includes provider registry, streaming, caching, and orchestration.
"""

from .provider_registry import ProviderRegistry, ProviderDiscovery
from .streaming import StreamingResponse, AsyncStreamingManager
from .caching import ResponseCache, EmbeddingCache, ImageCache, CacheConfig
from .orchestration import (
    ProviderOrchestrator,
    LoadBalancer,
    FallbackManager,
    RoutingStrategyManager,
)
# Alias for backward compatibility
RoutingStrategy = RoutingStrategyManager
from .models import (
    ProviderMetadata,
    ModelMetadata,
    UsageStats,
    PerformanceMetrics,
    HealthStatus,
)

__all__ = [
    # Provider Registry
    "ProviderRegistry",
    "ProviderDiscovery",
    
    # Streaming
    "StreamingResponse",
    "AsyncStreamingManager",
    
    # Caching
    "ResponseCache",
    "EmbeddingCache", 
    "ImageCache",
    "CacheConfig",
    
    # Orchestration
    "ProviderOrchestrator",
    "LoadBalancer",
    "FallbackManager",
    "RoutingStrategy",
    "RoutingStrategyManager",
    
    # Models
    "ProviderMetadata",
    "ModelMetadata",
    "UsageStats",
    "PerformanceMetrics",
    "HealthStatus",
]
