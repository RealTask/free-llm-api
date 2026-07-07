"""
Advanced Rate Limiting

Enhanced rate limiting with multiple algorithms and strategies.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from collections import deque
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Request-based limits
    requests_per_second: Optional[int] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    
    # Token-based limits
    tokens_per_second: Optional[int] = None
    tokens_per_minute: Optional[int] = None
    tokens_per_hour: Optional[int] = None
    tokens_per_day: Optional[int] = None
    
    # Other limits
    concurrent_requests: Optional[int] = None
    burst_limit: Optional[int] = None
    
    # Behavior
    block_on_limit: bool = True
    wait_on_limit: bool = False
    max_wait_time: float = 60.0  # seconds
    
    # Notifications
    on_limit_reached: Optional[Callable[[str], None]] = None
    on_limit_reset: Optional[Callable[[str], None]] = None
    
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
            "block_on_limit": self.block_on_limit,
            "wait_on_limit": self.wait_on_limit,
            "max_wait_time": self.max_wait_time,
        }


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.
    
    Allows bursting up to a maximum capacity, then refills at a fixed rate.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._tokens: float = float(config.burst_limit or config.requests_per_minute or 100)
        self._max_tokens: float = self._tokens
        self._last_refill: float = time.time()
        self._refill_rate: float = 0.0
        
        if config.requests_per_second:
            self._refill_rate = config.requests_per_second
        elif config.requests_per_minute:
            self._refill_rate = config.requests_per_minute / 60.0
        elif config.requests_per_hour:
            self._refill_rate = config.requests_per_hour / 3600.0
        
        self._lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        
        if elapsed > 0:
            self._tokens = min(
                self._max_tokens,
                self._tokens + elapsed * self._refill_rate
            )
            self._last_refill = now
    
    def check(self, tokens: int = 1) -> bool:
        """
        Check if tokens are available.
        
        Args:
            tokens: Number of tokens to check
            
        Returns:
            bool: True if tokens are available
        """
        with self._lock:
            self._refill()
            return self._tokens >= tokens
    
    def acquire(self, tokens: int = 1, wait: bool = False) -> bool:
        """
        Acquire tokens.
        
        Args:
            tokens: Number of tokens to acquire
            wait: Whether to wait if tokens are not available
            
        Returns:
            bool: True if tokens were acquired
        """
        with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            
            if wait and self.config.wait_on_limit:
                # Calculate wait time
                needed = tokens - self._tokens
                wait_time = needed / self._refill_rate if self._refill_rate > 0 else float('inf')
                
                if wait_time <= self.config.max_wait_time:
                    time.sleep(wait_time)
                    self._tokens = max(0, self._tokens - tokens)
                    return True
            
            if self.config.on_limit_reached:
                self.config.on_limit_reached("token_bucket")
            
            return False
    
    def release(self, tokens: int = 1):
        """Release tokens back to the bucket."""
        with self._lock:
            self._tokens = min(self._max_tokens, self._tokens + tokens)
    
    def reset(self):
        """Reset the rate limiter."""
        with self._lock:
            self._tokens = self._max_tokens
            self._last_refill = time.time()
    
    @property
    def available_tokens(self) -> float:
        """Get available tokens."""
        with self._lock:
            self._refill()
            return self._tokens
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        with self._lock:
            self._refill()
            return {
                "type": "token_bucket",
                "available_tokens": self._tokens,
                "max_tokens": self._max_tokens,
                "refill_rate": self._refill_rate,
                "last_refill": self._last_refill,
            }


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter.
    
    Tracks requests in a sliding time window for more accurate rate limiting.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests: deque = deque()
        self._tokens_used: deque = deque()
        self._lock = threading.Lock()
        
        # Set window size based on config
        self._window_size = 1.0  # seconds
        if config.requests_per_second:
            self._window_size = 1.0
            self._max_requests = config.requests_per_second
        elif config.requests_per_minute:
            self._window_size = 60.0
            self._max_requests = config.requests_per_minute
        elif config.requests_per_hour:
            self._window_size = 3600.0
            self._max_requests = config.requests_per_hour
        else:
            self._max_requests = 100
    
    def _cleanup(self):
        """Remove old requests from the window."""
        now = time.time()
        while self._requests and now - self._requests[0] > self._window_size:
            self._requests.popleft()
        
        while self._tokens_used and now - self._tokens_used[0][0] > self._window_size:
            self._tokens_used.popleft()
    
    def check(self, tokens: int = 1) -> bool:
        """
        Check if a request can be made.
        
        Args:
            tokens: Number of tokens for the request
            
        Returns:
            bool: True if request is allowed
        """
        with self._lock:
            self._cleanup()
            
            # Check request count
            if len(self._requests) >= self._max_requests:
                if self.config.on_limit_reached:
                    self.config.on_limit_reached("sliding_window_requests")
                return False
            
            # Check token count
            total_tokens = sum(t for _, t in self._tokens_used)
            if self.config.tokens_per_minute:
                max_tokens = self.config.tokens_per_minute * (self._window_size / 60.0)
                if total_tokens + tokens > max_tokens:
                    if self.config.on_limit_reached:
                        self.config.on_limit_reached("sliding_window_tokens")
                    return False
            
            return True
    
    def acquire(self, tokens: int = 1, wait: bool = False) -> bool:
        """
        Acquire permission for a request.
        
        Args:
            tokens: Number of tokens for the request
            wait: Whether to wait if limit is reached
            
        Returns:
            bool: True if permission was acquired
        """
        with self._lock:
            self._cleanup()
            
            # Check limits
            if len(self._requests) >= self._max_requests:
                if wait and self.config.wait_on_limit:
                    # Calculate wait time (simplified)
                    if self._requests:
                        oldest = self._requests[0]
                        wait_time = (oldest + self._window_size) - time.time()
                        if wait_time > 0 and wait_time <= self.config.max_wait_time:
                            time.sleep(wait_time)
                            self._cleanup()
                else:
                    if self.config.on_limit_reached:
                        self.config.on_limit_reached("sliding_window_requests")
                    return False
            
            # Check token limit
            total_tokens = sum(t for _, t in self._tokens_used)
            if self.config.tokens_per_minute:
                max_tokens = self.config.tokens_per_minute * (self._window_size / 60.0)
                if total_tokens + tokens > max_tokens:
                    if wait and self.config.wait_on_limit:
                        # Simplified wait calculation
                        time.sleep(1.0)
                        self._cleanup()
                    else:
                        if self.config.on_limit_reached:
                            self.config.on_limit_reached("sliding_window_tokens")
                        return False
            
            # Record request
            now = time.time()
            self._requests.append(now)
            self._tokens_used.append((now, tokens))
            
            return True
    
    def reset(self):
        """Reset the rate limiter."""
        with self._lock:
            self._requests.clear()
            self._tokens_used.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        with self._lock:
            self._cleanup()
            total_tokens = sum(t for _, t in self._tokens_used)
            return {
                "type": "sliding_window",
                "window_size": self._window_size,
                "requests_in_window": len(self._requests),
                "max_requests": self._max_requests,
                "tokens_in_window": total_tokens,
            }


class AdvancedRateLimiter:
    """
    Advanced rate limiter combining multiple strategies.
    
    Supports token bucket, sliding window, and fixed window algorithms.
    Can be used for both request-based and token-based rate limiting.
    """
    
    def __init__(
        self,
        config: Optional[RateLimitConfig] = None,
        name: str = "default",
    ):
        self.config = config or RateLimitConfig()
        self.name = name
        self._limiters: List[Union[TokenBucketRateLimiter, SlidingWindowRateLimiter]] = []
        self._concurrent_requests: int = 0
        self._max_concurrent: int = self.config.concurrent_requests or 100
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        
        # Create appropriate limiters
        self._init_limiters()
    
    def _init_limiters(self):
        """Initialize the appropriate rate limiters."""
        # Token bucket for burst limiting
        if self.config.burst_limit or self.config.requests_per_second:
            self._limiters.append(TokenBucketRateLimiter(self.config))
        
        # Sliding window for accurate rate limiting
        if (self.config.requests_per_minute or 
            self.config.requests_per_hour or 
            self.config.tokens_per_minute):
            self._limiters.append(SlidingWindowRateLimiter(self.config))
    
    def check(self, tokens: int = 1) -> bool:
        """
        Check if a request can be made.
        
        Args:
            tokens: Number of tokens for the request
            
        Returns:
            bool: True if request is allowed
        """
        # Check concurrent requests
        with self._lock:
            if self._concurrent_requests >= self._max_concurrent:
                if self.config.on_limit_reached:
                    self.config.on_limit_reached("concurrent_requests")
                return False
        
        # Check all limiters
        for limiter in self._limiters:
            if not limiter.check(tokens):
                return False
        
        return True
    
    async def check_async(self, tokens: int = 1) -> bool:
        """
        Async version of check.
        
        Args:
            tokens: Number of tokens for the request
            
        Returns:
            bool: True if request is allowed
        """
        # Check concurrent requests
        async with self._async_lock:
            if self._concurrent_requests >= self._max_concurrent:
                if self.config.on_limit_reached:
                    self.config.on_limit_reached("concurrent_requests")
                return False
        
        # Check all limiters
        for limiter in self._limiters:
            if not limiter.check(tokens):
                return False
        
        return True
    
    def acquire(self, tokens: int = 1, wait: bool = False) -> bool:
        """
        Acquire permission for a request.
        
        Args:
            tokens: Number of tokens for the request
            wait: Whether to wait if limit is reached
            
        Returns:
            bool: True if permission was acquired
        """
        # Check concurrent requests
        with self._lock:
            if self._concurrent_requests >= self._max_concurrent:
                if wait and self.config.wait_on_limit:
                    # Wait for a slot to become available
                    start = time.time()
                    while (self._concurrent_requests >= self._max_concurrent and 
                           time.time() - start < self.config.max_wait_time):
                        time.sleep(0.1)
                    
                    if self._concurrent_requests >= self._max_concurrent:
                        if self.config.on_limit_reached:
                            self.config.on_limit_reached("concurrent_requests")
                        return False
                else:
                    if self.config.on_limit_reached:
                        self.config.on_limit_reached("concurrent_requests")
                    return False
            
            self._concurrent_requests += 1
        
        # Acquire from all limiters
        for limiter in self._limiters:
            if not limiter.acquire(tokens, wait):
                with self._lock:
                    self._concurrent_requests -= 1
                return False
        
        return True
    
    async def acquire_async(self, tokens: int = 1, wait: bool = False) -> bool:
        """
        Async version of acquire.
        
        Args:
            tokens: Number of tokens for the request
            wait: Whether to wait if limit is reached
            
        Returns:
            bool: True if permission was acquired
        """
        # Check concurrent requests
        async with self._async_lock:
            if self._concurrent_requests >= self._max_concurrent:
                if wait and self.config.wait_on_limit:
                    # Wait for a slot to become available
                    start = time.time()
                    while (self._concurrent_requests >= self._max_concurrent and 
                           time.time() - start < self.config.max_wait_time):
                        await asyncio.sleep(0.1)
                    
                    if self._concurrent_requests >= self._max_concurrent:
                        if self.config.on_limit_reached:
                            self.config.on_limit_reached("concurrent_requests")
                        return False
                else:
                    if self.config.on_limit_reached:
                        self.config.on_limit_reached("concurrent_requests")
                    return False
            
            self._concurrent_requests += 1
        
        # Acquire from all limiters
        for limiter in self._limiters:
            if not limiter.acquire(tokens, wait):
                async with self._async_lock:
                    self._concurrent_requests -= 1
                return False
        
        return True
    
    def release(self, tokens: int = 1):
        """
        Release permission after a request completes.
        
        Args:
            tokens: Number of tokens used
        """
        with self._lock:
            self._concurrent_requests = max(0, self._concurrent_requests - 1)
        
        for limiter in self._limiters:
            if isinstance(limiter, TokenBucketRateLimiter):
                limiter.release(tokens)
    
    async def release_async(self, tokens: int = 1):
        """
        Async version of release.
        
        Args:
            tokens: Number of tokens used
        """
        async with self._async_lock:
            self._concurrent_requests = max(0, self._concurrent_requests - 1)
        
        for limiter in self._limiters:
            if isinstance(limiter, TokenBucketRateLimiter):
                limiter.release(tokens)
    
    def reset(self):
        """Reset all rate limiters."""
        with self._lock:
            self._concurrent_requests = 0
        
        for limiter in self._limiters:
            limiter.reset()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        result = {
            "name": self.name,
            "concurrent_requests": self._concurrent_requests,
            "max_concurrent": self._max_concurrent,
            "limiters": [limiter.stats for limiter in self._limiters],
        }
        return result
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.acquire_async()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release_async()


class RateLimiterFactory:
    """Factory for creating rate limiters."""
    
    @staticmethod
    def create(
        config: RateLimitConfig,
        limiter_type: str = "advanced",
        name: str = "default",
    ) -> AdvancedRateLimiter:
        """
        Create a rate limiter.
        
        Args:
            config: Rate limit configuration
            limiter_type: Type of limiter (advanced, token_bucket, sliding_window)
            name: Name for the limiter
            
        Returns:
            AdvancedRateLimiter: Rate limiter instance
        """
        if limiter_type == "token_bucket":
            limiter = AdvancedRateLimiter(config, name)
            limiter._limiters = [TokenBucketRateLimiter(config)]
            return limiter
        elif limiter_type == "sliding_window":
            limiter = AdvancedRateLimiter(config, name)
            limiter._limiters = [SlidingWindowRateLimiter(config)]
            return limiter
        else:
            return AdvancedRateLimiter(config, name)
