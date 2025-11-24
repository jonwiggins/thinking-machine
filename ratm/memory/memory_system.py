"""Unified multi-level memory system for RATM."""

from typing import Optional

from .semantic_memory import SemanticMemory
from .episodic_memory import EpisodicMemory
from ..types import Insight, ReasoningTrace, ToolCall


class WorkingMemory:
    """Short-term working memory for current context."""

    def __init__(self, max_context_size: int = 8000):
        """Initialize working memory."""
        self.max_context_size = max_context_size
        self.current_context: list[str] = []
        self.active_goal: Optional[str] = None
        self.current_step: int = 0

    def add_to_context(self, text: str) -> None:
        """Add text to working memory context."""
        self.current_context.append(text)

        # Truncate if too large (simple strategy: keep most recent)
        total_length = sum(len(t) for t in self.current_context)
        while total_length > self.max_context_size and len(self.current_context) > 1:
            removed = self.current_context.pop(0)
            total_length -= len(removed)

    def get_context(self) -> str:
        """Get current working memory context."""
        return "\n".join(self.current_context)

    def set_goal(self, goal: str) -> None:
        """Set the current active goal."""
        self.active_goal = goal

    def clear(self) -> None:
        """Clear working memory."""
        self.current_context.clear()
        self.active_goal = None
        self.current_step = 0


class MetaMemory:
    """Self-knowledge about capabilities, limitations, and learned preferences."""

    def __init__(self):
        """Initialize meta-memory."""
        self.capabilities: dict[str, float] = {}  # capability -> confidence
        self.tool_preferences: dict[str, dict[str, float]] = {}  # task_type -> {tool: score}
        self.strategy_preferences: dict[str, str] = {}  # problem_type -> preferred_strategy
        self.learned_limitations: list[str] = []

    def record_capability(self, capability: str, confidence: float) -> None:
        """Record knowledge about a capability."""
        self.capabilities[capability] = confidence

    def get_capability_confidence(self, capability: str) -> float:
        """Get confidence level for a capability."""
        return self.capabilities.get(capability, 0.5)

    def learn_tool_preference(
        self, task_type: str, tool_name: str, effectiveness: float
    ) -> None:
        """Learn which tools work well for which tasks."""
        if task_type not in self.tool_preferences:
            self.tool_preferences[task_type] = {}

        # Exponential moving average
        current = self.tool_preferences[task_type].get(tool_name, 0.5)
        alpha = 0.3
        self.tool_preferences[task_type][tool_name] = (
            alpha * effectiveness + (1 - alpha) * current
        )

    def get_preferred_tools(self, task_type: str, top_k: int = 3) -> list[str]:
        """Get preferred tools for a task type."""
        if task_type not in self.tool_preferences:
            return []

        tools = self.tool_preferences[task_type]
        sorted_tools = sorted(tools.items(), key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in sorted_tools[:top_k]]

    def record_limitation(self, limitation: str) -> None:
        """Record a learned limitation."""
        if limitation not in self.learned_limitations:
            self.learned_limitations.append(limitation)

    def clear(self) -> None:
        """Clear meta-memory."""
        self.capabilities.clear()
        self.tool_preferences.clear()
        self.strategy_preferences.clear()
        self.learned_limitations.clear()


class MemorySystem:
    """Unified multi-level memory hierarchy."""

    def __init__(self, persist_directory: str = "./ratm_memory"):
        """Initialize the complete memory system."""
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory(persist_directory=persist_directory)
        self.semantic = SemanticMemory(persist_directory=persist_directory)
        self.meta = MetaMemory()

    def consolidate_to_semantic(self, insight: Insight) -> str:
        """Move an insight from working/episodic to semantic memory."""
        return self.semantic.store_insight(insight)

    def recall_similar_experience(self, query: str) -> tuple[list[Insight], list[ReasoningTrace]]:
        """Recall similar experiences from both semantic and episodic memory."""
        insights = self.semantic.retrieve_similar_insights(query)
        episodes = self.episodic.search_similar_episodes(query)
        return insights, episodes

    def clear_all(self) -> None:
        """Clear all memory systems (use with caution)."""
        self.working.clear()
        self.episodic.clear()
        self.semantic.clear()
        self.meta.clear()
