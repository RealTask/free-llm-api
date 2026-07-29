"""
Rate Limiter

Rate limiting utilities for API providers.
"""

import time
import asyncio
from typing import Optional, Callable, Any, List, Dict
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: Optional[float] = None
    requests_per_minute: Optional[float] = None
    requests_per_hour: Optional[float] = None
    requests_per_day: Optional[float] = None
    tokens_per_second: Optional[float] = None
    tokens_per_minute: Optional[float] = None
    tokens_per_hour: Optional[float] = None
    tokens_per_day: Optional[float] = None
    burst_limit: Optional[int] = None
    buffer: float = 0.1  # Use 10% buffer below limits
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "requests_per_day": self.requests_per_day,
            "tokens_per_second": self.tokens_per_second,
            "tokens_per_minute": self.tokens_per_minute,
            "tokens_per_hour": self.tokens_per_hour,
            "tokens_per_day": self.tokens_per_day,
            "burst_limit": self.burst_limit,
            "buffer": self.buffer,
        }


class RateLimiter:
    """
    Simple rate limiter that tracks request counts over time periods.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize the rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self._request_times: deque = deque()
        self._token_counts: deque = deque()
        self._last_check: float = time.time()
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, request_type: str = "request", count: int = 1) -> bool:
        """
        Check if a request would exceed rate limits.
        
        Args:
            request_type: Type of request ('request' or 'token')
            count: Number of requests/tokens
            
        Returns:
            bool: True if within rate limits, False otherwise
        """
        async with self._lock:
            current_time = time.time()
            
            # Clean up old entries
            self._cleanup_old_entries(current_time)
            
            # Check different time periods
            if request_type == "request":
                if self.config.requests_per_second is not None:
                    if not self._check_limit(
                        self._request_times, 
                        current_time, 
                        self.config.requests_per_second, 
                        1.0, 
                        count
                    ):
                        return False
                
                if self.config.requests_per_minute is not None:
                    if not self._check_limit(
                        self._request_times, 
                        current_time, 
                        self.config.requests_per_minute, 
                        60.0, 
                        count
                    ):
                        return False
                
                if self.config.requests_per_hour is not None:
                    if not self._check_limit(
                        self._request_times, 
                        current_time, 
                        self.config.requests_per_hour, 
                        3600.0, 
                        count
                    ):
                        return False
                
                if self.config.requests_per_day is not None:
                    if not self._check_limit(
                        self._request_times, 
                        current_time, 
                        self.config.requests_per_day, 
                        86400.0, 
                        count
                    ):
                        return False
            
            elif request_type == "token":
                if self.config.tokens_per_second is not None:
                    if not self._check_limit(
                        self._token_counts, 
                        current_time, 
                        self.config.tokens_per_second, 
                        1.0, 
                        count
                    ):
                        return False
                
                if self.config.tokens_per_minute is not None:
                    if not self._check_limit(
                        self._token_counts, 
                        current_time, 
                        self.config.tokens_per_minute, 
                        60.0, 
                        count
                    ):
                        return False
                
                if self.config.tokens_per_hour is not None:
                    if not self._check_limit(
                        self._token_counts, 
                        current_time, 
                        self.config.tokens_per_hour, 
                        3600.0, 
                        count
                    ):
                        return False
                
                if self.config.tokens_per_day is not None:
                    if not self._check_limit(
                        self._token_counts, 
                        current_time, 
                        self.config.tokens_per_day, 
                        86400.0, 
                        count
                    ):
                        return False
            
            # Check burst limit
            if self.config.burst_limit is not None:
                if len(self._request_times) >= self.config.burst_limit:
                    return False
            
            return True
    
    def _check_limit(
        self, 
        queue: deque, 
        current_time: float, 
        limit: float, 
        period: float, 
        count: int
    ) -> bool:
        """Check if a specific limit would be exceeded."""
        # Apply buffer
        effective_limit = limit * (1 - self.config.buffer)
        
        # Count recent requests within the period
        recent_count = 0
        for timestamp in queue:
            if current_time - timestamp <= period:
                recent_count += 1
        
        # Check if adding the new requests would exceed the limit
        return (recent_count + count) <= effective_limit
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries from the queues."""
        # Clean up request times older than 24 hours
        while self._request_times and (current_time - self._request_times[0]) > 86400:
            self._request_times.popleft()
        
        # Clean up token counts older than 24 hours
        while self._token_counts and (current_time - self._token_counts[0][0]) > 86400:
            self._token_counts.popleft()
    
    async def record_request(self, request_type: str = "request", count: int = 1):
        """
        Record a request or token usage.
        
        Args:
            request_type: Type of request ('request' or 'token')
            count: Number of requests/tokens
        """
        async with self._lock:
            current_time = time.time()
            
            if request_type == "request":
                for _ in range(count):
                    self._request_times.append(current_time)
            else:
                for _ in range(count):
                    self._token_counts.append((current_time, count))
    
    async def wait_for_rate_limit(self, request_type: str = "request", count: int = 1):
        """
        Wait until rate limit allows the request.
        
        Args:
            request_type: Type of request ('request' or 'token')
            count: Number of requests/tokens
        """
        while not await self.check_rate_limit(request_type, count):
            await asyncio.sleep(0.1)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for more sophisticated rate limiting.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the token bucket rate limiter.
        
        Args:
            rate: Tokens per second
            capacity: Maximum bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            bool: True if tokens were consumed, False if rate limited
        """
        async with self._lock:
            current_time = time.time()
            
            # Add tokens based on elapsed time
            elapsed = current_time - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = current_time
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_and_consume(self, tokens: int = 1):
        """
        Wait until tokens are available and consume them.
        
        Args:
            tokens: Number of tokens to consume
        """
        while not await self.consume(tokens):
            await asyncio.sleep(0.01)
    
    def get_available_tokens(self) -> float:
        """Get the current number of available tokens."""
        current_time = time.time()
        elapsed = current_time - self.last_update
        tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        return tokens


class MultiRateLimiter:
    """
    Rate limiter that supports multiple rate limits.
    """
    
    def __init__(self, configs: Optional[List[RateLimitConfig]] = None):
        """
        Initialize the multi-rate limiter.
        
        Args:
            configs: List of rate limit configurations
        """
        self.limiters = []
        if configs:
            for config in configs:
                self.limiters.append(RateLimiter(config))
    
    async def check_rate_limit(self, request_type: str = "request", count: int = 1) -> bool:
        """
        Check all rate limits.
        
        Args:
            request_type: Type of request ('request' or 'token')
            count: Number of requests/tokens
            
        Returns:
            bool: True if all rate limits allow the request
        """
        results = []
        for limiter in self.limiters:
            results.append(await limiter.check_rate_limit(request_type, count))
        return all(results)
    
    async def record_request(self, request_type: str = "request", count: int = 1):
        """
        Record a request for all limiters.
        
        Args:
            request_type: Type of request ('request' or 'token')
            count: Number of requests/tokens
        """
        for limiter in self.limiters:
            await limiter.record_request(request_type, count)