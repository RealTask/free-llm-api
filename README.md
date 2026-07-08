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

## 📝 Contributing

Contributions are welcome! Please ensure:
1. All new providers are tested
2. Rate limits and quotas are verified
3. Documentation is updated
4. Follow the existing code structure

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- All the API providers for offering free tiers
- The open-source community for their contributions
- Researchers and developers who shared their findings

---

**Last Updated**: July 7, 2026
**Maintainer**: [RealTask](https://github.com/RealTask)
**Research Source**: Free AI Model APIs in 2026: Comprehensive Research Report
