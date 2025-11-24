"""
RATM: Recursive Adaptive Thinking Machine

A novel ASI framework using LLMs as cognitive components.
"""

from .core.thinking_machine import ThinkingMachine
from .types import (
    CognitiveBudget,
    ReasoningStrategy,
    ThinkingResult,
    Insight,
    ReasoningTrace,
)

__version__ = "0.1.0"

__all__ = [
    "ThinkingMachine",
    "CognitiveBudget",
    "ReasoningStrategy",
    "ThinkingResult",
    "Insight",
    "ReasoningTrace",
]
