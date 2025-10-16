# 🚀 Quick Start Guide

Get the Multi-Agent Creativity System running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- An API key from OpenAI or Anthropic
- Conda (optional, but recommended)

## Step 1: Setup Environment

### Option A: Using the setup script (recommended)

```bash
cd /path/to/MULTI_AGENT
chmod +x setup.sh
./setup.sh
```

### Option B: Manual setup

```bash
# 1. Activate conda environment (if using conda)
conda activate graph

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create directories
mkdir -p data reports
```

## Step 2: Configure API Keys

Create a `.env` file in the project root:

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Getting API Keys:**
- Anthropic (Required): https://console.anthropic.com/settings/keys

**Note:** The system now uses **Claude Sonnet 4.5** by default for all agents. You need an Anthropic API key. See `MODEL_INFO.md` for details and alternative model options.

## Step 3: Run Your First Generation

### Quick Test (Single Batch)

```bash
python main.py generate --domain "GRC" --num-ideas 5
```

This will:
- Generate 5 SaaS ideas in the GRC domain
- Evaluate each idea on 4 dimensions
- Display results with scores
- Save to `reports/batch_results_grc.json`

**Expected Output:**
```
🚀 Multi-Agent Creativity System Initialized
   Generator: claude-sonnet-4.5-20250514
   Critic: claude-sonnet-4.5-20250514
   ...

🎯 Generating 5 SaaS ideas in GRC domain

1. ComplianceGuard AI (Score: 0.823)
   Problem: Organizations struggle to maintain compliance...
   Target: Compliance Officers and Risk Managers
   Differentiator: AI-powered risk prediction...
```

### Full Creative Loop

```bash
python main.py creative-loop --domain "DevOps" --num-ideas 5 --max-iterations 5
```

This runs the complete multi-agent system:
- Multiple iterations with evolution
- Idea synthesis and disruption
- Automatic convergence detection
- Comprehensive final report

**Time estimate:** 5-15 minutes depending on iterations

## Step 4: Explore Results

### View in Terminal
Results are displayed in the terminal with scores and details.

### Check JSON Output
```bash
cat reports/top_saas_ideas.json
```

### Access Database
```python
python
>>> from core.database import IdeaDatabase
>>> db = IdeaDatabase()
>>> ideas = db.get_top_ideas(k=10)
>>> print(ideas[0]['idea_name'])
```

## 🎯 Common Use Cases

### 1. Quick Brainstorming
```bash
python main.py generate --domain "Cloud Infrastructure" --num-ideas 10
```
Perfect for: Quick ideation sessions, exploring a domain

### 2. Deep Exploration
```bash
python main.py creative-loop --domain "AI/ML Operations" --num-ideas 5 --max-iterations 10
```
Perfect for: Finding truly novel ideas, comprehensive exploration

### 3. Multiple Domains
```bash
for domain in "DevOps" "GRC" "Cybersecurity"; do
  python main.py generate --domain "$domain" --num-ideas 5
done
```
Perfect for: Portfolio planning, market scanning

### 4. Programmatic Usage
```python
# example.py
from core.orchestrator import CreativityOrchestrator

orchestrator = CreativityOrchestrator()
results = orchestrator.generate_single_batch(domain="GRC", num_ideas=5)

for r in results[:3]:
    print(f"{r['idea']['idea_name']}: {r['evaluation']['composite_score']:.3f}")
```

## 🔧 Troubleshooting

### "No API keys found"
**Solution:** Create `.env` file with `ANTHROPIC_API_KEY` (required for Claude Sonnet 4.5)

### "Module not found"
**Solution:** Run `pip install -r requirements.txt`

### Generation takes too long
**Solution:** 
- Use fewer ideas: `--num-ideas 3`
- Use faster models in `config.py`:
  ```python
  GENERATOR_MODEL = "gpt-3.5-turbo"
  ```

### Low quality ideas
**Solution:**
- Run creative-loop (not just generate)
- Increase iterations: `--max-iterations 10`
- Claude Sonnet 4.5 provides excellent quality by default

### Import errors
**Solution:** Make sure you're in the project root directory:
```bash
cd /path/to/MULTI_AGENT
python main.py generate --domain GRC
```

## 📊 Understanding the Output

### Idea Structure
```json
{
  "idea_name": "CloudAudit Pro",
  "problem_statement": "What problem this solves",
  "target_user": "Who needs this",
  "core_features": ["Feature 1", "Feature 2", "Feature 3"],
  "differentiator": "What makes it unique",
  "tech_stack": ["Python", "React", "AWS"],
  "revenue_model": "Subscription"
}
```

### Scores Explained
- **Novelty (0-1):** How innovative/unique the idea is
- **Feasibility (0-1):** How realistic to build
- **Market Fit (0-1):** How well it addresses market needs
- **Viability (0-1):** Business sustainability potential
- **Composite Score:** Weighted average (higher = better)

**Score Interpretation:**
- 0.0-0.4: Weak idea
- 0.4-0.6: Moderate potential
- 0.6-0.8: Strong idea
- 0.8-1.0: Exceptional concept

## 🎓 Next Steps

1. **Explore Domains:**
   - Try all 8 domains: DevOps, Cloud, GRC, BI, AI/ML, Cybersecurity, Data Analytics, Collaboration

2. **Customize Agents:**
   - Edit prompts in `agents/*_agent.py`
   - Adjust scoring weights in `config.py`

3. **Build on Ideas:**
   - Export top ideas: `python main.py export`
   - Create PRDs for best concepts
   - Prototype promising ideas

4. **Integrate with Workflow:**
   - Use programmatically in your pipeline
   - Schedule regular ideation runs
   - Feed into product roadmap

## 📚 More Resources

- **Full Documentation:** [README.md](README.md)
- **Agent Details:** [docs/prompts_and_roles.md](docs/prompts_and_roles.md)
- **Examples:** Run `python example.py`
- **Configuration:** Edit `config.py` or `.env`

## 🎉 You're Ready!

Start generating innovative SaaS ideas:

```bash
python main.py generate --domain "GRC" --num-ideas 5
```

Happy ideating! 🚀

---

**Questions or Issues?** Check the [README.md](README.md) or review the code in `core/` and `agents/` directories.

