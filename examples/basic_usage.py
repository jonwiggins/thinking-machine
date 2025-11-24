"""Basic usage example for RATM."""

import os
from ratm import ThinkingMachine

# Set your API key (or set ANTHROPIC_API_KEY environment variable)
API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def main():
    """Demonstrate basic RATM usage."""
    print("=" * 60)
    print("RATM: Recursive Adaptive Thinking Machine")
    print("Basic Usage Example")
    print("=" * 60)

    # Initialize the thinking machine
    machine = ThinkingMachine(
        llm_provider="anthropic",
        model="claude-sonnet-4-5-20250929",
        api_key=API_KEY,
        max_recursion_depth=3,
        initial_budget=5000,
        verbose=True,
    )

    # Example 1: Simple problem solving
    print("\n📚 Example 1: Simple Math Problem")
    result = machine.solve(
        problem="Calculate the compound interest on $10,000 at 5% annual rate for 3 years",
        context={"domain": "finance"},
    )

    print(f"\nSolution: {result.solution}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Strategy used: {result.strategy_used.value}")

    # Example 2: More complex problem
    print("\n\n🔬 Example 2: Design Problem")
    result = machine.solve(
        problem="Design a simple caching system that supports TTL (time-to-live) and LRU eviction",
        context={"domain": "system_design", "complexity": "medium"},
    )

    print(f"\nSolution: {result.solution}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Insights learned: {len(result.insights_learned)}")

    # Example 3: Using custom tools
    print("\n\n🔧 Example 3: Custom Tool")

    def string_reverser(text: str) -> str:
        """Reverse a string."""
        return text[::-1]

    machine.register_tool(
        name="reverse",
        func=string_reverser,
        description="Reverse a string",
        category="text",
    )

    result = machine.solve(
        problem="Reverse the string 'Hello RATM!'",
    )

    print(f"\nSolution: {result.solution}")

    # Show memory stats
    print("\n\n📊 Memory Statistics:")
    stats = machine.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
