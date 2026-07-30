"""
CLI Commands

Command implementations for the CLI.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from free_llm_api import FreeLLMAPI, FreeLLMAPIConfig

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a CLI command."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class BaseCommand:
    """Base class for CLI commands."""
    
    def __init__(self, api: FreeLLMAPI):
        self.api = api
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute the command."""
        raise NotImplementedError
    
    def get_help(self) -> str:
        """Get help text for the command."""
        return ""
    
    def get_usage(self) -> str:
        """Get usage text for the command."""
        return ""


class ChatCommand(BaseCommand):
    """Command for chatting with LLMs."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute chat command."""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: chat <prompt> [options]",
                error="No prompt provided",
            )
        
        # Parse arguments
        prompt = " ".join(args)
        provider = None
        model = None
        temperature = 0.7
        max_tokens = None
        stream = False
        
        # Simple argument parsing (for more complex parsing, use argparse)
        if "--provider" in args:
            idx = args.index("--provider")
            if idx + 1 < len(args):
                provider = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        
        if "--model" in args:
            idx = args.index("--model")
            if idx + 1 < len(args):
                model = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        
        if "--temperature" in args:
            idx = args.index("--temperature")
            if idx + 1 < len(args):
                try:
                    temperature = float(args[idx + 1])
                except ValueError:
                    pass
                args = args[:idx] + args[idx + 2:]
        
        if "--max-tokens" in args:
            idx = args.index("--max-tokens")
            if idx + 1 < len(args):
                try:
                    max_tokens = int(args[idx + 1])
                except ValueError:
                    pass
                args = args[:idx] + args[idx + 2:]
        
        if "--stream" in args:
            stream = True
            args = [a for a in args if a != "--stream"]
        
        # Rebuild prompt from remaining args
        prompt = " ".join(args)
        
        if not prompt:
            return CommandResult(
                success=False,
                message="No prompt provided",
                error="Please provide a prompt",
            )
        
        try:
            if stream:
                # Streaming mode
                print("\n" + "=" * 50)
                print(f"Streaming response (provider: {provider or 'auto'}, model: {model or 'auto'})")
                print("=" * 50 + "\n")
                
                async for chunk in self.api.stream(
                    prompt,
                    model=model,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    print(chunk.content, end="", flush=True)
                
                print("\n\n" + "=" * 50)
                print("Streaming complete")
                print("=" * 50)
                
                return CommandResult(
                    success=True,
                    message="Streaming complete",
                )
            else:
                # Non-streaming mode
                result = await self.api.chat(
                    prompt,
                    model=model,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                if result.success:
                    print("\n" + "=" * 50)
                    print(f"Response from {result.provider}/{result.model}")
                    print(f"Latency: {result.latency_ms:.2f}ms")
                    print("=" * 50 + "\n")
                    print(result.content)
                    print("\n" + "=" * 50)
                    
                    return CommandResult(
                        success=True,
                        message="Chat completed",
                        data={
                            "provider": result.provider,
                            "model": result.model,
                            "latency_ms": result.latency_ms,
                            "cached": result.cached,
                        },
                    )
                else:
                    return CommandResult(
                        success=False,
                        message="Chat failed",
                        error=result.error,
                    )
                    
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error during chat",
                error=str(e),
            )
    
    def get_help(self) -> str:
        return """
Chat with an LLM

Usage:
  chat <prompt> [options]

Options:
  --provider <name>   Specify provider (e.g., groq, openrouter)
  --model <name>      Specify model
  --temperature <t>   Set temperature (0.0-1.0)
  --max-tokens <n>    Set maximum tokens
  --stream           Enable streaming mode

Examples:
  chat "What is AI?"
  chat "Tell me a story" --provider groq --model llama-3.1-8b-instant
  chat "Explain quantum computing" --stream
"""
    
    def get_usage(self) -> str:
        return "chat <prompt> [options]"


class ListCommand(BaseCommand):
    """Command for listing providers and models."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute list command."""
        if not args:
            # List all providers
            providers = self.api.list_providers()
            
            print("\n" + "=" * 50)
            print("Available Providers")
            print("=" * 50 + "\n")
            
            for provider in providers:
                info = self.api.get_provider_info(provider)
                if info:
                    status = info.get("status", "unknown")
                    models_count = len(info.get("models", []))
                    print(f"  {provider:20} [{status:12}] - {models_count} models")
            
            print(f"\nTotal: {len(providers)} providers")
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message=f"Listed {len(providers)} providers",
                data={"providers": providers},
            )
        
        if args[0] == "models":
            # List models
            if len(args) > 1:
                provider = args[1]
                models = self.api.list_models(provider=provider)
            else:
                models = self.api.list_models()
            
            print("\n" + "=" * 50)
            print(f"Available Models {'for ' + provider if len(args) > 1 else ''}")
            print("=" * 50 + "\n")
            
            for model in models:
                print(f"  {model['provider']:20} - {model['model']:30} ({model.get('category', 'general')})")
            
            print(f"\nTotal: {len(models)} models")
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message=f"Listed {len(models)} models",
                data={"models": models},
            )
        
        return CommandResult(
            success=False,
            message="Unknown list command",
            error=f"Unknown argument: {args[0]}",
        )
    
    def get_help(self) -> str:
        return """
List providers and models

Usage:
  list [providers|models] [provider]

Commands:
  list              List all providers
  list models      List all models
  list models <p>  List models for provider <p>

Examples:
  list
  list models
  list models groq
"""
    
    def get_usage(self) -> str:
        return "list [providers|models] [provider]"


class InfoCommand(BaseCommand):
    """Command for getting provider/model information."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute info command."""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: info <provider> [model]",
                error="No provider specified",
            )
        
        provider = args[0]
        model = args[1] if len(args) > 1 else None
        
        if model:
            # Get model info
            info = self.api.get_model_info(provider, model)
            if not info:
                return CommandResult(
                    success=False,
                    message=f"Model {model} not found for provider {provider}",
                    error="Model not found",
                )
            
            print("\n" + "=" * 50)
            print(f"Model: {provider}/{model}")
            print("=" * 50 + "\n")
            
            for key, value in info.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")
            
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message=f"Showed info for {provider}/{model}",
                data=info,
            )
        else:
            # Get provider info
            info = self.api.get_provider_info(provider)
            if not info:
                return CommandResult(
                    success=False,
                    message=f"Provider {provider} not found",
                    error="Provider not found",
                )
            
            print("\n" + "=" * 50)
            print(f"Provider: {provider}")
            print("=" * 50 + "\n")
            
            print(f"  Category: {info.get('category', 'unknown')}")
            print(f"  Type: {info.get('type', 'unknown')}")
            print(f"  Status: {info.get('status', 'unknown')}")
            print(f"  Requires Auth: {info.get('requires_auth', False)}")
            print(f"  Commercial Usage: {info.get('commercial_usage_allowed', False)}")
            print(f"  Response Time: {info.get('response_time_avg', 0):.2f}s")
            print(f"  Success Rate: {info.get('success_rate', 0) * 100:.1f}%")
            
            print("\n  Rate Limits:")
            rate_limits = info.get("rate_limits", {})
            for key, value in rate_limits.items():
                if value is not None:
                    print(f"    {key}: {value}")
            
            print("\n  Models:")
            models = info.get("models", [])
            for model_info in models:
                print(f"    - {model_info.get('name', 'unknown')}")
            
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message=f"Showed info for {provider}",
                data=info,
            )
    
    def get_help(self) -> str:
        return """
Get provider or model information

Usage:
  info <provider> [model]

Examples:
  info groq
  info groq llama-3.1-8b-instant
"""
    
    def get_usage(self) -> str:
        return "info <provider> [model]"


class BenchmarkCommand(BaseCommand):
    """Command for running benchmarks."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute benchmark command."""
        provider = None
        model = None
        benchmark_type = "latency"
        
        # Parse arguments
        if "--provider" in args:
            idx = args.index("--provider")
            if idx + 1 < len(args):
                provider = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        
        if "--model" in args:
            idx = args.index("--model")
            if idx + 1 < len(args):
                model = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        
        if "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                benchmark_type = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        
        try:
            print("\n" + "=" * 50)
            print(f"Running benchmark (type: {benchmark_type})")
            if provider:
                print(f"Provider: {provider}")
            if model:
                print(f"Model: {model}")
            print("=" * 50 + "\n")
            
            results = await self.api.run_benchmark(
                provider=provider,
                model=model,
                benchmark_type=benchmark_type,
            )
            
            # Display results
            for key, result in results.items():
                print(f"\n{key}:")
                print(f"  Avg Latency: {result.get('avg_latency_ms', 0):.2f}ms")
                print(f"  Min Latency: {result.get('min_latency_ms', 0):.2f}ms")
                print(f"  Max Latency: {result.get('max_latency_ms', 0):.2f}ms")
                print(f"  Requests/sec: {result.get('requests_per_second', 0):.2f}")
                print(f"  Success Rate: {result.get('success_rate', 0) * 100:.1f}%")
                print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")
            
            print("\n" + "=" * 50)
            print("Benchmark complete")
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message="Benchmark completed",
                data=results,
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message="Benchmark failed",
                error=str(e),
            )
    
    def get_help(self) -> str:
        return """
Run benchmarks on providers

Usage:
  benchmark [options]

Options:
  --provider <name>   Benchmark specific provider
  --model <name>      Benchmark specific model
  --type <type>       Benchmark type (latency, throughput, quality, cost, comprehensive)

Examples:
  benchmark
  benchmark --provider groq --type latency
  benchmark --provider groq --model llama-3.1-8b-instant --type comprehensive
"""
    
    def get_usage(self) -> str:
        return "benchmark [options]"


class HealthCommand(BaseCommand):
    """Command for checking provider health."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute health command."""
        if not args:
            # Show health summary
            health = self.api.get_health_status()
            
            print("\n" + "=" * 50)
            print("Provider Health Summary")
            print("=" * 50 + "\n")
            
            print(f"Total Providers: {health.get('total_providers', 0)}")
            print(f"  Available: {health.get('available', 0)}")
            print(f"  Degraded: {health.get('degraded', 0)}")
            print(f"  Unavailable: {health.get('unavailable', 0)}")
            
            print("\nProvider Status:")
            for provider, info in health.get("providers", {}).items():
                status = info.get("status", "unknown")
                response_time = info.get("response_time", 0)
                consecutive_failures = info.get("consecutive_failures", 0)
                
                status_symbol = "✓" if status == "available" else "⚠" if status == "degraded" else "✗"
                print(f"  {status_symbol} {provider:20} [{status:12}] - {response_time:.2f}s response time")
            
            print("=" * 50)
            
            return CommandResult(
                success=True,
                message="Health summary displayed",
                data=health,
            )
        
        # Check specific provider
        provider = args[0]
        health = self.api.get_health_status(provider)
        
        if not health:
            return CommandResult(
                success=False,
                message=f"Provider {provider} not found",
                error="Provider not found",
            )
        
        print("\n" + "=" * 50)
        print(f"Health Status: {provider}")
        print("=" * 50 + "\n")
        
        for key, value in health.items():
            print(f"  {key}: {value}")
        
        print("=" * 50)
        
        return CommandResult(
            success=True,
            message=f"Health status for {provider}",
            data=health,
        )
    
    def get_help(self) -> str:
        return """
Check provider health status

Usage:
  health [provider]

Examples:
  health
  health groq
"""
    
    def get_usage(self) -> str:
        return "health [provider]"


class ConfigCommand(BaseCommand):
    """Command for managing configuration."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute config command."""
        if not args:
            # Show current config
            print("\n" + "=" * 50)
            print("Current Configuration")
            print("=" * 50 + "\n")
            
            config_dict = {
                "default_provider": self.api.config.default_provider,
                "default_model": self.api.config.default_model,
                "enable_caching": self.api.config.enable_caching,
                "enable_health_monitoring": self.api.config.enable_health_monitoring,
                "enable_benchmarking": self.api.config.enable_benchmarking,
                "default_streaming": self.api.config.default_streaming,
                "max_retries": self.api.config.max_retries,
                "retry_delay": self.api.config.retry_delay,
                "log_level": self.api.config.log_level,
            }
            
            for key, value in config_dict.items():
                print(f"  {key}: {value}")
            
            print("\n" + "=" * 50)
            
            return CommandResult(
                success=True,
                message="Configuration displayed",
                data=config_dict,
            )
        
        if args[0] == "set":
            if len(args) < 3:
                return CommandResult(
                    success=False,
                    message="Usage: config set <key> <value>",
                    error="Insufficient arguments",
                )
            
            key = args[1]
            value = args[2]
            
            # Update config
            if hasattr(self.api.config, key):
                # Convert value to appropriate type
                current_type = type(getattr(self.api.config, key))
                try:
                    if current_type == bool:
                        value = value.lower() in ("true", "1", "yes")
                    elif current_type == int:
                        value = int(value)
                    elif current_type == float:
                        value = float(value)
                except ValueError:
                    return CommandResult(
                        success=False,
                        message=f"Invalid value for {key}",
                        error="Value conversion failed",
                    )
                
                setattr(self.api.config, key, value)
                
                print(f"\nConfiguration updated: {key} = {value}")
                
                return CommandResult(
                    success=True,
                    message=f"Updated {key}",
                    data={key: value},
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"Unknown configuration key: {key}",
                    error="Key not found",
                )
        
        return CommandResult(
            success=False,
            message="Unknown config command",
            error=f"Unknown command: {args[0]}",
        )
    
    def get_help(self) -> str:
        return """
Manage configuration

Usage:
  config [show|set <key> <value>]

Commands:
  config              Show current configuration
  config set <k> <v>  Set configuration value

Examples:
  config
  config set default_provider groq
  config set enable_caching false
"""
    
    def get_usage(self) -> str:
        return "config [show|set <key> <value>]"


class StatsCommand(BaseCommand):
    """Command for showing statistics."""
    
    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)
    
    async def execute(self, args: List[str]) -> CommandResult:
        """Execute stats command."""
        stats = self.api.get_stats()
        
        print("\n" + "=" * 50)
        print("API Statistics")
        print("=" * 50 + "\n")
        
        print("Cache:")
        cache_stats = stats.get("cache", {})
        for cache_name, cache_info in cache_stats.items():
            print(f"  {cache_name}:")
            for key, value in cache_info.items():
                print(f"    {key}: {value}")
        
        print("\nRate Limiter:")
        rate_limiter_stats = stats.get("rate_limiter", {})
        for key, value in rate_limiter_stats.items():
            print(f"  {key}: {value}")
        
        print("\nOrchestrator:")
        orchestrator_stats = stats.get("orchestrator", {})
        for key, value in orchestrator_stats.items():
            print(f"  {key}: {value}")
        
        print("\nProviders:")
        providers_stats = stats.get("providers", {})
        for key, value in providers_stats.items():
            print(f"  {key}: {value}")
        
        print("=" * 50)
        
        return CommandResult(
            success=True,
            message="Statistics displayed",
            data=stats,
        )
    
    def get_help(self) -> str:
        return """
Show API statistics

Usage:
  stats

Examples:
  stats
"""
    
    def get_usage(self) -> str:
        return "stats"


class InstallCommand(BaseCommand):
    """Command for installing production dependencies."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute install command."""
        print("\n" + "=" * 50)
        print("Installing production dependencies...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["pip", "install", "-r", "requirements.txt"])
        
        if result.returncode == 0:
            print("\nInstallation complete!")
            return CommandResult(success=True, message="Installation complete")
        else:
            print("\nInstallation failed!")
            return CommandResult(success=False, message="Installation failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nInstall production dependencies\n\nUsage:\n  install\n\nExamples:\n  install\n"""

    def get_usage(self) -> str:
        return "install"


class DevInstallCommand(BaseCommand):
    """Command for installing in development mode."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute dev-install command."""
        print("\n" + "=" * 50)
        print("Installing in development mode with all dependencies...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["pip", "install", "-e", ".[dev,all]"])
        
        if result.returncode == 0:
            print("\nDevelopment installation complete!")
            return CommandResult(success=True, message="Development installation complete")
        else:
            print("\nDevelopment installation failed!")
            return CommandResult(success=False, message="Development installation failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nInstall in development mode with all dependencies\n\nUsage:\n  dev-install\n\nExamples:\n  dev-install\n"""

    def get_usage(self) -> str:
        return "dev-install"


class RequirementsCommand(BaseCommand):
    """Command for installing/upgrading all requirements."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute requirements command."""
        print("\n" + "=" * 50)
        print("Installing/upgrading requirements...")
        print("=" * 50 + "\n")
        
        import subprocess
        subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"])
        subprocess.run(["pip", "install", "--upgrade", "-e", ".[dev,all]"])
        
        print("\nRequirements upgrade complete!")
        return CommandResult(success=True, message="Requirements upgrade complete")

    def get_help(self) -> str:
        return """\nInstall/upgrade all requirements\n\nUsage:\n  requirements\n\nExamples:\n  requirements\n"""

    def get_usage(self) -> str:
        return "requirements"


class TestCommand(BaseCommand):
    """Command for running tests."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute test command."""
        print("\n" + "=" * 50)
        print("Running tests...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["pytest", "tests/", "-v"])
        
        if result.returncode == 0:
            print("\nAll tests passed!")
            return CommandResult(success=True, message="All tests passed")
        else:
            print("\nSome tests failed!")
            return CommandResult(success=False, message="Some tests failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nRun tests with pytest\n\nUsage:\n  test\n\nExamples:\n  test\n"""

    def get_usage(self) -> str:
        return "test"


class TestCovCommand(BaseCommand):
    """Command for running tests with coverage."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute test-cov command."""
        print("\n" + "=" * 50)
        print("Running tests with coverage...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term-missing"])
        
        if result.returncode == 0:
            print("\nTests with coverage complete!")
            return CommandResult(success=True, message="Tests with coverage complete")
        else:
            print("\nTests failed!")
            return CommandResult(success=False, message="Tests failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nRun tests with coverage report\n\nUsage:\n  test-cov\n\nExamples:\n  test-cov\n"""

    def get_usage(self) -> str:
        return "test-cov"


class LintCommand(BaseCommand):
    """Command for running linters."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute lint command."""
        print("\n" + "=" * 50)
        print("Running linters...")
        print("=" * 50 + "\n")
        
        import subprocess
        subprocess.run(["mypy", ".", "--ignore-missing-imports"])
        result = subprocess.run(["ruff", "check", "."])
        
        if result.returncode == 0:
            print("\nLinting complete!")
            return CommandResult(success=True, message="Linting complete")
        else:
            print("\nLinting found issues!")
            return CommandResult(success=False, message="Linting found issues")

    def get_help(self) -> str:
        return """\nRun linters (mypy, ruff)\n\nUsage:\n  lint\n\nExamples:\n  lint\n"""

    def get_usage(self) -> str:
        return "lint"


class FormatCommand(BaseCommand):
    """Command for formatting code."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute format command."""
        print("\n" + "=" * 50)
        print("Formatting code...")
        print("=" * 50 + "\n")
        
        import subprocess
        subprocess.run(["black", "."])
        subprocess.run(["isort", "."])
        
        print("\nFormatting complete!")
        return CommandResult(success=True, message="Formatting complete")

    def get_help(self) -> str:
        return """\nFormat code with black and isort\n\nUsage:\n  format\n\nExamples:\n  format\n"""

    def get_usage(self) -> str:
        return "format"


class CheckCommand(BaseCommand):
    """Command for running all checks."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute check command."""
        print("\n" + "=" * 50)
        print("Running all checks (lint + test)...")
        print("=" * 50 + "\n")
        
        lint_cmd = LintCommand(self.api)
        await lint_cmd.execute([])
        
        test_cmd = TestCommand(self.api)
        await test_cmd.execute([])
        
        print("\nAll checks complete!")
        return CommandResult(success=True, message="All checks complete")

    def get_help(self) -> str:
        return """\nRun all checks (lint + test)\n\nUsage:\n  check\n\nExamples:\n  check\n"""

    def get_usage(self) -> str:
        return "check"


class CleanCommand(BaseCommand):
    """Command for cleaning build artifacts."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute clean command."""
        print("\n" + "=" * 50)
        print("Cleaning build artifacts...")
        print("=" * 50 + "\n")
        
        import os
        import shutil
        
        dirs_to_remove = ["build", "dist", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov"]
        for d in dirs_to_remove:
            if os.path.exists(d):
                shutil.rmtree(d)
                print(f"Removed: {d}")
        
        # Remove egg-info directories
        for item in os.listdir("."):
            if item.endswith(".egg-info"):
                shutil.rmtree(item)
                print(f"Removed: {item}")
        
        # Remove __pycache__ and .pyc files
        for root, dirs, files in os.walk("."):
            if "__pycache__" in dirs:
                shutil.rmtree(os.path.join(root, "__pycache__"))
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyo"):
                    os.remove(os.path.join(root, f))
        
        print("\nClean complete!")
        return CommandResult(success=True, message="Clean complete")

    def get_help(self) -> str:
        return """\nClean build artifacts and cache\n\nUsage:\n  clean\n\nExamples:\n  clean\n"""

    def get_usage(self) -> str:
        return "clean"


class BuildCommand(BaseCommand):
    """Command for building the package."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute build command."""
        print("\n" + "=" * 50)
        print("Building package...")
        print("=" * 50 + "\n")
        
        clean_cmd = CleanCommand(self.api)
        await clean_cmd.execute([])
        
        import subprocess
        result = subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])
        
        if result.returncode == 0:
            print("\nBuild complete! Check dist/ directory")
            return CommandResult(success=True, message="Build complete")
        else:
            print("\nBuild failed!")
            return CommandResult(success=False, message="Build failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nBuild package for distribution\n\nUsage:\n  build\n\nExamples:\n  build\n"""

    def get_usage(self) -> str:
        return "build"


class PublishCommand(BaseCommand):
    """Command for publishing to PyPI."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute publish command."""
        print("\n" + "=" * 50)
        print("Publishing package to PyPI...")
        print("WARNING: This will publish to PyPI. Make sure you have twine installed and configured.")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["twine", "upload", "dist/*"])
        
        if result.returncode == 0:
            print("\nPublish complete!")
            return CommandResult(success=True, message="Publish complete")
        else:
            print("\nPublish failed!")
            return CommandResult(success=False, message="Publish failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nPublish package to PyPI (requires twine)\n\nUsage:\n  publish\n\nExamples:\n  publish\n"""

    def get_usage(self) -> str:
        return "publish"


class PublishTestCommand(BaseCommand):
    """Command for publishing to TestPyPI."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute publish-test command."""
        print("\n" + "=" * 50)
        print("Publishing package to TestPyPI...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["twine", "upload", "--repository", "testpypi", "dist/*"])
        
        if result.returncode == 0:
            print("\nPublish to TestPyPI complete!")
            return CommandResult(success=True, message="Publish to TestPyPI complete")
        else:
            print("\nPublish to TestPyPI failed!")
            return CommandResult(success=False, message="Publish to TestPyPI failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nPublish package to TestPyPI\n\nUsage:\n  publish-test\n\nExamples:\n  publish-test\n"""

    def get_usage(self) -> str:
        return "publish-test"


class DocsCommand(BaseCommand):
    """Command for generating documentation."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute docs command."""
        print("\n" + "=" * 50)
        print("Documentation generation placeholder")
        print("Future: Generate Sphinx or MkDocs documentation")
        print("=" * 50)
        return CommandResult(success=True, message="Documentation placeholder")

    def get_help(self) -> str:
        return """\nGenerate documentation (placeholder for future docs)\n\nUsage:\n  docs\n\nExamples:\n  docs\n"""

    def get_usage(self) -> str:
        return "docs"


class ServerCommand(BaseCommand):
    """Command for starting the FastAPI web server."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute server command."""
        print("\n" + "=" * 50)
        print("Starting FastAPI web server...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["llmapi-server", "--host", "0.0.0.0", "--port", "8000"])
        
        return CommandResult(success=True, message="Server started")

    def get_help(self) -> str:
        return """\nStart the FastAPI web server\n\nUsage:\n  server\n\nExamples:\n  server\n"""

    def get_usage(self) -> str:
        return "server"


class ServerReloadCommand(BaseCommand):
    """Command for starting the FastAPI web server with auto-reload."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute server-reload command."""
        print("\n" + "=" * 50)
        print("Starting FastAPI web server with auto-reload...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["llmapi-server", "--host", "0.0.0.0", "--port", "8000", "--reload"])
        
        return CommandResult(success=True, message="Server started with reload")

    def get_help(self) -> str:
        return """\nStart the FastAPI web server with auto-reload\n\nUsage:\n  server-reload\n\nExamples:\n  server-reload\n"""

    def get_usage(self) -> str:
        return "server-reload"


class InteractiveCommand(BaseCommand):
    """Command for starting interactive CLI mode."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute interactive command."""
        from cli.main import CLIApp
        
        cli = CLIApp()
        await cli.run_interactive()
        
        return CommandResult(success=True, message="Interactive mode complete")

    def get_help(self) -> str:
        return """\nStart interactive CLI mode\n\nUsage:\n  interactive\n\nExamples:\n  interactive\n"""

    def get_usage(self) -> str:
        return "interactive"


class BenchmarkAllCommand(BaseCommand):
    """Command for running comprehensive benchmarks on all providers."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute benchmark-all command."""
        print("\n" + "=" * 50)
        print("Running comprehensive benchmarks on all providers...")
        print("=" * 50 + "\n")
        
        providers = ["groq", "google_ai_studio", "openrouter", "mistral"]
        
        for provider in providers:
            print(f"\nBenchmarking {provider}...")
            bench_cmd = BenchmarkCommand(self.api)
            await bench_cmd.execute(["--provider", provider, "--type", "comprehensive"])
        
        print("\nBenchmark all complete!")
        return CommandResult(success=True, message="Benchmark all complete")

    def get_help(self) -> str:
        return """\nRun comprehensive benchmarks on all providers\n\nUsage:\n  benchmark-all\n\nExamples:\n  benchmark-all\n"""

    def get_usage(self) -> str:
        return "benchmark-all"


class SetupConfigCommand(BaseCommand):
    """Command for setting up configuration from template."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute setup-config command."""
        print("\n" + "=" * 50)
        print("Setting up configuration...")
        print("=" * 50 + "\n")
        
        import shutil
        import os
        
        src = "config/api_keys_template.py"
        dst = "config/api_keys.py"
        
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print("Configuration setup complete! Edit config/api_keys.py with your API keys")
            return CommandResult(success=True, message="Configuration setup complete")
        else:
            print("Config already exists")
            return CommandResult(success=True, message="Config already exists")

    def get_help(self) -> str:
        return """\nSetup configuration from template\n\nUsage:\n  setup-config\n\nExamples:\n  setup-config\n"""

    def get_usage(self) -> str:
        return "setup-config"


class VenvCommand(BaseCommand):
    """Command for creating virtual environment."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute venv command."""
        print("\n" + "=" * 50)
        print("Creating virtual environment...")
        print("=" * 50 + "\n")
        
        import subprocess
        result = subprocess.run(["python", "-m", "venv", "venv"])
        
        if result.returncode == 0:
            print("\nVirtual environment created!")
            print("Activate it with: source venv/bin/activate")
            return CommandResult(success=True, message="Virtual environment created")
        else:
            print("\nVirtual environment creation failed!")
            return CommandResult(success=False, message="Virtual environment creation failed", error=f"Exit code: {result.returncode}")

    def get_help(self) -> str:
        return """\nCreate virtual environment\n\nUsage:\n  venv\n\nExamples:\n  venv\n"""

    def get_usage(self) -> str:
        return "venv"


class ActivateCommand(BaseCommand):
    """Command for printing activation command."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute activate command."""
        print("\nTo activate the virtual environment, run:")
        print("  source venv/bin/activate")
        return CommandResult(success=True, message="Activation command printed")

    def get_help(self) -> str:
        return """\nPrint activation command for virtual environment\n\nUsage:\n  activate\n\nExamples:\n  activate\n"""

    def get_usage(self) -> str:
        return "activate"


class CICommand(BaseCommand):
    """Command for running CI pipeline."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute ci command."""
        print("\n" + "=" * 50)
        print("Running CI pipeline...")
        print("=" * 50 + "\n")
        
        dev_install = DevInstallCommand(self.api)
        await dev_install.execute([])
        
        lint = LintCommand(self.api)
        await lint.execute([])
        
        test_cov = TestCovCommand(self.api)
        await test_cov.execute([])
        
        print("\nCI pipeline complete!")
        return CommandResult(success=True, message="CI pipeline complete")

    def get_help(self) -> str:
        return """\nRun CI pipeline (install, lint, test)\n\nUsage:\n  ci\n\nExamples:\n  ci\n"""

    def get_usage(self) -> str:
        return "ci"


class VersionCommand(BaseCommand):
    """Command for showing current version."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute version command."""
        print("\nCurrent version:")
        
        import re
        with open("setup.py", "r") as f:
            content = f.read()
            match = re.search(r'version="(\d+\.\d+\.\d+)"', content)
            if match:
                print(match.group(1))
                return CommandResult(success=True, message=f"Version: {match.group(1)}", data=match.group(1))
        
        return CommandResult(success=False, message="Version not found")

    def get_help(self) -> str:
        return """\nShow current version\n\nUsage:\n  version\n\nExamples:\n  version\n"""

    def get_usage(self) -> str:
        return "version"


class BumpPatchCommand(BaseCommand):
    """Command for bumping patch version."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute bump-patch command."""
        print("\nBumping patch version...")
        
        import re
        with open("setup.py", "r") as f:
            content = f.read()
        
        match = re.search(r'version="(\d+)\.(\d+)\.(\d+)"', content)
        if match:
            major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
            new_version = f"{major}.{minor}.{patch + 1}"
            content = re.sub(r'version="\d+\.\d+\.\d+"', f'version="{new_version}"', content)
            with open("setup.py", "w") as f:
                f.write(content)
            print(f"Version bumped to {new_version}")
            return CommandResult(success=True, message=f"Version bumped to {new_version}", data=new_version)
        
        return CommandResult(success=False, message="Version not found")

    def get_help(self) -> str:
        return """\nBump patch version (x.y.z -> x.y.z+1)\n\nUsage:\n  bump-patch\n\nExamples:\n  bump-patch\n"""

    def get_usage(self) -> str:
        return "bump-patch"


class BumpMinorCommand(BaseCommand):
    """Command for bumping minor version."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute bump-minor command."""
        print("\nBumping minor version...")
        
        import re
        with open("setup.py", "r") as f:
            content = f.read()
        
        match = re.search(r'version="(\d+)\.(\d+)\.(\d+)"', content)
        if match:
            major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
            new_version = f"{major}.{minor + 1}.0"
            content = re.sub(r'version="\d+\.\d+\.\d+"', f'version="{new_version}"', content)
            with open("setup.py", "w") as f:
                f.write(content)
            print(f"Version bumped to {new_version}")
            return CommandResult(success=True, message=f"Version bumped to {new_version}", data=new_version)
        
        return CommandResult(success=False, message="Version not found")

    def get_help(self) -> str:
        return """\nBump minor version (x.y.z -> x.y+1.0)\n\nUsage:\n  bump-minor\n\nExamples:\n  bump-minor\n"""

    def get_usage(self) -> str:
        return "bump-minor"


class BumpMajorCommand(BaseCommand):
    """Command for bumping major version."""

    def __init__(self, api: FreeLLMAPI):
        super().__init__(api)

    async def execute(self, args: List[str]) -> CommandResult:
        """Execute bump-major command."""
        print("\nBumping major version...")
        
        import re
        with open("setup.py", "r") as f:
            content = f.read()
        
        match = re.search(r'version="(\d+)\.(\d+)\.(\d+)"', content)
        if match:
            major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
            new_version = f"{major + 1}.0.0"
            content = re.sub(r'version="\d+\.\d+\.\d+"', f'version="{new_version}"', content)
            with open("setup.py", "w") as f:
                f.write(content)
            print(f"Version bumped to {new_version}")
            return CommandResult(success=True, message=f"Version bumped to {new_version}", data=new_version)
        
        return CommandResult(success=False, message="Version not found")

    def get_help(self) -> str:
        return """\nBump major version (x.y.z -> x+1.0.0)\n\nUsage:\n  bump-major\n\nExamples:\n  bump-major\n"""

    def get_usage(self) -> str:
        return "bump-major"


# Command registry
COMMANDS = {
    "chat": ChatCommand,
    "list": ListCommand,
    "info": InfoCommand,
    "benchmark": BenchmarkCommand,
    "health": HealthCommand,
    "config": ConfigCommand,
    "stats": StatsCommand,
    "install": InstallCommand,
    "dev-install": DevInstallCommand,
    "requirements": RequirementsCommand,
    "test": TestCommand,
    "test-cov": TestCovCommand,
    "lint": LintCommand,
    "format": FormatCommand,
    "check": CheckCommand,
    "clean": CleanCommand,
    "build": BuildCommand,
    "publish": PublishCommand,
    "publish-test": PublishTestCommand,
    "docs": DocsCommand,
    "server": ServerCommand,
    "server-reload": ServerReloadCommand,
    "interactive": InteractiveCommand,
    "benchmark-all": BenchmarkAllCommand,
    "setup-config": SetupConfigCommand,
    "venv": VenvCommand,
    "activate": ActivateCommand,
    "ci": CICommand,
    "version": VersionCommand,
    "bump-patch": BumpPatchCommand,
    "bump-minor": BumpMinorCommand,
    "bump-major": BumpMajorCommand,
}

__all__ = ["COMMANDS", "CommandResult", "BaseCommand"]
