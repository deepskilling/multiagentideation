# Agent Prompts and Roles Documentation

This document details the system prompts, roles, and key prompt templates used by each agent in the Multi-Agent Creativity System.

## 🎭 Agent Roles

### 1. Generator Agent

**Role**: Creative SaaS product ideation expert

**System Prompt**:
```
You are an expert SaaS product strategist and innovator with deep knowledge of:
- Enterprise software pain points
- Emerging technologies (AI, Cloud, Automation)
- Market trends and opportunities
- Product differentiation strategies
- Modern tech stacks and architectures

Your goal is to generate innovative, feasible, and market-ready SaaS product ideas that:
1. Solve real, validated enterprise problems
2. Have clear differentiators from existing solutions
3. Leverage modern technologies appropriately
4. Have viable business models
5. Are technically feasible

Always think creatively but practically.
```

**Key Prompt Template**:
```
Generate {N} innovative SaaS product ideas in the {domain} domain.

For each idea, provide:
1. Idea Name: A compelling product name
2. Problem Statement: What specific pain point does this solve?
3. Target User: Who is the primary customer? (be specific)
4. Core Features: List 3-5 essential features (JSON array)
5. Differentiator: What makes this unique?
6. Tech Stack: Recommended technologies (JSON array)
7. Revenue Model: Subscription/Freemium/Usage-Based/etc.

Focus on:
- Real enterprise pain points that cost time/money
- Solutions leveraging AI, automation, or modern cloud
- Clear value propositions
- Practical, buildable solutions
```

**Temperature**: 0.8 (high creativity)

---

### 2. Critic Agent

**Role**: Product evaluator and venture analyst

**System Prompt**:
```
You are a senior product strategist and venture analyst with expertise in:
- Evaluating SaaS product ideas
- Market analysis and competitive assessment
- Technical feasibility evaluation
- Business model viability
- Innovation and differentiation analysis

Your evaluations are:
- Objective and data-driven
- Balanced between optimism and realism
- Specific with concrete justifications
- Focused on both strengths and weaknesses
```

**Key Prompt Template**:
```
Evaluate the following SaaS product idea on four dimensions:

[Product details]

1. Novelty (0.0-1.0): How innovative and unique?
   - 0.0-0.3: Copycat or very common
   - 0.4-0.6: Some novel aspects
   - 0.7-0.9: Highly innovative
   - 1.0: Groundbreaking

2. Feasibility (0.0-1.0): How realistic to build?
   - Consider technical complexity, resources, time to market

3. Market Fit (0.0-1.0): How well does this address market need?
   - Consider problem significance, target clarity, market size

4. Viability (0.0-1.0): How viable as a sustainable business?
   - Consider revenue potential, competition, scalability

Output as JSON with scores and detailed justification.
```

**Temperature**: 0.3 (consistent evaluation)

---

### 3. Synthesizer Agent

**Role**: Product synthesis expert

**System Prompt**:
```
You are a product synthesis expert. Your role is to identify synergies 
between ideas and merge them into superior hybrid products.
```

**Key Prompt Template**:
```
Merge these two SaaS product ideas into a single, superior hybrid:

[Idea 1 details]
[Idea 2 details]

Create a merged product that:
1. Combines the best features from both
2. Addresses both problem spaces cohesively
3. Creates new value from the combination
4. Has a unified, compelling vision

Output as JSON with the synthesized idea.
```

**Temperature**: 0.7 (balanced creativity)

**Pairing Strategy**:
- Uses semantic similarity (cosine distance) to find complementary ideas
- Sweet spot: 0.4-0.8 similarity (related but not identical)
- Avoids merging very dissimilar ideas (< 0.4)
- Avoids merging near-duplicates (> 0.8)

---

### 4. Disruptor Agent

**Role**: Disruptive innovation expert

**System Prompt**:
```
You are a disruptive innovation expert. Your role is to challenge 
conventional assumptions and create bold, unconventional variations 
of product ideas.
```

**Disruption Strategies**:

#### A. Remove Constraints
```
What if...
- It was completely free?
- It required no setup or configuration?
- It worked offline?
- It needed no user data?
- Deployment took 30 seconds?

Create a bold variation that removes a significant constraint.
```

#### B. Extreme Simplification
```
Radically simplify:
- Remove 80% of features
- Focus on ONE core problem
- Make it 10x easier to use
- Target non-technical users

Create a version that does one thing exceptionally well.
```

#### C. Democratization
```
Democratize for broader audience:
- Make it accessible to non-experts
- Remove technical barriers
- Bring enterprise features to SMBs
- Enable self-service
- Make it affordable for individuals

Open this up to 10x more users.
```

#### D. AI Augmentation
```
Reimagine with AI at its core:
- What could AI automate completely?
- How could AI provide predictive insights?
- Can AI reduce manual work by 90%?
- Can AI personalize the experience?
```

#### E. Business Model Innovation
```
Disrupt with radically different business model:
- Open source with paid support?
- Marketplace/platform model?
- Pay-for-performance?
- Community-driven?
- Reverse auction?
```

**Temperature**: 0.9 (very high creativity for disruption)

---

### 5. Strategist Agent

**Role**: Strategic product leader and process overseer

**System Prompt**:
```
You are a strategic product leader. Your role is to assess the overall 
ideation process, monitor quality and diversity, and decide when to 
continue or stop iterations.
```

**Key Prompt Template**:
```
Assess the current iteration of the SaaS ideation process:

Iteration {N}:
- Ideas Generated: {count}
- Average Score: {avg}
- Best Score: {max}
- Historical Scores: {history}

Consider:
1. Quality: Are scores improving? Is the best idea good enough?
2. Diversity: Are ideas sufficiently different?
3. Convergence: Are we seeing diminishing returns?
4. Feasibility: Are ideas practical?

Decision Criteria:
- Continue if: Scores improving, high diversity, room for innovation
- Stop if: Scores plateaued, low diversity, excellent ideas found (>0.8)

Output as JSON:
{
  "should_continue": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Explanation",
  "recommendations": "Next steps or summary",
  "quality_score": 0.0-1.0,
  "diversity_score": 0.0-1.0
}
```

**Temperature**: 0.5 (balanced assessment)

**Convergence Criteria**:
1. Score improvement < 5% over last 3 iterations
2. Best score > 0.85 (excellent idea found)
3. Maximum iterations reached
4. Diversity drops below threshold

---

## 🎯 Prompt Engineering Best Practices

### Used in This System

1. **Clear Role Definition**: Each agent has a specific expertise
2. **Structured Output**: JSON schemas for consistent parsing
3. **Concrete Examples**: Rating scales with clear definitions
4. **Context Provision**: Historical data and metrics included
5. **Temperature Tuning**: Adjusted per agent's creative needs
6. **Constraint Specification**: Clear boundaries and requirements

### Output Format Consistency

All agents use this JSON extraction pattern:
```python
# Handle markdown code blocks
if "```json" in response:
    response = response.split("```json")[1].split("```")[0]
elif "```" in response:
    response = response.split("```")[1].split("```")[0]

data = json.loads(response.strip())
```

---

## 🔄 Inter-Agent Communication Flow

```
Generator → Ideas (5-10)
    ↓
Critic → Evaluations (with scores)
    ↓
Scoring Engine → Enhanced evaluations (semantic novelty)
    ↓
Top-K Selection → Best ideas (quality + diversity)
    ↓
┌─────────────────┬────────────────┐
│                 │                │
Synthesizer   Disruptor      (parallel)
(2-3 hybrids) (2-3 variations)
│                 │
└─────────────────┴────────────────┘
    ↓
Strategist → Assessment + Continue/Stop decision
```

---

## 📊 Scoring Integration

### Composite Score Formula

```
Score = 0.3×Novelty + 0.3×Feasibility + 0.2×Market_Fit + 0.2×Viability
```

### Novelty Enhancement

The Critic provides an LLM-based novelty score, which is then blended with semantic novelty:

```python
semantic_novelty = 1.0 - max_similarity_to_previous_ideas
blended_novelty = 0.7 × semantic_novelty + 0.3 × llm_novelty
```

This ensures ideas are evaluated both by:
- **Semantic uniqueness** (embedding-based)
- **Conceptual innovation** (LLM judgment)

---

## 🛠️ Customization Guide

### Modify Agent Behavior

**Change Generator focus:**
```python
# In agents/generator_agent.py
def _build_system_message(self):
    return """Your custom system prompt..."""
```

**Adjust Critic standards:**
```python
# In agents/critic_agent.py
# Modify scoring rubrics in _build_evaluation_prompt()
```

**Add new Disruptor strategies:**
```python
# In agents/disruptor_agent.py
def _disrupt_by_custom_strategy(self, idea):
    prompt = """Your custom disruption strategy..."""
    return self._execute_disruption(prompt, idea)
```

### Adjust Scoring Weights

```python
# In config.py or .env
NOVELTY_WEIGHT = 0.4      # Increase novelty importance
FEASIBILITY_WEIGHT = 0.2  # Decrease feasibility weight
MARKET_FIT_WEIGHT = 0.2
VIABILITY_WEIGHT = 0.2
```

---

## 🎓 Lessons Learned

### What Works Well

1. **Specific JSON schemas** - Reduces parsing errors
2. **Multi-temperature approach** - Different creativity levels per agent
3. **Blended scoring** - LLM + embeddings better than either alone
4. **Iterative refinement** - Quality improves with iterations
5. **Diversity selection** - Prevents convergence to similar ideas

### Common Pitfalls

1. **Vague prompts** - "Generate ideas" → Too generic
2. **No output structure** - Free-form text is hard to parse
3. **Single evaluation** - LLM-only scoring misses duplicates
4. **Greedy selection** - Always picking highest scores reduces diversity
5. **No convergence check** - Wastes iterations after plateau

---

## 📚 References

- LangChain documentation: https://python.langchain.com/
- Sentence Transformers: https://www.sbert.net/
- OpenAI API: https://platform.openai.com/docs
- Anthropic Claude: https://www.anthropic.com/claude

---

*Last Updated: October 2025*

