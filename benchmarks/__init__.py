"""RATM Benchmark Suite

Test-driven development framework for ASI research.
"""

from .base import Benchmark, BenchmarkResult, BenchmarkRunner
from .tier1.hotpot_qa import HotpotQABenchmark
from .tier1.aime import AIMEBenchmark

__all__ = [
    "Benchmark",
    "BenchmarkResult",
    "BenchmarkRunner",
    "HotpotQABenchmark",
    "AIMEBenchmark",
]
