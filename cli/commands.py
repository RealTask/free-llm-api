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


# Command registry
COMMANDS = {
    "chat": ChatCommand,
    "list": ListCommand,
    "info": InfoCommand,
    "benchmark": BenchmarkCommand,
    "health": HealthCommand,
    "config": ConfigCommand,
    "stats": StatsCommand,
}
