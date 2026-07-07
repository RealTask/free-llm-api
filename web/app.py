"""
FastAPI Application

Main FastAPI application for the free LLM API.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from typing import Any, Dict, Optional

from free_llm_api import FreeLLMAPI, FreeLLMAPIConfig

logger = logging.getLogger(__name__)

# Global API instance
_api: Optional[FreeLLMAPI] = None


def get_api() -> FreeLLMAPI:
    """Get the global API instance."""
    global _api
    if _api is None:
        _api = FreeLLMAPI()
    return _api


async def initialize_api():
    """Initialize the global API instance."""
    api = get_api()
    if not api._initialized:
        await api.initialize()
    return api


def create_app(
    config: Optional[FreeLLMAPIConfig] = None,
    debug: bool = False,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config: Optional API configuration
        debug: Whether to run in debug mode
        
    Returns:
        FastAPI: Configured FastAPI application
    """
    # Create API instance with config
    global _api
    _api = FreeLLMAPI(config or FreeLLMAPIConfig())
    
    # Create FastAPI app
    app = FastAPI(
        title="Free LLM API",
        description="A comprehensive API for accessing free LLM providers",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=debug,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from .routes import (
        chat_router,
        providers_router,
        models_router,
        health_router,
        benchmark_router,
        stats_router,
    )
    
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(providers_router, prefix="/api/v1/providers", tags=["providers"])
    app.include_router(models_router, prefix="/api/v1/models", tags=["models"])
    app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
    app.include_router(benchmark_router, prefix="/api/v1/benchmark", tags=["benchmark"])
    app.include_router(stats_router, prefix="/api/v1/stats", tags=["stats"])
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        logger.info("Starting Free LLM API server...")
        await initialize_api()
        logger.info("Free LLM API server started")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event handler."""
        logger.info("Shutting down Free LLM API server...")
        if _api:
            await _api.close()
        logger.info("Free LLM API server stopped")
    
    # Add root endpoint
    @app.get("/", summary="Root endpoint")
    async def root():
        """Root endpoint."""
        return {
            "name": "Free LLM API",
            "version": "2.0.0",
            "description": "A comprehensive API for accessing free LLM providers",
            "docs": "/docs",
        }
    
    # Add health check endpoint
    @app.get("/health", summary="Health check")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    # Add error handler
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger.error(f"Error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
            },
        )
    
    return app


# Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "free_llm_api.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
