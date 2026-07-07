"""
Main API Class

The main FreeLLMAPI class that provides a unified interface to all providers.
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from dataclasses import dataclass, field

from core.models import (
    RequestContext,
    ResponseResult,
    ProviderStatus,
    ProviderCategory,
)
from core.provider_registry import ProviderRegistry, get_registry
from core.orchestration import ProviderOrchestrator
from core.streaming import AsyncStreamingManager, StreamChunk, StreamingResponse
from core.caching import CacheManager, CacheConfig
from services.health_monitor import HealthMonitor, get_health_monitor
from services.benchmarking import BenchmarkRunner, get_benchmark_runner
from middleware.rate_limiting import AdvancedRateLimiter, RateLimitConfig

logger = logging.getLogger(__name__)


@dataclass
class FreeLLMAPIConfig:
    """Configuration for FreeLLMAPI."""
    # Provider selection
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    
    # Caching
    enable_caching: bool = True
    cache_config: Optional[CacheConfig] = None
    
    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_config: Optional[RateLimitConfig] = None
    
    # Health monitoring
    enable_health_monitoring: bool = True
    health_check_interval: float = 60.0
    
    # Benchmarking
    enable_benchmarking: bool = False
    benchmark_on_startup: bool = False
    
    # Streaming
    default_streaming: bool = False
    
    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Logging
    log_level: str = "INFO"
    log_requests: bool = True


class FreeLLMAPI:
    """
    Main API class for accessing free LLM providers.
    
    Provides a unified interface to all supported providers with:
    - Automatic provider selection
    - Load balancing and fallback
    - Streaming support
    - Caching
    - Health monitoring
    - Rate limiting
    
    Example:
        api = FreeLLMAPI()
        
        # Simple chat
        response = await api.chat("What is AI?")
        
        # With specific provider
        response = await api.chat("What is AI?", provider="groq")
        
        # Streaming
        async for chunk in api.stream("Tell me a story"):
            print(chunk, end="", flush=True)
        
        # Embeddings
        embedding = await api.embed("Hello world")
        
        # List providers
        providers = api.list_providers()
    """
    
    def __init__(self, config: Optional[FreeLLMAPIConfig] = None):
        """
        Initialize FreeLLMAPI.
        
        Args:
            config: Optional configuration
        """
        self.config = config or FreeLLMAPIConfig()
        
        # Initialize components
        self.registry = get_registry()
        self.orchestrator = ProviderOrchestrator(registry=self.registry)
        self.streaming_manager = AsyncStreamingManager()
        self.cache_manager = CacheManager(
            self.config.cache_config or CacheConfig(enabled=self.config.enable_caching)
        )
        self.health_monitor = get_health_monitor()
        self.benchmark_runner = get_benchmark_runner()
        
        # Rate limiter
        self.rate_limiter = AdvancedRateLimiter(
            self.config.rate_limit_config or RateLimitConfig(),
            "global"
        )
        
        # State
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the API and all components."""
        async with self._lock:
            if self._initialized:
                return
            
            # Initialize registry
            await self.registry.initialize()
            
            # Initialize orchestrator
            await self.orchestrator.initialize()
            
            # Initialize health monitor if enabled
            if self.config.enable_health_monitoring:
                await self.health_monitor.initialize()
                await self.health_monitor.start()
            
            # Run benchmark on startup if enabled
            if self.config.enable_benchmarking and self.config.benchmark_on_startup:
                await self.benchmark_runner.initialize()
                # Run a quick benchmark
                try:
                    await self.benchmark_runner.run_benchmark(
                        benchmark_type="latency",
                        num_requests=3,
                    )
                except Exception as e:
                    logger.warning(f"Startup benchmark failed: {e}")
            
            self._initialized = True
            logger.info("FreeLLMAPI initialized")
    
    async def chat(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        use_streaming: bool = False,
        context: Optional[RequestContext] = None,
        **kwargs
    ) -> ResponseResult:
        """
        Send a chat message and get a response.
        
        Args:
            messages: Chat message(s)
            model: Model to use (None for automatic selection)
            provider: Provider to use (None for automatic selection)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_cache: Whether to use caching
            use_streaming: Whether to use streaming
            context: Optional request context
            **kwargs: Additional provider-specific arguments
            
        Returns:
            ResponseResult: Response with metadata
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        if use_cache and self.config.enable_caching:
            cached = await self.cache_manager.get_response(
                provider or "",
                model or "",
                messages,
                {"temperature": temperature, "max_tokens": max_tokens, **kwargs},
            )
            if cached:
                logger.info(f"Cache hit for {provider}/{model}")
                return ResponseResult(
                    request_context=context or RequestContext(
                        provider=provider or "",
                        model=model or "",
                    ),
                    content=cached,
                    provider=provider or "",
                    model=model or "",
                    latency_ms=0,
                    success=True,
                    cached=True,
                )
        
        # Use orchestrator for the request
        result = await self.orchestrator.chat(
            messages=messages,
            model=model or self.config.default_model,
            provider=provider or self.config.default_provider,
            context=context,
            use_cache=False,  # We handle caching here
            use_streaming=use_streaming,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Cache the response if successful
        if use_cache and self.config.enable_caching and result.success:
            await self.cache_manager.set_response(
                result.provider,
                result.model,
                messages,
                result.content,
                {"temperature": temperature, "max_tokens": max_tokens, **kwargs},
            )
        
        return result
    
    async def stream(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[RequestContext] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream a chat response.
        
        Args:
            messages: Chat message(s)
            model: Model to use
            provider: Provider to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            context: Optional request context
            **kwargs: Additional provider-specific arguments
            
        Yields:
            StreamChunk: Streaming chunks
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Select provider if not specified
        if not provider:
            provider = provider or self.config.default_provider
        
        # Get provider instance
        provider_instance = self.registry.get_provider(provider)
        if not provider_instance:
            raise Exception(f"Provider {provider} not available")
        
        # Select model if not specified
        if not model:
            available_models = provider_instance.get_available_models()
            if available_models:
                model = model or available_models[0] or self.config.default_model
        
        # Use streaming manager
        async for chunk in self.streaming_manager.stream(
            provider_instance,
            model,
            messages,
            context,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def embed(
        self,
        text: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> ResponseResult:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            model: Model to use
            provider: Provider to use
            use_cache: Whether to use caching
            **kwargs: Additional arguments
            
        Returns:
            ResponseResult: Response with embedding
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        if use_cache and self.config.enable_caching:
            cached = await self.cache_manager.get_embedding(
                provider or "",
                model or "",
                text,
                kwargs,
            )
            if cached:
                logger.info(f"Embedding cache hit for {provider}/{model}")
                return ResponseResult(
                    request_context=RequestContext(
                        provider=provider or "",
                        model=model or "",
                    ),
                    content=cached,
                    provider=provider or "",
                    model=model or "",
                    latency_ms=0,
                    success=True,
                    cached=True,
                )
        
        # Use orchestrator
        result = await self.orchestrator.embed(
            text=text,
            model=model,
            provider=provider,
            **kwargs
        )
        
        # Cache the embedding if successful
        if use_cache and self.config.enable_caching and result.success:
            await self.cache_manager.set_embedding(
                result.provider,
                result.model,
                text,
                result.content,
                kwargs,
            )
        
        return result
    
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> ResponseResult:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image
            model: Model to use
            provider: Provider to use
            use_cache: Whether to use caching
            **kwargs: Additional arguments
            
        Returns:
            ResponseResult: Response with image data
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        if use_cache and self.config.enable_caching:
            cached = await self.cache_manager.get_image(
                provider or "",
                model or "",
                prompt,
                kwargs,
            )
            if cached:
                logger.info(f"Image cache hit for {provider}/{model}")
                return ResponseResult(
                    request_context=RequestContext(
                        provider=provider or "",
                        model=model or "",
                    ),
                    content=cached,
                    provider=provider or "",
                    model=model or "",
                    latency_ms=0,
                    success=True,
                    cached=True,
                )
        
        # Use orchestrator
        result = await self.orchestrator.generate_image(
            prompt=prompt,
            model=model,
            provider=provider,
            **kwargs
        )
        
        # Cache the image if successful
        if use_cache and self.config.enable_caching and result.success:
            await self.cache_manager.set_image(
                result.provider,
                result.model,
                prompt,
                result.content,
                kwargs,
            )
        
        return result
    
    def list_providers(
        self,
        category: Optional[ProviderCategory] = None,
        status: Optional[ProviderStatus] = None,
    ) -> List[str]:
        """
        List available providers.
        
        Args:
            category: Optional category filter
            status: Optional status filter
            
        Returns:
            List[str]: List of provider names
        """
        return self.registry.list_providers(category, status)
    
    def list_models(
        self,
        provider: Optional[str] = None,
        category: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Args:
            provider: Optional provider filter
            category: Optional model category filter
            capability: Optional capability filter
            
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        return self.registry.list_models(provider, category, capability)
    
    def get_provider_info(self, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dict[str, Any]: Provider information or None
        """
        metadata = self.registry.get_metadata(provider)
        if not metadata:
            return None
        
        return {
            "name": metadata.name,
            "category": metadata.category.value,
            "type": metadata.provider_type.value,
            "status": metadata.status.value,
            "models": [m.to_dict() for m in metadata.models],
            "rate_limits": metadata.rate_limits.to_dict(),
            "requires_auth": metadata.requires_auth,
            "commercial_usage_allowed": metadata.commercial_usage_allowed,
            "response_time_avg": metadata.response_time_avg,
            "success_rate": metadata.success_rate,
        }
    
    def get_model_info(
        self,
        provider: str,
        model: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Dict[str, Any]: Model information or None
        """
        metadata = self.registry.get_metadata(provider)
        if not metadata:
            return None
        
        for m in metadata.models:
            if m.name == model:
                return m.to_dict()
        
        return None
    
    def get_health_status(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status of providers.
        
        Args:
            provider: Optional provider name (None for all providers)
            
        Returns:
            Dict[str, Any]: Health status information
        """
        if provider:
            status = self.health_monitor.get_health_status(provider)
            if status:
                return status.to_dict()
            return {}
        else:
            return self.health_monitor.get_health_summary()
    
    async def run_benchmark(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        benchmark_type: str = "comprehensive",
    ) -> Dict[str, Any]:
        """
        Run a benchmark on providers.
        
        Args:
            provider: Optional provider name (None for all)
            model: Optional model name
            benchmark_type: Type of benchmark (latency, throughput, quality, cost, comprehensive)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        from services.benchmarking import BenchmarkType
        
        try:
            benchmark_type_enum = BenchmarkType(benchmark_type)
        except ValueError:
            benchmark_type_enum = BenchmarkType.COMPREHENSIVE
        
        results = await self.benchmark_runner.run_benchmark(
            provider=provider,
            model=model,
            benchmark_type=benchmark_type_enum,
        )
        
        return {k: v.to_dict() for k, v in results.items()}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get API statistics.
        
        Returns:
            Dict[str, Any]: Statistics including cache, rate limiting, etc.
        """
        return {
            "cache": self.cache_manager.stats,
            "rate_limiter": self.rate_limiter.stats,
            "orchestrator": self.orchestrator.get_stats(),
            "providers": {
                "total": len(self.registry.list_providers()),
                "available": len(self.registry.list_providers(status=ProviderStatus.AVAILABLE)),
            },
        }
    
    def search_providers(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search providers by name, description, or tags.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching providers
        """
        return self.registry.search_providers(query, limit)
    
    def get_best_provider(
        self,
        task: str = "general",
        min_context: Optional[int] = None,
        streaming: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best provider for a specific task.
        
        Args:
            task: Task type (general, coding, chat, etc.)
            min_context: Minimum context window required
            streaming: Whether streaming is required
            
        Returns:
            Dict[str, Any]: Best provider information or None
        """
        return self.registry.get_best_provider(task, min_context, streaming)
    
    async def close(self):
        """Close the API and cleanup resources."""
        # Stop health monitor
        if self.config.enable_health_monitoring:
            await self.health_monitor.stop()
        
        # Cleanup registry
        self.registry.cleanup()
        
        self._initialized = False
        logger.info("FreeLLMAPI closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.run(self.close())
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global API instance
_api: Optional[FreeLLMAPI] = None


def get_api(config: Optional[FreeLLMAPIConfig] = None) -> FreeLLMAPI:
    """Get the global FreeLLMAPI instance."""
    global _api
    if _api is None:
        _api = FreeLLMAPI(config)
    return _api


async def initialize_api(config: Optional[FreeLLMAPIConfig] = None) -> FreeLLMAPI:
    """Initialize and get the global FreeLLMAPI instance."""
    api = get_api(config)
    await api.initialize()
    return api
