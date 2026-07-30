# Free LLM API - Makefile
# Production-ready build automation for the Free LLM API project

.PHONY: help install dev-install requirements test lint format clean build publish docs server cli interactive health benchmark config stats

# Default target
help: ## Display this help message
	@echo "Free LLM API - Available Commands"
	@echo "=================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Installation
install: ## Install production dependencies
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

dev-install: ## Install in development mode with all dev dependencies
	@echo "Installing in development mode with dev dependencies..."
	pip install -e ".[dev,all]"

requirements: ## Install/upgrade all requirements
	@echo "Installing/upgrading requirements..."
	pip install --upgrade -r requirements.txt
	pip install --upgrade -e ".[dev,all]"

# Testing & Quality
test: ## Run tests with pytest
	@echo "Running tests..."
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

lint: ## Run linters (mypy, ruff)
	@echo "Running linters..."
	mypy . --ignore-missing-imports || true
	ruff check .

format: ## Format code with black and isort
	@echo "Formatting code..."
	black .
	isort .

check: ## Run all checks (lint + test)
	@echo "Running all checks..."
	$(MAKE) lint
	$(MAKE) test

# Build & Distribution
clean: ## Clean build artifacts and cache
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Clean complete!"

build: ## Build package for distribution
	@echo "Building package..."
	$(MAKE) clean
	python setup.py sdist bdist_wheel
	@echo "Build complete! Check dist/ directory"

publish: ## Publish package to PyPI (requires twine)
	@echo "Publishing package to PyPI..."
	@echo "WARNING: This will publish to PyPI. Make sure you have twine installed and configured."
	twine upload dist/*
	@echo "Publish complete!"

publish-test: ## Publish package to TestPyPI
	@echo "Publishing package to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "Publish to TestPyPI complete!"

# Documentation
docs: ## Generate documentation (placeholder for future docs)
	@echo "Documentation generation placeholder"
	@echo "Future: Generate Sphinx or MkDocs documentation"

# Server & CLI
server: ## Start the FastAPI web server
	@echo "Starting FastAPI web server..."
	free-llm-server --host 0.0.0.0 --port 8000

server-reload: ## Start the FastAPI web server with auto-reload
	@echo "Starting FastAPI web server with auto-reload..."
	free-llm-server --host 0.0.0.0 --port 8000 --reload

cli: ## Run the CLI tool
	@echo "Free LLM API CLI"
	@echo "Usage: free-llm [command] [options]"
	@echo ""
	free-llm --help

interactive: ## Start interactive CLI mode
	@echo "Starting interactive CLI mode..."
	free-llm --interactive

# Utility Commands
health: ## Check health of all providers
	@echo "Checking provider health..."
	free-llm health

benchmark: ## Run benchmarks on default provider
	@echo "Running benchmarks..."
	free-llm benchmark

benchmark-all: ## Run comprehensive benchmarks on all providers
	@echo "Running comprehensive benchmarks on all providers..."
	@for provider in groq google_ai_studio openrouter mistral; do \
		echo "Benchmarking $$provider..."; \
		free-llm benchmark --provider $$provider --type comprehensive || true; \
	done

config: ## Show current configuration
	@echo "Current configuration:"
	free-llm config

stats: ## Show API usage statistics
	@echo "API usage statistics:"
	free-llm stats

list-providers: ## List all available providers
	@echo "Available providers:"
	free-llm list

list-models: ## List all available models
	@echo "Available models:"
	free-llm list models

# Development Helpers
setup-config: ## Setup configuration from template
	@echo "Setting up configuration..."
	cp -n config/api_keys_template.py config/api_keys.py || echo "Config already exists"
	@echo "Configuration setup complete! Edit config/api_keys.py with your API keys"

venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created!"
	@echo "Activate it with: source venv/bin/activate"

activate: ## Print activation command for virtual environment
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"

# CI/CD
ci: ## Run CI pipeline (install, lint, test)
	@echo "Running CI pipeline..."
	$(MAKE) dev-install
	$(MAKE) lint
	$(MAKE) test-cov

# Version Management
version: ## Show current version
	@echo "Current version:"
	@grep -m1 "version=" setup.py | cut -d'"' -f2

bump-patch: ## Bump patch version (x.y.z -> x.y.z+1)
	@echo "Bumping patch version..."
	@python -c "import re; f='setup.py'; content=open(f).read(); v=re.search(r'version=\"(\d+)\.(\d+)\.(\d+)\"', content); new_v=f'{v.group(1)}.{v.group(2)}.{int(v.group(3))+1}'; content=re.sub(r'version=\"\d+\.\d+\.\d+\"', f'version=\"{new_v}\"', content); open(f,'w').write(content); print(f'Version bumped to {new_v}')"

bump-minor: ## Bump minor version (x.y.z -> x.y+1.0)
	@echo "Bumping minor version..."
	@python -c "import re; f='setup.py'; content=open(f).read(); v=re.search(r'version=\"(\d+)\.(\d+)\.(\d+)\"', content); new_v=f'{v.group(1)}.{int(v.group(2))+1}.0'; content=re.sub(r'version=\"\d+\.\d+\.\d+\"', f'version=\"{new_v}\"', content); open(f,'w').write(content); print(f'Version bumped to {new_v}')"

bump-major: ## Bump major version (x.y.z -> x+1.0.0)
	@echo "Bumping major version..."
	@python -c "import re; f='setup.py'; content=open(f).read(); v=re.search(r'version=\"(\d+)\.(\d+)\.(\d+)\"', content); new_v=f'{int(v.group(1))+1}.0.0'; content=re.sub(r'version=\"\d+\.\d+\.\d+\"', f'version=\"{new_v}\"', content); open(f,'w').write(content); print(f'Version bumped to {new_v}')"
