# RATM Test Suite: Hard Problems for ASI Development

Based on comprehensive research into 2025 AI benchmarks, this test suite defines concrete, measurable challenges for developing and evaluating ASI-level systems.

## Philosophy

**Test-Driven ASI Development**: Rather than building systems in a vacuum, we define success criteria first through the hardest problems AI currently fails to solve, then iterate on architectures until they pass.

## Test Suite Structure

Tests are organized by difficulty tier and required capabilities:

- **Tier 1**: Foundation (Current SOTA: 60-90% success)
- **Tier 2**: Advanced (Current SOTA: 20-60% success)
- **Tier 3**: Frontier (Current SOTA: <20% success)
- **Tier 4**: Unsolved (Current SOTA: <5% success)

---

## TIER 1: FOUNDATION TESTS

These establish baseline capabilities. Current SOTA models achieve 60-90% on these.

### T1.1: Multi-Step Code Generation (SWE-bench Verified)

**Benchmark**: SWE-bench Verified (500 real GitHub issues)
**Current SOTA**: 72.7% (Claude Sonnet 4), 74.9% (GPT-5)
**Target**: >80%

**Test Cases**:
```python
# Test Case 1: Multi-file refactoring
def test_sphinx_napoleon_param():
    """
    Issue: napoleon_use_param should affect 'other parameters' section
    Repo: sphinx-doc/sphinx
    Files to modify: 2-3 files
    Tests to pass: 8 unit tests

    Success criteria:
    - All tests pass
    - No regression in other tests
    - Code follows repository style
    """

# Test Case 2: Performance optimization
def test_django_query_optimization():
    """
    Issue: Optimize N+1 queries in admin interface
    Repo: django/django
    Files to modify: 1-2 files
    Tests to pass: 15 unit tests
    Benchmark: Must be 50% faster than baseline

    Success criteria:
    - Performance improvement verified
    - All existing tests pass
    - No breaking changes
    """

# Test Case 3: Bug fix with debugging
def test_matplotlib_legend_bug():
    """
    Issue: Legend labels not updating when data changes
    Repo: matplotlib/matplotlib
    Files to modify: 1-2 files
    Tests to pass: 12 unit tests

    Success criteria:
    - Bug reproduction confirmed
    - Fix verified with new tests
    - Edge cases handled
    """
```

**Evaluation Metrics**:
- Pass@1: First attempt success rate
- Test coverage: % of tests passing
- Code quality: Style compliance, no regressions
- Efficiency: Tokens used, time taken

**RATM Requirements**:
- Tool use: File reading, code editing, test execution
- Memory: Track changes across files
- Subagents: Potentially spawn debugging or testing subagents
- Budget: Allocate 5K-10K tokens per issue

---

### T1.2: Multi-Hop Question Answering (HotpotQA)

**Benchmark**: HotpotQA (113K multi-hop QA pairs)
**Current SOTA**: 89% (HiVA hierarchical agents), 79.7% accuracy
**Target**: >85%

**Test Cases**:
```python
# Test Case 1: Two-hop reasoning
def test_two_hop_qa():
    """
    Q: "What government position was held by the woman who portrayed
        Corliss Archer in the film Kiss and Tell?"

    Required reasoning:
    1. Who portrayed Corliss Archer in Kiss and Tell? → Shirley Temple
    2. What government position did Shirley Temple hold? → U.S. Ambassador

    Success criteria:
    - Identify both reasoning steps
    - Retrieve correct intermediate fact
    - Provide final answer with justification
    """

# Test Case 2: Three-hop reasoning with constraint
def test_three_hop_constrained():
    """
    Q: "In what year was the founder of the company that produced
        the first commercial GPS receiver born?"

    Required reasoning:
    1. What company produced first commercial GPS receiver? → Magellan
    2. Who founded Magellan? → [founder name]
    3. When was [founder] born? → [year]

    Success criteria:
    - All intermediate facts correct
    - Final answer correct
    - Evidence for each hop provided
    """
```

**Evaluation Metrics**:
- Exact Match (EM): Exact answer match
- F1 Score: Token overlap
- Supporting Facts: % of correct evidence retrieval
- Hop Completion: % of intermediate steps correct

**RATM Requirements**:
- Decomposition: Break question into subquestions
- Memory: Track intermediate facts in working memory
- Search: Retrieve relevant information
- Verification: Check consistency across hops

---

### T1.3: High School Math Competition (AIME)

**Benchmark**: AIME (15 problems, median human score 4-6)
**Current SOTA**: 96.7% (o3), 94.6% (GPT-5)
**Target**: >90%

**Test Cases**:
```python
# Test Case 1: Combinatorics
def test_aime_2024_problem_7():
    """
    Problem: "In how many ways can 8 people be seated around a circular
    table such that no two of Alice, Bob, and Charlie sit next to each other?"

    Answer: 2880

    Required reasoning:
    - Circular permutation principles
    - Inclusion-exclusion principle
    - Constraint satisfaction

    Success criteria:
    - Correct numerical answer
    - Valid solution approach shown
    - Edge cases considered
    """

# Test Case 2: Number theory
def test_aime_2025_problem_3():
    """
    Problem: "Find the number of positive integers n ≤ 1000 for which
    the polynomial x² + x - n can be factored as (x + a)(x + b) where
    a and b are integers."

    Answer: 31

    Required reasoning:
    - Factorization conditions
    - Systematic enumeration
    - Mathematical proof

    Success criteria:
    - Correct answer
    - Complete solution with justification
    - No calculation errors
    """
```

**Evaluation Metrics**:
- Correctness: Exact numerical answer
- Reasoning Quality: Solution approach validity
- Tool Use: Calculator/Python usage
- Efficiency: Steps to solution

**RATM Requirements**:
- Tool use: Python interpreter for calculations
- Multi-step reasoning: Track solution progress
- Verification: Check answer against problem constraints
- Budget: 2K-4K tokens per problem

---

## TIER 2: ADVANCED TESTS

These test capabilities beyond current SOTA. Success rate: 20-60%.

### T2.1: Abstract Visual Reasoning (ARC-AGI-2)

**Benchmark**: ARC-AGI-2 (launched March 2025)
**Current SOTA**: 16% (Grok 4 Thinking)
**Target**: >30%

**Test Cases**:
```python
# Test Case 1: Multi-step compositional pattern
def test_arc_compositional():
    """
    Input: 3 example grid transformations showing:
    - Step 1: Identify red squares
    - Step 2: Place blue square above each red square
    - Step 3: Connect blue squares with green line

    Test: Apply to novel grid configuration

    Success criteria:
    - Identify all three transformation steps
    - Apply in correct sequence
    - Handle edge cases (boundaries, overlaps)
    - Generalize to different grid sizes
    """

# Test Case 2: Contextual rule application
def test_arc_contextual():
    """
    Input: Examples where same symbol behaves differently based on:
    - Position (corners vs. center)
    - Neighbors (adjacent colors)
    - Global patterns (symmetry)

    Test: Determine context-dependent behavior in new grid

    Success criteria:
    - Recognize contextual factors
    - Apply rules conditionally
    - Avoid superficial pattern matching
    """
```

**Evaluation Metrics**:
- Exact Grid Match: Complete transformation correctness
- Partial Credit: Correct sub-patterns
- Generalization: Performance on unseen variants
- Reasoning Trace: Quality of explanations

**RATM Requirements**:
- **Critical**: True abstraction (not pattern matching)
- Few-shot learning from 3-5 examples
- Compositional reasoning
- Symbolic understanding
- Core knowledge priors (object permanence, causality)

---

### T2.2: Long-Context Reasoning (MuSR)

**Benchmark**: MuSR (murder mysteries, ~1000 words each)
**Current SOTA**: Near random chance
**Target**: >50%

**Test Cases**:
```python
# Test Case 1: Murder mystery
def test_musr_murder_mystery():
    """
    Scenario: 1000-word mystery with:
    - 6 suspects
    - 15 clues scattered throughout
    - 3 red herrings
    - 8 alibi constraints
    - 4 timeline dependencies

    Task: Identify the murderer and explain reasoning

    Success criteria:
    - Correct suspect identified
    - All clues integrated
    - Alibis verified
    - Timeline consistent
    - Red herrings dismissed with justification
    """

# Test Case 2: Team allocation puzzle
def test_musr_team_allocation():
    """
    Scenario: Allocate 20 people to 5 teams with:
    - Skill requirements per team
    - Personality compatibility constraints
    - Budget limitations
    - Previous team history
    - Individual preferences

    Task: Create valid allocation maximizing constraints

    Success criteria:
    - All hard constraints satisfied
    - Optimization of soft constraints
    - Explanation of trade-offs
    - Alternative solutions considered
    """
```

**Evaluation Metrics**:
- Correctness: Final answer accuracy
- Constraint Satisfaction: % of constraints met
- Reasoning Completeness: All clues considered
- Efficiency: Tokens/time to solution

**RATM Requirements**:
- Long-context tracking (8K+ tokens)
- Systematic constraint checking
- State management across reasoning
- Subgoal decomposition
- Memory consolidation

---

### T2.3: Graduate-Level Science (GPQA Diamond)

**Benchmark**: GPQA Diamond (198 PhD-level questions)
**Current SOTA**: 88% (Grok 4), 85.7% (GPT-5 reasoning)
**Target**: >85%

**Test Cases**:
```python
# Test Case 1: Quantum mechanics
def test_gpqa_quantum():
    """
    Q: "A quantum mechanical system contains a particle of mass m moving
    in an isotropic three-dimensional potential V(r) = 1/2mω²r².
    What is the energy of the third excited state and how many linearly
    independent eigenfunctions exist for this state?"

    Required knowledge:
    - 3D quantum harmonic oscillator
    - Degeneracy calculations
    - Energy level formulas

    Success criteria:
    - Correct energy formula
    - Correct degeneracy count
    - Physical reasoning demonstrated
    """

# Test Case 2: Organic chemistry
def test_gpqa_chemistry():
    """
    Q: "When cyclopentadiene is treated with ethylene in the presence
    of heat, what is the major product and what mechanism explains its formation?"

    Required knowledge:
    - Diels-Alder reaction
    - Stereochemistry
    - Reaction mechanisms

    Success criteria:
    - Correct product structure
    - Mechanism steps explained
    - Stereochemistry specified
    """
```

**Evaluation Metrics**:
- Accuracy: Correct answer selection
- Reasoning Quality: Explanation correctness
- Domain Knowledge: Appropriate concepts applied
- Confidence Calibration: Uncertainty matching accuracy

**RATM Requirements**:
- Deep domain knowledge (semantic memory)
- Multi-step scientific reasoning
- Theoretical framework application
- Tool use (calculations, structure drawing)

---

## TIER 3: FRONTIER TESTS

Cutting-edge challenges. Current SOTA: <20%.

### T3.1: Research-Level Mathematics (FrontierMath)

**Benchmark**: FrontierMath (original unpublished math problems)
**Current SOTA**: <2% (most models), ~25% (o3 with max compute)
**Target**: >15%

**Test Cases**:
```python
# Test Case 1: Undergraduate-level number theory
def test_frontiermath_number_theory():
    """
    Problem: [Original problem from FrontierMath corpus]

    Tier: 2 (undergraduate)
    Topics: Prime numbers, modular arithmetic
    Expected solution time: 2-4 hours (expert mathematician)

    Success criteria:
    - Valid proof or counterexample
    - All edge cases addressed
    - Mathematical rigor maintained
    - Novel approach if standard methods fail
    """

# Test Case 2: Graduate-level analysis
def test_frontiermath_analysis():
    """
    Problem: [Original problem from FrontierMath corpus]

    Tier: 3 (graduate)
    Topics: Banach spaces, functional analysis
    Expected solution time: 1-2 days (expert)

    Success criteria:
    - Complete mathematical proof
    - Proper use of theorems
    - Counterexamples where applicable
    - Creative insight demonstrated
    """
```

**Evaluation Metrics**:
- Correctness: Mathematical validity
- Rigor: Proof completeness
- Creativity: Novel approaches
- Efficiency: Solution elegance

**RATM Requirements**:
- **Critical**: Mathematical creativity
- Extended reasoning (hours/days)
- Proof verification and debugging
- Hypothesis generation and testing
- Meta-reasoning about approaches
- Budget requests with justification

---

### T3.2: Open-Ended System Design

**Benchmark**: Real-world architecture problems
**Current SOTA**: Not systematically benchmarked
**Target**: Expert-validated quality

**Test Cases**:
```python
# Test Case 1: Distributed cache design
def test_system_design_cache():
    """
    Requirements:
    - 10K requests/sec
    - <10ms p99 latency
    - TTL support
    - LRU eviction
    - Multi-datacenter
    - Fault tolerance
    - Cost: <$5K/month

    Deliverable:
    - Architecture diagram
    - Component specifications
    - Trade-off analysis
    - Failure mode analysis
    - Cost breakdown

    Evaluation:
    - Expert panel review (5 senior engineers)
    - Feasibility check
    - Completeness assessment
    - Novelty/creativity score
    """

# Test Case 2: Legacy system migration
def test_system_migration():
    """
    Scenario:
    - Monolithic PHP app (500K LOC)
    - MySQL with 50 tables
    - 5M users
    - Zero downtime requirement
    - 6-month timeline
    - Team of 8 engineers

    Deliverable:
    - Migration strategy
    - Risk mitigation plan
    - Rollback procedures
    - Testing strategy
    - Timeline with milestones

    Evaluation:
    - Completeness of planning
    - Risk awareness
    - Practicality
    - Industry best practices
    """
```

**Evaluation Metrics**:
- Expert Rating: Panel evaluation (1-10)
- Completeness: All requirements addressed
- Feasibility: Implementable within constraints
- Creativity: Novel solutions vs. standard approaches
- Trade-off Reasoning: Explicit justification

**RATM Requirements**:
- Multi-constraint reasoning
- Trade-off analysis
- Long-horizon planning
- Subagent coordination (different aspects)
- Tool use (cost calculators, diagram generation)

---

### T3.3: Scientific Hypothesis Generation

**Benchmark**: Novel research hypotheses
**Current SOTA**: High hallucination rate (33-48%)
**Target**: >50% expert-validated as interesting

**Test Cases**:
```python
# Test Case 1: Materials science
def test_hypothesis_materials():
    """
    Context:
    - Literature on superconductivity (100 papers)
    - Current SOTA: Critical temp 203K
    - Research constraints: Ambient pressure

    Task: Generate 5 testable hypotheses for room-temp superconductors

    Evaluation:
    - Expert panel (3 materials scientists)
    - Novelty: Not in literature
    - Plausibility: Physical principles sound
    - Testability: Experiments definable
    - Interestingness: Worth pursuing

    Success: ≥2/5 hypotheses rated "worth investigating"
    """

# Test Case 2: Computational biology
def test_hypothesis_biology():
    """
    Context:
    - Protein folding database
    - Recent AlphaFold predictions
    - Unsolved: Dynamics prediction

    Task: Propose approach for predicting conformational changes

    Evaluation:
    - Computational biologist review
    - Builds on existing knowledge
    - Addresses known limitations
    - Computationally tractable
    - Experimentally verifiable

    Success: Hypothesis deemed "publishable if validated"
    """
```

**Evaluation Metrics**:
- Novelty Score: Not in training data (1-5)
- Plausibility Score: Physically/logically sound (1-5)
- Testability Score: Can be experimentally verified (1-5)
- Interestingness Score: Worth research effort (1-5)
- Overall: Average ≥3.5/5 to pass

**RATM Requirements**:
- **Critical**: True creativity beyond recombination
- Literature synthesis (semantic memory)
- Gap identification
- Theoretical reasoning
- Constraint checking (physics, chemistry, biology)
- Uncertainty quantification

---

## TIER 4: UNSOLVED CHALLENGES

The hardest problems. Current AI achieves <5%.

### T4.1: ARC-AGI-2 Unsolved Tasks

**Benchmark**: ARC-AGI-2 hardest problems
**Current SOTA**: ~16% overall, <5% on hardest subset
**Target**: >20% on hardest subset

**Approach**: Iterative prototype development
- Prototype 1: Enhanced pattern matching
- Prototype 2: Symbolic abstraction layer
- Prototype 3: Core knowledge priors
- Prototype 4: Meta-learning from failures

---

### T4.2: Multi-Year Strategic Planning

**Benchmark**: Business strategy simulation
**Current SOTA**: Not solved
**Target**: Competitive with human strategists

**Test Case**:
```python
def test_strategic_planning():
    """
    Scenario: Tech startup (Series A, $10M raised)
    - Market: AI development tools
    - Competition: 15 competitors
    - Team: 25 people
    - Runway: 18 months

    Task: Develop 3-year strategy including:
    - Product roadmap
    - Market positioning
    - Hiring plan
    - Revenue projections
    - Risk mitigation
    - Pivot scenarios

    Evaluation: Benchmark against actual successful startups
    """
```

---

### T4.3: Novel Theorem Discovery

**Benchmark**: Automated theorem proving with novelty
**Current SOTA**: Can prove known theorems, struggles with novelty
**Target**: Generate 1 interesting theorem per 100 attempts

**Test Case**:
```python
def test_theorem_discovery():
    """
    Domain: Number theory or graph theory

    Task: Discover and prove novel theorems

    Evaluation by mathematicians:
    - Is it correct?
    - Is it novel?
    - Is it interesting?
    - Could it lead to further research?

    Success: 1% "interesting" rate
    """
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
**Goal**: Pass 80% of Tier 1 tests

**Focus**:
- SWE-bench Verified (500 test cases)
- HotpotQA (1000 test cases)
- AIME practice problems (100 problems)

**Prototype 1**:
- Basic ReAct with tool use
- Simple working memory
- No subagents yet

**Success Criteria**:
- SWE-bench: >60%
- HotpotQA: >75%
- AIME: >80%

---

### Phase 2: Advanced (Weeks 5-8)
**Goal**: Pass 50% of Tier 2 tests

**Focus**:
- ARC-AGI-2 (100 problems)
- MuSR (50 problems)
- GPQA Diamond (50 problems)

**Prototype 2**:
- Add episodic memory
- Implement subagent spawning
- Budget allocation system

**Success Criteria**:
- ARC-AGI-2: >20%
- MuSR: >40%
- GPQA: >80%

---

### Phase 3: Frontier (Weeks 9-12)
**Goal**: Make progress on Tier 3

**Focus**:
- FrontierMath (20 problems)
- System design (10 cases)
- Hypothesis generation (20 tasks)

**Prototype 3**:
- Semantic memory + insights
- Meta-reasoning capabilities
- Adaptive strategy switching

**Success Criteria**:
- FrontierMath: >5%
- System design: Expert rating >6/10
- Hypotheses: >30% "interesting"

---

### Phase 4: Research (Weeks 13+)
**Goal**: Attack unsolved problems

**Focus**:
- ARC-AGI-2 hardest subset
- Multi-year planning
- Theorem discovery

**Prototype N**:
- Novel architectures as needed
- Experimental approaches
- Fundamental research

---

## EVALUATION FRAMEWORK

### Automated Evaluation
```python
class BenchmarkRunner:
    def run_test_suite(self, model, tier=1):
        """Run all tests in a tier and report metrics."""
        results = {
            'accuracy': 0.0,
            'pass_rate': 0.0,
            'efficiency': {},  # tokens, time per test
            'by_category': {},
        }
        # Implementation
        return results
```

### Human Evaluation
- Expert panels for Tier 3+
- Blind comparison with human solutions
- Novelty and creativity assessment

### Continuous Integration
```bash
# Run nightly on test suite
python -m ratm.benchmarks.run_suite --tier 1 --model ratm-v0.2
python -m ratm.benchmarks.run_suite --tier 2 --model ratm-v0.2
```

---

## CONCLUSION

This test suite provides:
1. **Clear success criteria** across 4 difficulty tiers
2. **Concrete test cases** with evaluation metrics
3. **Phased roadmap** from foundation to research
4. **Automated + human evaluation**
5. **Iterative prototype development**

By focusing on tests first and prototypes second, we ensure our ASI research is grounded in solving real, hard problems that current AI cannot handle.

The progression from Tier 1 (current SOTA struggles) to Tier 4 (completely unsolved) provides a clear path for measuring progress and identifying where novel approaches are needed.

**Next Steps**:
1. Implement benchmark runners for Tier 1 tests
2. Establish baseline with current RATM
3. Iterate on architecture based on failure modes
4. Scale to harder tiers as capabilities improve
