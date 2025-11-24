"""Basic tests for RATM components."""

import pytest
from ratm.types import CognitiveBudget, Insight, ReasoningTrace, ReasoningStrategy
from ratm.memory.memory_system import MemorySystem, WorkingMemory, MetaMemory
from ratm.budget.budget_allocator import BudgetAllocator
from ratm.tools.tool_system import ToolRegistry


class TestCognitiveBudget:
    """Test cognitive budget functionality."""

    def test_budget_creation(self):
        """Test budget creation with defaults."""
        budget = CognitiveBudget()
        assert budget.max_tokens == 10000
        assert budget.tokens_used == 0
        assert not budget.is_exhausted()

    def test_budget_exhaustion(self):
        """Test budget exhaustion detection."""
        budget = CognitiveBudget(max_tokens=100)
        budget.tokens_used = 100
        assert budget.is_exhausted()

    def test_remaining_ratio(self):
        """Test remaining budget ratio calculation."""
        budget = CognitiveBudget(max_tokens=1000)
        budget.tokens_used = 250
        assert budget.remaining_ratio() == 0.75


class TestWorkingMemory:
    """Test working memory functionality."""

    def test_add_to_context(self):
        """Test adding text to context."""
        memory = WorkingMemory(max_context_size=100)
        memory.add_to_context("test")
        assert "test" in memory.get_context()

    def test_context_truncation(self):
        """Test automatic context truncation."""
        memory = WorkingMemory(max_context_size=50)
        memory.add_to_context("a" * 30)
        memory.add_to_context("b" * 30)
        context = memory.get_context()
        assert len(context) <= 50

    def test_goal_setting(self):
        """Test goal setting and retrieval."""
        memory = WorkingMemory()
        memory.set_goal("solve problem")
        assert memory.active_goal == "solve problem"


class TestMetaMemory:
    """Test meta-memory functionality."""

    def test_capability_recording(self):
        """Test recording capabilities."""
        meta = MetaMemory()
        meta.record_capability("math", 0.8)
        assert meta.get_capability_confidence("math") == 0.8

    def test_tool_preference_learning(self):
        """Test tool preference learning."""
        meta = MetaMemory()
        meta.learn_tool_preference("math", "calculator", 0.9)
        meta.learn_tool_preference("math", "search", 0.3)
        preferred = meta.get_preferred_tools("math", top_k=1)
        assert preferred[0] == "calculator"

    def test_limitation_recording(self):
        """Test limitation recording."""
        meta = MetaMemory()
        meta.record_limitation("Cannot access external APIs")
        assert "Cannot access external APIs" in meta.learned_limitations


class TestBudgetAllocator:
    """Test budget allocation system."""

    def test_budget_allocation(self):
        """Test basic budget allocation."""
        allocator = BudgetAllocator()
        available = CognitiveBudget(max_tokens=10000)

        allocated = allocator.allocate_budget(
            task_description="Simple task",
            available_budget=available,
            strategy=ReasoningStrategy.REACT,
        )

        assert allocated.max_tokens <= available.max_tokens
        assert allocated.max_tokens > 0

    def test_complexity_estimation(self):
        """Test task complexity estimation."""
        allocator = BudgetAllocator()

        simple_complexity = allocator._estimate_complexity("What is 2+2?")
        complex_complexity = allocator._estimate_complexity(
            "Design a comprehensive distributed system with multiple "
            "complex components that need to integrate and optimize performance"
        )

        assert complex_complexity > simple_complexity

    def test_learning_from_execution(self):
        """Test learning from execution results."""
        allocator = BudgetAllocator()

        initial_avg = allocator.strategy_costs[ReasoningStrategy.REACT]["avg_tokens"]

        allocator.learn_from_execution(
            strategy=ReasoningStrategy.REACT,
            actual_tokens=5000,
            actual_time=30.0,
            success=True,
        )

        new_avg = allocator.strategy_costs[ReasoningStrategy.REACT]["avg_tokens"]
        assert new_avg != initial_avg


class TestToolRegistry:
    """Test tool registry functionality."""

    def test_tool_registration(self):
        """Test registering a tool."""
        registry = ToolRegistry()

        def test_tool(x: str) -> int:
            return int(x) * 2

        registry.register("double", test_tool, "Double a number")
        assert "double" in registry.list_tools()

    def test_tool_execution(self):
        """Test executing a registered tool."""
        registry = ToolRegistry()

        def add(a: str, b: str) -> int:
            return int(a) + int(b)

        registry.register("add", add, "Add two numbers")

        result = registry.execute("add", "5", "3")
        assert result.success
        assert result.result == 8

    def test_tool_error_handling(self):
        """Test tool error handling."""
        registry = ToolRegistry()

        def failing_tool(x: str) -> int:
            raise ValueError("Test error")

        registry.register("fail", failing_tool, "A failing tool")

        result = registry.execute("fail", "test")
        assert not result.success
        assert "Test error" in result.error

    def test_success_rate_tracking(self):
        """Test success rate tracking."""
        registry = ToolRegistry()

        def sometimes_fails(x: str) -> int:
            if int(x) < 5:
                raise ValueError("Too small")
            return int(x)

        registry.register("sometimes", sometimes_fails, "Sometimes fails")

        # Execute multiple times
        registry.execute("sometimes", "10")  # Success
        registry.execute("sometimes", "2")   # Fail
        registry.execute("sometimes", "8")   # Success

        success_rate = registry.get_success_rate("sometimes")
        assert 0.6 <= success_rate <= 0.7  # 2/3 success


class TestInsight:
    """Test insight functionality."""

    def test_insight_creation(self):
        """Test creating an insight."""
        insight = Insight(
            pattern_description="Use binary search",
            problem_context="Search in sorted array",
            solution_approach="Divide and conquer",
        )
        assert insight.effectiveness_score == 0.5
        assert insight.usage_count == 0

    def test_insight_feedback(self):
        """Test applying feedback to insights."""
        insight = Insight(
            pattern_description="Test pattern",
            problem_context="Test context",
            solution_approach="Test approach",
            effectiveness_score=0.5,
        )

        # Positive feedback
        insight.apply_feedback(success=True)
        assert insight.effectiveness_score > 0.5
        assert insight.usage_count == 1

        # Negative feedback
        initial_score = insight.effectiveness_score
        insight.apply_feedback(success=False)
        assert insight.effectiveness_score < initial_score
        assert insight.usage_count == 2


class TestReasoningTrace:
    """Test reasoning trace functionality."""

    def test_trace_creation(self):
        """Test creating a reasoning trace."""
        trace = ReasoningTrace(
            step_number=1,
            thought="I should use tool X",
            action="use_tool(X)",
            observation="Tool returned Y",
            confidence=0.8,
        )

        assert trace.step_number == 1
        assert trace.confidence == 0.8
        assert trace.strategy_used == ReasoningStrategy.REACT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
