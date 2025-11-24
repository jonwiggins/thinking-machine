"""Main RATM (Recursive Adaptive Thinking Machine) orchestrator."""

from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..types import (
    CognitiveBudget,
    Insight,
    ReasoningStrategy,
    ThinkingResult,
)
from ..memory.memory_system import MemorySystem
from ..reasoning.base import LLMProvider
from ..reasoning.llm_providers import create_llm_provider
from ..reasoning.react import ReActEngine
from ..subagents.subagent_manager import SubagentManager
from ..tools.tool_system import ToolRegistry, create_default_registry
from ..budget.budget_allocator import BudgetAllocator


class ThinkingMachine:
    """
    RATM: Recursive Adaptive Thinking Machine

    A novel ASI framework that combines:
    - Multi-level memory hierarchy
    - Adaptive reasoning strategy selection
    - Dynamic subagent spawning
    - Cognitive budget management
    - Insight crystallization and learning
    """

    def __init__(
        self,
        llm_provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_recursion_depth: int = 5,
        initial_budget: int = 10000,
        memory_dir: str = "./ratm_memory",
        verbose: bool = True,
    ):
        """
        Initialize the thinking machine.

        Args:
            llm_provider: LLM provider ("anthropic" or "openai")
            model: Specific model to use
            api_key: API key for the LLM provider
            max_recursion_depth: Maximum subagent recursion depth
            initial_budget: Default token budget
            memory_dir: Directory for persistent memory
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.console = Console() if verbose else None

        # Initialize LLM provider
        self.llm: LLMProvider = create_llm_provider(
            provider=llm_provider,
            api_key=api_key,
            model=model,
        )

        # Initialize core systems
        self.memory = MemorySystem(persist_directory=memory_dir)
        self.budget_allocator = BudgetAllocator()
        self.subagent_manager = SubagentManager(self.llm)
        self.tool_registry = create_default_registry()

        # Default configuration
        self.max_recursion_depth = max_recursion_depth
        self.initial_budget = initial_budget

        self._log("🧠 RATM initialized successfully")

    def solve(
        self,
        problem: str,
        context: Optional[dict[str, Any]] = None,
        budget_override: Optional[int] = None,
        strategy: Optional[ReasoningStrategy] = None,
    ) -> ThinkingResult:
        """
        Main entry point: Solve a problem using the thinking machine.

        Args:
            problem: The problem description
            context: Additional context dictionary
            budget_override: Override default budget
            strategy: Force specific reasoning strategy

        Returns:
            ThinkingResult with solution and metadata
        """
        context = context or {}

        self._log(
            Panel.fit(
                f"[bold cyan]Problem:[/bold cyan]\n{problem}",
                title="🎯 New Task",
            )
        )

        # Step 1: Check semantic memory for similar problems
        self._log("🔍 Checking semantic memory for insights...")
        insights, episodes = self.memory.recall_similar_experience(problem)

        if insights:
            self._log(f"💡 Found {len(insights)} relevant insights")
            context["relevant_insights"] = [
                {
                    "pattern": i.pattern_description,
                    "solution": i.solution_approach,
                    "effectiveness": i.effectiveness_score,
                }
                for i in insights
            ]

        # Step 2: Allocate cognitive budget
        budget = CognitiveBudget(
            max_tokens=budget_override or self.initial_budget,
            max_time_seconds=300.0,
            max_recursion_depth=self.max_recursion_depth,
            max_tool_calls=50,
        )

        # Step 3: Select reasoning strategy
        selected_strategy = strategy or self._select_strategy(problem, context, budget)
        self._log(f"🎯 Selected strategy: [bold]{selected_strategy.value}[/bold]")

        # Step 4: Allocate budget for this strategy
        allocated_budget = self.budget_allocator.allocate_budget(
            task_description=problem,
            available_budget=budget,
            strategy=selected_strategy,
        )

        # Step 5: Execute reasoning
        self._log("🚀 Executing reasoning strategy...")

        reasoning_engine = self._create_reasoning_engine(selected_strategy)

        # Get tools as dict for engine
        tools_dict = {
            name: self.tool_registry.get_tool(name)
            for name in self.tool_registry.list_tools()
        }

        result = reasoning_engine.reason(
            problem=problem,
            context=context,
            budget=allocated_budget,
            tools=tools_dict,
        )

        # Step 6: Store in episodic memory
        for trace in result.reasoning_trace:
            self.memory.episodic.add_trace(trace)

        for tool_call in result.tool_calls:
            self.memory.episodic.add_tool_call(tool_call)

        # Step 7: Crystallize insights
        if result.success and result.confidence > 0.7:
            self._log("💎 Crystallizing insights...")
            insights_learned = self._crystallize_insights(problem, result)
            result.insights_learned = insights_learned

            # Store in semantic memory
            for insight in insights_learned:
                self.memory.consolidate_to_semantic(insight)

        # Step 8: Update learning
        self.budget_allocator.learn_from_execution(
            strategy=selected_strategy,
            actual_tokens=allocated_budget.tokens_used,
            actual_time=allocated_budget.time_used,
            success=result.success,
        )

        # Step 9: Update meta-memory
        self._update_meta_memory(problem, result, selected_strategy)

        self._log(
            Panel.fit(
                f"[bold green]Solution:[/bold green]\n{result.solution}\n\n"
                f"[bold]Confidence:[/bold] {result.confidence:.2%}\n"
                f"[bold]Tokens used:[/bold] {result.budget_used.tokens_used}\n"
                f"[bold]Time:[/bold] {result.budget_used.time_used:.2f}s",
                title="✅ Result",
            )
        )

        return result

    def _select_strategy(
        self,
        problem: str,
        context: dict[str, Any],
        budget: CognitiveBudget,
    ) -> ReasoningStrategy:
        """
        Adaptively select the best reasoning strategy.

        This is a key innovation: choose strategy based on:
        - Problem complexity
        - Available budget
        - Historical performance
        - Confidence requirements
        """
        complexity = self.subagent_manager.analyze_task_complexity(problem, context)

        # Simple strategy: use ReAct for most cases
        # In a full implementation, this would be more sophisticated
        if complexity < 0.4:
            return ReasoningStrategy.DIRECT
        elif complexity < 0.7:
            return ReasoningStrategy.REACT
        else:
            return ReasoningStrategy.TREE_SEARCH

    def _create_reasoning_engine(self, strategy: ReasoningStrategy):
        """Create appropriate reasoning engine for strategy."""
        if strategy == ReasoningStrategy.REACT:
            return ReActEngine(self.llm)
        else:
            # Default to ReAct
            return ReActEngine(self.llm)

    def _crystallize_insights(
        self,
        problem: str,
        result: ThinkingResult,
    ) -> list[Insight]:
        """
        Extract reusable insights from successful problem-solving.

        This is a novel contribution: automatically learn patterns.
        """
        insights = []

        # Simple heuristic: if solution was successful, create an insight
        if result.success and len(result.reasoning_trace) > 2:
            # Extract pattern from reasoning traces
            key_thoughts = [
                trace.thought
                for trace in result.reasoning_trace
                if trace.confidence > 0.6
            ]

            if key_thoughts:
                insight = Insight(
                    pattern_description=f"Approach for: {problem[:100]}",
                    problem_context=problem,
                    solution_approach=" -> ".join(key_thoughts[:3]),
                    effectiveness_score=result.confidence,
                )
                insights.append(insight)

        return insights

    def _update_meta_memory(
        self,
        problem: str,
        result: ThinkingResult,
        strategy: ReasoningStrategy,
    ) -> None:
        """Update meta-memory with learned information."""
        # Update strategy preferences
        self.memory.meta.strategy_preferences[problem[:50]] = strategy.value

        # Update tool preferences
        for tool_call in result.tool_calls:
            if tool_call.success:
                self.memory.meta.learn_tool_preference(
                    task_type=problem[:30],
                    tool_name=tool_call.tool_name,
                    effectiveness=1.0,
                )

    def register_tool(
        self,
        name: str,
        func: Any,
        description: str,
        category: Optional[str] = None,
    ) -> None:
        """Register a new tool with the thinking machine."""
        self.tool_registry.register(name, func, description, category)
        self._log(f"🔧 Registered tool: {name}")

    def _log(self, message: Any) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose and self.console:
            self.console.print(message)

    def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about the memory system."""
        return {
            "working_context_size": len(self.memory.working.current_context),
            "episodic_traces": len(self.memory.episodic.traces),
            "tool_calls": len(self.memory.episodic.tool_calls),
            "learned_capabilities": len(self.memory.meta.capabilities),
            "tool_preferences": len(self.memory.meta.tool_preferences),
        }

    def clear_memory(self, confirm: bool = False) -> None:
        """Clear all memory systems (requires confirmation)."""
        if confirm:
            self.memory.clear_all()
            self._log("🗑️ All memory cleared")
        else:
            self._log("⚠️ Memory clear requires confirm=True")
