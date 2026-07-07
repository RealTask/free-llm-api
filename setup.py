#!/usr/bin/env python3
"""
Setup script for Free LLM API - Advanced Edition

A comprehensive, production-ready library for accessing free LLM API providers.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="free-llm-api",
    version="2.0.0",
    description="A comprehensive, production-ready library for accessing free LLM API providers with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="realtast",
    author_email="",
    url="https://github.com/realtast/free-llm-api",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "requests>=2.31.0",
        "httpx>=0.25.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "anyio>=4.0.0",
        
        # Rate limiting
        "ratelimit>=2.2.1",
        "backoff>=2.2.1",
        
        # Image generation (optional)
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        
        # Web server (optional)
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        
        # CLI
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "local-inference": [
            "torch>=2.0.0",
            "transformers>=4.37.0",
            "accelerate>=0.25.0",
            "diffusers>=0.25.0",
        ],
        "redis": [
            "redis>=5.0.0",
        ],
        "all": [
            "torch>=2.0.0",
            "transformers>=4.37.0",
            "accelerate>=0.25.0",
            "diffusers>=0.25.0",
            "redis>=5.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "mypy>=1.5.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "ruff>=0.1.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "free-llm=free_llm_api.cli.main:main",
            "free-llm-server=free_llm_api.web.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Framework :: AsyncIO",
    ],
    keywords=[
        "llm", "ai", "machine-learning", "api", "free", "providers",
        "google", "groq", "mistral", "openrouter", "huggingface",
        "image-generation", "speech-to-text", "text-to-speech", "embeddings",
        "fastapi", "async", "streaming", "caching", "load-balancing",
        "health-monitoring", "benchmarking", "cli", "web-server",
    ],
    project_urls={
        "Bug Reports": "https://github.com/realtast/free-llm-api/issues",
        "Source": "https://github.com/realtast/free-llm-api",
        "Documentation": "https://github.com/realtast/free-llm-api#readme",
    },
)
