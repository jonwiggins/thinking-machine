"""Tool calling system with learning capabilities."""

from typing import Any, Callable, Optional
from datetime import datetime

from ..types import ToolCall


class Tool:
    """A tool that can be called by the thinking machine."""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        category: Optional[str] = None,
    ):
        """Initialize a tool."""
        self.name = name
        self.func = func
        self.description = description
        self.category = category or "general"

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool."""
        return self.func(*args, **kwargs)


class ToolRegistry:
    """Registry of available tools with usage tracking and learning."""

    def __init__(self):
        """Initialize tool registry."""
        self.tools: dict[str, Tool] = {}
        self.usage_stats: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        category: Optional[str] = None,
    ) -> None:
        """Register a new tool."""
        tool = Tool(name=name, func=func, description=description, category=category)
        self.tools[name] = tool
        self.usage_stats[name] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_execution_time": 0.0,
            "last_used": None,
        }

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def execute(self, name: str, *args: Any, **kwargs: Any) -> ToolCall:
        """Execute a tool and track the result."""
        tool = self.get_tool(name)

        if not tool:
            return ToolCall(
                tool_name=name,
                arguments={"args": args, "kwargs": kwargs},
                success=False,
                error=f"Tool '{name}' not found",
            )

        start_time = datetime.now()

        try:
            result = tool(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()

            # Update stats
            self.usage_stats[name]["total_calls"] += 1
            self.usage_stats[name]["successful_calls"] += 1
            self.usage_stats[name]["total_execution_time"] += execution_time
            self.usage_stats[name]["last_used"] = start_time

            return ToolCall(
                tool_name=name,
                arguments={"args": args, "kwargs": kwargs},
                result=result,
                success=True,
                execution_time=execution_time,
                timestamp=start_time,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            # Update stats
            self.usage_stats[name]["total_calls"] += 1
            self.usage_stats[name]["failed_calls"] += 1
            self.usage_stats[name]["total_execution_time"] += execution_time

            return ToolCall(
                tool_name=name,
                arguments={"args": args, "kwargs": kwargs},
                success=False,
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time,
            )

    def get_success_rate(self, name: str) -> float:
        """Get success rate for a tool."""
        stats = self.usage_stats.get(name)
        if not stats or stats["total_calls"] == 0:
            return 0.5  # Neutral default

        return stats["successful_calls"] / stats["total_calls"]

    def get_avg_execution_time(self, name: str) -> float:
        """Get average execution time for a tool."""
        stats = self.usage_stats.get(name)
        if not stats or stats["total_calls"] == 0:
            return 0.0

        return stats["total_execution_time"] / stats["total_calls"]

    def list_tools(self, category: Optional[str] = None) -> list[str]:
        """List available tools, optionally filtered by category."""
        if category:
            return [
                name
                for name, tool in self.tools.items()
                if tool.category == category
            ]
        return list(self.tools.keys())

    def get_tool_descriptions(self) -> dict[str, str]:
        """Get descriptions of all tools."""
        return {name: tool.description for name, tool in self.tools.items()}


# Built-in tools
def calculator(expression: str) -> float:
    """Evaluate a mathematical expression safely."""
    try:
        # Safe eval with limited namespace
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


def search_memory(query: str) -> str:
    """Search semantic memory (placeholder)."""
    return f"Search results for: {query}"


def create_default_registry() -> ToolRegistry:
    """Create a registry with default tools."""
    registry = ToolRegistry()

    registry.register(
        name="calculator",
        func=calculator,
        description="Evaluate mathematical expressions",
        category="computation",
    )

    registry.register(
        name="search_memory",
        func=search_memory,
        description="Search semantic memory for relevant information",
        category="memory",
    )

    return registry
