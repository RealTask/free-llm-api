"""
Health Monitor

Comprehensive health monitoring for AI providers.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from core.models import (
    ProviderStatus,
    HealthStatus,
    ProviderMetadata,
)
from core.provider_registry import ProviderRegistry, get_registry

logger = logging.getLogger(__name__)


class HealthCheckType(Enum):
    """Types of health checks."""
    CONNECTIVITY = "connectivity"
    LATENCY = "latency"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    MODEL_AVAILABILITY = "model_availability"
    FULL = "full"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    check_interval: float = 60.0  # seconds
    timeout: float = 30.0  # seconds
    max_retries: int = 3
    retry_delay: float = 5.0  # seconds
    
    # Which checks to perform
    check_connectivity: bool = True
    check_latency: bool = True
    check_rate_limits: bool = True
    check_authentication: bool = True
    check_model_availability: bool = True
    
    # Thresholds
    latency_threshold: float = 5.0  # seconds
    success_rate_threshold: float = 0.95
    
    # Notifications
    on_status_change: Optional[Callable[[str, ProviderStatus, ProviderStatus], None]] = None
    on_health_check_failure: Optional[Callable[[str, HealthCheckType, str], None]] = None
    on_health_check_success: Optional[Callable[[str, HealthCheckType], None]] = None


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    provider: str
    check_type: HealthCheckType
    success: bool
    latency: Optional[float] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "check_type": self.check_type.value,
            "success": self.success,
            "latency": self.latency,
            "error": self.error,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthMonitor:
    """
    Monitor the health of AI providers.
    
    Performs regular health checks and maintains status information.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        config: Optional[HealthCheckConfig] = None,
    ):
        self.registry = registry or get_registry()
        self.config = config or HealthCheckConfig()
        self._health_status: Dict[str, HealthStatus] = {}
        self._last_check: Dict[str, datetime] = {}
        self._check_history: Dict[str, List[HealthCheckResult]] = {}
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the health monitor."""
        await self.registry.initialize()
        
        # Initialize health status for all providers
        providers = self.registry.list_providers()
        for provider in providers:
            self._health_status[provider] = HealthStatus(
                provider=provider,
                status=ProviderStatus.UNKNOWN,
            )
            self._check_history[provider] = []
        
        logger.info(f"Health monitor initialized with {len(providers)} providers")
    
    async def start(self):
        """Start the health monitoring loop."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitor started")
    
    async def stop(self):
        """Stop the health monitoring loop."""
        if not self._running:
            return
        
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self.check_all_providers()
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
            
            await asyncio.sleep(self.config.check_interval)
    
    async def check_all_providers(self):
        """Check the health of all providers."""
        providers = self.registry.list_providers()
        
        tasks = []
        for provider in providers:
            task = asyncio.create_task(self.check_provider(provider))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Completed health check for {len(providers)} providers")
    
    async def check_provider(
        self,
        provider: str,
        check_types: Optional[List[HealthCheckType]] = None,
    ) -> Dict[HealthCheckType, HealthCheckResult]:
        """
        Check the health of a specific provider.
        
        Args:
            provider: Provider name
            check_types: Optional list of check types to perform
            
        Returns:
            Dict[HealthCheckType, HealthCheckResult]: Results for each check type
        """
        if check_types is None:
            check_types = [
                HealthCheckType.CONNECTIVITY,
                HealthCheckType.LATENCY,
                HealthCheckType.RATE_LIMIT,
            ]
        
        results = {}
        
        for check_type in check_types:
            try:
                result = await self._perform_check(provider, check_type)
                results[check_type] = result
                
                if result.success:
                    if self.config.on_health_check_success:
                        self.config.on_health_check_success(provider, check_type)
                else:
                    if self.config.on_health_check_failure:
                        self.config.on_health_check_failure(
                            provider, check_type, result.error or ""
                        )
            except Exception as e:
                logger.error(f"Error checking {provider} for {check_type.value}: {e}")
                results[check_type] = HealthCheckResult(
                    provider=provider,
                    check_type=check_type,
                    success=False,
                    error=str(e),
                )
        
        # Update overall health status
        await self._update_health_status(provider, results)
        
        return results
    
    async def _perform_check(
        self,
        provider: str,
        check_type: HealthCheckType,
    ) -> HealthCheckResult:
        """Perform a specific health check."""
        start_time = time.time()
        
        try:
            if check_type == HealthCheckType.CONNECTIVITY:
                return await self._check_connectivity(provider)
            elif check_type == HealthCheckType.LATENCY:
                return await self._check_latency(provider)
            elif check_type == HealthCheckType.RATE_LIMIT:
                return await self._check_rate_limit(provider)
            elif check_type == HealthCheckType.AUTHENTICATION:
                return await self._check_authentication(provider)
            elif check_type == HealthCheckType.MODEL_AVAILABILITY:
                return await self._check_model_availability(provider)
            elif check_type == HealthCheckType.FULL:
                return await self._check_full(provider)
            else:
                return HealthCheckResult(
                    provider=provider,
                    check_type=check_type,
                    success=False,
                    error=f"Unknown check type: {check_type}",
                )
        finally:
            latency = time.time() - start_time
            logger.debug(f"Health check {check_type.value} for {provider} took {latency:.2f}s")
    
    async def _check_connectivity(self, provider: str) -> HealthCheckResult:
        """Check if the provider is reachable."""
        try:
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.CONNECTIVITY,
                    success=False,
                    error=f"Provider {provider} not found",
                )
            
            # Try to get available models (this tests connectivity)
            models = provider_instance.get_available_models()
            
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.CONNECTIVITY,
                success=True,
                details={"models_count": len(models)},
            )
        except Exception as e:
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.CONNECTIVITY,
                success=False,
                error=str(e),
            )
    
    async def _check_latency(self, provider: str) -> HealthCheckResult:
        """Check the latency of the provider."""
        try:
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.LATENCY,
                    success=False,
                    error=f"Provider {provider} not found",
                )
            
            # Get available models
            models = provider_instance.get_available_models()
            if not models:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.LATENCY,
                    success=False,
                    error="No models available",
                )
            
            # Use the first model for a simple test
            model = models[0]
            
            # Time a simple request
            start = time.time()
            try:
                # Use a simple prompt
                response = await provider_instance.chat(
                    model,
                    "Health check: please respond with 'OK'",
                    max_tokens=10,
                )
                latency = time.time() - start
                
                # Check if response is reasonable
                if "OK" in response.upper() or len(response) > 0:
                    return HealthCheckResult(
                        provider=provider,
                        check_type=HealthCheckType.LATENCY,
                        success=True,
                        latency=latency,
                        details={"model": model, "response_length": len(response)},
                    )
                else:
                    return HealthCheckResult(
                        provider=provider,
                        check_type=HealthCheckType.LATENCY,
                        success=False,
                        latency=latency,
                        error="Unexpected response",
                        details={"response": response[:100]},
                    )
            except Exception as e:
                latency = time.time() - start
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.LATENCY,
                    success=False,
                    latency=latency,
                    error=str(e),
                )
        except Exception as e:
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.LATENCY,
                success=False,
                error=str(e),
            )
    
    async def _check_rate_limit(self, provider: str) -> HealthCheckResult:
        """Check if the provider is within rate limits."""
        try:
            metadata = self.registry.get_metadata(provider)
            if not metadata:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.RATE_LIMIT,
                    success=False,
                    error=f"Provider {provider} metadata not found",
                )
            
            # Check if we have recent request data
            health_status = self._health_status.get(provider)
            if health_status:
                # Check consecutive failures
                if health_status.consecutive_failures >= self.config.max_retries:
                    return HealthCheckResult(
                        provider=provider,
                        check_type=HealthCheckType.RATE_LIMIT,
                        success=False,
                        error=f"Too many consecutive failures: {health_status.consecutive_failures}",
                    )
            
            # For now, just check if we can get a provider instance
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.RATE_LIMIT,
                    success=False,
                    error=f"Provider {provider} not available",
                )
            
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.RATE_LIMIT,
                success=True,
                details={
                    "rate_limits": metadata.rate_limits.to_dict(),
                },
            )
        except Exception as e:
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.RATE_LIMIT,
                success=False,
                error=str(e),
            )
    
    async def _check_authentication(self, provider: str) -> HealthCheckResult:
        """Check if authentication is working."""
        try:
            metadata = self.registry.get_metadata(provider)
            if not metadata:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.AUTHENTICATION,
                    success=False,
                    error=f"Provider {provider} metadata not found",
                )
            
            if not metadata.requires_auth:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.AUTHENTICATION,
                    success=True,
                    details={"requires_auth": False},
                )
            
            # Try to create a provider instance
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.AUTHENTICATION,
                    success=False,
                    error="Could not create provider instance",
                )
            
            # If we can create the instance, authentication is likely working
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.AUTHENTICATION,
                success=True,
                details={"requires_auth": True, "api_key_set": bool(provider_instance.api_key)},
            )
        except Exception as e:
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.AUTHENTICATION,
                success=False,
                error=str(e),
            )
    
    async def _check_model_availability(self, provider: str) -> HealthCheckResult:
        """Check if models are available."""
        try:
            provider_instance = self.registry.get_provider(provider)
            if not provider_instance:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.MODEL_AVAILABILITY,
                    success=False,
                    error=f"Provider {provider} not found",
                )
            
            models = provider_instance.get_available_models()
            
            if not models:
                return HealthCheckResult(
                    provider=provider,
                    check_type=HealthCheckType.MODEL_AVAILABILITY,
                    success=False,
                    error="No models available",
                )
            
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.MODEL_AVAILABILITY,
                success=True,
                details={
                    "models_count": len(models),
                    "models": models[:10],  # First 10 models
                },
            )
        except Exception as e:
            return HealthCheckResult(
                provider=provider,
                check_type=HealthCheckType.MODEL_AVAILABILITY,
                success=False,
                error=str(e),
            )
    
    async def _check_full(self, provider: str) -> HealthCheckResult:
        """Perform a full health check."""
        results = await self.check_provider(
            provider,
            [
                HealthCheckType.CONNECTIVITY,
                HealthCheckType.LATENCY,
                HealthCheckType.RATE_LIMIT,
                HealthCheckType.AUTHENTICATION,
                HealthCheckType.MODEL_AVAILABILITY,
            ],
        )
        
        # Aggregate results
        all_success = all(r.success for r in results.values())
        total_latency = sum(r.latency or 0 for r in results.values())
        avg_latency = total_latency / len(results) if results else 0
        
        return HealthCheckResult(
            provider=provider,
            check_type=HealthCheckType.FULL,
            success=all_success,
            latency=avg_latency,
            details={
                "checks": {k.value: v.to_dict() for k, v in results.items()},
            },
        )
    
    async def _update_health_status(
        self,
        provider: str,
        results: Dict[HealthCheckType, HealthCheckResult],
    ):
        """Update the health status based on check results."""
        async with self._lock:
            # Get current status
            current_status = self._health_status.get(provider)
            if not current_status:
                current_status = HealthStatus(provider=provider)
                self._health_status[provider] = current_status
            
            # Update last check time
            current_status.last_check = datetime.now()
            
            # Check for failures
            failures = [r for r in results.values() if not r.success]
            
            if not failures:
                # All checks passed
                if current_status.status != ProviderStatus.AVAILABLE:
                    old_status = current_status.status
                    current_status.status = ProviderStatus.AVAILABLE
                    current_status.consecutive_failures = 0
                    current_status.last_success = datetime.now()
                    
                    if self.config.on_status_change:
                        self.config.on_status_change(provider, old_status, ProviderStatus.AVAILABLE)
            else:
                # Some checks failed
                current_status.consecutive_failures += 1
                current_status.last_failure = datetime.now()
                
                # Set error message from first failure
                first_failure = failures[0]
                current_status.error_message = first_failure.error
                
                # Update status based on consecutive failures
                if current_status.consecutive_failures >= self.config.max_retries:
                    if current_status.status != ProviderStatus.UNAVAILABLE:
                        old_status = current_status.status
                        current_status.status = ProviderStatus.UNAVAILABLE
                        
                        if self.config.on_status_change:
                            self.config.on_status_change(
                                provider, old_status, ProviderStatus.UNAVAILABLE
                            )
                else:
                    if current_status.status != ProviderStatus.DEGRADED:
                        old_status = current_status.status
                        current_status.status = ProviderStatus.DEGRADED
                        
                        if self.config.on_status_change:
                            self.config.on_status_change(
                                provider, old_status, ProviderStatus.DEGRADED
                            )
            
            # Update response time
            latency_results = [
                r for r in results.values() 
                if r.check_type == HealthCheckType.LATENCY and r.latency
            ]
            if latency_results:
                current_status.response_time = sum(r.latency for r in latency_results) / len(latency_results)
            
            # Store check history
            self._check_history[provider].append(list(results.values())[-1])  # Store last result
            if len(self._check_history[provider]) > 100:
                self._check_history[provider] = self._check_history[provider][-100:]
            
            # Update registry
            self.registry.update_status(
                provider,
                current_status.status,
                current_status.response_time,
                current_status.error_message,
            )
    
    def get_health_status(self, provider: str) -> Optional[HealthStatus]:
        """Get the health status of a provider."""
        return self._health_status.get(provider)
    
    def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """Get the health status of all providers."""
        return self._health_status.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health status."""
        summary = {
            "total_providers": len(self._health_status),
            "available": 0,
            "degraded": 0,
            "unavailable": 0,
            "maintenance": 0,
            "rate_limited": 0,
            "providers": {},
        }
        
        for provider, status in self._health_status.items():
            summary[status.status.value] = summary.get(status.status.value, 0) + 1
            summary["providers"][provider] = {
                "status": status.status.value,
                "last_check": status.last_check.isoformat() if status.last_check else None,
                "response_time": status.response_time,
                "consecutive_failures": status.consecutive_failures,
            }
        
        return summary
    
    def get_check_history(
        self,
        provider: str,
        limit: int = 10,
    ) -> List[HealthCheckResult]:
        """Get the check history for a provider."""
        return self._check_history.get(provider, [])[-limit:]
    
    async def force_check(self, provider: str) -> Dict[HealthCheckType, HealthCheckResult]:
        """
        Force a health check for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dict[HealthCheckType, HealthCheckResult]: Results for each check
        """
        return await self.check_provider(provider)


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor(
    registry: Optional[ProviderRegistry] = None,
    config: Optional[HealthCheckConfig] = None,
) -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor(registry, config)
    return _health_monitor
