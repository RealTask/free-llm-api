"""
OpenRouter Provider

Implementation for OpenRouter API.
Gateway to multiple model providers with 20 req/min, 50 req/day baseline,
extendable to 1,000 req/day with $10 lifetime credit.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
import httpx

from ..base_provider import BaseLLMProvider, ProviderConfig, ProviderCategory, ProviderType, ModelInfo, RateLimit

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter API Provider.
    
    Features:
    - Gateway to 20+ free models
    - Easy to switch between providers
    - Baseline: 20 req/min, 50 req/day
    - Extended: Up to 1,000 req/day with $10 lifetime credit
    - Access to latest models from various providers
    
    Limitations:
    - Lower baseline limits
    - Shared quota across models
    
    Best for: Testing multiple models, small-scale projects
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default configuration for OpenRouter."""
        models = [
            ModelInfo(
                name="hermes-3-llama-3.1-405b",
                description="Hermes 3 Llama 3.1 405B",
                parameters="405B",
                context_window=128000,
                license="Llama 3.1",
                category="general",
                tags=["hermes", "llama", "large"]
            ),
            ModelInfo(
                name="llama-3.2-3b-instruct",
                description="Llama 3.2 3B Instruct",
                parameters="3B",
                context_window=128000,
                license="Llama 3.2",
                category="general",
                tags=["llama", "small"]
            ),
            ModelInfo(
                name="llama-3.2-70b-instruct",
                description="Llama 3.2 70B Instruct",
                parameters="70B",
                context_window=128000,
                license="Llama 3.2",
                category="general",
                tags=["llama", "large"]
            ),
            ModelInfo(
                name="cognitivecomputations/dolphin-mistral-24b-venice-edition",
                description="Dolphin Mistral 24B Venice Edition",
                parameters="24B",
                context_window=128000,
                license="Apache 2.0",
                category="general",
                tags=["dolphin", "mistral", "apache-2.0"]
            ),
            ModelInfo(
                name="cohere/north-mini-code",
                description="Cohere North Mini Code",
                parameters="Unknown",
                context_window=128000,
                license="Proprietary",
                category="coding",
                tags=["cohere", "coding"]
            ),
            ModelInfo(
                name="google/gemma-4-26b-a4b-it",
                description="Google Gemma 4 26B A4B IT",
                parameters="26B",
                context_window=128000,
                license="Apache 2.0",
                category="general",
                tags=["google", "gemma", "apache-2.0"]
            ),
            ModelInfo(
                name="google/gemma-4-31b-it",
                description="Google Gemma 4 31B IT",
                parameters="31B",
                context_window=128000,
                license="Apache 2.0",
                category="general",
                tags=["google", "gemma", "apache-2.0"]
            ),
            ModelInfo(
                name="nvidia/nemotron-3-nano",
                description="NVIDIA Nemotron 3 Nano",
                parameters="Unknown",
                context_window=128000,
                license="Proprietary",
                category="general",
                tags=["nvidia", "nemotron"]
            ),
            ModelInfo(
                name="nvidia/nemotron-3-mini",
                description="NVIDIA Nemotron 3 Mini",
                parameters="Unknown",
                context_window=128000,
                license="Proprietary",
                category="general",
                tags=["nvidia", "nemotron"]
            ),
            ModelInfo(
                name="nvidia/nemotron-3-120b-a12b",
                description="NVIDIA Nemotron 3 120B A12B",
                parameters="120B",
                context_window=128000,
                license="Proprietary",
                category="general",
                tags=["nvidia", "nemotron", "large"]
            ),
            ModelInfo(
                name="openai/gpt-oss-120b",
                description="OpenAI GPT-OSS 120B",
                parameters="120B",
                context_window=128000,
                license="MIT",
                category="general",
                tags=["openai", "open-model"]
            ),
            ModelInfo(
                name="openai/gpt-oss-20b",
                description="OpenAI GPT-OSS 20B",
                parameters="20B",
                context_window=128000,
                license="MIT",
                category="general",
                tags=["openai", "open-model"]
            ),
            ModelInfo(
                name="qwen/qwen3-coder",
                description="Qwen 3 Coder",
                parameters="Unknown",
                context_window=128000,
                license="Apache 2.0",
                category="coding",
                tags=["qwen", "coding", "apache-2.0"]
            ),
            ModelInfo(
                name="qwen/qwen3-next-80b",
                description="Qwen 3 Next 80B",
                parameters="80B",
                context_window=128000,
                license="Apache 2.0",
                category="general",
                tags=["qwen", "apache-2.0"]
            ),
            ModelInfo(
                name="poolside/laguna",
                description="Poolside Laguna",
                parameters="Unknown",
                context_window=128000,
                license="Apache 2.0",
                category="general",
                tags=["poolside", "apache-2.0"]
            ),
        ]
        
        return ProviderConfig(
            name="OpenRouter",
            category=ProviderCategory.LLM,
            provider_type=ProviderType.CLOUD,
            base_url=cls.BASE_URL,
            api_key_env_var="OPENROUTER_API_KEY",
            rate_limits=RateLimit(
                requests_per_minute=20,
                requests_per_day=50,  # Baseline, can be extended to 1000
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
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key
            app_name: Optional app name for tracking
        """
        # Try to get API key from environment if not provided
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
    
    async def chat(
        self,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat completion request to OpenRouter.
        
        Args:
            model: Model name
            messages: Chat messages (string or list of message dicts)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            str: Generated text response
        """
        if not self._check_rate_limits():
            raise RateLimitExceededError("OpenRouter rate limit exceeded")
        
        # Convert string message to list format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Format messages for OpenRouter API (OpenAI-compatible format)
        openrouter_messages = []
        for msg in messages:
            if isinstance(msg, str):
                openrouter_messages.append({"role": "user", "content": msg})
            else:
                openrouter_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        payload = {
            "model": model,
            "messages": openrouter_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 8192,
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        if "stop" in kwargs:
            payload["stop"] = kwargs["stop"]
        if "stream" in kwargs:
            payload["stream"] = kwargs["stream"]
        
        url = f"{self.BASE_URL}/chat/completions"
        
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
                    raise APIError(f"OpenRouter API error: {error_msg}")
                
                result = response.json()
                
                # Extract text from response
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0].get("message", {}).get("content", "")
                
                return ""
                
        except httpx.TimeoutException:
            raise APIError("Request timeout")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def complete(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a text completion request.
        
        Args:
            model: Model name
            prompt: Text prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            str: Generated text
        """
        # For OpenRouter, we'll use chat completion for text completion
        return await self.chat(model, prompt, temperature, max_tokens, **kwargs)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from OpenRouter.
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        url = f"{self.BASE_URL}/models"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                    raise APIError(f"OpenRouter models API error: {error_msg}")
                
                result = response.json()
                return result.get("data", [])
                
        except httpx.TimeoutException:
            raise APIError("Request timeout")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.session.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())


class APIError(Exception):
    """API error exception."""
    pass


class RateLimitExceededError(Exception):
    """Rate limit exceeded exception."""
    pass