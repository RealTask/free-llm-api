# Free LLM API - Comprehensive Provider Collection

A curated collection of free LLM API providers with their capabilities, limitations, and best use cases based on 2026 research.

## 🚀 Quick Start Commands

### Installation & Setup
```bash
# Clone and install
git clone https://github.com/RealTask/free-llm-api.git
cd free-llm-api
pip install -e ".[all]"

# Set up API keys (copy template)
cp config/api_keys_template.py config/api_keys.py
# Edit config/api_keys.py with your API keys

# Verify installation
python -c "from free_llm_api import FreeLLMAPI; print('✓ Installation successful')"
```

### Basic Usage Commands
```bash
# Quick chat (auto-selects best provider)
free-llm chat "What is Artificial Intelligence?"

# Chat with specific provider and model
free-llm chat "Explain quantum computing" --provider groq --model llama-3.1-8b-instant

# Stream response in real-time
free-llm chat "Write a short story" --stream

# Get embedding for text
free-llm embed "Machine learning is fascinating" --provider openrouter

# Generate an image
free-llm image "A beautiful sunset over the ocean, digital art"
```

### Provider Management Commands
