"""
Caching Layer

Advanced caching for responses, embeddings, and images.
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import shelve
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta

from .models import CacheEntry, RequestContext

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for caching."""
    enabled: bool = True
    default_ttl: float = 3600.0  # 1 hour in seconds
    max_size: int = 10000  # Maximum number of entries
    cache_type: str = "memory"  # memory, disk, redis
    cache_dir: str = ".cache/free_llm_api"
    redis_url: Optional[str] = None
    compress: bool = True
    encrypt: bool = False
    encryption_key: Optional[str] = None
    
    # Separate TTLs for different types
    response_ttl: float = 3600.0
    embedding_ttl: float = 86400.0  # 24 hours
    image_ttl: float = 86400.0
    
    # Size limits
    max_response_size: int = 100000  # 100KB
    max_embedding_size: int = 10000  # 10KB
    max_image_size: int = 1000000  # 1MB


class BaseCache:
    """Base cache class."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
            "size": self.size,
        }
    
    @property
    def size(self) -> int:
        """Get current cache size."""
        return 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        raise NotImplementedError
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Set a value in cache."""
        raise NotImplementedError
    
    async def delete(self, key: str):
        """Delete a value from cache."""
        raise NotImplementedError
    
    async def clear(self):
        """Clear the cache."""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        raise NotImplementedError
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        results = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        return results
    
    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[float] = None,
    ):
        """Set multiple values in cache."""
        for key, value in items.items():
            await self.set(key, value, ttl)
    
    def _increment_hits(self):
        self._hits += 1
    
    def _increment_misses(self):
        self._misses += 1
    
    def _increment_evictions(self):
        self._evictions += 1


class MemoryCache(BaseCache):
    """In-memory cache implementation."""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
    
    @property
    def size(self) -> int:
        return len(self._cache)
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._increment_misses()
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._increment_misses()
                return None
            
            self._increment_hits()
            return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        async with self._lock:
            # Check size limit
            if len(self._cache) >= self.config.max_size:
                # Evict oldest entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at.timestamp())
                del self._cache[oldest_key]
                self._increment_evictions()
            
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.config.default_ttl,
                metadata=metadata or {},
            )
            self._cache[key] = entry
    
    async def delete(self, key: str):
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    async def clear(self):
        async with self._lock:
            self._cache.clear()
    
    async def exists(self, key: str) -> bool:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            return not entry.is_expired()
    
    def cleanup_expired(self):
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)


class DiskCache(BaseCache):
    """Disk-based cache implementation."""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache_dir = Path(config.cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
    
    @property
    def size(self) -> int:
        return len(list(self._cache_dir.glob("*.cache")))
    
    def _get_cache_path(self, key: str) -> Path:
        # Use first 2 characters as subdirectory for better organization
        subdir = key[:2]
        return self._cache_dir / subdir / f"{key}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            self._increment_misses()
            return None
        
        try:
            with open(cache_path, "rb") as f:
                entry = pickle.load(f)
            
            if entry.is_expired():
                await self.delete(key)
                self._increment_misses()
                return None
            
            self._increment_hits()
            return entry.value
            
        except Exception as e:
            logger.error(f"Error reading cache file {cache_path}: {e}")
            self._increment_misses()
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        cache_path = self._get_cache_path(key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl or self.config.default_ttl,
            metadata=metadata or {},
        )
        
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.error(f"Error writing cache file {cache_path}: {e}")
    
    async def delete(self, key: str):
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    async def clear(self):
        import shutil
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def exists(self, key: str) -> bool:
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, "rb") as f:
                entry = pickle.load(f)
            return not entry.is_expired()
        except Exception:
            return False


class ResponseCache:
    """Cache for LLM responses."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: BaseCache = self._create_cache(config)
    
    def _create_cache(self, config: CacheConfig) -> BaseCache:
        """Create the appropriate cache implementation."""
        if config.cache_type == "redis":
            try:
                return RedisCache(config)
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}, falling back to memory cache")
        elif config.cache_type == "disk":
            return DiskCache(config)
        else:
            return MemoryCache(config)
    
    def generate_key(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a cache key for a response."""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        key_data = {
            "provider": provider,
            "model": model,
            "messages": messages,
            "params": params or {},
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Get a cached response."""
        if not self.config.enabled:
            return None
        
        key = self.generate_key(provider, model, messages, params)
        return await self._cache.get(key)
    
    async def set(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        response: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache a response."""
        if not self.config.enabled:
            return
        
        key = self.generate_key(provider, model, messages, params)
        
        # Check size limit
        if len(response) > self.config.max_response_size:
            logger.warning(f"Response too large to cache: {len(response)} bytes")
            return
        
        await self._cache.set(
            key,
            response,
            ttl=self.config.response_ttl,
            metadata={
                "provider": provider,
                "model": model,
                "type": "response",
                "timestamp": datetime.now().isoformat(),
            },
        )
    
    async def delete(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        params: Optional[Dict[str, Any]] = None,
    ):
        """Delete a cached response."""
        key = self.generate_key(provider, model, messages, params)
        await self._cache.delete(key)
    
    async def clear(self):
        """Clear the response cache."""
        await self._cache.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats


class EmbeddingCache:
    """Cache for embeddings."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: BaseCache = self._create_cache(config)
    
    def _create_cache(self, config: CacheConfig) -> BaseCache:
        """Create the appropriate cache implementation."""
        if config.cache_type == "redis":
            try:
                return RedisCache(config)
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}, falling back to memory cache")
        elif config.cache_type == "disk":
            return DiskCache(config)
        else:
            return MemoryCache(config)
    
    def generate_key(
        self,
        provider: str,
        model: str,
        text: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a cache key for an embedding."""
        key_data = {
            "provider": provider,
            "model": model,
            "text": text,
            "params": params or {},
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(
        self,
        provider: str,
        model: str,
        text: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[float]]:
        """Get a cached embedding."""
        if not self.config.enabled:
            return None
        
        key = self.generate_key(provider, model, text, params)
        return await self._cache.get(key)
    
    async def set(
        self,
        provider: str,
        model: str,
        text: str,
        embedding: List[float],
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache an embedding."""
        if not self.config.enabled:
            return
        
        key = self.generate_key(provider, model, text, params)
        
        # Check size limit
        import sys
        size = sys.getsizeof(embedding)
        if size > self.config.max_embedding_size:
            logger.warning(f"Embedding too large to cache: {size} bytes")
            return
        
        await self._cache.set(
            key,
            embedding,
            ttl=self.config.embedding_ttl,
            metadata={
                "provider": provider,
                "model": model,
                "type": "embedding",
                "timestamp": datetime.now().isoformat(),
            },
        )
    
    async def get_batch(
        self,
        provider: str,
        model: str,
        texts: List[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[int, Optional[List[float]]]:
        """Get multiple cached embeddings."""
        keys = [self.generate_key(provider, model, text, params) for text in texts]
        cached = await self._cache.get_many(keys)
        
        result = {}
        for i, key in enumerate(keys):
            result[i] = cached.get(key)
        return result
    
    async def set_batch(
        self,
        provider: str,
        model: str,
        texts: List[str],
        embeddings: List[List[float]],
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache multiple embeddings."""
        for text, embedding in zip(texts, embeddings):
            await self.set(provider, model, text, embedding, params)
    
    async def clear(self):
        """Clear the embedding cache."""
        await self._cache.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats


class ImageCache:
    """Cache for generated images."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: BaseCache = self._create_cache(config)
    
    def _create_cache(self, config: CacheConfig) -> BaseCache:
        """Create the appropriate cache implementation."""
        if config.cache_type == "redis":
            try:
                return RedisCache(config)
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}, falling back to disk cache")
        elif config.cache_type == "disk":
            return DiskCache(config)
        else:
            # Use disk cache for images (they can be large)
            return DiskCache(config)
    
    def generate_key(
        self,
        provider: str,
        model: str,
        prompt: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a cache key for an image."""
        key_data = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "params": params or {},
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(
        self,
        provider: str,
        model: str,
        prompt: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[bytes]:
        """Get a cached image."""
        if not self.config.enabled:
            return None
        
        key = self.generate_key(provider, model, prompt, params)
        return await self._cache.get(key)
    
    async def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        image_data: bytes,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache an image."""
        if not self.config.enabled:
            return
        
        key = self.generate_key(provider, model, prompt, params)
        
        # Check size limit
        if len(image_data) > self.config.max_image_size:
            logger.warning(f"Image too large to cache: {len(image_data)} bytes")
            return
        
        await self._cache.set(
            key,
            image_data,
            ttl=self.config.image_ttl,
            metadata={
                "provider": provider,
                "model": model,
                "type": "image",
                "size": len(image_data),
                "timestamp": datetime.now().isoformat(),
            },
        )
    
    async def clear(self):
        """Clear the image cache."""
        await self._cache.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats


class MultiLevelCache:
    """Multi-level cache with fallback."""
    
    def __init__(self, configs: List[CacheConfig]):
        self.caches = [
            ResponseCache(config) for config in configs
        ]
    
    async def get(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Get from caches in order."""
        for cache in self.caches:
            result = await cache.get(provider, model, messages, params)
            if result is not None:
                return result
        return None
    
    async def set(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        response: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Set in all caches."""
        for cache in self.caches:
            await cache.set(provider, model, messages, response, params)
    
    async def clear(self):
        """Clear all caches."""
        for cache in self.caches:
            await cache.clear()


# Try to import redis for RedisCache
try:
    import redis.asyncio as redis
    
    class RedisCache(BaseCache):
        """Redis-based cache implementation."""
        
        def __init__(self, config: CacheConfig):
            super().__init__(config)
            self._redis = redis.from_url(config.redis_url or "redis://localhost:6379")
        
        @property
        def size(self) -> int:
            # This is approximate
            return self._redis.dbsize()
        
        async def get(self, key: str) -> Optional[Any]:
            data = await self._redis.get(f"cache:{key}")
            if data is None:
                self._increment_misses()
                return None
            
            try:
                entry = pickle.loads(data)
                if entry.is_expired():
                    await self.delete(key)
                    self._increment_misses()
                    return None
                
                self._increment_hits()
                return entry.value
            except Exception as e:
                logger.error(f"Error deserializing cache entry: {e}")
                self._increment_misses()
                return None
        
        async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ):
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.config.default_ttl,
                metadata=metadata or {},
            )
            
            data = pickle.dumps(entry)
            
            if ttl:
                await self._redis.setex(
                    f"cache:{key}",
                    int(ttl),
                    data
                )
            else:
                await self._redis.set(f"cache:{key}", data)
        
        async def delete(self, key: str):
            await self._redis.delete(f"cache:{key}")
        
        async def clear(self):
            # Clear all cache keys
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match="cache:*")
                if not keys:
                    break
                await self._redis.delete(*keys)
        
        async def exists(self, key: str) -> bool:
            return await self._redis.exists(f"cache:{key}")
        
        async def get_many(self, keys: List[str]) -> Dict[str, Any]:
            results = {}
            for key in keys:
                value = await self.get(key)
                if value is not None:
                    results[key] = value
            return results
        
        async def close(self):
            await self._redis.close()
    
except ImportError:
    # Redis not available, create a dummy class
    class RedisCache(BaseCache):
        """Dummy Redis cache when redis is not installed."""
        def __init__(self, config: CacheConfig):
            super().__init__(config)
            raise ImportError("redis package not installed. Install with: pip install redis")


# Global cache instances
_response_cache: Optional[ResponseCache] = None
_embedding_cache: Optional[EmbeddingCache] = None
_image_cache: Optional[ImageCache] = None


def get_response_cache(config: Optional[CacheConfig] = None) -> ResponseCache:
    """Get the global response cache instance."""
    global _response_cache
    if _response_cache is None:
        cache_config = config or CacheConfig()
        _response_cache = ResponseCache(cache_config)
    return _response_cache


def get_embedding_cache(config: Optional[CacheConfig] = None) -> EmbeddingCache:
    """Get the global embedding cache instance."""
    global _embedding_cache
    if _embedding_cache is None:
        cache_config = config or CacheConfig()
        _embedding_cache = EmbeddingCache(cache_config)
    return _embedding_cache


def get_image_cache(config: Optional[CacheConfig] = None) -> ImageCache:
    """Get the global image cache instance."""
    global _image_cache
    if _image_cache is None:
        cache_config = config or CacheConfig()
        _image_cache = ImageCache(cache_config)
    return _image_cache


class CacheManager:
    """Manager for all cache types."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.response_cache = ResponseCache(self.config)
        self.embedding_cache = EmbeddingCache(self.config)
        self.image_cache = ImageCache(self.config)
    
    async def get_response(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Get a cached response."""
        return await self.response_cache.get(provider, model, messages, params)
    
    async def set_response(
        self,
        provider: str,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        response: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache a response."""
        await self.response_cache.set(provider, model, messages, response, params)
    
    async def get_embedding(
        self,
        provider: str,
        model: str,
        text: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[float]]:
        """Get a cached embedding."""
        return await self.embedding_cache.get(provider, model, text, params)
    
    async def set_embedding(
        self,
        provider: str,
        model: str,
        text: str,
        embedding: List[float],
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache an embedding."""
        await self.embedding_cache.set(provider, model, text, embedding, params)
    
    async def get_image(
        self,
        provider: str,
        model: str,
        prompt: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[bytes]:
        """Get a cached image."""
        return await self.image_cache.get(provider, model, prompt, params)
    
    async def set_image(
        self,
        provider: str,
        model: str,
        prompt: str,
        image_data: bytes,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Cache an image."""
        await self.image_cache.set(provider, model, prompt, image_data, params)
    
    async def clear_all(self):
        """Clear all caches."""
        await self.response_cache.clear()
        await self.embedding_cache.clear()
        await self.image_cache.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get all cache statistics."""
        return {
            "response_cache": self.response_cache.stats,
            "embedding_cache": self.embedding_cache.stats,
            "image_cache": self.image_cache.stats,
        }
