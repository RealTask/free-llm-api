"""
API Keys Template

Template for API keys configuration. Copy this file to api_keys.py and fill in your keys.
"""

# API Keys Template
# Copy this file to api_keys.py and fill in your actual API keys

API_KEYS_TEMPLATE = {
    # LLM Providers
    "GOOGLE_AI_STUDIO_API_KEY": "your-google-ai-studio-api-key",
    "GROQ_API_KEY": "your-groq-api-key",
    "MISTRAL_API_KEY": "your-mistral-api-key",
    "OPENROUTER_API_KEY": "your-openrouter-api-key",
    "CEREBRAS_API_KEY": "your-cerebras-api-key",
    "COHERE_API_KEY": "your-cohere-api-key",
    "CLOUDFLARE_API_KEY": "your-cloudflare-api-key",
    "CLOUDFLARE_ACCOUNT_ID": "your-cloudflare-account-id",
    "HUGGINGFACE_API_KEY": "your-huggingface-api-key",
    "NVIDIA_API_KEY": "your-nvidia-api-key",
    "VERCEL_AI_API_KEY": "your-vercel-ai-api-key",
    "GITHUB_COPILOT_API_KEY": "your-github-copilot-api-key",
    
    # Image Providers
    "GOOGLE_GEMINI_API_KEY": "your-google-gemini-api-key",
    "ADOBE_FIREFLY_API_KEY": "your-adobe-firefly-api-key",
    "MIDJOURNEY_API_KEY": "your-midjourney-api-key",
    "OPENAI_API_KEY": "your-openai-api-key",
    "IMAGEN_API_KEY": "your-imagen-api-key",
    
    # Speech Providers
    # Note: Groq and Google TTS use the same keys as their main services
    # WHISPER_BASE_URL: "your-whisper-local-api-url",  # For local Whisper
    
    # Embedding Providers
    # Note: Most embedding providers use the same keys as their main services
    
    # Local Deployment
    "STABLE_DIFFUSION_BASE_URL": "http://localhost:7860",  # ComfyUI default
    "FLUX_BASE_URL": "http://localhost:7860",  # ComfyUI with FLUX
    "WHISPER_BASE_URL": "http://localhost:9000",  # Local Whisper API
    "HUGGINGFACE_EMBEDDINGS_BASE_URL": "http://localhost:8000",  # Local embeddings API
}

# Default settings
DEFAULT_SETTINGS = {
    "rate_limit_enabled": True,
    "retry_on_failure": True,
    "max_retries": 3,
    "timeout_seconds": 120,
    "debug_mode": False,
    "log_requests": True,
}


def get_api_keys_template() -> dict:
    """Get the API keys template."""
    return API_KEYS_TEMPLATE.copy()


def get_default_settings() -> dict:
    """Get default settings."""
    return DEFAULT_SETTINGS.copy()