"""HotpotQA: Multi-hop question answering benchmark."""

from typing import Any
import re

from ratm import ThinkingResult
from ..base import Benchmark, BenchmarkResult, DifficultyTier


class HotpotQABenchmark(Benchmark):
    """
    HotpotQA benchmark for multi-hop reasoning.

    Tests ability to:
    - Decompose questions into sub-questions
    - Retrieve and integrate information
    - Track intermediate reasoning steps
    """

    def __init__(self):
        super().__init__(
            name="HotpotQA",
            tier=DifficultyTier.TIER_1,
            description="Multi-hop question answering requiring 2-3 reasoning steps",
            target_score=0.85,
        )

    def load_test_cases(self) -> list[dict[str, Any]]:
        """Load HotpotQA test cases."""
        # Sample test cases (in production, load from dataset)
        return [
            {
                "id": "hotpot_001",
                "input": "What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?",
                "expected": "U.S. Ambassador to Ghana",
                "hops": [
                    "Who portrayed Corliss Archer in Kiss and Tell? → Shirley Temple",
                    "What government position did Shirley Temple hold? → U.S. Ambassador to Ghana",
                ],
                "metadata": {
                    "difficulty": "easy",
                    "num_hops": 2,
                },
            },
            {
                "id": "hotpot_002",
                "input": "The director of the romantic comedy 'Big Stone Gap' is based in what New York city?",
                "expected": "New York City",
                "hops": [
                    "Who directed 'Big Stone Gap'? → Adriana Trigiani",
                    "What New York city is Adriana Trigiani based in? → New York City",
                ],
                "metadata": {
                    "difficulty": "medium",
                    "num_hops": 2,
                },
            },
            {
                "id": "hotpot_003",
                "input": "What profession does Nicholas Ray and Elia Kazan have in common?",
                "expected": "Film director",
                "hops": [
                    "What is Nicholas Ray's profession? → Film director",
                    "What is Elia Kazan's profession? → Film director",
                    "What do they have in common? → Film director",
                ],
                "metadata": {
                    "difficulty": "easy",
                    "num_hops": 2,
                },
            },
            {
                "id": "hotpot_004",
                "input": "In what year was the founder of the company that produced the first commercial GPS receiver born?",
                "expected": "1943",
                "hops": [
                    "What company produced the first commercial GPS receiver? → Magellan Corporation",
                    "Who founded Magellan Corporation? → Ed Tuck",
                    "When was Ed Tuck born? → 1943",
                ],
                "metadata": {
                    "difficulty": "hard",
                    "num_hops": 3,
                },
            },
            {
                "id": "hotpot_005",
                "input": "Which genus contains more species, Leontopodium or Calluna?",
                "expected": "Leontopodium",
                "hops": [
                    "How many species are in Leontopodium? → 40-50 species",
                    "How many species are in Calluna? → 1 species",
                    "Which has more? → Leontopodium",
                ],
                "metadata": {
                    "difficulty": "medium",
                    "num_hops": 3,
                },
            },
        ]

    def evaluate(
        self,
        test_case: dict[str, Any],
        result: ThinkingResult,
    ) -> BenchmarkResult:
        """Evaluate HotpotQA result."""
        expected = test_case["expected"].lower().strip()
        actual = result.solution.lower().strip()

        # Check if expected answer is in the solution
        success = expected in actual or self._fuzzy_match(expected, actual)

        # Calculate score based on exact match and reasoning quality
        score = 0.0
        if success:
            score = 1.0

            # Bonus for showing intermediate steps
            trace_text = " ".join([t.thought for t in result.reasoning_trace]).lower()
            for hop in test_case.get("hops", []):
                hop_query = hop.split("→")[0].strip().lower()
                if any(word in trace_text for word in hop_query.split()[:3]):
                    score += 0.1  # Bonus for each hop identified

            score = min(score, 1.0)

        return BenchmarkResult(
            test_name=test_case["id"],
            success=success,
            score=score,
            expected_output=expected,
            actual_output=actual,
            reasoning_trace=[t.thought for t in result.reasoning_trace],
            metrics={
                "hops_expected": len(test_case.get("hops", [])),
                "reasoning_steps": len(result.reasoning_trace),
                "confidence": result.confidence,
            },
            tokens_used=result.budget_used.tokens_used,
            time_seconds=result.budget_used.time_used,
            tool_calls=result.budget_used.tool_calls_made,
            subagents_spawned=result.subagents_spawned,
        )

    def _fuzzy_match(self, expected: str, actual: str) -> bool:
        """Check if expected answer matches actual with some tolerance."""
        # Remove punctuation and extra spaces
        expected_clean = re.sub(r'[^\w\s]', '', expected).strip()
        actual_clean = re.sub(r'[^\w\s]', '', actual).strip()

        # Check various matches
        return (
            expected_clean in actual_clean
            or actual_clean in expected_clean
            or self._token_overlap(expected_clean, actual_clean) > 0.8
        )

    def _token_overlap(self, s1: str, s2: str) -> float:
        """Calculate token overlap between two strings."""
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union)
