"""Base classes for reasoning strategies."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..types import (
    CognitiveBudget,
    ReasoningTrace,
    ReasoningStrategy,
    ThinkingResult,
)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> tuple[str, int]:
        """
        Generate a response from the LLM.

        Returns:
            tuple of (response_text, tokens_used)
        """
        pass


class ReasoningEngine(ABC):
    """Abstract base class for reasoning strategies."""

    def __init__(self, llm: LLMProvider):
        """Initialize reasoning engine with an LLM provider."""
        self.llm = llm

    @abstractmethod
    def reason(
        self,
        problem: str,
        context: dict[str, Any],
        budget: CognitiveBudget,
        tools: Optional[dict[str, Any]] = None,
    ) -> ThinkingResult:
        """
        Execute reasoning strategy to solve a problem.

        Args:
            problem: The problem to solve
            context: Additional context
            budget: Cognitive budget for this reasoning task
            tools: Available tools for execution

        Returns:
            ThinkingResult with solution and traces
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> ReasoningStrategy:
        """Return the strategy type."""
        pass

    def _create_trace(
        self,
        step_number: int,
        thought: str,
        action: Optional[str] = None,
        observation: Optional[str] = None,
        confidence: float = 0.5,
    ) -> ReasoningTrace:
        """Helper to create a reasoning trace."""
        return ReasoningTrace(
            step_number=step_number,
            thought=thought,
            action=action,
            observation=observation,
            confidence=confidence,
            strategy_used=self.get_strategy_name(),
        )
