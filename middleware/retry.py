"""
Retry Logic Module

Advanced retry logic with exponential backoff.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [Exception])
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


class AdvancedRetry:
    """Advanced retry mechanism with exponential backoff."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self._retry_counts: Dict[str, int] = {}
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number."""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                should_retry = any(
                    isinstance(e, exc_type) 
                    for exc_type in self.config.retry_on_exceptions
                )
                
                if not should_retry or attempt == self.config.max_retries:
                    raise
                
                delay = self.calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)
        
        raise last_exception


async def retry_with_advanced_backoff(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """Convenience function for retrying with advanced backoff."""
    retry = AdvancedRetry(config)
    return await retry.execute_with_retry(func, *args, **kwargs)
