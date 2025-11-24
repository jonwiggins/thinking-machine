"""Core types and data structures for RATM."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ReasoningStrategy(Enum):
    """Available reasoning strategies."""

    REACT = "react"  # Fast: Reason → Act → Observe
    TREE_SEARCH = "tree_search"  # Deep: Explore multiple paths
    REFLEXION = "reflexion"  # Reflective: Learn from mistakes
    DIRECT = "direct"  # Simplest: Direct answer without tools


class MemoryType(Enum):
    """Types of memory in the hierarchy."""

    WORKING = "working"  # Current context
    EPISODIC = "episodic"  # Recent experiences
    SEMANTIC = "semantic"  # Long-term knowledge
    META = "meta"  # Self-knowledge


class ConfidenceLevel(Enum):
    """Confidence in reasoning quality."""

    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 0.95


@dataclass
class CognitiveBudget:
    """Resource allocation for a thinking task."""

    max_tokens: int = 10000  # Maximum tokens to use
    max_time_seconds: float = 300.0  # Maximum wall-clock time
    max_recursion_depth: int = 5  # Maximum subagent depth
    max_tool_calls: int = 50  # Maximum tool invocations

    # Current usage
    tokens_used: int = 0
    time_used: float = 0.0
    recursion_depth: int = 0
    tool_calls_made: int = 0

    start_time: Optional[datetime] = None

    def start(self) -> None:
        """Start tracking budget usage."""
        self.start_time = datetime.now()

    def is_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        if self.start_time:
            self.time_used = (datetime.now() - self.start_time).total_seconds()

        return (
            self.tokens_used >= self.max_tokens
            or self.time_used >= self.max_time_seconds
            or self.recursion_depth >= self.max_recursion_depth
            or self.tool_calls_made >= self.max_tool_calls
        )

    def remaining_ratio(self) -> float:
        """Get the minimum remaining ratio across all budget dimensions."""
        ratios = [
            1.0 - (self.tokens_used / self.max_tokens),
            1.0 - (self.time_used / self.max_time_seconds),
            1.0 - (self.recursion_depth / self.max_recursion_depth),
            1.0 - (self.tool_calls_made / self.max_tool_calls),
        ]
        return max(0.0, min(ratios))


@dataclass
class ReasoningTrace:
    """A trace of reasoning steps."""

    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    confidence: float = 0.5
    strategy_used: ReasoningStrategy = ReasoningStrategy.REACT
    timestamp: datetime = field(default_factory=datetime.now)
    subagent_id: Optional[str] = None


@dataclass
class Insight:
    """A crystallized insight learned from problem-solving."""

    pattern_description: str
    problem_context: str
    solution_approach: str
    effectiveness_score: float = 0.5
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[list[float]] = None  # For semantic search

    def apply_feedback(self, success: bool) -> None:
        """Update effectiveness based on feedback."""
        self.usage_count += 1
        # Exponential moving average
        alpha = 0.3
        new_score = 1.0 if success else 0.0
        self.effectiveness_score = alpha * new_score + (1 - alpha) * self.effectiveness_score


@dataclass
class ToolCall:
    """A record of a tool invocation."""

    tool_name: str
    arguments: dict[str, Any]
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SubagentSpec:
    """Specification for spawning a subagent."""

    competency: str  # What this agent is specialized for
    task: str  # Specific task to accomplish
    parent_id: Optional[str] = None
    depth: int = 0
    allocated_budget: Optional[CognitiveBudget] = None


@dataclass
class ThinkingResult:
    """Result of a thinking machine operation."""

    solution: str
    confidence: float
    reasoning_trace: list[ReasoningTrace]
    insights_learned: list[Insight]
    tool_calls: list[ToolCall]
    budget_used: CognitiveBudget
    subagents_spawned: int = 0
    strategy_used: ReasoningStrategy = ReasoningStrategy.REACT
    success: bool = True
    error: Optional[str] = None
