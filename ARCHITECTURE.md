# RATM Architecture Documentation

## Overview

RATM (Recursive Adaptive Thinking Machine) is a novel ASI framework that uses LLMs as cognitive components within a sophisticated thinking machine architecture. This document describes the system's architecture, novel contributions, and implementation details.

## Core Philosophy

Unlike traditional LLM frameworks that use the model as the entire system, RATM treats LLMs as **cognitive processors** within a larger thinking machine. The system provides:

1. **Memory** - Multi-level hierarchy for context, experience, and knowledge
2. **Budget Management** - Dynamic resource allocation with learning
3. **Adaptive Reasoning** - Strategy selection based on problem characteristics
4. **Recursive Decomposition** - Dynamic subagent spawning by competency
5. **Learning** - Insight crystallization and cross-problem knowledge transfer

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ThinkingMachine                          │
│                    (Main Orchestrator)                      │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│ Memory System │  │Budget Manager│  │Subagent Mgr  │
└───────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│   Working     │  │  Allocator   │  │   Dynamic    │
│   Episodic    │  │  Requestor   │  │   Spawning   │
│   Semantic    │  │   Learner    │  │  Execution   │
│     Meta      │  └──────────────┘  └──────────────┘
└───────────────┘
        │
        ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│   ChromaDB    │  │ Reasoning    │  │Tool Registry │
│ Vector Store  │  │  Engines     │  │   Learning   │
└───────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  LLM Provider│
                   │(Claude/GPT)  │
                   └──────────────┘
```

## Novel Contributions

### 1. Cognitive Budget System

**Innovation**: Dynamic resource allocation where each task receives a computational budget (tokens, time, recursion depth, tool calls). The system learns to allocate efficiently.

**Implementation**: `ratm/budget/budget_allocator.py`

**Key Features**:
- Multi-dimensional budgets (tokens, time, depth, calls)
- Adaptive allocation based on task complexity
- Budget request system with justification analysis
- Learning from actual usage patterns

**Algorithm**:
```python
allocated_budget = base_cost * complexity_multiplier * priority_multiplier
```

Where:
- `base_cost`: Historical average for the strategy
- `complexity_multiplier`: 0.5 + estimated_complexity
- `priority_multiplier`: 0.7 + (0.6 * priority)

### 2. Insight Crystallization

**Innovation**: Automatically extract reusable problem-solving patterns and store them in semantic memory for future use.

**Implementation**: `ratm/core/thinking_machine.py:_crystallize_insights()`

**Process**:
1. After successful problem solving (confidence > 0.7)
2. Extract high-confidence reasoning steps
3. Create Insight object with pattern description
4. Store in vector database for semantic search
5. Apply effectiveness feedback on reuse

**Data Structure**:
```python
Insight(
    pattern_description: str,
    problem_context: str,
    solution_approach: str,
    effectiveness_score: float,
    usage_count: int,
    embedding: vector
)
```

### 3. Adaptive Strategy Switching

**Innovation**: Dynamically choose reasoning strategy based on problem complexity, budget availability, and confidence requirements.

**Implementation**: `ratm/core/thinking_machine.py:_select_strategy()`

**Strategy Ladder**:
- **DIRECT** (complexity < 0.4): Immediate answer, no tools
- **REACT** (complexity 0.4-0.7): Iterative reasoning and acting
- **TREE_SEARCH** (complexity > 0.7): Multi-path exploration
- **REFLEXION** (after failure): Self-reflection and retry

**Selection Algorithm**:
```python
complexity = analyze_task_complexity(problem)
if complexity < 0.4:
    return DIRECT
elif complexity < 0.7:
    return REACT
else:
    return TREE_SEARCH
```

### 4. Dynamic Subagent Specialization

**Innovation**: Instead of fixed-role agents, spawn specialized subagents dynamically based on competency requirements. Agents can recursively spawn their own subagents.

**Implementation**: `ratm/subagents/subagent_manager.py`

**Key Features**:
- Competency-based spawning (not role-based)
- Automatic budget allocation to subagents
- Recursive spawning with depth limits
- Result aggregation and consolidation

**Spawning Decision**:
```python
should_spawn = (
    task_complexity >= 0.6 AND
    budget_remaining >= 0.2 AND
    current_depth < max_depth AND
    active_subagents < max_concurrent
)
```

### 5. Multi-Level Memory Hierarchy

**Innovation**: Four-level memory system modeled after cognitive psychology, with automatic consolidation and vector search.

**Implementation**: `ratm/memory/memory_system.py`

**Levels**:

#### Working Memory
- Short-term context (8K chars)
- Active goal tracking
- Current step counter
- Auto-truncation when full

#### Episodic Memory
- Recent reasoning traces
- Tool call history
- Vector-searchable episodes
- Success rate tracking

#### Semantic Memory
- Long-term knowledge
- Crystallized insights
- Vector embeddings
- Cross-problem patterns

#### Meta-Memory
- Self-knowledge about capabilities
- Tool-task preference mappings
- Strategy effectiveness
- Learned limitations

**Memory Consolidation**:
```
Working → Episodic (automatic, every step)
Episodic → Semantic (on success, confidence > 0.7)
All → Meta (on task completion)
```

## Implementation Details

### Memory Backend

Uses **ChromaDB** for vector storage:
- Automatic embedding generation
- Cosine similarity search
- Persistent storage
- Collections for insights, episodes, knowledge

### LLM Integration

Supports multiple providers:
- **Anthropic Claude** (primary)
- **OpenAI GPT** (secondary)

Provider interface in `ratm/reasoning/base.py`:
```python
class LLMProvider(ABC):
    def generate(prompt, system, max_tokens, temperature)
        -> (response, tokens_used)
```

### Reasoning Engines

Current implementations:
- **ReActEngine**: Thought → Action → Observation loop
- **DirectEngine**: (TODO) Single-pass generation
- **TreeSearchEngine**: (TODO) Multi-path MCTS
- **ReflexionEngine**: (TODO) Self-reflection loop

### Tool System

Registry-based with automatic learning:
- Tool registration by name
- Usage tracking (calls, success rate, timing)
- Effectiveness learning per task type
- Meta-memory integration

## Research Foundation

RATM builds upon and extends:

1. **ReAct** (Yao et al., 2022)
   - Synergizing reasoning and acting
   - Extended with adaptive strategy switching

2. **Tree of Thoughts** (Yao et al., 2023)
   - Multi-path exploration
   - Integrated as one strategy option

3. **Reflexion** (Shinn et al., 2023)
   - Self-reflection and learning
   - Extended with insight crystallization

4. **LATS** (Zhou et al., 2023)
   - Language Agent Tree Search
   - Informed budget allocation decisions

5. **MemGPT** (Packer et al., 2023)
   - Virtual memory abstraction
   - Extended to four-level hierarchy

6. **AutoGPT/BabyAGI** (2023)
   - Autonomous task decomposition
   - Improved with competency-based subagents

## Performance Characteristics

### Time Complexity

- **Memory Retrieval**: O(log n) for vector search
- **Strategy Selection**: O(1) heuristic
- **Subagent Spawning**: O(1) decision
- **Budget Allocation**: O(1) computation

### Space Complexity

- **Working Memory**: O(context_size) ≈ 8KB
- **Episodic Memory**: O(max_traces) ≈ 1000 traces
- **Semantic Memory**: O(insights) unbounded, disk-backed
- **Meta Memory**: O(capabilities + tools) ≈ 1KB

### Token Usage

Typical token consumption by strategy:
- **DIRECT**: 500 tokens
- **REACT**: 2,000 tokens
- **TREE_SEARCH**: 5,000 tokens
- **REFLEXION**: 3,000 tokens

## Future Enhancements

### Planned Features

1. **Tree Search Implementation**
   - Monte Carlo Tree Search
   - Value function learning
   - Best-first exploration

2. **Multi-Agent Collaboration**
   - Subagent communication protocols
   - Shared memory spaces
   - Consensus mechanisms

3. **Advanced Learning**
   - Reinforcement learning for strategy selection
   - Meta-learning for quick adaptation
   - Transfer learning across domains

4. **Enhanced Memory**
   - Graph-based semantic memory
   - Temporal reasoning support
   - Causal relationship tracking

5. **Tool Learning**
   - Automatic tool composition
   - Tool creation from examples
   - Safety verification

### Research Directions

1. **Cognitive Architecture**
   - Integrate with cognitive science models
   - Attention mechanisms
   - Working memory capacity models

2. **Scalability**
   - Distributed execution
   - Parallel subagent processing
   - Incremental learning

3. **Interpretability**
   - Reasoning trace visualization
   - Decision explanation
   - Confidence calibration

4. **Safety**
   - Budget enforcement
   - Tool sandboxing
   - Alignment mechanisms

## Benchmarking

To benchmark RATM:

```python
from ratm import ThinkingMachine
from ratm.benchmarks import run_benchmark

machine = ThinkingMachine()
results = run_benchmark(machine, benchmark="GPQA")
```

Recommended benchmarks:
- **GPQA**: Graduate-level questions
- **MATH**: Mathematical reasoning
- **HumanEval**: Code generation
- **MMLU**: Multitask understanding

## Contributing

To contribute a new reasoning strategy:

1. Inherit from `ReasoningEngine`
2. Implement `reason()` method
3. Register in `_create_reasoning_engine()`
4. Add tests

See `ratm/reasoning/react.py` for reference.

## Citation

If you use RATM in research, please cite:

```bibtex
@software{ratm2025,
  title={RATM: Recursive Adaptive Thinking Machine},
  author={RATM Contributors},
  year={2025},
  url={https://github.com/jonwiggins/thinking-machine}
}
```

## License

MIT License - See LICENSE file for details.
