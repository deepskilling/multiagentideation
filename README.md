# 🚀 Multi-Agent Creativity System for SaaS Product Ideation

An autonomous multi-agent AI system that generates, evaluates, and evolves innovative SaaS product ideas using specialized LLM agents working collaboratively.

## 🎯 Overview

This system implements a creative loop with five specialized AI agents:

1. **Generator Agent** - Creates novel SaaS product ideas
2. **Critic Agent** - Evaluates ideas on novelty, feasibility, market fit, and viability
3. **Synthesizer Agent** - Merges complementary ideas into superior hybrids
4. **Disruptor Agent** - Challenges assumptions and creates bold variations
5. **Strategist Agent** - Oversees the process and determines convergence

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator                          │
│              (Creative Loop Controller)                 │
└───────────┬──────────────────────────────────┬─────────┘
            │                                  │
    ┌───────▼────────┐                ┌───────▼────────┐
    │    Generator    │                │     Critic     │
    │   (GPT-4/Claude)│                │  (GPT-4/Claude)│
    └───────┬─────────┘                └───────┬────────┘
            │                                  │
    ┌───────▼────────────────────────────────▼────────┐
    │           Synthesizer & Disruptor               │
    │            (Idea Evolution)                     │
    └───────────────────┬─────────────────────────────┘
                        │
                ┌───────▼────────┐
                │   Strategist   │
                │ (Convergence)  │
                └────────────────┘
                        │
        ┌───────────────▼──────────────────┐
        │  DuckDB + FAISS                  │
        │  (Ideas, Scores, Embeddings)     │
        └──────────────────────────────────┘
```

## ⚡ Quick Start

### 1. Installation

```bash
# Clone the repository
cd /path/to/MULTI_AGENT

# Create and activate conda environment (if using conda)
conda activate graph

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# LLM API Keys (Anthropic required for Claude Sonnet 4.5)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional: Override default models (all agents use Claude Sonnet 4.5 by default)
# GENERATOR_MODEL=claude-sonnet-4.5-20250514
# CRITIC_MODEL=claude-sonnet-4.5-20250514
```

**Note:** The system now uses **Claude Sonnet 4.5** for all agents by default. See `MODEL_INFO.md` for details.

### 3. Run the System

**Generate a batch of ideas:**
```bash
python main.py generate --domain "GRC" --num-ideas 10
```

**Run the full creative loop:**
```bash
python main.py creative-loop --domain "DevOps" --num-ideas 5 --max-iterations 5
```

**Export top ideas:**
```bash
python main.py export --output my_ideas.json
```

## 📋 Commands

### `generate`
Generate a single batch of ideas without iteration.

```bash
python main.py generate \
  --domain "Cloud Infrastructure" \
  --num-ideas 10 \
  --output results.json
```

**Options:**
- `--domain`: Target domain (DevOps, Cloud Infrastructure, GRC, BI, AI/ML, etc.)
- `--num-ideas`: Number of ideas to generate (default: 5)
- `--output`: Output JSON file path (optional)

### `creative-loop`
Run the full multi-agent creative loop with iteration.

```bash
python main.py creative-loop \
  --domain "GRC" \
  --num-ideas 5 \
  --max-iterations 10
```

**Options:**
- `--domain`: Target domain
- `--num-ideas`: Ideas per iteration (default: 5)
- `--max-iterations`: Maximum iterations (default: 10)
- `--output`: Output file for final report (optional)

**What happens in each iteration:**
1. Generator creates N new ideas
2. Critic evaluates each idea on 4 dimensions
3. Top K ideas are selected (balancing quality + diversity)
4. Synthesizer merges complementary pairs
5. Disruptor creates bold variations
6. Strategist assesses progress and decides to continue/stop

### `export`
Export top ideas from the database to JSON.

```bash
python main.py export --output top_ideas.json
```

## 🎨 Domains

Choose from these pre-configured domains:

- **DevOps** - CI/CD, automation, infrastructure
- **Cloud Infrastructure** - Cloud management, orchestration
- **GRC** - Governance, Risk, Compliance
- **Business Intelligence** - Analytics, dashboards, reporting
- **AI/ML Operations** - MLOps, model management
- **Cybersecurity** - Security tools, threat detection
- **Data Analytics** - Data processing, insights
- **Enterprise Collaboration** - Team productivity, communication

## 📊 Output Schema

Each generated idea includes:

```json
{
  "idea_name": "CloudAudit Pro",
  "problem_statement": "Organizations struggle to maintain compliance...",
  "target_user": "Cloud Security Engineers and Compliance Officers",
  "core_features": [
    "Real-time compliance monitoring",
    "Automated audit reports",
    "Multi-cloud support"
  ],
  "differentiator": "AI-powered risk prediction",
  "tech_stack": ["Python", "React", "Terraform", "PostgreSQL"],
  "revenue_model": "Subscription",
  "domain": "GRC"
}
```

Each evaluation includes:

```json
{
  "novelty": 0.85,
  "feasibility": 0.78,
  "market_fit": 0.82,
  "viability": 0.76,
  "composite_score": 0.803,
  "justification": "Detailed reasoning..."
}
```

## 🧮 Scoring System

**Composite Score Formula:**

```
Score = 0.3×Novelty + 0.3×Feasibility + 0.2×Market_Fit + 0.2×Viability
```

**Dimensions:**

- **Novelty** (30%): Semantic uniqueness + LLM assessment of innovation
- **Feasibility** (30%): Technical viability, resources, time-to-market
- **Market Fit** (20%): Problem significance, target clarity, demand
- **Viability** (20%): Revenue potential, competition, scalability, ROI

## 📁 Project Structure

```
MULTI_AGENT/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base class for all agents
│   ├── generator_agent.py     # Idea generation
│   ├── critic_agent.py        # Idea evaluation
│   ├── synthesizer_agent.py   # Idea merging
│   ├── disruptor_agent.py     # Bold variations
│   └── strategist_agent.py    # Strategic oversight
├── core/
│   ├── __init__.py
│   ├── models.py              # Pydantic data models
│   ├── database.py            # DuckDB interface
│   ├── scoring.py             # Scoring engine + embeddings
│   └── orchestrator.py        # Main creative loop
├── data/
│   ├── ideas.db               # DuckDB database
│   └── vectors/               # FAISS vector store
├── reports/
│   └── top_saas_ideas.json    # Generated ideas
├── docs/
│   └── prompts_and_roles.md   # Agent prompts documentation
├── ui/
│   └── dashboard/             # (Future) Web dashboard
├── config.py                  # Configuration management
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

Edit `config.py` or use environment variables:

```python
# Scoring Weights (must sum to ~1.0)
NOVELTY_WEIGHT = 0.3
FEASIBILITY_WEIGHT = 0.3
MARKET_FIT_WEIGHT = 0.2
VIABILITY_WEIGHT = 0.2

# Creative Loop Parameters
MAX_ITERATIONS = 10
TOP_K_IDEAS = 5
SIMILARITY_THRESHOLD = 0.85  # For duplicate detection

# Model Selection - All agents use Claude Sonnet 4.5
GENERATOR_MODEL = "claude-sonnet-4.5-20250514"
CRITIC_MODEL = "claude-sonnet-4.5-20250514"
SYNTHESIZER_MODEL = "claude-sonnet-4.5-20250514"
DISRUPTOR_MODEL = "claude-sonnet-4.5-20250514"
STRATEGIST_MODEL = "claude-sonnet-4.5-20250514"
```

**See `MODEL_INFO.md` for detailed model configuration and cost estimation.**

## 🎯 Use Cases

1. **Product Ideation** - Generate 100s of validated SaaS concepts
2. **Market Research** - Identify gaps and opportunities
3. **Innovation Workshops** - Seed discussions with AI-generated ideas
4. **Competitive Analysis** - Explore alternative approaches
5. **Portfolio Planning** - Evaluate multiple product directions

## 🧠 Key Features

✅ **Multi-Agent Collaboration** - Specialized agents with distinct roles  
✅ **Semantic Novelty Detection** - Uses embeddings to ensure uniqueness  
✅ **Iterative Refinement** - Ideas evolve through multiple rounds  
✅ **Diversity + Quality Balance** - Selects diverse high-quality ideas  
✅ **Automatic Convergence** - Strategist detects when to stop  
✅ **Persistent Storage** - All ideas stored in DuckDB  
✅ **Flexible LLM Support** - Works with OpenAI and Anthropic models  

## 📈 Example Output

```
🔄 ITERATION 3/10
────────────────────────────────────────────────────────────
  1️⃣  Generator: Creating ideas...
      Generated 5 ideas
  2️⃣  Computing embeddings...
  3️⃣  Critic: Evaluating ideas...
      Evaluation complete
  4️⃣  Selecting top ideas...
      Selected top 5 ideas
        1. CloudGuard AI (Score: 0.823)
        2. ComplianceFlow Pro (Score: 0.798)
        3. RiskRadar 360 (Score: 0.776)
  5️⃣  Synthesizer: Merging ideas...
      Created 2 synthesized ideas
  6️⃣  Disruptor: Creating variations...
      Created 2 disrupted variations

📊 Iteration 3 Summary:
   Ideas Generated: 5
   Best Score: 0.823
   Should Continue: True
```

## 🚀 Advanced Usage

### Programmatic Access

```python
from core.orchestrator import CreativityOrchestrator

# Initialize
orchestrator = CreativityOrchestrator()

# Run creative loop
report = orchestrator.run_creative_loop(
    domain="GRC",
    initial_ideas=10,
    max_iterations=5
)

# Access results
top_ideas = orchestrator.db.get_top_ideas(k=10)
```

### Custom Agent Behavior

Modify agent prompts in `agents/*_agent.py` files to customize behavior.

### Batch Processing

Process multiple domains:

```python
domains = ["DevOps", "GRC", "Cloud Infrastructure"]
for domain in domains:
    orchestrator.run_creative_loop(domain=domain)
```

## 🔮 Future Enhancements

- [ ] Interactive web dashboard (Streamlit/React)
- [ ] Market Sentinel agent (real-time trend monitoring)
- [ ] Persona Simulation agents (customer perspective)
- [ ] Financial Analyst agent (ROI estimation)
- [ ] Prototype Generator (auto-generate PRDs)
- [ ] Fine-tuning on successful ideas
- [ ] Multi-domain synthesis
- [ ] API endpoints (FastAPI)

## 📄 License

[Specify your license]

## 👥 Credits

Developed for Deepskilling / CognitiveBricks

## 🐛 Troubleshooting

**Issue: "No API keys found"**
- Create a `.env` file with `ANTHROPIC_API_KEY` (required for Claude Sonnet 4.5)

**Issue: "Module not found"**
- Run `pip install -r requirements.txt`

**Issue: "Model not found" or "Invalid model"**
- Verify model name in config: `claude-sonnet-4.5-20250514`
- Check Anthropic's latest API documentation for current model names
- See `MODEL_INFO.md` for alternative model options

**Issue: Slow generation**
- Reduce `--num-ideas`
- Claude Sonnet 4.5 is generally fast, but network latency can affect speed

**Issue: Low quality ideas**
- Increase `--max-iterations`
- Adjust scoring weights in `config.py`
- Claude Sonnet 4.5 provides high-quality outputs by default

## 📞 Support

For issues or questions, contact [your contact info]

---

**Happy Ideating! 🚀**

