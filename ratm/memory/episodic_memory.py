"""Episodic memory for storing recent reasoning traces and experiences."""

from collections import deque
from typing import Optional
import chromadb
from chromadb.config import Settings

from ..types import ReasoningTrace, ToolCall


class EpisodicMemory:
    """Short-to-medium term memory of recent reasoning episodes."""

    def __init__(
        self,
        max_traces: int = 1000,
        persist_directory: str = "./ratm_memory",
    ):
        """Initialize episodic memory."""
        self.max_traces = max_traces
        self.traces: deque[ReasoningTrace] = deque(maxlen=max_traces)
        self.tool_calls: deque[ToolCall] = deque(maxlen=max_traces)

        # Vector store for semantic search over episodes
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        self.episodes_collection = self.client.get_or_create_collection(
            name="episodes",
            metadata={"description": "Recent reasoning episodes"},
        )

    def add_trace(self, trace: ReasoningTrace) -> None:
        """Add a reasoning trace to episodic memory."""
        self.traces.append(trace)

        # Also store in vector DB for semantic retrieval
        trace_text = f"Thought: {trace.thought}"
        if trace.action:
            trace_text += f" | Action: {trace.action}"
        if trace.observation:
            trace_text += f" | Observation: {trace.observation}"

        trace_id = f"trace_{trace.timestamp.isoformat()}_{trace.step_number}"

        self.episodes_collection.add(
            documents=[trace_text],
            metadatas=[
                {
                    "thought": trace.thought,
                    "strategy": trace.strategy_used.value,
                    "confidence": trace.confidence,
                    "timestamp": trace.timestamp.isoformat(),
                }
            ],
            ids=[trace_id],
        )

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call record to episodic memory."""
        self.tool_calls.append(tool_call)

    def get_recent_traces(self, n: int = 10) -> list[ReasoningTrace]:
        """Get the n most recent reasoning traces."""
        return list(self.traces)[-n:] if len(self.traces) >= n else list(self.traces)

    def search_similar_episodes(
        self, query: str, top_k: int = 5
    ) -> list[ReasoningTrace]:
        """Search for similar reasoning episodes."""
        results = self.episodes_collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        traces = []
        if results["documents"] and results["metadatas"]:
            for metadata in results["metadatas"][0]:
                trace = ReasoningTrace(
                    step_number=0,  # We don't store this in metadata
                    thought=metadata["thought"],
                    confidence=metadata["confidence"],
                    strategy_used=metadata["strategy"],
                )
                traces.append(trace)

        return traces

    def get_tool_call_history(self, tool_name: Optional[str] = None) -> list[ToolCall]:
        """Get history of tool calls, optionally filtered by tool name."""
        if tool_name:
            return [tc for tc in self.tool_calls if tc.tool_name == tool_name]
        return list(self.tool_calls)

    def get_tool_success_rate(self, tool_name: str) -> float:
        """Calculate success rate for a specific tool."""
        tool_history = self.get_tool_call_history(tool_name)
        if not tool_history:
            return 0.5  # Default neutral

        successful = sum(1 for tc in tool_history if tc.success)
        return successful / len(tool_history)

    def clear(self) -> None:
        """Clear episodic memory."""
        self.traces.clear()
        self.tool_calls.clear()
        self.client.delete_collection("episodes")
        self.episodes_collection = self.client.create_collection("episodes")
