"""
Orchestration

Advanced orchestration for managing multiple providers, load balancing, and fallback.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta

from .models import (
    ProviderMetadata,
    ProviderStatus,
    LoadBalancingStrategy,
    RoutingStrategy,
    RequestContext,
    ResponseResult,
    HealthStatus,
)
from .provider_registry import ProviderRegistry, get_registry

logger = logging.getLogger(__name__)


@dataclass
class ProviderWeight:
    """Weight configuration for a provider."""
    provider: str
    weight: float = 1.0
    priority: int = 0
    max_requests: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "weight": self.weight,
            "priority": self.priority,
            "max_requests": self.max_requests,
        }


@dataclass
class RoutingRule:
    """Routing rule for requests."""
    condition: Callable[[RequestContext], bool]
    provider: str
    priority: int = 0
    
    def matches(self, context: RequestContext) -> bool:
        """Check if this rule matches the context."""
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating routing rule: {e}")
            return False


class LoadBalancer:
    """
    Load balancer for distributing requests across providers.
    
    Supports multiple strategies: round-robin, random, least-connections, 
    least-latency, weighted, and priority-based.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
    ):
        self.registry = registry or get_registry()
        self.strategy = strategy
        self._provider_stats: Dict[str, Dict[str, Any]] = {}
        self._request_counts: Dict[str, int] = {}
        self._last_used: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        self._weights: Dict[str, ProviderWeight] = {}
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """Set the load balancing strategy."""
        self.strategy = strategy
        logger.info(f"Load balancing strategy set to: {strategy.value}")
    
    def set_weight(self, provider: str, weight: float, priority: int = 0):
        """Set weight for a provider."""
        self._weights[provider] = ProviderWeight(
            provider=provider,
            weight=weight,
            priority=priority,
        )
        logger.info(f"Set weight for {provider}: {weight}, priority: {priority}")
    
    def get_provider_stats(self, provider: str) -> Dict[str, Any]:
        """Get statistics for a provider."""
        return self._provider_stats.get(provider, {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "avg_latency": 0.0,
            "last_request": None,
        })
    
    def record_request(
        self,
        provider: str,
        latency: float,
        success: bool,
    ):
        """Record a request to a provider."""
        if provider not in self._provider_stats:
            self._provider_stats[provider] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "total_latency": 0.0,
                "last_request": datetime.now(),
            }
        
        stats = self._provider_stats[provider]
        stats["requests"] += 1
        stats["total_latency"] += latency
        
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        
        stats["last_request"] = datetime.now()
        stats["avg_latency"] = stats["total_latency"] / stats["requests"]
    
    async def select_provider(
        self,
        providers: Optional[List[str]] = None,
        category: Optional[str] = None,
        exclude: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Select the best provider based on the current strategy.
        
        Args:
            providers: Optional list of provider names to choose from
            category: Optional category filter
            exclude: Optional list of providers to exclude
            
        Returns:
            str: Selected provider name or None
        """
        # Get available providers
        if providers is None:
            providers = self.registry.list_providers()
        
        # Filter by category
        if category:
            providers = [
                p for p in providers 
                if self.registry.get_metadata(p).category.value == category
            ]
        
        # Exclude specified providers
        if exclude:
            providers = [p for p in providers if p not in exclude]
        
        # Filter out unavailable providers
        available_providers = [
            p for p in providers
            if self.registry.get_metadata(p).status == ProviderStatus.AVAILABLE
        ]
        
        if not available_providers:
            logger.warning("No available providers")
            return None
        
        # Apply strategy
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(available_providers)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random(available_providers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(available_providers)
        elif self.strategy == LoadBalancingStrategy.LEAST_LATENCY:
            return self._least_latency(available_providers)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            return self._weighted(available_providers)
        elif self.strategy == LoadBalancingStrategy.PRIORITY:
            return self._priority(available_providers)
        else:
            return self._round_robin(available_providers)
    
    def _round_robin(self, providers: List[str]) -> str:
        """Round-robin selection."""
        # Sort by last used time
        sorted_providers = sorted(
            providers,
            key=lambda p: self._last_used.get(p, datetime.min),
        )
        
        # Select the least recently used
        selected = sorted_providers[0]
        self._last_used[selected] = datetime.now()
        return selected
    
    def _random(self, providers: List[str]) -> str:
        """Random selection."""
        return random.choice(providers)
    
    def _least_connections(self, providers: List[str]) -> str:
        """Select provider with least active connections."""
        # For now, use request counts as proxy for connections
        sorted_providers = sorted(
            providers,
            key=lambda p: self._request_counts.get(p, 0),
        )
        return sorted_providers[0]
    
    def _least_latency(self, providers: List[str]) -> str:
        """Select provider with least average latency."""
        sorted_providers = sorted(
            providers,
            key=lambda p: self.get_provider_stats(p).get("avg_latency", float('inf')),
        )
        return sorted_providers[0]
    
    def _weighted(self, providers: List[str]) -> str:
        """Weighted selection."""
        weights = []
        for provider in providers:
            weight = self._weights.get(provider, ProviderWeight(provider, 1.0)).weight
            weights.append(weight)
        
        # Normalize weights
        total = sum(weights)
        if total == 0:
            return random.choice(providers)
        
        probabilities = [w / total for w in weights]
        return random.choices(providers, weights=probabilities, k=1)[0]
    
    def _priority(self, providers: List[str]) -> str:
        """Priority-based selection."""
        # Sort by priority (higher is better)
        sorted_providers = sorted(
            providers,
            key=lambda p: self._weights.get(p, ProviderWeight(p, 1.0, 0)).priority,
            reverse=True,
        )
        return sorted_providers[0]


class FallbackManager:
    """
    Fallback manager for handling provider failures.
    
    Implements automatic fallback to alternative providers when requests fail.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True,
    ):
        self.registry = registry or get_registry()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        self._fallback_chains: Dict[str, List[str]] = {}
        self._error_counts: Dict[str, int] = {}
    
    def set_fallback_chain(
        self,
        primary: str,
        fallbacks: List[str],
    ):
        """
        Set a fallback chain for a primary provider.
        
        Args:
            primary: Primary provider name
            fallbacks: List of fallback provider names in order
        """
        self._fallback_chains[primary] = fallbacks
        logger.info(f"Set fallback chain for {primary}: {fallbacks}")
    
    def get_fallback_chain(self, provider: str) -> List[str]:
        """
        Get the fallback chain for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List[str]: Fallback chain
        """
        return self._fallback_chains.get(provider, [])
    
    def record_error(self, provider: str):
        """Record an error for a provider."""
        self._error_counts[provider] = self._error_counts.get(provider, 0) + 1
        logger.warning(f"Error recorded for {provider}, total: {self._error_counts[provider]}")
    
    def get_error_count(self, provider: str) -> int:
        """Get error count for a provider."""
        return self._error_counts.get(provider, 0)
    
    def reset_error_count(self, provider: str):
        """Reset error count for a provider."""
        self._error_counts[provider] = 0
    
    async def execute_with_fallback(
        self,
        provider_name: str,
        method: str,
        args: tuple,
        kwargs: Dict[str, Any],
        fallback_providers: Optional[List[str]] = None,
    ) -> Any:
        """
        Execute a method with automatic fallback.
        
        Args:
            provider_name: Primary provider name
            method: Method name to call
            args: Positional arguments
            kwargs: Keyword arguments
            fallback_providers: Optional list of fallback providers
            
        Returns:
            Any: Result from successful provider
            
        Raises:
            Exception: If all providers fail
        """
        # Get fallback chain
        if fallback_providers is None:
            fallback_providers = self.get_fallback_chain(provider_name)
        
        all_providers = [provider_name] + fallback_providers
        last_error = None
        
        for i, provider in enumerate(all_providers):
            try:
                # Get provider instance
                provider_instance = self.registry.get_provider(provider)
                if not provider_instance:
                    logger.warning(f"Provider {provider} not available")
                    continue
                
                # Get method
                method_func = getattr(provider_instance, method)
                if not method_func:
                    logger.warning(f"Method {method} not found on provider {provider}")
                    continue
                
                # Execute
                if asyncio.iscoroutinefunction(method_func):
                    result = await method_func(*args, **kwargs)
                else:
                    result = method_func(*args, **kwargs)
                
                # Success - reset error count
                self.reset_error_count(provider)
                logger.info(f"Success with provider {provider}")
                return result
                
            except Exception as e:
                last_error = e
                self.record_error(provider)
                logger.warning(f"Provider {provider} failed: {e}")
                
                # Wait before retrying
                if i < len(all_providers) - 1:
                    delay = self._calculate_delay(i)
                    logger.info(f"Waiting {delay:.2f}s before trying next provider")
                    await asyncio.sleep(delay)
        
        # All providers failed
        error_msg = f"All providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry."""
        if self.exponential_backoff:
            return self.retry_delay * (2 ** attempt)
        return self.retry_delay


class RoutingStrategy:
    """
    Routing strategy for directing requests to appropriate providers.
    
    Supports multiple strategies: random, cost-optimized, performance-optimized,
    capability-based, and geographic.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        strategy: RoutingStrategy = RoutingStrategy.COST_OPTIMIZED,
    ):
        self.registry = registry or get_registry()
        self.strategy = strategy
        self._routing_rules: List[RoutingRule] = []
    
    def set_strategy(self, strategy: RoutingStrategy):
        """Set the routing strategy."""
        self.strategy = strategy
        logger.info(f"Routing strategy set to: {strategy.value}")
    
    def add_routing_rule(self, rule: RoutingRule):
        """Add a custom routing rule."""
        self._routing_rules.append(rule)
        logger.info(f"Added routing rule for {rule.provider}")
    
    async def route_request(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Route a request to the appropriate provider.
        
        Args:
            context: Request context
            providers: Optional list of candidate providers
            
        Returns:
            str: Selected provider name or None
        """
        # First, check custom routing rules
        for rule in self._routing_rules:
            if rule.matches(context):
                logger.info(f"Routing to {rule.provider} based on custom rule")
                return rule.provider
        
        # Apply strategy
        if self.strategy == RoutingStrategy.RANDOM:
            return self._random_route(context, providers)
        elif self.strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._cost_optimized_route(context, providers)
        elif self.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            return self._performance_optimized_route(context, providers)
        elif self.strategy == RoutingStrategy.CAPABILITY_BASED:
            return self._capability_based_route(context, providers)
        elif self.strategy == RoutingStrategy.GEOGRAPHIC:
            return self._geographic_route(context, providers)
        else:
            return self._random_route(context, providers)
    
    def _random_route(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Random routing."""
        if providers is None:
            providers = self.registry.list_providers()
        
        available = [
            p for p in providers
            if self.registry.get_metadata(p).status == ProviderStatus.AVAILABLE
        ]
        
        return random.choice(available) if available else None
    
    def _cost_optimized_route(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Cost-optimized routing."""
        if providers is None:
            providers = self.registry.list_providers()
        
        best_provider = None
        best_cost = float('inf')
        
        for provider in providers:
            metadata = self.registry.get_metadata(provider)
            if metadata.status != ProviderStatus.AVAILABLE:
                continue
            
            # Calculate cost score (lower is better)
            # For free providers, use rate limits as proxy for cost
            cost_score = self._calculate_cost_score(metadata)
            
            if cost_score < best_cost:
                best_cost = cost_score
                best_provider = provider
        
        return best_provider
    
    def _calculate_cost_score(self, metadata: ProviderMetadata) -> float:
        """Calculate a cost score for a provider."""
        score = 0.0
        
        # Prefer providers with higher rate limits
        if metadata.rate_limits.requests_per_day:
            score += 10000 / metadata.rate_limits.requests_per_day
        
        # Prefer providers with higher success rates
        if metadata.success_rate:
            score += (1 - metadata.success_rate) * 10
        
        # Prefer providers with lower latency
        if metadata.response_time_avg:
            score += metadata.response_time_avg / 1000
        
        return score
    
    def _performance_optimized_route(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Performance-optimized routing."""
        if providers is None:
            providers = self.registry.list_providers()
        
        best_provider = None
        best_performance = -1.0
        
        for provider in providers:
            metadata = self.registry.get_metadata(provider)
            if metadata.status != ProviderStatus.AVAILABLE:
                continue
            
            # Calculate performance score (higher is better)
            performance_score = self._calculate_performance_score(metadata)
            
            if performance_score > best_performance:
                best_performance = performance_score
                best_provider = provider
        
        return best_provider
    
    def _calculate_performance_score(self, metadata: ProviderMetadata) -> float:
        """Calculate a performance score for a provider."""
        score = 0.0
        
        # Higher rate limits = better
        if metadata.rate_limits.requests_per_day:
            score += metadata.rate_limits.requests_per_day / 1000
        
        # Higher success rate = better
        if metadata.success_rate:
            score += metadata.success_rate * 10
        
        # Lower latency = better
        if metadata.response_time_avg:
            score += 1000 / (metadata.response_time_avg + 1)
        
        return score
    
    def _capability_based_route(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Capability-based routing."""
        if providers is None:
            providers = self.registry.list_providers()
        
        # Check if context specifies required capabilities
        required_capabilities = context.metadata.get("required_capabilities", [])
        
        if not required_capabilities:
            return self._random_route(context, providers)
        
        best_provider = None
        best_match_count = 0
        
        for provider in providers:
            metadata = self.registry.get_metadata(provider)
            if metadata.status != ProviderStatus.AVAILABLE:
                continue
            
            # Count matching capabilities
            match_count = 0
            for capability in required_capabilities:
                for model in metadata.models:
                    if getattr(model.capabilities, capability, False):
                        match_count += 1
                        break
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_provider = provider
        
        return best_provider
    
    def _geographic_route(
        self,
        context: RequestContext,
        providers: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Geographic routing based on user location."""
        # For now, just use random routing
        # In a real implementation, this would use the user's location
        # to select the nearest provider
        return self._random_route(context, providers)


class ProviderOrchestrator:
    """
    Main orchestrator for managing provider interactions.
    
    Combines load balancing, fallback, and routing strategies.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        load_balancer: Optional[LoadBalancer] = None,
        fallback_manager: Optional[FallbackManager] = None,
        routing_strategy: Optional[RoutingStrategy] = None,
    ):
        self.registry = registry or get_registry()
        self.load_balancer = load_balancer or LoadBalancer(registry)
        self.fallback_manager = fallback_manager or FallbackManager(registry)
        self.routing_strategy = routing_strategy or RoutingStrategy(registry)
        self._request_history: List[RequestContext] = []
    
    async def initialize(self):
        """Initialize the orchestrator."""
        await self.registry.initialize()
        logger.info("Orchestrator initialized")
    
    async def chat(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[RequestContext] = None,
        use_cache: bool = True,
        use_streaming: bool = False,
        **kwargs
    ) -> ResponseResult:
        """
        Send a chat request through the orchestrator.
        
        Args:
            messages: Chat messages
            model: Optional model name
            provider: Optional provider name
            context: Optional request context
            use_cache: Whether to use caching
            use_streaming: Whether to use streaming
            **kwargs: Additional arguments
            
        Returns:
            ResponseResult: Response result
        """
        # Create request context
        context = context or RequestContext(
            provider=provider or "",
            model=model or "",
        )
        
        start_time = datetime.now()
        
        try:
            # Select provider if not specified
            if not provider:
                provider = await self._select_provider(context, model)
                if not provider:
                    raise Exception("No available provider")
                context.provider = provider
            
            # Get provider instance
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                raise Exception(f"Provider {provider} not available")
            
            # Select model if not specified
            if not model:
                available_models = provider_instance.get_available_models()
                if available_models:
                    model = available_models[0]
                    context.model = model
            
            # Execute request
            if use_streaming and hasattr(provider_instance, "stream_chat"):
                # For streaming, we'll collect all chunks
                from .streaming import get_streaming_manager
                streaming_manager = get_streaming_manager()
                
                response = await streaming_manager.collect_stream(
                    provider_instance,
                    model,
                    messages,
                    context,
                    **kwargs
                )
                
                result = ResponseResult(
                    request_context=context,
                    content=response.full_text,
                    provider=provider,
                    model=model,
                    latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    success=True,
                    cached=False,
                )
            else:
                # Non-streaming request
                response = await provider_instance.chat(model, messages, **kwargs)
                
                result = ResponseResult(
                    request_context=context,
                    content=response,
                    provider=provider,
                    model=model,
                    latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    success=True,
                    cached=False,
                )
            
            # Record request in load balancer
            self.load_balancer.record_request(
                provider,
                result.latency_ms,
                result.success,
            )
            
            # Record in request history
            self._request_history.append(context)
            
            return result
            
        except Exception as e:
            # Handle error with fallback
            logger.error(f"Request failed: {e}")
            
            # Try fallback
            if self.fallback_manager.max_retries > 0:
                try:
                    fallback_result = await self.fallback_manager.execute_with_fallback(
                        provider or "",
                        "chat",
                        (model, messages),
                        kwargs,
                    )
                    
                    return ResponseResult(
                        request_context=context,
                        content=fallback_result,
                        provider=provider or "fallback",
                        model=model or "",
                        latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        success=True,
                        cached=False,
                        error=str(e),
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
            
            return ResponseResult(
                request_context=context,
                content="",
                provider=provider or "",
                model=model or "",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                cached=False,
                error=str(e),
            )
    
    async def _select_provider(
        self,
        context: RequestContext,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """Select the best provider for a request."""
        # First, try routing strategy
        provider = await self.routing_strategy.route_request(context)
        if provider:
            return provider
        
        # Fall back to load balancer
        provider = await self.load_balancer.select_provider()
        if provider:
            return provider
        
        # Fall back to registry's best provider
        best = self.registry.get_best_provider()
        if best:
            return best["name"]
        
        return None
    
    async def embed(
        self,
        text: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[RequestContext] = None,
        **kwargs
    ) -> ResponseResult:
        """
        Generate embeddings through the orchestrator.
        
        Args:
            text: Text to embed
            model: Optional model name
            provider: Optional provider name
            context: Optional request context
            **kwargs: Additional arguments
            
        Returns:
            ResponseResult: Response result with embedding
        """
        context = context or RequestContext(
            provider=provider or "",
            model=model or "",
        )
        
        start_time = datetime.now()
        
        try:
            # Select provider if not specified
            if not provider:
                provider = await self._select_provider(context, model)
                if not provider:
                    raise Exception("No available provider")
                context.provider = provider
            
            # Get provider instance
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                raise Exception(f"Provider {provider} not available")
            
            # Select model if not specified
            if not model:
                available_models = provider_instance.get_available_models()
                if available_models:
                    model = available_models[0]
                    context.model = model
            
            # Execute request
            if hasattr(provider_instance, "embed"):
                embedding = await provider_instance.embed(model, text, **kwargs)
                
                result = ResponseResult(
                    request_context=context,
                    content=embedding,
                    provider=provider,
                    model=model,
                    latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    success=True,
                    cached=False,
                )
            else:
                raise Exception(f"Provider {provider} does not support embeddings")
            
            # Record request
            self.load_balancer.record_request(
                provider,
                result.latency_ms,
                result.success,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Embedding request failed: {e}")
            return ResponseResult(
                request_context=context,
                content=[],
                provider=provider or "",
                model=model or "",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                cached=False,
                error=str(e),
            )
    
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[RequestContext] = None,
        **kwargs
    ) -> ResponseResult:
        """
        Generate an image through the orchestrator.
        
        Args:
            prompt: Image generation prompt
            model: Optional model name
            provider: Optional provider name
            context: Optional request context
            **kwargs: Additional arguments
            
        Returns:
            ResponseResult: Response result with image data
        """
        context = context or RequestContext(
            provider=provider or "",
            model=model or "",
        )
        
        start_time = datetime.now()
        
        try:
            # For now, just use the first available image provider
            # In a real implementation, this would use the full orchestration
            from providers.image.stable_diffusion import StableDiffusionProvider
            
            sd_provider = StableDiffusionProvider()
            image_data = await sd_provider.generate(prompt, model, **kwargs)
            
            result = ResponseResult(
                request_context=context,
                content=image_data,
                provider="stable_diffusion",
                model=model or "stable_diffusion_3.5",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=True,
                cached=False,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ResponseResult(
                request_context=context,
                content=b"",
                provider=provider or "",
                model=model or "",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                cached=False,
                error=str(e),
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "load_balancer": self.load_balancer.stats,
            "fallback_manager": {
                "error_counts": self.fallback_manager._error_counts,
            },
            "request_history_count": len(self._request_history),
        }
    
    def clear_history(self):
        """Clear request history."""
        self._request_history.clear()
