"""
Middleware Package

Middleware for the free LLM API providers.
Includes rate limiting, retry logic, authentication, and request processing.
"""

from .rate_limiting import (
    AdvancedRateLimiter,
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
    RateLimitConfig,
)
from .retry import (
    AdvancedRetry,
    RetryConfig,
    retry_with_advanced_backoff,
)
from .authentication import (
    APIKeyManager,
    APIKeyValidator,
    TokenManager,
)
from .request_processing import (
    RequestProcessor,
    ResponseProcessor,
    ErrorHandler,
)
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig

__all__ = [
    # Rate Limiting
    "AdvancedRateLimiter",
    "TokenBucketRateLimiter",
    "SlidingWindowRateLimiter",
    "RateLimitConfig",
    
    # Retry
    "AdvancedRetry",
    "RetryConfig",
    "retry_with_advanced_backoff",
    
    # Authentication
    "APIKeyManager",
    "APIKeyValidator",
    "TokenManager",
    
    # Request Processing
    "RequestProcessor",
    "ResponseProcessor",
    "ErrorHandler",
    
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
]
