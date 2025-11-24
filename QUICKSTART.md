# RATM Quick Start Guide

Get started with RATM in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/jonwiggins/thinking-machine.git
cd thinking-machine

# Install dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

## Basic Usage

### 1. Initialize the Thinking Machine

```python
from ratm import ThinkingMachine

# Initialize with Anthropic Claude (recommended)
machine = ThinkingMachine(
    llm_provider="anthropic",
    api_key="your-api-key",  # or set ANTHROPIC_API_KEY env var
    verbose=True  # Show reasoning process
)

# Or use OpenAI
machine = ThinkingMachine(
    llm_provider="openai",
    api_key="your-openai-key",
    model="gpt-4"
)
```

### 2. Solve a Problem

```python
result = machine.solve(
    problem="Design a caching system with LRU eviction",
    context={"domain": "system_design"}
)

print(result.solution)
print(f"Confidence: {result.confidence:.2%}")
```

### 3. Register Custom Tools

```python
def web_search(query: str) -> str:
    """Search the web and return results."""
    # Your implementation
    return results

machine.register_tool(
    name="search",
    func=web_search,
    description="Search the web for information",
    category="retrieval"
)

# Use the tool
result = machine.solve("What's the latest news on AI?")
```

## Key Features

### Automatic Strategy Selection

RATM automatically chooses the best reasoning strategy:

```python
# Simple problem → DIRECT strategy
result = machine.solve("What is 2 + 2?")

# Medium complexity → REACT strategy
result = machine.solve("Explain how binary search works")

# High complexity → TREE_SEARCH strategy
result = machine.solve(
    "Design a distributed consensus algorithm with "
    "Byzantine fault tolerance"
)
```

### Budget Management

Control resource usage:

```python
# Set default budget
machine = ThinkingMachine(initial_budget=5000)

# Override per task
result = machine.solve(
    problem="Complex task...",
    budget_override=10000  # Allow more resources
)

# Check usage
print(f"Tokens used: {result.budget_used.tokens_used}")
print(f"Time: {result.budget_used.time_used:.2f}s")
```

### Learning from Experience

RATM learns and improves:

```python
# Solve similar problems
for problem in similar_problems:
    result = machine.solve(problem)

    # Insights are automatically crystallized
    print(f"Learned {len(result.insights_learned)} insights")

# Next time, RATM will recall and reuse insights!
```

### Memory System

Access the multi-level memory:

```python
# Get memory statistics
stats = machine.get_memory_stats()
print(stats)

# The machine automatically:
# - Stores reasoning traces in episodic memory
# - Crystallizes insights to semantic memory
# - Learns tool preferences in meta-memory
# - Manages working context automatically
```

## Examples

### Example 1: Math Problem

```python
result = machine.solve(
    "Calculate compound interest: $10,000 at 5% for 3 years"
)
```

### Example 2: Code Design

```python
result = machine.solve(
    problem="Design a rate limiter using the token bucket algorithm",
    context={"constraints": "Handle 10k requests/second"}
)
```

### Example 3: With Custom Tools

```python
def calculator(expression: str) -> float:
    return eval(expression)

machine.register_tool("calc", calculator, "Evaluate math expressions")

result = machine.solve("What is (123 * 456) + 789?")
```

## Configuration Options

```python
machine = ThinkingMachine(
    # LLM Configuration
    llm_provider="anthropic",      # "anthropic" or "openai"
    model="claude-sonnet-4-5",     # Specific model
    api_key="your-key",            # API key

    # Resource Limits
    max_recursion_depth=5,         # Max subagent depth
    initial_budget=10000,          # Default token budget

    # Memory
    memory_dir="./ratm_memory",    # Persistent storage

    # Output
    verbose=True                   # Show reasoning process
)
```

## Understanding Results

```python
result = machine.solve("Your problem")

# The solution
print(result.solution)              # Final answer

# Metadata
print(result.confidence)            # Confidence score (0-1)
print(result.strategy_used)         # Strategy that was used
print(result.success)               # Whether it succeeded

# Traces
for trace in result.reasoning_trace:
    print(trace.thought)            # Reasoning step
    print(trace.action)             # Action taken
    print(trace.observation)        # Observation

# Learning
for insight in result.insights_learned:
    print(insight.pattern_description)
    print(insight.effectiveness_score)

# Resources
budget = result.budget_used
print(f"Tokens: {budget.tokens_used}")
print(f"Time: {budget.time_used:.2f}s")
print(f"Remaining: {budget.remaining_ratio():.1%}")
```

## Advanced Features

### Force Specific Strategy

```python
from ratm import ReasoningStrategy

result = machine.solve(
    problem="Your problem",
    strategy=ReasoningStrategy.REACT  # Force ReAct
)
```

### Clear Memory

```python
# Clear all memory (requires confirmation)
machine.clear_memory(confirm=True)
```

## Troubleshooting

### API Key Issues

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key"

# Or pass directly
machine = ThinkingMachine(api_key="your-key")
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e .

# Or install specific dependency
pip install chromadb anthropic
```

### Memory Issues

```bash
# Clear persistent memory
rm -rf ./ratm_memory

# Or in code
machine.clear_memory(confirm=True)
```

## Next Steps

1. **Read the README**: Understand the core concepts
2. **Check ARCHITECTURE.md**: Deep dive into the system design
3. **Run examples**: Try `examples/basic_usage.py` and `examples/advanced_usage.py`
4. **Experiment**: Try your own problems and tools

## Resources

- **GitHub**: https://github.com/jonwiggins/thinking-machine
- **Issues**: Report bugs and request features
- **Discussions**: Share use cases and get help

## Getting Help

If you encounter issues:

1. Check the examples in `examples/`
2. Read the architecture docs in `ARCHITECTURE.md`
3. Search existing GitHub issues
4. Open a new issue with reproducible example

Happy thinking! 🧠✨
