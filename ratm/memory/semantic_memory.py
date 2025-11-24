"""Semantic memory system using vector embeddings for insight storage and retrieval."""

import chromadb
from chromadb.config import Settings
from typing import Optional
import uuid

from ..types import Insight


class SemanticMemory:
    """Long-term semantic memory with vector search for insights."""

    def __init__(self, persist_directory: str = "./ratm_memory"):
        """Initialize semantic memory with ChromaDB backend."""
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        # Collection for insights
        self.insights_collection = self.client.get_or_create_collection(
            name="insights",
            metadata={"description": "Crystallized problem-solving insights"},
        )

        # Collection for general knowledge
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "General semantic knowledge"},
        )

    def store_insight(self, insight: Insight) -> str:
        """Store an insight in semantic memory."""
        insight_id = str(uuid.uuid4())

        # Combine fields for embedding
        text = f"{insight.pattern_description} | {insight.problem_context} | {insight.solution_approach}"

        self.insights_collection.add(
            documents=[text],
            metadatas=[
                {
                    "pattern": insight.pattern_description,
                    "context": insight.problem_context,
                    "solution": insight.solution_approach,
                    "effectiveness": insight.effectiveness_score,
                    "usage_count": insight.usage_count,
                }
            ],
            ids=[insight_id],
        )

        return insight_id

    def retrieve_similar_insights(
        self, problem_description: str, top_k: int = 5, min_effectiveness: float = 0.3
    ) -> list[Insight]:
        """Retrieve insights similar to the given problem."""
        results = self.insights_collection.query(
            query_texts=[problem_description],
            n_results=top_k,
        )

        insights = []
        if results["documents"] and results["metadatas"]:
            for metadata in results["metadatas"][0]:
                # Filter by effectiveness
                if metadata.get("effectiveness", 0.0) >= min_effectiveness:
                    insight = Insight(
                        pattern_description=metadata["pattern"],
                        problem_context=metadata["context"],
                        solution_approach=metadata["solution"],
                        effectiveness_score=metadata["effectiveness"],
                        usage_count=metadata["usage_count"],
                    )
                    insights.append(insight)

        return insights

    def update_insight_effectiveness(
        self, insight_id: str, success: bool
    ) -> None:
        """Update insight effectiveness based on usage feedback."""
        # Get current metadata
        result = self.insights_collection.get(ids=[insight_id])
        if not result["metadatas"]:
            return

        metadata = result["metadatas"][0]
        current_effectiveness = metadata.get("effectiveness", 0.5)
        usage_count = metadata.get("usage_count", 0) + 1

        # Update effectiveness with exponential moving average
        alpha = 0.3
        new_score = 1.0 if success else 0.0
        new_effectiveness = alpha * new_score + (1 - alpha) * current_effectiveness

        # Update metadata
        self.insights_collection.update(
            ids=[insight_id],
            metadatas=[
                {
                    **metadata,
                    "effectiveness": new_effectiveness,
                    "usage_count": usage_count,
                }
            ],
        )

    def store_knowledge(self, key: str, content: str, metadata: Optional[dict] = None) -> None:
        """Store general semantic knowledge."""
        self.knowledge_collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[key],
        )

    def retrieve_knowledge(self, query: str, top_k: int = 3) -> list[str]:
        """Retrieve relevant knowledge."""
        results = self.knowledge_collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        if results["documents"]:
            return results["documents"][0]
        return []

    def clear(self) -> None:
        """Clear all memory (use with caution)."""
        self.client.delete_collection("insights")
        self.client.delete_collection("knowledge")
        self.insights_collection = self.client.create_collection("insights")
        self.knowledge_collection = self.client.create_collection("knowledge")
