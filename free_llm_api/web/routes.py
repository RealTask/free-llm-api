"""
API Routes

Route definitions for the FastAPI web server.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os

from free_llm_api import FreeLLMAPI, get_api

logger = logging.getLogger(__name__)

# Setup templates
templates_path = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_path)


# Models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    messages: Union[str, List[Dict[str, Any]]]
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    use_cache: bool = True
    stream: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": "What is AI?",
                "model": "llama-3.1-8b-instant",
                "provider": "groq",
                "temperature": 0.7,
                "max_tokens": 100,
                "use_cache": True,
                "stream": False,
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    request_id: str
    provider: str
    model: str
    content: str
    latency_ms: float
    success: bool
    cached: bool = False
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_12345",
                "provider": "groq",
                "model": "llama-3.1-8b-instant",
                "content": "AI stands for Artificial Intelligence...",
                "latency_ms": 123.45,
                "success": True,
                "cached": False,
                "error": None,
            }
        }


class EmbedRequest(BaseModel):
    """Request model for embedding endpoint."""
    text: str
    model: Optional[str] = None
    provider: Optional[str] = None
    use_cache: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello world",
                "model": "text-embedding-ada-002",
                "provider": "openrouter",
                "use_cache": True,
            }
        }


class ImageRequest(BaseModel):
    """Request model for image generation endpoint."""
    prompt: str
    model: Optional[str] = None
    provider: Optional[str] = None
    use_cache: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A beautiful sunset over mountains",
                "model": "stable-diffusion-3.5",
                "provider": "stable_diffusion",
                "use_cache": True,
            }
        }


# Get API instance
async def get_api_instance() -> FreeLLMAPI:
    """Dependency to get API instance."""
    api = get_api()
    if not api._initialized:
        await api.initialize()
    return api


# Web UI Routes
web_router = APIRouter()


@web_router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Home page."""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "active_page": "home"
    })


@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard"
    })


@web_router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat page."""
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "active_page": "chat"
    })


@web_router.get("/providers", response_class=HTMLResponse)
async def providers_page(request: Request):
    """Providers page."""
    return templates.TemplateResponse("providers.html", {
        "request": request,
        "active_page": "providers"
    })


@web_router.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Models page."""
    return templates.TemplateResponse("models.html", {
        "request": request,
        "active_page": "models"
    })


@web_router.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    """Health status page."""
    return templates.TemplateResponse("health.html", {
        "request": request,
        "active_page": "health"
    })


@web_router.get("/benchmarks", response_class=HTMLResponse)
async def benchmarks_page(request: Request):
    """Benchmarks page."""
    return templates.TemplateResponse("benchmarks.html", {
        "request": request,
        "active_page": "benchmarks"
    })


@web_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "active_page": "settings"
    })


# Chat router
chat_router = APIRouter()


@chat_router.post("/", response_model=ChatResponse, summary="Send chat message")
async def chat(
    request: ChatRequest,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Send a chat message to an LLM.
    
    This endpoint allows you to send messages to various LLM providers
    with automatic provider selection, load balancing, and caching.
    """
    try:
        result = await api.chat(
            messages=request.messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_cache=request.use_cache,
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail={"error": result.error or "Chat failed"},
            )
        
        return ChatResponse(
            request_id=result.request_context.request_id,
            provider=result.provider,
            model=result.model,
            content=result.content,
            latency_ms=result.latency_ms,
            success=result.success,
            cached=result.cached,
            error=result.error,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


@chat_router.post("/stream", summary="Stream chat response")
async def chat_stream(
    request: ChatRequest,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Stream a chat response from an LLM.
    
    This endpoint returns a streaming response for real-time interaction.
    """
    try:
        # Get provider instance
        provider = request.provider or api.config.default_provider
        provider_instance = api.registry.get_provider(provider)
        if not provider_instance:
            raise HTTPException(
                status_code=400,
                detail={"error": f"Provider {provider} not available"},
            )
        
        # Get model
        model = request.model or api.config.default_model
        if not model:
            available_models = provider_instance.get_available_models()
            if available_models:
                model = available_models[0]
        
        # Create streaming generator
        async def generate():
            async for chunk in api.stream(
                messages=request.messages,
                model=model,
                provider=provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                # Format as SSE
                data = json.dumps({
                    "content": chunk.content,
                    "provider": chunk.provider,
                    "model": chunk.model,
                    "chunk_id": chunk.chunk_id,
                    "finish_reason": chunk.finish_reason,
                })
                yield f"data: {data}\n\n"
            
            # Send completion event
            yield "event: complete\ndata: {}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
        
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Providers router
providers_router = APIRouter()


@providers_router.get("/", summary="List all providers")
async def list_providers(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    List all available providers with optional filtering.
    """
    try:
        from core.models import ProviderCategory, ProviderStatus
        
        category_enum = None
        if category:
            try:
                category_enum = ProviderCategory(category)
            except ValueError:
                pass
        
        status_enum = None
        if status:
            try:
                status_enum = ProviderStatus(status)
            except ValueError:
                pass
        
        providers = api.list_providers(category_enum, status_enum)
        
        # Get details for each provider
        result = []
        for provider in providers:
            info = api.get_provider_info(provider)
            if info:
                result.append({
                    "name": provider,
                    "info": info,
                })
        
        return {"providers": result, "count": len(result)}
        
    except Exception as e:
        logger.error(f"List providers error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


@providers_router.get("/{provider}", summary="Get provider information")
async def get_provider(
    provider: str,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Get detailed information about a specific provider.
    """
    try:
        info = api.get_provider_info(provider)
        if not info:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Provider {provider} not found"},
            )
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get provider error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Models router
models_router = APIRouter()


@models_router.get("/", summary="List all models")
async def list_models(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    category: Optional[str] = Query(None, description="Filter by category"),
    capability: Optional[str] = Query(None, description="Filter by capability"),
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    List all available models with optional filtering.
    """
    try:
        models = api.list_models(provider, category, capability)
        return {"models": models, "count": len(models)}
        
    except Exception as e:
        logger.error(f"List models error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


@models_router.get("/{provider}/{model}", summary="Get model information")
async def get_model(
    provider: str,
    model: str,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Get detailed information about a specific model.
    """
    try:
        info = api.get_model_info(provider, model)
        if not info:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Model {model} not found for provider {provider}"},
            )
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Health router
health_router = APIRouter()


@health_router.get("/", summary="Get health summary")
async def get_health_summary(
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Get a summary of health status for all providers.
    """
    try:
        return api.get_health_status()
        
    except Exception as e:
        logger.error(f"Health summary error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


@health_router.get("/{provider}", summary="Get provider health status")
async def get_provider_health(
    provider: str,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Get health status for a specific provider.
    """
    try:
        health = api.get_health_status(provider)
        if not health:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Provider {provider} not found"},
            )
        return health
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider health error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Benchmark router
benchmark_router = APIRouter()


@benchmark_router.post("/", summary="Run benchmark")
async def run_benchmark(
    provider: Optional[str] = Query(None, description="Provider to benchmark"),
    model: Optional[str] = Query(None, description="Model to benchmark"),
    benchmark_type: str = Query("latency", description="Type of benchmark"),
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Run a benchmark on providers.
    """
    try:
        results = await api.run_benchmark(
            provider=provider,
            model=model,
            benchmark_type=benchmark_type,
        )
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Stats router
stats_router = APIRouter()


@stats_router.get("/", summary="Get API statistics")
async def get_stats(
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Get API statistics including cache, rate limiting, and provider stats.
    """
    try:
        return api.get_stats()
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Embedding router
embed_router = APIRouter()


@embed_router.post("/", summary="Generate embeddings")
async def embed(
    request: EmbedRequest,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Generate embeddings for text.
    """
    try:
        result = await api.embed(
            text=request.text,
            model=request.model,
            provider=request.provider,
            use_cache=request.use_cache,
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail={"error": result.error or "Embedding failed"},
            )
        
        return {
            "provider": result.provider,
            "model": result.model,
            "embedding": result.content,
            "latency_ms": result.latency_ms,
            "success": result.success,
            "cached": result.cached,
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )


# Image router
image_router = APIRouter()


@image_router.post("/", summary="Generate image")
async def generate_image(
    request: ImageRequest,
    api: FreeLLMAPI = Depends(get_api_instance),
):
    """
    Generate an image from a text prompt.
    """
    try:
        result = await api.generate_image(
            prompt=request.prompt,
            model=request.model,
            provider=request.provider,
            use_cache=request.use_cache,
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail={"error": result.error or "Image generation failed"},
            )
        
        # Return image as bytes
        return JSONResponse(content={
            "provider": result.provider,
            "model": result.model,
            "image": result.content.hex() if isinstance(result.content, bytes) else result.content,
            "latency_ms": result.latency_ms,
            "success": result.success,
            "cached": result.cached,
        })
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)},
        )
