"""
Provider Registry

Advanced provider registry with dynamic loading, discovery, and management.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
import asyncio

from .models import (
    ProviderMetadata,
    ProviderCategory,
    ProviderType,
    ProviderStatus,
    ModelMetadata,
    ModelCapability,
    RateLimit,
)
from providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


@dataclass
class ProviderDiscovery:
    """Provider discovery and dynamic loading."""
    
    search_paths: List[str] = field(default_factory=lambda: [
        "providers.llm",
        "providers.image", 
        "providers.speech",
        "providers.embeddings",
    ])
    
    def discover_providers(self) -> Dict[str, Type[BaseProvider]]:
        """
        Discover all available provider classes.
        
        Returns:
            Dict[str, Type[BaseProvider]]: Dictionary of provider names to classes
        """
        providers = {}
        
        for search_path in self.search_paths:
            try:
                module = importlib.import_module(search_path)
                self._discover_from_module(module, providers, search_path)
            except ImportError as e:
                logger.warning(f"Could not import module {search_path}: {e}")
            except Exception as e:
                logger.error(f"Error discovering providers in {search_path}: {e}")
        
        return providers
    
    def _discover_from_module(
        self,
        module: Any,
        providers: Dict[str, Type[BaseProvider]],
        base_path: str
    ):
        """Recursively discover providers from a module."""
        # Check if module has provider classes
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseProvider) and obj != BaseProvider:
                provider_name = obj.__name__.replace("Provider", "")
                providers[provider_name.lower()] = obj
                logger.debug(f"Discovered provider: {provider_name} from {base_path}")
        
        # Check submodules
        if hasattr(module, "__path__"):
            for _, submodule_name, _ in pkgutil.iter_modules(module.__path__):
                try:
                    submodule = importlib.import_module(f"{module.__name__}.{submodule_name}")
                    self._discover_from_module(submodule, providers, f"{base_path}.{submodule_name}")
                except ImportError as e:
                    logger.warning(f"Could not import submodule {submodule_name}: {e}")
    
    def get_provider_class(self, name: str) -> Optional[Type[BaseProvider]]:
        """
        Get a provider class by name.
        
        Args:
            name: Provider name (case-insensitive)
            
        Returns:
            Type[BaseProvider]: Provider class or None if not found
        """
        providers = self.discover_providers()
        return providers.get(name.lower())
    
    def list_available_providers(self) -> List[str]:
        """
        List all available provider names.
        
        Returns:
            List[str]: List of provider names
        """
        return list(self.discover_providers().keys())


class ProviderRegistry:
    """
    Central registry for all AI providers.
    
    Manages provider instances, metadata, and provides discovery capabilities.
    """
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._metadata: Dict[str, ProviderMetadata] = {}
        self._discovery = ProviderDiscovery()
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the registry and discover all providers."""
        async with self._lock:
            if self._initialized:
                return
            
            # Discover all provider classes
            provider_classes = self._discovery.discover_providers()
            
            # Initialize metadata for each provider
            for name, provider_class in provider_classes.items():
                try:
                    # Skip base provider classes
                    if provider_class.__name__.startswith('Base'):
                        logger.debug(f"Skipping base provider class: {provider_class.__name__}")
                        continue
                    
                    # Get default config from provider class method
                    try:
                        config = provider_class.get_default_config()
                    except (AttributeError, TypeError):
                        # If get_default_config doesn't work, skip this provider
                        logger.warning(f"Could not get config for {name}, skipping")
                        continue
                    
                    # Validate config
                    if config is None or not hasattr(config, 'category') or config.category is None:
                        logger.warning(f"Invalid config for {name}, skipping")
                        continue
                    
                    # Create metadata
                    metadata = ProviderMetadata(
                        name=name,
                        category=config.category,
                        provider_type=config.provider_type,
                        base_url=config.base_url,
                        api_key_env_var=config.api_key_env_var,
                        rate_limits=config.rate_limits,
                        requires_auth=config.requires_auth,
                        requires_phone_verification=config.requires_phone_verification,
                        data_training_opt_out_available=config.data_training_opt_out_available,
                        commercial_usage_allowed=config.commercial_usage_allowed,
                        region=config.region,
                        models=[
                            ModelMetadata(
                                id=model.name,
                                name=model.name,
                                description=model.description,
                                parameters=model.parameters,
                                context_window=model.context_window,
                                license=model.license,
                                category=model.category,
                                tags=model.tags,
                                capabilities=ModelCapability(
                                    supports_chat=True,
                                    supports_completion=True,
                                    supports_streaming=True,
                                )
                            ) for model in config.models
                        ],
                        tags=[name],
                    )
                    
                    self._metadata[name] = metadata
                    logger.info(f"Registered provider metadata: {name}")
                    
                except Exception as e:
                    logger.error(f"Error initializing metadata for {name}: {e}")
            
            self._initialized = True
    
    def get_provider(
        self,
        name: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> Optional[BaseProvider]:
        """
        Get a provider instance by name.
        
        Args:
            name: Provider name
            api_key: Optional API key
            **kwargs: Additional arguments for provider initialization
            
        Returns:
            BaseProvider: Provider instance or None if not found
        """
        provider_class = self._discovery.get_provider_class(name)
        if not provider_class:
            logger.warning(f"Provider {name} not found")
            return None
        
        # Check if we already have an instance
        cache_key = f"{name}_{api_key}" if api_key else name
        if cache_key in self._providers:
            return self._providers[cache_key]
        
        try:
            # Create new instance
            if api_key:
                provider = provider_class(api_key=api_key, **kwargs)
            else:
                provider = provider_class(**kwargs)
            
            self._providers[cache_key] = provider
            logger.info(f"Created provider instance: {name}")
            return provider
            
        except Exception as e:
            logger.error(f"Error creating provider {name}: {e}")
            return None
    
    def get_metadata(self, name: str) -> Optional[ProviderMetadata]:
        """
        Get provider metadata by name.
        
        Args:
            name: Provider name
            
        Returns:
            ProviderMetadata: Metadata or None if not found
        """
        return self._metadata.get(name.lower())
    
    def list_providers(
        self,
        category: Optional[ProviderCategory] = None,
        status: Optional[ProviderStatus] = None,
    ) -> List[str]:
        """
        List available providers with optional filtering.
        
        Args:
            category: Optional category filter
            status: Optional status filter
            
        Returns:
            List[str]: List of provider names
        """
        providers = []
        
        for name, metadata in self._metadata.items():
            if category and metadata.category != category:
                continue
            if status and metadata.status != status:
                continue
            providers.append(name)
        
        return sorted(providers)
    
    def list_models(
        self,
        provider: Optional[str] = None,
        category: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List available models with optional filtering.
        
        Args:
            provider: Optional provider filter
            category: Optional model category filter
            capability: Optional capability filter
            
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        
        for name, metadata in self._metadata.items():
            if provider and name.lower() != provider.lower():
                continue
            
            for model in metadata.models:
                if category and model.category != category:
                    continue
                if capability and not getattr(model.capabilities, capability, False):
                    continue
                
                models.append({
                    "provider": name,
                    "model": model.name,
                    "description": model.description,
                    "parameters": model.parameters,
                    "context_window": model.context_window,
                    "category": model.category,
                    "tags": model.tags,
                })
        
        return models
    
    def get_best_provider(
        self,
        task: str = "general",
        min_context: Optional[int] = None,
        streaming: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best provider for a specific task.
        
        Args:
            task: Task type (general, coding, chat, etc.)
            min_context: Minimum context window required
            streaming: Whether streaming is required
            
        Returns:
            Dict[str, Any]: Best provider information or None
        """
        best_provider = None
        best_score = -1
        
        for name, metadata in self._metadata.items():
            if metadata.status != ProviderStatus.AVAILABLE:
                continue
            
            score = 0
            
            # Score based on task
            if task in [m.category for m in metadata.models]:
                score += 10
            
            # Score based on context window
            if min_context:
                for model in metadata.models:
                    if model.context_window and model.context_window >= min_context:
                        score += 5
                        break
            
            # Score based on streaming
            if streaming:
                for model in metadata.models:
                    if model.capabilities.supports_streaming:
                        score += 3
                        break
            
            # Score based on rate limits
            if metadata.rate_limits.requests_per_day:
                score += min(metadata.rate_limits.requests_per_day / 1000, 5)
            
            if score > best_score:
                best_score = score
                best_provider = {
                    "name": name,
                    "metadata": metadata,
                    "score": score,
                }
        
        return best_provider
    
    def search_providers(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search providers by name, description, or tags.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching providers
        """
        query_lower = query.lower()
        results = []
        
        for name, metadata in self._metadata.items():
            # Check name
            if query_lower in name.lower():
                results.append({"name": name, "metadata": metadata, "match": "name"})
                continue
            
            # Check description
            if metadata.models and any(
                query_lower in m.description.lower() 
                for m in metadata.models
            ):
                results.append({"name": name, "metadata": metadata, "match": "description"})
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in metadata.tags):
                results.append({"name": name, "metadata": metadata, "match": "tag"})
                continue
            
            # Check model names
            if any(query_lower in m.name.lower() for m in metadata.models):
                results.append({"name": name, "metadata": metadata, "match": "model"})
        
        return results[:limit]
    
    def register_custom_provider(
        self,
        name: str,
        provider_class: Type[BaseProvider],
        metadata: Optional[ProviderMetadata] = None,
    ):
        """
        Register a custom provider.
        
        Args:
            name: Provider name
            provider_class: Provider class
            metadata: Optional metadata
        """
        # Register the provider class
        self._discovery.search_paths.append(f"custom.{name}")
        
        # Create a module-like object for the provider
        import types
        custom_module = types.ModuleType(f"custom.{name}")
        custom_module.__dict__[name] = provider_class
        
        # Add to discovered providers
        self._discovery._discover_from_module(custom_module, self._providers, f"custom.{name}")
        
        # Add metadata
        if metadata:
            self._metadata[name.lower()] = metadata
        else:
            # Create default metadata
            config = provider_class.get_default_config()
            self._metadata[name.lower()] = ProviderMetadata(
                name=name,
                category=config.category,
                provider_type=config.provider_type,
                base_url=config.base_url,
                api_key_env_var=config.api_key_env_var,
                rate_limits=config.rate_limits,
                requires_auth=config.requires_auth,
                models=[
                    ModelMetadata(
                        id=m.name,
                        name=m.name,
                        description=m.description,
                        parameters=m.parameters,
                        context_window=m.context_window,
                        license=m.license,
                        category=m.category,
                        tags=m.tags,
                    ) for m in config.models
                ],
            )
        
        logger.info(f"Registered custom provider: {name}")
    
    def update_status(
        self,
        name: str,
        status: ProviderStatus,
        response_time: Optional[float] = None,
        error_message: Optional[str] = None,
    ):
        """
        Update the status of a provider.
        
        Args:
            name: Provider name
            status: New status
            response_time: Optional response time
            error_message: Optional error message
        """
        if name.lower() in self._metadata:
            metadata = self._metadata[name.lower()]
            metadata.status = status
            metadata.last_checked = datetime.now()
            if response_time:
                metadata.response_time_avg = response_time
            if error_message:
                metadata.error_message = error_message
            logger.info(f"Updated status for {name}: {status.value}")
    
    def get_provider_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Dict[str, Any]: Provider statistics or None
        """
        metadata = self._metadata.get(name.lower())
        if not metadata:
            return None
        
        return {
            "name": name,
            "status": metadata.status.value,
            "response_time_avg": metadata.response_time_avg,
            "success_rate": metadata.success_rate,
            "error_rate": metadata.error_rate,
            "models_count": len(metadata.models),
            "rate_limits": metadata.rate_limits.to_dict(),
        }
    
    def cleanup(self):
        """Clean up provider instances."""
        for name, provider in self._providers.items():
            if hasattr(provider, "close"):
                try:
                    if asyncio.iscoroutinefunction(provider.close):
                        asyncio.run(provider.close())
                    else:
                        provider.close()
                except Exception as e:
                    logger.error(f"Error closing provider {name}: {e}")
        
        self._providers.clear()
        logger.info("Cleaned up provider instances")


# Global registry instance
_registry: Optional[ProviderRegistry] = None


def get_registry() -> ProviderRegistry:
    """Get the global provider registry instance."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


async def initialize_registry():
    """Initialize the global provider registry."""
    registry = get_registry()
    await registry.initialize()
    return registry
