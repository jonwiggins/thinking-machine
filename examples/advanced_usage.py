"""Advanced usage examples demonstrating RATM's unique features."""

import os
from ratm import ThinkingMachine, ReasoningStrategy

API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def example_insight_learning():
    """Demonstrate insight crystallization and learning."""
    print("\n" + "=" * 60)
    print("Example: Insight Learning")
    print("=" * 60)

    machine = ThinkingMachine(
        llm_provider="anthropic",
        api_key=API_KEY,
        verbose=True,
    )

    # Solve similar problems to see learning in action
    problems = [
        "How do you implement a queue using two stacks?",
        "How do you implement a stack using two queues?",
        "How do you reverse a linked list?",
    ]

    for i, problem in enumerate(problems, 1):
        print(f"\n\n🧩 Problem {i}: {problem}")
        result = machine.solve(problem)

        print(f"\nInsights learned: {len(result.insights_learned)}")
        for insight in result.insights_learned:
            print(f"  - {insight.pattern_description[:80]}...")


def example_budget_management():
    """Demonstrate cognitive budget allocation."""
    print("\n" + "=" * 60)
    print("Example: Budget Management")
    print("=" * 60)

    machine = ThinkingMachine(
        llm_provider="anthropic",
        api_key=API_KEY,
        initial_budget=2000,  # Smaller budget
        verbose=True,
    )

    # Complex problem with limited budget
    result = machine.solve(
        problem="Design a distributed database system with support for transactions, "
        "replication, and automatic failover",
        budget_override=3000,  # Override for this specific task
    )

    print(f"\nBudget used: {result.budget_used.tokens_used} tokens")
    print(f"Time used: {result.budget_used.time_used:.2f} seconds")
    print(f"Budget remaining: {result.budget_used.remaining_ratio():.1%}")


def example_custom_tools():
    """Demonstrate custom tool integration and learning."""
    print("\n" + "=" * 60)
    print("Example: Custom Tools with Learning")
    print("=" * 60)

    machine = ThinkingMachine(
        llm_provider="anthropic",
        api_key=API_KEY,
        verbose=True,
    )

    # Register custom tools
    def fibonacci(n: str) -> int:
        """Calculate the nth Fibonacci number."""
        n_int = int(n)
        if n_int <= 1:
            return n_int
        a, b = 0, 1
        for _ in range(2, n_int + 1):
            a, b = b, a + b
        return b

    def is_prime(n: str) -> bool:
        """Check if a number is prime."""
        n_int = int(n)
        if n_int < 2:
            return False
        for i in range(2, int(n_int ** 0.5) + 1):
            if n_int % i == 0:
                return False
        return True

    machine.register_tool(
        name="fibonacci",
        func=fibonacci,
        description="Calculate the nth Fibonacci number",
        category="math",
    )

    machine.register_tool(
        name="is_prime",
        func=is_prime,
        description="Check if a number is prime",
        category="math",
    )

    # Use the tools
    result = machine.solve(
        problem="Find the 20th Fibonacci number and check if it's prime",
    )

    print(f"\nTools used: {len(result.tool_calls)}")
    for tc in result.tool_calls:
        print(f"  - {tc.tool_name}: success={tc.success}, result={tc.result}")


def example_strategy_selection():
    """Demonstrate adaptive strategy selection."""
    print("\n" + "=" * 60)
    print("Example: Adaptive Strategy Selection")
    print("=" * 60)

    machine = ThinkingMachine(
        llm_provider="anthropic",
        api_key=API_KEY,
        verbose=True,
    )

    # Simple problem - should use DIRECT or REACT
    print("\n🎯 Simple Problem:")
    result1 = machine.solve("What is 2 + 2?")
    print(f"Strategy selected: {result1.strategy_used.value}")

    # Complex problem - should use TREE_SEARCH
    print("\n\n🎯 Complex Problem:")
    result2 = machine.solve(
        problem="Design a comprehensive fault-tolerant distributed system with "
        "support for consensus, replication, and automatic recovery"
    )
    print(f"Strategy selected: {result2.strategy_used.value}")

    # Force a specific strategy
    print("\n\n🎯 Forced Strategy:")
    result3 = machine.solve(
        problem="Explain recursion",
        strategy=ReasoningStrategy.REACT,
    )
    print(f"Strategy used: {result3.strategy_used.value}")


def main():
    """Run all advanced examples."""
    print("\n🚀 RATM Advanced Usage Examples\n")

    try:
        example_insight_learning()
    except Exception as e:
        print(f"Error in insight learning example: {e}")

    try:
        example_budget_management()
    except Exception as e:
        print(f"Error in budget management example: {e}")

    try:
        example_custom_tools()
    except Exception as e:
        print(f"Error in custom tools example: {e}")

    try:
        example_strategy_selection()
    except Exception as e:
        print(f"Error in strategy selection example: {e}")


if __name__ == "__main__":
    main()
