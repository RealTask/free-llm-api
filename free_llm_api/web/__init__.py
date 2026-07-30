"""
Web Package

FastAPI web server for the free LLM API.
"""

from .app import create_app
from .routes import (
    chat_router,
    providers_router,
    models_router,
    health_router,
    benchmark_router,
    stats_router,
)

__all__ = [
    "create_app",
    "chat_router",
    "providers_router",
    "models_router",
    "health_router",
    "benchmark_router",
    "stats_router",
]
