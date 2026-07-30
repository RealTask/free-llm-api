"""
Core Models

Data models and types for the advanced LLM API system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json


class ProviderStatus(Enum):
    """Status of a provider."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"


class ProviderCategory(Enum):
    """Categories of AI providers."""
    LLM = "llm"
    IMAGE = "image"
    SPEECH = "speech"
    EMBEDDINGS = "embeddings"
    MULTIMODAL = "multimodal"


class ProviderType(Enum):
    """Types of providers."""
    CLOUD = "cloud"
    LOCAL = "local"
    HYBRID = "hybrid"


class CacheType(Enum):
    """Types of caching."""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"
    DATABASE = "database"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_LATENCY = "least_latency"
    WEIGHTED = "weighted"
    PRIORITY = "priority"


class RoutingStrategy(Enum):
    """Routing strategies."""
    RANDOM = "random"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    CAPABILITY_BASED = "capability_based"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"


@dataclass
class RateLimit:
    """Enhanced rate limit configuration."""
    requests_per_second: Optional[int] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    tokens_per_second: Optional[int] = None
    tokens_per_minute: Optional[int] = None
    tokens_per_hour: Optional[int] = None
    tokens_per_day: Optional[int] = None
    concurrent_requests: Optional[int] = None
    burst_limit: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "requests_per_day": self.requests_per_day,
            "tokens_per_second": self.tokens_per_second,
            "tokens_per_minute": self.tokens_per_minute,
            "tokens_per_hour": self.tokens_per_hour,
            "tokens_per_day": self.tokens_per_day,
            "concurrent_requests": self.concurrent_requests,
            "burst_limit": self.burst_limit,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RateLimit":
        return cls(**{k: v for k, v in data.items() if v is not None})


@dataclass
class ModelCapability:
    """Model capabilities and features."""
    supports_chat: bool = True
    supports_completion: bool = True
    supports_streaming: bool = True
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    supports_tools: bool = False
    supports_json_mode: bool = False
    max_context_length: Optional[int] = None
    max_tokens: Optional[int] = None
    supports_system_prompt: bool = True
    supports_function_calling: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        return {
            "supports_chat": self.supports_chat,
            "supports_completion": self.supports_completion,
            "supports_streaming": self.supports_streaming,
            "supports_embeddings": self.supports_embeddings,
            "supports_vision": self.supports_vision,
            "supports_audio": self.supports_audio,
            "supports_tools": self.supports_tools,
            "supports_json_mode": self.supports_json_mode,
            "max_context_length": self.max_context_length,
            "max_tokens": self.max_tokens,
            "supports_system_prompt": self.supports_system_prompt,
            "supports_function_calling": self.supports_function_calling,
        }


@dataclass
class ModelMetadata:
    """Enhanced model information."""
    id: str
    name: str
    description: str = ""
    provider: str = ""
    parameters: Optional[str] = None
    context_window: Optional[int] = None
    license: Optional[str] = None
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"
    release_date: Optional[str] = None
    capabilities: ModelCapability = field(default_factory=ModelCapability)
    pricing: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "parameters": self.parameters,
            "context_window": self.context_window,
            "license": self.license,
            "category": self.category,
            "tags": self.tags,
            "version": self.version,
            "release_date": self.release_date,
            "capabilities": self.capabilities.to_dict(),
            "pricing": self.pricing,
            "performance": self.performance,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        capabilities = data.get("capabilities", {})
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            provider=data.get("provider", ""),
            parameters=data.get("parameters"),
            context_window=data.get("context_window"),
            license=data.get("license"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            version=data.get("version", "1.0"),
            release_date=data.get("release_date"),
            capabilities=ModelCapability(**capabilities) if capabilities else ModelCapability(),
            pricing=data.get("pricing"),
            performance=data.get("performance"),
        )


@dataclass
class ProviderMetadata:
    """Enhanced provider information."""
    name: str
    category: ProviderCategory
    provider_type: ProviderType = ProviderType.CLOUD
    base_url: Optional[str] = None
    api_key_env_var: Optional[str] = None
    rate_limits: RateLimit = field(default_factory=RateLimit)
    requires_auth: bool = True
    requires_phone_verification: bool = False
    data_training_opt_out_available: bool = False
    commercial_usage_allowed: bool = True
    region: str = "global"
    models: List[ModelMetadata] = field(default_factory=list)
    status: ProviderStatus = ProviderStatus.AVAILABLE
    last_checked: Optional[datetime] = None
    response_time_avg: Optional[float] = None
    success_rate: Optional[float] = None
    error_rate: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "provider_type": self.provider_type.value,
            "base_url": self.base_url,
            "api_key_env_var": self.api_key_env_var,
            "rate_limits": self.rate_limits.to_dict(),
            "requires_auth": self.requires_auth,
            "requires_phone_verification": self.requires_phone_verification,
            "data_training_opt_out_available": self.data_training_opt_out_available,
            "commercial_usage_allowed": self.commercial_usage_allowed,
            "region": self.region,
            "models": [model.to_dict() for model in self.models],
            "status": self.status.value,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "response_time_avg": self.response_time_avg,
            "success_rate": self.success_rate,
            "error_rate": self.error_rate,
            "tags": self.tags,
            "documentation_url": self.documentation_url,
            "support_url": self.support_url,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderMetadata":
        models = [ModelMetadata.from_dict(m) for m in data.get("models", [])]
        rate_limits = RateLimit.from_dict(data.get("rate_limits", {}))
        return cls(
            name=data.get("name", ""),
            category=ProviderCategory(data.get("category", "llm")),
            provider_type=ProviderType(data.get("provider_type", "cloud")),
            base_url=data.get("base_url"),
            api_key_env_var=data.get("api_key_env_var"),
            rate_limits=rate_limits,
            requires_auth=data.get("requires_auth", True),
            requires_phone_verification=data.get("requires_phone_verification", False),
            data_training_opt_out_available=data.get("data_training_opt_out_available", False),
            commercial_usage_allowed=data.get("commercial_usage_allowed", True),
            region=data.get("region", "global"),
            models=models,
            status=ProviderStatus(data.get("status", "available")),
            last_checked=datetime.fromisoformat(data.get("last_checked")) if data.get("last_checked") else None,
            response_time_avg=data.get("response_time_avg"),
            success_rate=data.get("success_rate"),
            error_rate=data.get("error_rate"),
            tags=data.get("tags", []),
            documentation_url=data.get("documentation_url"),
            support_url=data.get("support_url"),
        )


@dataclass
class UsageStats:
    """Usage statistics for a provider or model."""
    provider: str
    model: Optional[str] = None
    requests_count: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    total_latency_ms: float = 0.0
    last_request_time: Optional[datetime] = None
    first_request_time: Optional[datetime] = None
    
    @property
    def avg_latency_ms(self) -> float:
        if self.requests_successful == 0:
            return 0.0
        return self.total_latency_ms / self.requests_successful
    
    @property
    def success_rate(self) -> float:
        total = self.requests_successful + self.requests_failed
        if total == 0:
            return 1.0
        return self.requests_successful / total
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "requests_count": self.requests_count,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "requests_successful": self.requests_successful,
            "requests_failed": self.requests_failed,
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_ms": self.avg_latency_ms,
            "success_rate": self.success_rate,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
            "first_request_time": self.first_request_time.isoformat() if self.first_request_time else None,
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for providers."""
    provider: str
    model: Optional[str] = None
    latency_ms: List[float] = field(default_factory=list)
    throughput: List[float] = field(default_factory=list)
    quality_scores: List[float] = field(default_factory=list)
    cost_per_request: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    
    def add_metric(
        self,
        latency_ms: Optional[float] = None,
        throughput: Optional[float] = None,
        quality_score: Optional[float] = None,
        cost: Optional[float] = None,
    ):
        timestamp = datetime.now()
        if latency_ms is not None:
            self.latency_ms.append(latency_ms)
        if throughput is not None:
            self.throughput.append(throughput)
        if quality_score is not None:
            self.quality_scores.append(quality_score)
        if cost is not None:
            self.cost_per_request.append(cost)
        self.timestamps.append(timestamp)
    
    @property
    def avg_latency(self) -> float:
        return sum(self.latency_ms) / len(self.latency_ms) if self.latency_ms else 0.0
    
    @property
    def avg_quality(self) -> float:
        return sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "avg_latency_ms": self.avg_latency,
            "avg_quality": self.avg_quality,
            "metrics_count": len(self.latency_ms),
        }


@dataclass
class HealthStatus:
    """Health status of a provider."""
    provider: str
    status: ProviderStatus = ProviderStatus.AVAILABLE
    last_check: datetime = field(default_factory=datetime.now)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "consecutive_failures": self.consecutive_failures,
            "response_time": self.response_time,
            "error_message": self.error_message,
        }


@dataclass
class CacheEntry:
    """Cache entry for responses, embeddings, or images."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    ttl: Optional[float] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now() > self.expires_at
        if self.ttl:
            return (datetime.now() - self.created_at).total_seconds() > self.ttl
        return False
    
    @classmethod
    def generate_key(
        cls,
        provider: str,
        model: str,
        prompt: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a cache key from request parameters."""
        key_data = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "params": params or {},
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()


@dataclass
class RequestContext:
    """Context for a request to a provider."""
    provider: str
    model: str
    request_id: str = field(default_factory=lambda: f"req_{datetime.now().timestamp()}_{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]}")
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "start_time": self.start_time.isoformat(),
        }


@dataclass
class ResponseResult:
    """Result of a provider request."""
    request_context: RequestContext
    content: Any
    provider: str
    model: str
    latency_ms: float
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    cached: bool = False
    finish_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_context.request_id,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "success": self.success,
            "error": self.error,
            "cached": self.cached,
            "finish_time": self.finish_time.isoformat(),
        }
