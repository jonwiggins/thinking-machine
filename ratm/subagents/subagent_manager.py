"""Dynamic subagent spawning and management system."""

import uuid
from typing import Any, Optional
from datetime import datetime

from ..types import (
    CognitiveBudget,
    SubagentSpec,
    ThinkingResult,
    ReasoningStrategy,
)
from ..reasoning.base import LLMProvider, ReasoningEngine


class Subagent:
    """A specialized subagent for handling specific subtasks."""

    def __init__(
        self,
        agent_id: str,
        spec: SubagentSpec,
        reasoning_engine: ReasoningEngine,
    ):
        """Initialize a subagent."""
        self.id = agent_id
        self.spec = spec
        self.reasoning_engine = reasoning_engine
        self.result: Optional[ThinkingResult] = None
        self.created_at = datetime.now()

    def execute(
        self,
        tools: Optional[dict[str, Any]] = None,
    ) -> ThinkingResult:
        """Execute the subagent's task."""
        context = {
            "competency": self.spec.competency,
            "parent_id": self.spec.parent_id,
            "depth": self.spec.depth,
        }

        budget = self.spec.allocated_budget or CognitiveBudget(
            max_tokens=2000,
            max_time_seconds=60.0,
            max_recursion_depth=3,
        )

        self.result = self.reasoning_engine.reason(
            problem=self.spec.task,
            context=context,
            budget=budget,
            tools=tools,
        )

        return self.result


class SubagentManager:
    """Manages dynamic spawning and coordination of subagents."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        max_concurrent_subagents: int = 5,
    ):
        """Initialize subagent manager."""
        self.llm_provider = llm_provider
        self.max_concurrent_subagents = max_concurrent_subagents
        self.active_subagents: dict[str, Subagent] = {}
        self.completed_subagents: dict[str, Subagent] = {}

    def should_spawn_subagent(
        self,
        task_complexity: float,
        budget_remaining: float,
        current_depth: int,
        max_depth: int,
    ) -> bool:
        """
        Decide if we should spawn a subagent based on various factors.

        Args:
            task_complexity: Estimated complexity (0.0 to 1.0)
            budget_remaining: Remaining budget ratio (0.0 to 1.0)
            current_depth: Current recursion depth
            max_depth: Maximum allowed depth

        Returns:
            True if subagent should be spawned
        """
        # Don't spawn if at max depth
        if current_depth >= max_depth:
            return False

        # Don't spawn if budget too low
        if budget_remaining < 0.2:
            return False

        # Don't spawn if too many active subagents
        if len(self.active_subagents) >= self.max_concurrent_subagents:
            return False

        # Spawn if task is complex enough
        complexity_threshold = 0.6
        return task_complexity >= complexity_threshold

    def spawn_subagent(
        self,
        competency: str,
        task: str,
        parent_id: Optional[str],
        depth: int,
        budget: CognitiveBudget,
        strategy: ReasoningStrategy = ReasoningStrategy.REACT,
    ) -> str:
        """
        Spawn a new subagent with specific competency.

        Returns:
            The subagent ID
        """
        agent_id = str(uuid.uuid4())

        # Allocate a portion of the parent's budget
        subagent_budget = CognitiveBudget(
            max_tokens=min(budget.max_tokens // 2, 2000),
            max_time_seconds=min(budget.max_time_seconds / 2, 60.0),
            max_recursion_depth=budget.max_recursion_depth - depth,
            max_tool_calls=budget.max_tool_calls // 2,
        )

        spec = SubagentSpec(
            competency=competency,
            task=task,
            parent_id=parent_id,
            depth=depth,
            allocated_budget=subagent_budget,
        )

        # Create reasoning engine based on strategy
        from ..reasoning.react import ReActEngine

        if strategy == ReasoningStrategy.REACT:
            reasoning_engine = ReActEngine(self.llm_provider)
        else:
            # Default to ReAct for now
            reasoning_engine = ReActEngine(self.llm_provider)

        subagent = Subagent(
            agent_id=agent_id,
            spec=spec,
            reasoning_engine=reasoning_engine,
        )

        self.active_subagents[agent_id] = subagent
        return agent_id

    def execute_subagent(
        self,
        agent_id: str,
        tools: Optional[dict[str, Any]] = None,
    ) -> ThinkingResult:
        """Execute a subagent and return its result."""
        if agent_id not in self.active_subagents:
            raise ValueError(f"Subagent {agent_id} not found")

        subagent = self.active_subagents[agent_id]
        result = subagent.execute(tools=tools)

        # Move to completed
        self.completed_subagents[agent_id] = subagent
        del self.active_subagents[agent_id]

        return result

    def get_subagent_result(self, agent_id: str) -> Optional[ThinkingResult]:
        """Get result of a completed subagent."""
        if agent_id in self.completed_subagents:
            return self.completed_subagents[agent_id].result
        return None

    def analyze_task_complexity(
        self,
        task: str,
        context: dict[str, Any],
    ) -> float:
        """
        Analyze task complexity to decide on subagent spawning.

        Returns:
            Complexity score from 0.0 to 1.0
        """
        # Simple heuristic based on task length and keywords
        complexity = 0.3  # Base complexity

        # Length factor
        if len(task) > 200:
            complexity += 0.2

        # Keyword indicators
        complex_keywords = [
            "multiple",
            "complex",
            "design",
            "optimize",
            "analyze",
            "comprehensive",
        ]

        for keyword in complex_keywords:
            if keyword.lower() in task.lower():
                complexity += 0.1

        return min(complexity, 1.0)

    def get_active_count(self) -> int:
        """Get number of active subagents."""
        return len(self.active_subagents)

    def get_total_count(self) -> int:
        """Get total number of subagents (active + completed)."""
        return len(self.active_subagents) + len(self.completed_subagents)
