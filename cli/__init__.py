"""
CLI Package

Command-line interface for the free LLM API.
"""

from .main import main, CLIApp
from .commands import (
    ChatCommand,
    ListCommand,
    InfoCommand,
    BenchmarkCommand,
    HealthCommand,
    ConfigCommand,
)

__all__ = [
    "main",
    "CLIApp",
    "ChatCommand",
    "ListCommand",
    "InfoCommand",
    "BenchmarkCommand",
    "HealthCommand",
    "ConfigCommand",
]
