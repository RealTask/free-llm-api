# Free LLM API - Comprehensive Provider Collection

A curated collection of free LLM API providers with their capabilities, limitations, and best use cases based on 2026 research.

## 🚀 Quick Start Commands

### Installation & Setup
```bash
git clone https://github.com/RealTask/free-llm-api.git
cd free-llm-api
pip install -e ".[all]"
cp config/api_keys_template.py config/api_keys.py
python -c "from free_llm_api import FreeLLMAPI; print('✓ Installation successful')"
```

### Basic Usage Commands
```bash
free-llm chat "What is Artificial Intelligence?"
free-llm chat "Explain quantum computing" --provider groq --model llama-3.1-8b-instant
free-llm chat "Write a short story" --stream
free-llm embed "Machine learning is fascinating" --provider openrouter
free-llm image "A beautiful sunset over the ocean, digital art"
```

### Provider Management Commands
```bash
free-llm list
free-llm list models
free-llm list models groq
free-llm info groq
free-llm info groq llama-3.1-8b-instant
free-llm search "image generation"
```

### Health & Monitoring Commands
```bash
free-llm health
free-llm health groq
free-llm health --watch --interval 30
free-llm test groq
```

### Benchmarking Commands
```bash
free-llm benchmark --provider groq
free-llm benchmark --provider groq --model llama-3.1-8b-instant --type latency
free-llm benchmark --providers groq,openrouter,mistral --type throughput
free-llm benchmark --all
free-llm benchmark --results
```

### Configuration Commands
```bash
free-llm config
free-llm config set default_provider groq
free-llm config set default_model llama-3.1-8b-instant
free-llm config set enable_caching true
free-llm config set enable_health_monitoring true
free-llm config set max_retries 3
free-llm config reset
```

### Advanced Usage Commands
```bash
free-llm --interactive
free-llm -i
free-llm batch --file prompts.txt --output responses.json
GROQ_API_KEY=your_key free-llm chat "Hello"
free-llm --debug chat "Test message"
free-llm chat "Explain AI" --save conversation.txt
```

### Web Server Commands
```bash
free-llm-server
free-llm-server --reload
free-llm-server --host 0.0.0.0 --port 8000
free-llm-server --config config/production.yaml
```

### Docker Commands
```bash
docker build -t free-llm-api .
docker run -p 8000:8000 free-llm-api
docker run -p 8000:8000 -e GROQ_API_KEY=your_key free-llm-api
docker run -p 8000:8000 -v $(pwd)/config:/app/config free-llm-api
```

### Statistics & Analytics Commands
```bash
free-llm stats
free-llm stats --detailed
free-llm stats --export stats.json
free-llm stats --reset
```

### Cache Management Commands
```bash
free-llm cache clear
free-llm cache clear --type response
free-llm cache clear --type embedding
free-llm cache clear --type image
free-llm cache stats
free-llm cache enable
free-llm cache disable
```

---

successfully downloaded text file (SHA: 7cdafd36cb6187f61c4da13504ef61543f2ed0fc)