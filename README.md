# RATM: Recursive Adaptive Thinking Machine

A novel ASI framework that uses LLMs as cognitive components within a sophisticated thinking machine architecture.

## Core Innovations

### 1. Cognitive Budget System
Dynamic resource allocation where each task receives a computational budget (tokens, time, recursion depth). The system learns to allocate efficiently and can request more resources with justification.

### 2. Insight Crystallization
After solving problems, the system extracts reusable patterns and stores them as "insights" in semantic memory. Future problems check for similar insights first, enabling learning from experience.

### 3. Adaptive Strategy Switching
Starts with fast ReAct-style reasoning and automatically escalates to tree search when confidence is low or the problem is complex. Uses self-assessment to dynamically choose the right reasoning strategy.

### 4. Dynamic Subagent Specialization
Unlike fixed-role systems (like BabyAGI's executor/creator/prioritizer), RATM spawns specialized subagents based on competency requirements. Subagents can recursively spawn their own subagents up to a budget limit.

### 5. Multi-Level Memory Hierarchy
- **Working Memory**: Current context and active reasoning
- **Episodic Memory**: Recent problem-solving traces (vector searchable)
- **Semantic Memory**: Long-term knowledge and crystallized insights
- **Meta-Memory**: Self-knowledge about capabilities and learned tool effectiveness

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    RATM Core                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Budget    │  │   Strategy   │  │  Insight  │ │
│  │  Allocator  │  │   Selector   │  │Crystallizer│ │
│  └─────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
           │                    │                │
           ▼                    ▼                ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Memory System   │  │ Reasoning Engine │  │  Tool System    │
│  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌───────────┐  │
│  │  Working   │  │  │  │   ReAct    │  │  │  │   Tools   │  │
│  │  Episodic  │  │  │  │ Tree Search│  │  │  │ Learning  │  │
│  │  Semantic  │  │  │  │ Reflexion  │  │  │  └───────────┘  │
│  │    Meta    │  │  │  └────────────┘  │  │                 │
│  └────────────┘  │  └──────────────────┘  └─────────────────┘
└──────────────────┘           │                      │
           │                   ▼                      │
           │         ┌──────────────────┐            │
           └────────▶│ Subagent Manager │◀───────────┘
                     └──────────────────┘
```

## Installation

```bash
pip install -e .
```

## Usage

```python
from ratm import ThinkingMachine

# Initialize the thinking machine
machine = ThinkingMachine(
    llm_provider="anthropic",  # or "openai"
    model="claude-sonnet-4-5",
    max_recursion_depth=5,
    initial_budget=10000  # tokens
)

# Solve a problem
result = machine.solve(
    problem="Design and implement a distributed caching system",
    context={"constraints": "Must handle 10k requests/sec"},
    budget_override=20000  # optional
)

print(result.solution)
print(result.reasoning_trace)
print(result.insights_learned)
```

## Key Components

- **ratm/core/**: Main orchestration logic
- **ratm/memory/**: Multi-level memory system
- **ratm/reasoning/**: Strategy implementations (ReAct, Tree Search, etc.)
- **ratm/subagents/**: Dynamic subagent spawning and management
- **ratm/tools/**: Tool calling interface and learning
- **ratm/budget/**: Cognitive budget allocation and tracking

## Research Foundation

RATM builds on and extends:
- **ReAct**: Reasoning and acting paradigm
- **Tree of Thoughts**: Multi-path exploration
- **Reflexion**: Self-reflection and improvement
- **LATS**: Language Agent Tree Search
- **MemGPT**: Virtual memory abstraction
- **AutoGPT/BabyAGI**: Recursive task decomposition

## Novel Contributions

1. First framework to implement dynamic cognitive budget allocation
2. Insight crystallization for cross-problem learning
3. Confidence-based adaptive strategy switching
4. Competency-based dynamic subagent spawning
5. Tool effectiveness learning and association mapping

## Test-Driven Development

RATM includes a comprehensive benchmark suite for measuring progress on hard AI problems:

### Benchmark Tiers

- **Tier 1**: Foundation (SOTA 60-90%) - HotpotQA, AIME
- **Tier 2**: Advanced (SOTA 20-60%) - ARC-AGI-2, GPQA, MuSR
- **Tier 3**: Frontier (SOTA <20%) - FrontierMath, System Design
- **Tier 4**: Unsolved (SOTA <5%) - Novel theorem discovery, multi-year planning

### Running Benchmarks

```bash
# Run Tier 1 foundation tests
python -m benchmarks.run_benchmarks --tier 1

# Run specific benchmark
python -m benchmarks.run_benchmarks --benchmark hotpot --max-tests 5

# Custom configuration
python -m benchmarks.run_benchmarks --tier 1 --budget 20000 --model claude-sonnet-4-5
```

### Programmatic Usage

```python
from ratm import ThinkingMachine
from benchmarks.tier1.hotpot_qa import HotpotQABenchmark

machine = ThinkingMachine()
benchmark = HotpotQABenchmark()
summary = benchmark.run(machine, max_tests=3)

print(f"Pass rate: {summary.pass_rate:.1%}")
print(f"Average score: {summary.average_score:.1%}")
```

**See `/benchmarks/BENCHMARKS.md` for complete documentation**

## Documentation

- **README.md**: This file - project overview
- **QUICKSTART.md**: 5-minute getting started guide
- **ARCHITECTURE.md**: Detailed system design and research
- **TEST_SUITE.md**: Complete test specification
- **benchmarks/BENCHMARKS.md**: Benchmark usage and results

## License

MIT
