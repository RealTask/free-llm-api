"""
OpenRouter Embeddings Provider

Implementation for OpenRouter Embeddings.
Access to various embedding models with shared LLM quota.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
import httpx

from ..base_provider import BaseEmbeddingProvider, ProviderConfig, ProviderCategory, ProviderType, ModelInfo, RateLimit

logger = logging.getLogger(__name__)


class OpenRouterEmbeddingsProvider(BaseEmbeddingProvider):
    """
    OpenRouter Embeddings Provider.
    
    Features:
    - Access to multiple embedding models from different providers
    - Easy access through OpenRouter
    - Shared quota with LLM models
    
    Limitations:
    - Shared quota with LLM models (20 req/min, 50 req/day baseline)
    - Lower limits than dedicated embedding services
    
    Best for: Testing different embedding models
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default configuration for OpenRouter Embeddings."""
        models = [
            ModelInfo(
                name="text-embedding-3-small",
                description="OpenAI Text Embedding 3 Small",
                parameters="Unknown",
                context_window=None,
                license="Proprietary",
                category="embeddings",
                tags=["openai", "small"]
            ),
            ModelInfo(
                name="text-embedding-3-large",
                description="OpenAI Text Embedding 3 Large",
                parameters="Unknown",
                context_window=None,
                license="Proprietary",
                category="embeddings",
                tags=["openai", "large"]
            ),
            ModelInfo(
                name="text-embedding-ada-002",
                description="OpenAI Text Embedding Ada 002",
                parameters="Unknown",
                context_window=None,
                license="Proprietary",
                category="embeddings",
                tags=["openai", "ada"]
            ),
            ModelInfo(
                name="sentence-transformers/all-mpnet-base-v2",
                description="All MPNet Base v2 - General-purpose embedding",
                parameters="420M",
                context_window=None,
                license="Apache 2.0",
                category="embeddings",
                tags=["general-purpose", "apache-2.0"]
            ),
            ModelInfo(
                name="sentence-transformers/all-MiniLM-L6-v2",
                description="All MiniLM L6 v2 - Lightweight embedding",
                parameters="80M",
                context_window=None,
                license="Apache 2.0",
                category="embeddings",
                tags=["lightweight", "fast", "apache-2.0"]
            ),
            ModelInfo(
                name="BAAI/bge-small-en-v1.5",
                description="BGE Small EN v1.5 - English embedding",
                parameters="110M",
                context_window=None,
                license="MIT",
                category="embeddings",
                tags=["english", "bge", "mit"]
            ),
            ModelInfo(
                name="BAAI/bge-base-en-v1.5",
                description="BGE Base EN v1.5 - English embedding",
                parameters="420M",
                context_window=None,
                license="MIT",
                category="embeddings",
                tags=["english", "bge", "mit"]
            ),
            ModelInfo(
                name="BAAI/bge-large-en-v1.5",
                description="BGE Large EN v1.5 - English embedding",
                parameters="1.5B",
                context_window=None,
                license="MIT",
                category="embeddings",
                tags=["english", "bge", "mit", "large"]
            ),
        ]
        
        return ProviderConfig(
            name="OpenRouter Embeddings",
            category=ProviderCategory.EMBEDDINGS,
            provider_type=ProviderType.CLOUD,
            base_url=cls.BASE_URL,
            api_key_env_var="OPENROUTER_API_KEY",
            rate_limits=RateLimit(
                requests_per_minute=20,  # Shared with LLM quota
                requests_per_day=50,  # Shared with LLM quota, baseline
            ),
            requires_auth=True,
            requires_phone_verification=False,
            data_training_opt_out_available=True,
            commercial_usage_allowed=True,
            region="global",
            models=models
        )
    
    def __init__(self, api_key: Optional[str] = None, app_name: Optional[str] = None):
        """
        Initialize OpenRouter Embeddings provider.
        
        Args:
            api_key: OpenRouter API key
            app_name: Optional app name for tracking
        """
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
        
        super().__init__(api_key=api_key)
        self.app_name = app_name or "llmapi"
        self.session = httpx.AsyncClient()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API."""
        headers = super()._get_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers["HTTP-Referer"] = self.app_name
        headers["X-Title"] = self.app_name
        return headers
    
    async def embed(
        self,
        model: str,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Generate embeddings for text using OpenRouter.
        
        Args:
            model: Embedding model name
            text: Text to embed
            **kwargs: Additional parameters
            
        Returns:
            List[float]: Embedding vector
        """
        if not self._check_rate_limits():
            raise RateLimitExceededError("OpenRouter Embeddings rate limit exceeded")
        
        payload = {
            "model": model,
            "input": text,
        }
        
        # Add optional parameters
        if "encoding_format" in kwargs:
            payload["encoding_format"] = kwargs["encoding_format"]
        if "user" in kwargs:
            payload["user"] = kwargs["user"]
        
        url = f"{self.BASE_URL}/embeddings"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=60.0
                )
                
                self._update_request_counters()
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                    raise APIError(f"OpenRouter Embeddings API error: {error_msg}")
                
                result = response.json()
                
                # Extract embedding from response
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0].get("embedding", [])
                
                raise APIError("No embedding data in response")
                
        except httpx.TimeoutException:
            raise APIError("Embedding generation timeout")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def embed_batch(
        self,
        model: str,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            model: Embedding model name
            texts: List of texts to embed
            **kwargs: Additional parameters
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self._check_rate_limits():
            raise RateLimitExceededError("OpenRouter Embeddings rate limit exceeded")
        
        payload = {
            "model": model,
            "input": texts,
        }
        
        # Add optional parameters
        if "encoding_format" in kwargs:
            payload["encoding_format"] = kwargs["encoding_format"]
        if "user" in kwargs:
            payload["user"] = kwargs["user"]
        
        url = f"{self.BASE_URL}/embeddings"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=120.0
                )
                
                self._update_request_counters()
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                    raise APIError(f"OpenRouter Embeddings batch API error: {error_msg}")
                
                result = response.json()
                
                # Extract embeddings from response
                if "data" in result:
                    return [item.get("embedding", []) for item in result["data"]]
                
                raise APIError("No embedding data in response")
                
        except httpx.TimeoutException:
            raise APIError("Batch embedding generation timeout")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.session.aclose()


class APIError(Exception):
    """API error exception."""
    pass


class RateLimitExceededError(Exception):
    """Rate limit exceeded exception."""
    pass