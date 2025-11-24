## RATM Benchmark Suite

Test-driven development framework for measuring progress toward ASI-level capabilities.

## Overview

The benchmark suite is organized into 4 difficulty tiers based on current SOTA performance:

- **Tier 1**: Foundation (60-90% SOTA) - Baseline capabilities
- **Tier 2**: Advanced (20-60% SOTA) - Beyond current models
- **Tier 3**: Frontier (<20% SOTA) - Cutting-edge challenges
- **Tier 4**: Unsolved (<5% SOTA) - Open research problems

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run Tier 1 benchmarks
python -m benchmarks.run_benchmarks --tier 1

# Run specific benchmark with limited tests
python -m benchmarks.run_benchmarks --benchmark hotpot --max-tests 3

# Use custom budget and model
python -m benchmarks.run_benchmarks --tier 1 --budget 20000 --model claude-sonnet-4-5
```

## Current Benchmarks

### Tier 1: Foundation

#### HotpotQA
- **Description**: Multi-hop question answering
- **Test Cases**: 5 sample problems (expandable to full dataset)
- **Target**: >85% accuracy
- **Current SOTA**: 89% (HiVA), 79.7% baseline
- **Tests**:
  - 2-hop reasoning
  - 3-hop reasoning
  - Supporting fact retrieval

**Example**:
```python
from ratm import ThinkingMachine
from benchmarks.tier1.hotpot_qa import HotpotQABenchmark

machine = ThinkingMachine()
benchmark = HotpotQABenchmark()
summary = benchmark.run(machine, max_tests=3, verbose=True)

print(f"Pass rate: {summary.pass_rate:.1%}")
print(f"Avg score: {summary.average_score:.1%}")
```

#### AIME (American Invitational Mathematics Examination)
- **Description**: Advanced high school math competition
- **Test Cases**: 5 sample problems
- **Target**: >90% accuracy
- **Current SOTA**: 96.7% (o3), 94.6% (GPT-5)
- **Tests**:
  - Algebra problems
  - Combinatorics
  - Number theory
  - Geometry

**Example**:
```python
from benchmarks.tier1.aime import AIMEBenchmark

benchmark = AIMEBenchmark()
summary = benchmark.run(machine, verbose=True)
```

### Tier 2: Advanced (Coming Soon)

- **ARC-AGI-2**: Abstract visual reasoning
- **MuSR**: Long-context reasoning
- **GPQA**: Graduate-level science

### Tier 3: Frontier (Planned)

- **FrontierMath**: Research-level mathematics
- **System Design**: Open-ended architecture problems
- **Scientific Hypotheses**: Novel research ideas

### Tier 4: Unsolved (Research)

- **ARC-AGI-2 Hardest**: Completely unsolved subset
- **Multi-Year Planning**: Strategic foresight
- **Theorem Discovery**: Novel mathematical insights

## Command-Line Interface

```bash
# General usage
python -m benchmarks.run_benchmarks [OPTIONS]

# Required (one of):
--tier {1,2,3,4}          Run all benchmarks in tier
--benchmark {hotpot,aime} Run specific benchmark

# Optional:
--max-tests N             Limit tests per benchmark
--llm-provider {anthropic,openai}  Choose provider
--model MODEL             Specific model
--api-key KEY             API key
--budget TOKENS           Token budget per problem
--verbose                 Detailed output (default)
--quiet                   Minimal output
```

## Programmatic Usage

### Running a Single Benchmark

```python
from ratm import ThinkingMachine
from benchmarks.tier1.hotpot_qa import HotpotQABenchmark

# Initialize machine
machine = ThinkingMachine(
    llm_provider="anthropic",
    initial_budget=10000,
)

# Run benchmark
benchmark = HotpotQABenchmark()
summary = benchmark.run(machine, max_tests=5)

# Access results
for result in summary.results:
    print(f"{result.test_name}: {result.score:.2%}")
    print(f"  Tokens: {result.tokens_used}")
    print(f"  Time: {result.time_seconds:.1f}s")
```

### Running Multiple Benchmarks

```python
from benchmarks.base import BenchmarkRunner, DifficultyTier
from benchmarks.tier1.hotpot_qa import HotpotQABenchmark
from benchmarks.tier1.aime import AIMEBenchmark

# Initialize runner
runner = BenchmarkRunner(machine)

# Run tier
benchmarks = [HotpotQABenchmark(), AIMEBenchmark()]
tier_summaries = runner.run_tier(
    DifficultyTier.TIER_1,
    benchmarks,
    verbose=True,
)

# Overall summary
runner.print_overall_summary()
```

### Custom Benchmark

```python
from benchmarks.base import Benchmark, BenchmarkResult, DifficultyTier
from ratm import ThinkingResult

class MyBenchmark(Benchmark):
    def __init__(self):
        super().__init__(
            name="MyBenchmark",
            tier=DifficultyTier.TIER_1,
            description="My custom benchmark",
            target_score=0.80,
        )

    def load_test_cases(self):
        return [
            {
                "id": "test_001",
                "input": "Problem description",
                "expected": "Expected answer",
                "metadata": {},
            }
        ]

    def evaluate(self, test_case, result: ThinkingResult):
        # Your evaluation logic
        success = test_case["expected"] in result.solution

        return BenchmarkResult(
            test_name=test_case["id"],
            success=success,
            score=1.0 if success else 0.0,
            expected_output=test_case["expected"],
            actual_output=result.solution,
            reasoning_trace=[t.thought for t in result.reasoning_trace],
            tokens_used=result.budget_used.tokens_used,
            time_seconds=result.budget_used.time_used,
        )

# Run it
benchmark = MyBenchmark()
summary = benchmark.run(machine)
```

## Evaluation Metrics

Each benchmark tracks:

### Performance Metrics
- **Accuracy**: % of correct answers
- **Pass Rate**: % of tests passing threshold
- **Average Score**: Mean score across tests
- **Confidence Calibration**: Correlation between confidence and correctness

### Efficiency Metrics
- **Tokens Used**: Computational cost
- **Time**: Wall-clock time
- **Tool Calls**: Number of external tool invocations
- **Subagents Spawned**: Recursion depth

### Quality Metrics
- **Reasoning Steps**: Number of intermediate thoughts
- **Verification**: Evidence of checking work
- **Creativity**: Novel approaches (human-evaluated for Tier 3+)

## Interpreting Results

### Tier 1 Goals
- **Pass Rate** >80%: Ready for Tier 2
- **Pass Rate** 60-80%: Baseline capabilities present
- **Pass Rate** <60%: Fundamental issues to address

### Tier 2 Goals
- **Pass Rate** >50%: Exceeding current SOTA
- **Pass Rate** 30-50%: Competitive with best models
- **Pass Rate** <30%: Not yet at frontier

### Tier 3/4 Goals
- **Any progress** is significant
- Focus on failure analysis
- Identify architectural limitations
- Guide research directions

## Continuous Integration

Run benchmarks automatically:

```bash
# Add to CI pipeline
python -m benchmarks.run_benchmarks --tier 1 --max-tests 10 --quiet

# Check exit code
if [ $? -eq 0 ]; then
    echo "Benchmarks passed"
else
    echo "Benchmarks failed"
fi
```

## Extending Benchmarks

### Adding Test Cases

Edit benchmark files to add more test cases:

```python
# benchmarks/tier1/hotpot_qa.py
def load_test_cases(self):
    return [
        # ... existing cases ...
        {
            "id": "hotpot_new",
            "input": "New question",
            "expected": "Expected answer",
            "hops": ["hop1", "hop2"],
            "metadata": {"difficulty": "hard"},
        },
    ]
```

### Loading Full Datasets

```python
import json

def load_test_cases(self):
    # Load from file
    with open("data/hotpot_qa_full.json") as f:
        data = json.load(f)

    return [
        {
            "id": item["_id"],
            "input": item["question"],
            "expected": item["answer"],
            # ...
        }
        for item in data
    ]
```

## Next Steps

1. **Run Tier 1**: Establish baseline performance
2. **Analyze Failures**: Understand where RATM struggles
3. **Iterate**: Improve architecture based on failure modes
4. **Scale Up**: Move to harder tiers
5. **Research**: Attack unsolved problems

## Resources

- Full test suite specification: `/TEST_SUITE.md`
- Research on benchmarks: `/ASI_LEVEL_CHALLENGES_REPORT.md`
- Multi-agent benchmarks: `/MULTI_AGENT_BENCHMARK_RESEARCH.md`

---

**Remember**: The goal isn't just to pass benchmarks, but to understand *why* certain problems are hard and develop novel approaches to solve them. Use benchmarks as diagnostic tools, not just score targets.
