"""Cognitive budget allocation and management system."""

from typing import Optional
from ..types import CognitiveBudget, ReasoningStrategy


class BudgetAllocator:
    """
    Manages cognitive budget allocation with learning capabilities.

    This is a novel component that learns to allocate computational resources
    efficiently based on task characteristics and historical performance.
    """

    def __init__(self):
        """Initialize budget allocator."""
        self.allocation_history: list[dict] = []
        self.strategy_costs: dict[ReasoningStrategy, dict] = {
            ReasoningStrategy.DIRECT: {"avg_tokens": 500, "avg_time": 5.0},
            ReasoningStrategy.REACT: {"avg_tokens": 2000, "avg_time": 30.0},
            ReasoningStrategy.TREE_SEARCH: {"avg_tokens": 5000, "avg_time": 120.0},
            ReasoningStrategy.REFLEXION: {"avg_tokens": 3000, "avg_time": 60.0},
        }

    def allocate_budget(
        self,
        task_description: str,
        available_budget: CognitiveBudget,
        strategy: ReasoningStrategy,
        priority: float = 0.5,
    ) -> CognitiveBudget:
        """
        Allocate budget for a specific task.

        Args:
            task_description: Description of the task
            available_budget: Total available budget
            strategy: Reasoning strategy to use
            priority: Task priority (0.0 to 1.0)

        Returns:
            Allocated cognitive budget
        """
        # Estimate task complexity
        complexity = self._estimate_complexity(task_description)

        # Get strategy cost estimates
        strategy_cost = self.strategy_costs[strategy]

        # Base allocation
        base_tokens = strategy_cost["avg_tokens"]
        base_time = strategy_cost["avg_time"]

        # Adjust based on complexity and priority
        complexity_multiplier = 0.5 + complexity
        priority_multiplier = 0.7 + (0.6 * priority)

        allocated_tokens = int(
            min(
                base_tokens * complexity_multiplier * priority_multiplier,
                available_budget.max_tokens * 0.8,
            )
        )

        allocated_time = min(
            base_time * complexity_multiplier * priority_multiplier,
            available_budget.max_time_seconds * 0.8,
        )

        budget = CognitiveBudget(
            max_tokens=allocated_tokens,
            max_time_seconds=allocated_time,
            max_recursion_depth=available_budget.max_recursion_depth,
            max_tool_calls=int(available_budget.max_tool_calls * 0.8),
        )

        # Record allocation
        self.allocation_history.append(
            {
                "task": task_description,
                "strategy": strategy,
                "allocated": budget,
                "complexity": complexity,
                "priority": priority,
            }
        )

        return budget

    def _estimate_complexity(self, task_description: str) -> float:
        """
        Estimate task complexity from description.

        Returns:
            Complexity score from 0.0 to 1.0
        """
        complexity = 0.3  # Base

        # Length-based
        word_count = len(task_description.split())
        if word_count > 50:
            complexity += 0.2
        elif word_count > 20:
            complexity += 0.1

        # Keyword-based
        complex_indicators = [
            "design",
            "optimize",
            "analyze",
            "complex",
            "comprehensive",
            "multiple",
            "integrate",
            "distributed",
            "scalable",
        ]

        for indicator in complex_indicators:
            if indicator.lower() in task_description.lower():
                complexity += 0.05

        return min(complexity, 1.0)

    def request_additional_budget(
        self,
        current_budget: CognitiveBudget,
        justification: str,
        max_increase_ratio: float = 0.5,
    ) -> Optional[CognitiveBudget]:
        """
        Request additional budget with justification.

        Returns:
            New budget if approved, None otherwise
        """
        # Analyze justification
        justification_score = self._analyze_justification(justification)

        if justification_score < 0.5:
            return None  # Rejected

        # Grant additional budget
        increase_ratio = justification_score * max_increase_ratio

        new_budget = CognitiveBudget(
            max_tokens=int(current_budget.max_tokens * (1 + increase_ratio)),
            max_time_seconds=current_budget.max_time_seconds * (1 + increase_ratio),
            max_recursion_depth=current_budget.max_recursion_depth,
            max_tool_calls=int(
                current_budget.max_tool_calls * (1 + increase_ratio)
            ),
        )

        # Copy current usage
        new_budget.tokens_used = current_budget.tokens_used
        new_budget.time_used = current_budget.time_used
        new_budget.recursion_depth = current_budget.recursion_depth
        new_budget.tool_calls_made = current_budget.tool_calls_made
        new_budget.start_time = current_budget.start_time

        return new_budget

    def _analyze_justification(self, justification: str) -> float:
        """
        Analyze budget increase justification.

        Returns:
            Justification strength score from 0.0 to 1.0
        """
        score = 0.3  # Base

        valid_reasons = [
            "complexity",
            "unexpected",
            "critical",
            "important",
            "necessary",
            "additional",
            "thorough",
        ]

        for reason in valid_reasons:
            if reason.lower() in justification.lower():
                score += 0.15

        return min(score, 1.0)

    def learn_from_execution(
        self,
        strategy: ReasoningStrategy,
        actual_tokens: int,
        actual_time: float,
        success: bool,
    ) -> None:
        """
        Learn from actual execution to improve future allocations.

        This updates the strategy cost estimates based on real usage.
        """
        if strategy not in self.strategy_costs:
            return

        # Exponential moving average
        alpha = 0.2

        current = self.strategy_costs[strategy]

        # Update averages
        current["avg_tokens"] = int(
            alpha * actual_tokens + (1 - alpha) * current["avg_tokens"]
        )

        current["avg_time"] = (
            alpha * actual_time + (1 - alpha) * current["avg_time"]
        )

        # Track success rate
        if "success_rate" not in current:
            current["success_rate"] = 0.5

        success_value = 1.0 if success else 0.0
        current["success_rate"] = (
            alpha * success_value + (1 - alpha) * current["success_rate"]
        )

    def get_strategy_efficiency(self, strategy: ReasoningStrategy) -> float:
        """
        Get efficiency score for a strategy (success rate per token).

        Returns:
            Efficiency score
        """
        if strategy not in self.strategy_costs:
            return 0.5

        costs = self.strategy_costs[strategy]
        success_rate = costs.get("success_rate", 0.5)
        avg_tokens = costs["avg_tokens"]

        # Efficiency = success per token
        return success_rate / (avg_tokens / 1000.0)
