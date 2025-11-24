"""ReAct (Reasoning and Acting) strategy implementation."""

import json
import re
from typing import Any, Optional

from .base import ReasoningEngine, LLMProvider
from ..types import (
    CognitiveBudget,
    ReasoningStrategy,
    ReasoningTrace,
    ThinkingResult,
    ToolCall,
)


class ReActEngine(ReasoningEngine):
    """ReAct: Alternating between reasoning and acting."""

    def __init__(self, llm: LLMProvider, max_steps: int = 10):
        """Initialize ReAct engine."""
        super().__init__(llm)
        self.max_steps = max_steps

    def get_strategy_name(self) -> ReasoningStrategy:
        """Return strategy type."""
        return ReasoningStrategy.REACT

    def reason(
        self,
        problem: str,
        context: dict[str, Any],
        budget: CognitiveBudget,
        tools: Optional[dict[str, Any]] = None,
    ) -> ThinkingResult:
        """Execute ReAct reasoning loop."""
        budget.start()
        traces: list[ReasoningTrace] = []
        tool_calls: list[ToolCall] = []
        solution = ""
        confidence = 0.5

        # Format available tools
        tools = tools or {}
        tools_description = self._format_tools(tools)

        system_prompt = """You are a reasoning agent using the ReAct (Reasoning and Acting) framework.

For each step, you should:
1. Think about what to do next
2. Decide on an action (use a tool or provide final answer)
3. Observe the result

Format your response as:
Thought: [your reasoning]
Action: [tool_name(arguments)] or ANSWER: [final answer]
"""

        # Build initial prompt
        prompt = f"""Problem: {problem}

Context: {json.dumps(context, indent=2)}

Available Tools:
{tools_description}

Let's solve this step by step using the ReAct framework.
"""

        conversation_history = []
        step = 0

        while step < self.max_steps and not budget.is_exhausted():
            # Generate reasoning step
            full_prompt = prompt if step == 0 else "\n".join(conversation_history)
            response, tokens = self.llm.generate(
                full_prompt,
                system=system_prompt,
                max_tokens=500,
                temperature=0.7,
            )

            budget.tokens_used += tokens
            step += 1

            # Parse response
            thought, action, is_final = self._parse_response(response)

            if is_final:
                # Final answer reached
                solution = action
                confidence = 0.8
                traces.append(
                    self._create_trace(
                        step_number=step,
                        thought=thought,
                        action=f"ANSWER: {action}",
                        confidence=confidence,
                    )
                )
                break

            # Execute action if it's a tool call
            observation = ""
            if action and not is_final:
                tool_call_result = self._execute_tool(action, tools)
                tool_calls.append(tool_call_result)
                observation = str(tool_call_result.result)
                budget.tool_calls_made += 1

            # Record trace
            traces.append(
                self._create_trace(
                    step_number=step,
                    thought=thought,
                    action=action,
                    observation=observation,
                    confidence=0.6,
                )
            )

            # Update conversation
            conversation_history.append(response)
            if observation:
                conversation_history.append(f"Observation: {observation}")

        if not solution:
            solution = "No solution found within budget constraints."
            confidence = 0.2

        return ThinkingResult(
            solution=solution,
            confidence=confidence,
            reasoning_trace=traces,
            insights_learned=[],
            tool_calls=tool_calls,
            budget_used=budget,
            strategy_used=self.get_strategy_name(),
            success=bool(solution),
        )

    def _format_tools(self, tools: dict[str, Any]) -> str:
        """Format tools for the prompt."""
        if not tools:
            return "No tools available."

        lines = []
        for name, tool_func in tools.items():
            doc = tool_func.__doc__ or "No description"
            lines.append(f"- {name}: {doc.strip()}")

        return "\n".join(lines)

    def _parse_response(self, response: str) -> tuple[str, str, bool]:
        """
        Parse LLM response into thought and action.

        Returns:
            (thought, action, is_final_answer)
        """
        thought = ""
        action = ""
        is_final = False

        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|$)", response, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()

        # Extract action
        action_match = re.search(r"Action:\s*(.+?)(?=\n|$)", response, re.DOTALL | re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()

        # Check for final answer
        answer_match = re.search(r"ANSWER:\s*(.+?)(?=\n|$)", response, re.DOTALL | re.IGNORECASE)
        if answer_match:
            action = answer_match.group(1).strip()
            is_final = True

        return thought, action, is_final

    def _execute_tool(self, action: str, tools: dict[str, Any]) -> ToolCall:
        """Execute a tool call from the action string."""
        # Parse tool call: tool_name(arg1, arg2, ...)
        match = re.match(r"(\w+)\((.*?)\)", action)

        if not match:
            return ToolCall(
                tool_name="unknown",
                arguments={},
                success=False,
                error=f"Could not parse action: {action}",
            )

        tool_name = match.group(1)
        args_str = match.group(2)

        if tool_name not in tools:
            return ToolCall(
                tool_name=tool_name,
                arguments={},
                success=False,
                error=f"Tool '{tool_name}' not found",
            )

        # Parse arguments (simple parsing)
        try:
            args = [arg.strip().strip('"\'') for arg in args_str.split(",")] if args_str else []
            result = tools[tool_name](*args)

            return ToolCall(
                tool_name=tool_name,
                arguments={"args": args},
                result=result,
                success=True,
            )
        except Exception as e:
            return ToolCall(
                tool_name=tool_name,
                arguments={"args": args_str},
                success=False,
                error=str(e),
            )
