"""Base classes for RATM benchmarks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum

from ratm import ThinkingMachine, ThinkingResult


class DifficultyTier(Enum):
    """Benchmark difficulty tiers."""

    TIER_1 = 1  # Foundation: 60-90% SOTA
    TIER_2 = 2  # Advanced: 20-60% SOTA
    TIER_3 = 3  # Frontier: <20% SOTA
    TIER_4 = 4  # Unsolved: <5% SOTA


@dataclass
class BenchmarkResult:
    """Result of running a benchmark test."""

    test_name: str
    success: bool
    score: float  # 0.0 to 1.0
    expected_output: Any
    actual_output: Any
    reasoning_trace: list
    metrics: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    # Efficiency metrics
    tokens_used: int = 0
    time_seconds: float = 0.0
    tool_calls: int = 0
    subagents_spawned: int = 0

    def __str__(self) -> str:
        """String representation."""
        status = "✓ PASS" if self.success else "✗ FAIL"
        return (
            f"{status} {self.test_name} (score: {self.score:.2%})\n"
            f"  Tokens: {self.tokens_used}, Time: {self.time_seconds:.2f}s, "
            f"Tools: {self.tool_calls}, Subagents: {self.subagents_spawned}"
        )


@dataclass
class BenchmarkSummary:
    """Summary of benchmark run results."""

    tier: DifficultyTier
    total_tests: int
    passed: int
    failed: int
    average_score: float
    total_tokens: int
    total_time: float
    results: list[BenchmarkResult]

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        return self.passed / self.total_tests if self.total_tests > 0 else 0.0

    def __str__(self) -> str:
        """String representation."""
        return (
            f"\n{'='*60}\n"
            f"Benchmark Summary - {self.tier.name}\n"
            f"{'='*60}\n"
            f"Tests: {self.passed}/{self.total_tests} passed ({self.pass_rate:.1%})\n"
            f"Average Score: {self.average_score:.1%}\n"
            f"Total Tokens: {self.total_tokens:,}\n"
            f"Total Time: {self.total_time:.1f}s\n"
            f"{'='*60}\n"
        )


class Benchmark(ABC):
    """Abstract base class for benchmarks."""

    def __init__(
        self,
        name: str,
        tier: DifficultyTier,
        description: str,
        target_score: float = 0.8,
    ):
        """Initialize benchmark."""
        self.name = name
        self.tier = tier
        self.description = description
        self.target_score = target_score
        self.results: list[BenchmarkResult] = []

    @abstractmethod
    def load_test_cases(self) -> list[dict[str, Any]]:
        """
        Load test cases for this benchmark.

        Returns:
            List of test case dictionaries with keys:
            - id: Unique test identifier
            - input: Test input
            - expected: Expected output
            - metadata: Additional information
        """
        pass

    @abstractmethod
    def evaluate(
        self,
        test_case: dict[str, Any],
        result: ThinkingResult,
    ) -> BenchmarkResult:
        """
        Evaluate a model's result on a test case.

        Args:
            test_case: The test case dictionary
            result: The model's ThinkingResult

        Returns:
            BenchmarkResult with evaluation metrics
        """
        pass

    def run(
        self,
        machine: ThinkingMachine,
        max_tests: Optional[int] = None,
        verbose: bool = True,
    ) -> BenchmarkSummary:
        """
        Run the benchmark on a thinking machine.

        Args:
            machine: ThinkingMachine to evaluate
            max_tests: Maximum number of tests to run (None = all)
            verbose: Print progress

        Returns:
            BenchmarkSummary with results
        """
        test_cases = self.load_test_cases()
        if max_tests:
            test_cases = test_cases[:max_tests]

        self.results = []
        total_tokens = 0
        total_time = 0.0

        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Benchmark: {self.name}")
            print(f"Tier: {self.tier.name} | Tests: {len(test_cases)}")
            print(f"Target Score: {self.target_score:.1%}")
            print(f"{'='*60}\n")

        for i, test_case in enumerate(test_cases, 1):
            if verbose:
                print(f"Test {i}/{len(test_cases)}: {test_case.get('id', 'unknown')}")

            try:
                # Run the thinking machine
                thinking_result = machine.solve(
                    problem=test_case["input"],
                    context=test_case.get("metadata", {}),
                )

                # Evaluate the result
                bench_result = self.evaluate(test_case, thinking_result)
                self.results.append(bench_result)

                # Track totals
                total_tokens += bench_result.tokens_used
                total_time += bench_result.time_seconds

                if verbose:
                    print(f"  {bench_result}\n")

            except Exception as e:
                error_result = BenchmarkResult(
                    test_name=test_case.get("id", "unknown"),
                    success=False,
                    score=0.0,
                    expected_output=test_case.get("expected"),
                    actual_output=None,
                    reasoning_trace=[],
                    error=str(e),
                )
                self.results.append(error_result)

                if verbose:
                    print(f"  ✗ ERROR: {e}\n")

        # Calculate summary
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        avg_score = (
            sum(r.score for r in self.results) / len(self.results)
            if self.results
            else 0.0
        )

        summary = BenchmarkSummary(
            tier=self.tier,
            total_tests=len(self.results),
            passed=passed,
            failed=failed,
            average_score=avg_score,
            total_tokens=total_tokens,
            total_time=total_time,
            results=self.results,
        )

        if verbose:
            print(summary)

        return summary


class BenchmarkRunner:
    """Runner for executing multiple benchmarks."""

    def __init__(self, machine: ThinkingMachine):
        """Initialize benchmark runner."""
        self.machine = machine
        self.summaries: dict[str, BenchmarkSummary] = {}

    def run_benchmark(
        self,
        benchmark: Benchmark,
        max_tests: Optional[int] = None,
        verbose: bool = True,
    ) -> BenchmarkSummary:
        """Run a single benchmark."""
        summary = benchmark.run(self.machine, max_tests=max_tests, verbose=verbose)
        self.summaries[benchmark.name] = summary
        return summary

    def run_tier(
        self,
        tier: DifficultyTier,
        benchmarks: list[Benchmark],
        verbose: bool = True,
    ) -> dict[str, BenchmarkSummary]:
        """Run all benchmarks in a tier."""
        if verbose:
            print(f"\n{'#'*60}")
            print(f"# Running Tier {tier.value} Benchmarks")
            print(f"{'#'*60}\n")

        tier_summaries = {}
        for benchmark in benchmarks:
            if benchmark.tier == tier:
                summary = self.run_benchmark(benchmark, verbose=verbose)
                tier_summaries[benchmark.name] = summary

        return tier_summaries

    def print_overall_summary(self) -> None:
        """Print summary of all benchmarks run."""
        if not self.summaries:
            print("No benchmarks have been run yet.")
            return

        print(f"\n{'#'*60}")
        print("# OVERALL BENCHMARK SUMMARY")
        print(f"{'#'*60}\n")

        for name, summary in self.summaries.items():
            print(f"{name}:")
            print(f"  Pass Rate: {summary.pass_rate:.1%}")
            print(f"  Avg Score: {summary.average_score:.1%}")
            print(f"  Tokens: {summary.total_tokens:,}")
            print(f"  Time: {summary.total_time:.1f}s\n")

        # Calculate overall stats
        total_tests = sum(s.total_tests for s in self.summaries.values())
        total_passed = sum(s.passed for s in self.summaries.values())
        overall_pass_rate = total_passed / total_tests if total_tests > 0 else 0.0

        print(f"{'='*60}")
        print(f"Overall: {total_passed}/{total_tests} passed ({overall_pass_rate:.1%})")
        print(f"{'='*60}\n")
