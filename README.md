# Free LLM API - Comprehensive Provider Collection

A curated collection of free LLM API providers with their capabilities, limitations, and best use cases based on 2026 research.

## 🎯 Overview

This repository provides a comprehensive catalog of free-tier and completely free AI model APIs across multiple categories:
- **Large Language Models (LLMs)**
- **Image Generation**
- **Embeddings**
- **Speech-to-Text/Text-to-Speech**
- **Multimodal models**

## 📊 Quick Recommendations by Use Case

| Use Case | Best Free API | Daily Limit | Notes |
|----------|---------------|-------------|-------|
| General LLM | Google AI Studio (Gemma 3) | 14,400 req | 30 req/min, Apache 2.0 models |
| Coding Agent | Groq (Llama 3.1 8B) | 14,400 req | 6,000 tokens/min |
| High Volume | Groq (Allam 2 7B) | 7,000 req | Best for bulk processing |
| Local Deployment | Stable Diffusion 3.5 | Unlimited | Hardware-limited only |
| Speech-to-Text | Groq (Whisper Large v3) | 2,000 req | Production-ready |
| Enterprise | Mistral La Plateforme | 1B tokens/mo | Requires phone verification |
| Multi-Model Access | OpenRouter | 50-1,000 req | 20+ free models |

## 🏆 Top Picks

- **🏆 Most Generous Free Tier**: Google AI Studio offers up to 14,400 requests/day for Gemma 3 models with 30 req/min
- **🎁 Best for Developers**: OpenRouter provides 20 req/min, 50 req/day baseline, extendable to 1,000 req/day with $10 lifetime credit
- **🚀 Highest Volume**: Groq offers 14,400 req/day for Llama 3.1 8B and 7,000 req/day for Allam 2 7B
- **💡 Open-Source Alternative**: Hugging Face Serverless Inference supports models <10GB with $0.10/month credits
- **🖼️ Free Image Generation**: Stable Diffusion 3.5 offers complete freedom for local deployment with no platform caps
- **🎤 Speech APIs**: Groq provides 2,000 req/day for Whisper Large v3 (STT)
- **🏢 Enterprise-Friendly**: Mistral La Plateforme offers 1M tokens/month free with phone verification

## 📁 Project Structure

```
free-llm-api/
├── providers/
│   ├── llm/
│   │   ├── google_ai_studio.py
│   │   ├── groq.py
│   │   ├── mistral.py
│   │   ├── openrouter.py
│   │   ├── cerebras.py
│   │   ├── cohere.py
│   │   ├── cloudflare.py
│   │   ├── huggingface.py
│   │   ├── nvidia.py
│   │   ├── vercel.py
│   │   └── github_models.py
│   ├── image/
│   │   ├── stable_diffusion.py
│   │   ├── flux.py
│   │   ├── google_gemini_image.py
│   │   ├── adobe_firefly.py
│   │   ├── midjourney.py
│   │   ├── gpt_image.py
│   │   └── imagen.py
│   ├── speech/
│   │   ├── groq_speech.py
│   │   ├── google_tts.py
│   │   └── whisper_local.py
│   └── embeddings/
│       ├── huggingface_embeddings.py
│       ├── cloudflare_embeddings.py
│       └── openrouter_embeddings.py
├── models/
│   ├── local_llms.py
│   ├── hardware_recommendations.py
│   └── ecosystem_tools.py
├── trial_credits/
│   └── providers_with_credits.py
├── config/
│   ├── api_keys_template.py
│   └── settings.py
├── utils/
│   ├── rate_limiter.py
│   ├── retry_logic.py
│   └── helpers.py
├── tests/
│   └── test_providers.py
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

1. Copy the template configuration:
```bash
cp config/api_keys_template.py config/api_keys.py
```

2. Edit `config/api_keys.py` with your API keys for various providers.

## 📖 Usage Examples

### Basic LLM Usage

```python
from providers.llm.groq import GroqProvider
from providers.llm.google_ai_studio import GoogleAIStudioProvider

# Initialize providers
groq = GroqProvider()
google = GoogleAIStudioProvider()

# Get responses
response = groq.chat("Llama 3.1 8B", "Hello, how are you?")
print(response)

response = google.chat("Gemma 3 27B Instruct", "Explain quantum computing")
print(response)
```

### Image Generation

```python
from providers.image.stable_diffusion import StableDiffusionProvider

sd = StableDiffusionProvider()
image = sd.generate("A beautiful sunset over mountains")
image.save("sunset.png")
```

### Speech-to-Text

```python
from providers.speech.groq_speech import GroqSpeechProvider

speech = GroqSpeechProvider()
transcription = speech.transcribe("audio.mp3")
print(transcription)
```

## 📊 Provider Details

See the individual provider files for detailed information about:
- Rate limits and quotas
- Available models
- Authentication requirements
- Best use cases
- Limitations and considerations

## ⚠️ Important Notes

- Free tiers may change without notice
- Some providers require phone number verification
- Data usage policies vary (some use data for training)
- Commercial usage rights differ by provider
- Rate limits are per-account, not per-API-key

## 🔍 Research Methodology

This collection is based on comprehensive research conducted in June 2026, consulting:
- Official provider documentation
- GitHub repositories
- API pricing pages
- Developer blogs and tutorials
- Tech news articles

## 📋 CLI Commands Reference

### Installation
```bash
pip install -e .
```

### Quick Start
```bash
# Interactive mode
free-llm --interactive
free-llm -i

# Simple chat
free-llm chat "What is AI?"
```

### Chat Commands
```bash
# Basic chat
free-llm chat "Your prompt here"

# With specific provider and model
free-llm chat "Tell me a story" --provider groq --model llama-3.1-8b-instant

# Stream responses
free-llm chat "Explain quantum computing" --stream

# With temperature
free-llm chat "Write a poem" --temperature 0.9

# With max tokens
free-llm chat "Summarize this article" --max-tokens 500
```

### Provider & Model Commands
```bash
# List all providers
free-llm list

# List all models
free-llm list models

# List models for a specific provider
free-llm list models groq
free-llm list models openrouter

# Get provider information
free-llm info groq

# Get model information
free-llm info groq llama-3.1-8b-instant
```

### Health & Status Commands
```bash
# Check all providers health
free-llm health

# Check specific provider health
free-llm health groq
free-llm health openrouter
```

### Benchmarking Commands
```bash
# Run benchmark on default provider
free-llm benchmark

# Benchmark specific provider
free-llm benchmark --provider groq

# Benchmark with specific type
free-llm benchmark --provider groq --type latency
free-llm benchmark --provider groq --type throughput
free-llm benchmark --provider groq --type comprehensive

# Benchmark specific model
free-llm benchmark --provider groq --model llama-3.1-8b-instant --type comprehensive
```

### Configuration Commands
```bash
# Show current configuration
free-llm config

# Set default provider
free-llm config set default_provider groq

# Set default model
free-llm config set default_model llama-3.1-8b-instant

# Enable/disable caching
free-llm config set enable_caching true
free-llm config set enable_caching false

# Enable/disable health monitoring
free-llm config set enable_health_monitoring true

# Set maximum retries
free-llm config set max_retries 3

# Set retry delay
free-llm config set retry_delay 2.0
```

### Statistics Commands
```bash
# Show API statistics
free-llm stats

# Show detailed statistics
free-llm stats --detailed
```

### Utility Commands
```bash
# Check version
free-llm --version
free-llm -v

# Show help
free-llm --help
free-llm -h
```

### Interactive Mode Commands
```
$ free-llm --interactive

Free LLM API - Interactive Mode
============================================================

Available commands:
  chat [prompt]           - Start a chat session
  list                   - List all providers and models
  list models            - List all available models
  list models [provider] - List models for a specific provider
  info [provider]        - Show provider information
  info [provider] [model] - Show model information
  health                 - Check provider health status
  health [provider]      - Check specific provider health
  benchmark              - Run performance benchmarks
  config                 - Show current configuration
  config set [key] [val] - Set configuration value
  stats                  - Show API usage statistics
  help                   - Show this help message
  exit                   - Exit interactive mode
  quit                   - Exit interactive mode

Examples:
  free-llm> chat "What is machine learning?"
  free-llm> chat "Write a story" --provider groq --stream
  free-llm> list
  free-llm> info groq
  free-llm> health
  free-llm> exit
```
