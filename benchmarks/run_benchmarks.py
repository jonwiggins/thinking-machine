"""Run RATM benchmark suite."""

import argparse
import os
import sys
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ratm import ThinkingMachine
from benchmarks.base import BenchmarkRunner, DifficultyTier
from benchmarks.tier1.hotpot_qa import HotpotQABenchmark
from benchmarks.tier1.aime import AIMEBenchmark


def get_tier_benchmarks(tier: int) -> list:
    """Get all benchmarks for a tier."""
    tier_enum = DifficultyTier(tier)

    if tier == 1:
        return [
            HotpotQABenchmark(),
            AIMEBenchmark(),
            # Add more Tier 1 benchmarks here
        ]
    elif tier == 2:
        # Tier 2 benchmarks (to be implemented)
        return []
    elif tier == 3:
        # Tier 3 benchmarks (to be implemented)
        return []
    elif tier == 4:
        # Tier 4 benchmarks (to be implemented)
        return []
    else:
        raise ValueError(f"Invalid tier: {tier}")


def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run RATM benchmark suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all Tier 1 benchmarks
  python -m benchmarks.run_benchmarks --tier 1

  # Run specific benchmark with limited tests
  python -m benchmarks.run_benchmarks --benchmark hotpot --max-tests 3

  # Use specific model
  python -m benchmarks.run_benchmarks --tier 1 --model claude-sonnet-4-5

  # Run with custom budget
  python -m benchmarks.run_benchmarks --tier 1 --budget 20000
        """,
    )

    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run all benchmarks in specified tier",
    )

    parser.add_argument(
        "--benchmark",
        type=str,
        choices=["hotpot", "aime"],
        help="Run specific benchmark",
    )

    parser.add_argument(
        "--max-tests",
        type=int,
        help="Maximum number of tests to run per benchmark",
    )

    parser.add_argument(
        "--llm-provider",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai"],
        help="LLM provider to use",
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Specific model to use (e.g., claude-sonnet-4-5, gpt-4)",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or set ANTHROPIC_API_KEY/OPENAI_API_KEY env var)",
    )

    parser.add_argument(
        "--budget",
        type=int,
        default=10000,
        help="Token budget per problem (default: 10000)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output (default: True)",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode (minimal output)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.tier and not args.benchmark:
        parser.error("Must specify either --tier or --benchmark")

    verbose = args.verbose and not args.quiet

    # Initialize ThinkingMachine
    if verbose:
        print("Initializing RATM ThinkingMachine...")

    machine = ThinkingMachine(
        llm_provider=args.llm_provider,
        model=args.model,
        api_key=args.api_key,
        initial_budget=args.budget,
        verbose=verbose,
    )

    # Initialize runner
    runner = BenchmarkRunner(machine)

    # Run benchmarks
    if args.benchmark:
        # Run specific benchmark
        if args.benchmark == "hotpot":
            benchmark = HotpotQABenchmark()
        elif args.benchmark == "aime":
            benchmark = AIMEBenchmark()
        else:
            print(f"Unknown benchmark: {args.benchmark}")
            return 1

        runner.run_benchmark(benchmark, max_tests=args.max_tests, verbose=verbose)

    elif args.tier:
        # Run all benchmarks in tier
        benchmarks = get_tier_benchmarks(args.tier)

        if not benchmarks:
            print(f"No benchmarks available for Tier {args.tier} yet.")
            print("This tier is planned for future implementation.")
            return 1

        tier_enum = DifficultyTier(args.tier)
        runner.run_tier(tier_enum, benchmarks, verbose=verbose)

    # Print overall summary
    if not args.quiet:
        runner.print_overall_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
