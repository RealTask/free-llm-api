"""
Benchmarking

Comprehensive benchmarking for AI providers and models.
"""

import asyncio
import csv
import json
import logging
import os
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum

from core.models import (
    ProviderMetadata,
    ModelMetadata,
    PerformanceMetrics,
)
from core.provider_registry import ProviderRegistry, get_registry

logger = logging.getLogger(__name__)


class BenchmarkType(Enum):
    """Types of benchmarks."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    QUALITY = "quality"
    COST = "cost"
    COMPREHENSIVE = "comprehensive"


class QualityMetric(Enum):
    """Quality metrics for benchmarking."""
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    CREATIVITY = "creativity"
    ACCURACY = "accuracy"
    FLUENCY = "fluency"


@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking."""
    # Test parameters
    num_requests: int = 10
    warmup_requests: int = 3
    max_tokens: int = 100
    temperature: float = 0.7
    
    # Prompts for testing
    prompts: List[str] = field(default_factory=lambda: [
        "Explain the concept of machine learning in simple terms.",
        "Write a short poem about artificial intelligence.",
        "What are the key differences between Python and JavaScript?",
        "Suggest 5 creative uses for AI in everyday life.",
        "Explain quantum computing to a 10-year-old.",
    ])
    
    # Benchmark types
    run_latency_test: bool = True
    run_throughput_test: bool = True
    run_quality_test: bool = False  # Requires human evaluation
    run_cost_test: bool = True
    
    # Timeouts
    timeout_per_request: float = 60.0  # seconds
    overall_timeout: float = 300.0  # seconds
    
    # Output
    output_dir: str = "benchmarks"
    output_format: str = "json"  # json, csv
    
    # Callbacks
    on_benchmark_start: Optional[Callable[[str, str], None]] = None
    on_benchmark_complete: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    on_benchmark_error: Optional[Callable[[str, str, str], None]] = None


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    provider: str
    model: str
    benchmark_type: BenchmarkType
    
    # Metrics
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    std_latency_ms: float = 0.0
    
    requests_per_second: float = 0.0
    tokens_per_second: float = 0.0
    
    quality_scores: Dict[str, float] = field(default_factory=dict)
    avg_quality: float = 0.0
    
    cost_per_request: float = 0.0
    cost_per_token: float = 0.0
    
    success_rate: float = 0.0
    error_rate: float = 0.0
    
    # Details
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    responses: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    num_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "benchmark_type": self.benchmark_type.value,
            "avg_latency_ms": self.avg_latency_ms,
            "min_latency_ms": self.min_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "std_latency_ms": self.std_latency_ms,
            "requests_per_second": self.requests_per_second,
            "tokens_per_second": self.tokens_per_second,
            "quality_scores": self.quality_scores,
            "avg_quality": self.avg_quality,
            "cost_per_request": self.cost_per_request,
            "cost_per_token": self.cost_per_token,
            "success_rate": self.success_rate,
            "error_rate": self.error_rate,
            "num_requests": self.num_requests,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_csv_row(self) -> List[str]:
        """Convert to CSV row."""
        return [
            self.provider,
            self.model,
            self.benchmark_type.value,
            str(self.avg_latency_ms),
            str(self.min_latency_ms),
            str(self.max_latency_ms),
            str(self.std_latency_ms),
            str(self.requests_per_second),
            str(self.tokens_per_second),
            str(self.avg_quality),
            str(self.cost_per_request),
            str(self.cost_per_token),
            str(self.success_rate),
            str(self.error_rate),
            str(self.num_requests),
            str(self.duration_seconds),
            self.timestamp.isoformat(),
        ]
    
    @classmethod
    def get_csv_headers(cls) -> List[str]:
        """Get CSV headers."""
        return [
            "provider",
            "model",
            "benchmark_type",
            "avg_latency_ms",
            "min_latency_ms",
            "max_latency_ms",
            "std_latency_ms",
            "requests_per_second",
            "tokens_per_second",
            "avg_quality",
            "cost_per_request",
            "cost_per_token",
            "success_rate",
            "error_rate",
            "num_requests",
            "duration_seconds",
            "timestamp",
        ]


class BenchmarkRunner:
    """
    Run benchmarks on AI providers and models.
    
    Supports latency, throughput, quality, and cost benchmarks.
    """
    
    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        config: Optional[BenchmarkConfig] = None,
    ):
        self.registry = registry or get_registry()
        self.config = config or BenchmarkConfig()
        self._output_dir = Path(self.config.output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._current_benchmark: Optional[str] = None
    
    async def initialize(self):
        """Initialize the benchmark runner."""
        await self.registry.initialize()
        logger.info("Benchmark runner initialized")
    
    async def run_benchmark(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        benchmark_type: BenchmarkType = BenchmarkType.COMPREHENSIVE,
    ) -> Dict[str, BenchmarkResult]:
        """
        Run a benchmark on a provider/model.
        
        Args:
            provider: Provider name (None for all providers)
            model: Model name (None for all models)
            benchmark_type: Type of benchmark to run
            
        Returns:
            Dict[str, BenchmarkResult]: Benchmark results keyed by provider_model
        """
        if self._running:
            raise Exception("Benchmark already in progress")
        
        self._running = True
        self._current_benchmark = f"{benchmark_type.value}_{provider or 'all'}_{model or 'all'}"
        
        try:
            # Get providers to test
            if provider:
                providers = [provider]
            else:
                providers = self.registry.list_providers()
            
            results = {}
            
            for p in providers:
                provider_metadata = self.registry.get_metadata(p)
                if not provider_metadata:
                    continue
                
                # Get models to test
                if model:
                    models = [m for m in provider_metadata.models if m.name == model]
                else:
                    models = provider_metadata.models
                
                for m in models:
                    key = f"{p}_{m.name}"
                    
                    if self.config.on_benchmark_start:
                        self.config.on_benchmark_start(p, m.name)
                    
                    try:
                        if benchmark_type == BenchmarkType.LATENCY:
                            result = await self._run_latency_benchmark(p, m.name)
                        elif benchmark_type == BenchmarkType.THROUGHPUT:
                            result = await self._run_throughput_benchmark(p, m.name)
                        elif benchmark_type == BenchmarkType.QUALITY:
                            result = await self._run_quality_benchmark(p, m.name)
                        elif benchmark_type == BenchmarkType.COST:
                            result = await self._run_cost_benchmark(p, m.name)
                        elif benchmark_type == BenchmarkType.COMPREHENSIVE:
                            result = await self._run_comprehensive_benchmark(p, m.name)
                        else:
                            result = await self._run_latency_benchmark(p, m.name)
                        
                        results[key] = result
                        
                        if self.config.on_benchmark_complete:
                            self.config.on_benchmark_complete(p, m.name, result.to_dict())
                        
                    except Exception as e:
                        logger.error(f"Error benchmarking {p}/{m.name}: {e}")
                        if self.config.on_benchmark_error:
                            self.config.on_benchmark_error(p, m.name, str(e))
            
            # Save results
            await self._save_results(results, benchmark_type)
            
            return results
            
        finally:
            self._running = False
            self._current_benchmark = None
    
    async def _run_latency_benchmark(
        self,
        provider: str,
        model: str,
    ) -> BenchmarkResult:
        """Run a latency benchmark."""
        start_time = time.time()
        
        provider_instance = self.registry.get_provider(provider)
        if not provider_instance:
            raise Exception(f"Provider {provider} not available")
        
        latencies = []
        errors = []
        responses = []
        
        # Warmup
        for _ in range(self.config.warmup_requests):
            try:
                await provider_instance.chat(
                    model,
                    self.config.prompts[0],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
            except Exception as e:
                logger.warning(f"Warmup error for {provider}/{model}: {e}")
        
        # Actual test
        for prompt in self.config.prompts[:self.config.num_requests]:
            try:
                request_start = time.time()
                response = await asyncio.wait_for(
                    provider_instance.chat(
                        model,
                        prompt,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    ),
                    timeout=self.config.timeout_per_request,
                )
                latency = (time.time() - request_start) * 1000  # ms
                
                latencies.append(latency)
                responses.append(response)
                
            except Exception as e:
                errors.append(str(e))
                latencies.append(self.config.timeout_per_request * 1000)  # Use timeout as latency
        
        duration = time.time() - start_time
        num_requests = len(self.config.prompts[:self.config.num_requests])
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        success_rate = (num_requests - len(errors)) / num_requests if num_requests > 0 else 0
        error_rate = len(errors) / num_requests if num_requests > 0 else 0
        
        return BenchmarkResult(
            provider=provider,
            model=model,
            benchmark_type=BenchmarkType.LATENCY,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            std_latency_ms=std_latency,
            requests_per_second=num_requests / duration if duration > 0 else 0,
            success_rate=success_rate,
            error_rate=error_rate,
            latencies=latencies,
            errors=errors,
            responses=responses,
            duration_seconds=duration,
            num_requests=num_requests,
        )
    
    async def _run_throughput_benchmark(
        self,
        provider: str,
        model: str,
    ) -> BenchmarkResult:
        """Run a throughput benchmark."""
        start_time = time.time()
        
        provider_instance = self.registry.get_provider(provider)
        if not provider_instance:
            raise Exception(f"Provider {provider} not available")
        
        latencies = []
        errors = []
        responses = []
        total_tokens = 0
        
        # Warmup
        for _ in range(self.config.warmup_requests):
            try:
                await provider_instance.chat(
                    model,
                    self.config.prompts[0],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
            except Exception as e:
                logger.warning(f"Warmup error for {provider}/{model}: {e}")
        
        # Actual test - run requests concurrently
        tasks = []
        for prompt in self.config.prompts[:self.config.num_requests]:
            task = asyncio.create_task(
                self._run_single_request(
                    provider_instance,
                    model,
                    prompt,
                )
            )
            tasks.append(task)
        
        # Wait for all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                latencies.append(self.config.timeout_per_request * 1000)
            else:
                latency, response, tokens = result
                latencies.append(latency * 1000)
                responses.append(response)
                total_tokens += tokens
        
        duration = time.time() - start_time
        num_requests = len(self.config.prompts[:self.config.num_requests])
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        success_rate = (num_requests - len(errors)) / num_requests if num_requests > 0 else 0
        error_rate = len(errors) / num_requests if num_requests > 0 else 0
        
        return BenchmarkResult(
            provider=provider,
            model=model,
            benchmark_type=BenchmarkType.THROUGHPUT,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            std_latency_ms=std_latency,
            requests_per_second=num_requests / duration if duration > 0 else 0,
            tokens_per_second=total_tokens / duration if duration > 0 else 0,
            success_rate=success_rate,
            error_rate=error_rate,
            latencies=latencies,
            errors=errors,
            responses=responses,
            duration_seconds=duration,
            num_requests=num_requests,
        )
    
    async def _run_single_request(
        self,
        provider_instance,
        model: str,
        prompt: str,
    ) -> tuple:
        """Run a single request for throughput test."""
        start = time.time()
        try:
            response = await asyncio.wait_for(
                provider_instance.chat(
                    model,
                    prompt,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                ),
                timeout=self.config.timeout_per_request,
            )
            latency = time.time() - start
            tokens = len(response.split())  # Approximate token count
            return (latency, response, tokens)
        except Exception as e:
            raise e
    
    async def _run_quality_benchmark(
        self,
        provider: str,
        model: str,
    ) -> BenchmarkResult:
        """
        Run a quality benchmark.
        
        Note: This requires human evaluation or a separate evaluation model.
        For now, this is a placeholder that returns dummy scores.
        """
        start_time = time.time()
        
        provider_instance = self.registry.get_provider(provider)
        if not provider_instance:
            raise Exception(f"Provider {provider} not available")
        
        # For now, just run the prompts and return dummy quality scores
        # In a real implementation, you would:
        # 1. Generate responses
        # 2. Evaluate them using human evaluators or an evaluation model
        # 3. Calculate quality scores
        
        responses = []
        errors = []
        
        for prompt in self.config.prompts[:self.config.num_requests]:
            try:
                response = await asyncio.wait_for(
                    provider_instance.chat(
                        model,
                        prompt,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    ),
                    timeout=self.config.timeout_per_request,
                )
                responses.append(response)
            except Exception as e:
                errors.append(str(e))
        
        duration = time.time() - start_time
        num_requests = len(self.config.prompts[:self.config.num_requests])
        
        # Dummy quality scores (in a real implementation, these would be calculated)
        quality_scores = {
            QualityMetric.COHERENCE.value: 0.85,
            QualityMetric.RELEVANCE.value: 0.90,
            QualityMetric.CREATIVITY.value: 0.75,
            QualityMetric.ACCURACY.value: 0.80,
            QualityMetric.FLUENCY.value: 0.95,
        }
        avg_quality = statistics.mean(quality_scores.values())
        
        success_rate = (num_requests - len(errors)) / num_requests if num_requests > 0 else 0
        error_rate = len(errors) / num_requests if num_requests > 0 else 0
        
        return BenchmarkResult(
            provider=provider,
            model=model,
            benchmark_type=BenchmarkType.QUALITY,
            quality_scores=quality_scores,
            avg_quality=avg_quality,
            success_rate=success_rate,
            error_rate=error_rate,
            errors=errors,
            responses=responses,
            duration_seconds=duration,
            num_requests=num_requests,
        )
    
    async def _run_cost_benchmark(
        self,
        provider: str,
        model: str,
    ) -> BenchmarkResult:
        """Run a cost benchmark."""
        start_time = time.time()
        
        provider_instance = self.registry.get_provider(provider)
        if not provider_instance:
            raise Exception(f"Provider {provider} not available")
        
        metadata = self.registry.get_metadata(provider)
        if not metadata:
            raise Exception(f"Provider {provider} metadata not found")
        
        # Get model metadata
        model_metadata = None
        for m in metadata.models:
            if m.name == model:
                model_metadata = m
                break
        
        if not model_metadata:
            raise Exception(f"Model {model} not found for provider {provider}")
        
        # For free providers, cost is 0
        # For paid providers, we would calculate based on pricing
        cost_per_request = 0.0
        cost_per_token = 0.0
        
        # Check if there's pricing information
        if model_metadata.pricing:
            cost_per_request = model_metadata.pricing.get("cost_per_request", 0.0)
            cost_per_token = model_metadata.pricing.get("cost_per_token", 0.0)
        
        # Run a few requests to get token counts
        total_tokens = 0
        for prompt in self.config.prompts[:min(3, self.config.num_requests)]:
            try:
                response = await asyncio.wait_for(
                    provider_instance.chat(
                        model,
                        prompt,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    ),
                    timeout=self.config.timeout_per_request,
                )
                total_tokens += len(response.split())
            except Exception:
                pass
        
        duration = time.time() - start_time
        num_requests = min(3, self.config.num_requests)
        
        return BenchmarkResult(
            provider=provider,
            model=model,
            benchmark_type=BenchmarkType.COST,
            cost_per_request=cost_per_request,
            cost_per_token=cost_per_token,
            success_rate=1.0,
            error_rate=0.0,
            duration_seconds=duration,
            num_requests=num_requests,
        )
    
    async def _run_comprehensive_benchmark(
        self,
        provider: str,
        model: str,
    ) -> BenchmarkResult:
        """Run a comprehensive benchmark combining all tests."""
        # Run individual benchmarks
        latency_result = await self._run_latency_benchmark(provider, model)
        throughput_result = await self._run_throughput_benchmark(provider, model)
        cost_result = await self._run_cost_benchmark(provider, model)
        
        # Combine results
        return BenchmarkResult(
            provider=provider,
            model=model,
            benchmark_type=BenchmarkType.COMPREHENSIVE,
            avg_latency_ms=latency_result.avg_latency_ms,
            min_latency_ms=latency_result.min_latency_ms,
            max_latency_ms=latency_result.max_latency_ms,
            std_latency_ms=latency_result.std_latency_ms,
            requests_per_second=throughput_result.requests_per_second,
            tokens_per_second=throughput_result.tokens_per_second,
            cost_per_request=cost_result.cost_per_request,
            cost_per_token=cost_result.cost_per_token,
            success_rate=latency_result.success_rate,
            error_rate=latency_result.error_rate,
            latencies=latency_result.latencies,
            errors=latency_result.errors + throughput_result.errors + cost_result.errors,
            responses=latency_result.responses,
            duration_seconds=latency_result.duration_seconds + throughput_result.duration_seconds + cost_result.duration_seconds,
            num_requests=latency_result.num_requests + throughput_result.num_requests + cost_result.num_requests,
        )
    
    async def _save_results(
        self,
        results: Dict[str, BenchmarkResult],
        benchmark_type: BenchmarkType,
    ):
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{benchmark_type.value}_{timestamp}"
        
        if self.config.output_format == "json":
            output_path = self._output_dir / f"{filename}.json"
            with open(output_path, "w") as f:
                json.dump(
                    {k: v.to_dict() for k, v in results.items()},
                    f,
                    indent=2,
                )
        else:  # csv
            output_path = self._output_dir / f"{filename}.csv"
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(BenchmarkResult.get_csv_headers())
                for result in results.values():
                    writer.writerow(result.to_csv_row())
        
        logger.info(f"Benchmark results saved to {output_path}")
    
    async def compare_providers(
        self,
        providers: List[str],
        model: Optional[str] = None,
        benchmark_type: BenchmarkType = BenchmarkType.LATENCY,
    ) -> Dict[str, BenchmarkResult]:
        """
        Compare multiple providers.
        
        Args:
            providers: List of provider names to compare
            model: Optional model name
            benchmark_type: Type of benchmark to run
            
        Returns:
            Dict[str, BenchmarkResult]: Benchmark results
        """
        results = {}
        
        for provider in providers:
            try:
                if model:
                    # Find a model with the given name
                    metadata = self.registry.get_metadata(provider)
                    if metadata:
                        for m in metadata.models:
                            if m.name == model:
                                result = await self._run_benchmark_for_type(
                                    provider, m.name, benchmark_type
                                )
                                results[f"{provider}_{m.name}"] = result
                                break
                else:
                    # Use first model
                    metadata = self.registry.get_metadata(provider)
                    if metadata and metadata.models:
                        result = await self._run_benchmark_for_type(
                            provider, metadata.models[0].name, benchmark_type
                        )
                        results[f"{provider}_{metadata.models[0].name}"] = result
            except Exception as e:
                logger.error(f"Error benchmarking {provider}: {e}")
        
        return results
    
    async def _run_benchmark_for_type(
        self,
        provider: str,
        model: str,
        benchmark_type: BenchmarkType,
    ) -> BenchmarkResult:
        """Run a specific benchmark type."""
        if benchmark_type == BenchmarkType.LATENCY:
            return await self._run_latency_benchmark(provider, model)
        elif benchmark_type == BenchmarkType.THROUGHPUT:
            return await self._run_throughput_benchmark(provider, model)
        elif benchmark_type == BenchmarkType.QUALITY:
            return await self._run_quality_benchmark(provider, model)
        elif benchmark_type == BenchmarkType.COST:
            return await self._run_cost_benchmark(provider, model)
        else:
            return await self._run_comprehensive_benchmark(provider, model)
    
    def get_benchmark_history(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get benchmark history from output directory."""
        history = []
        
        for file in sorted(self._output_dir.glob("benchmark_*.json"), reverse=True)[:limit]:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    history.append({
                        "filename": file.name,
                        "timestamp": file.stat().st_mtime,
                        "data": data,
                    })
            except Exception as e:
                logger.error(f"Error reading benchmark file {file}: {e}")
        
        return history


# Global benchmark runner instance
_benchmark_runner: Optional[BenchmarkRunner] = None


def get_benchmark_runner(
    registry: Optional[ProviderRegistry] = None,
    config: Optional[BenchmarkConfig] = None,
) -> BenchmarkRunner:
    """Get the global benchmark runner instance."""
    global _benchmark_runner
    if _benchmark_runner is None:
        _benchmark_runner = BenchmarkRunner(registry, config)
    return _benchmark_runner
