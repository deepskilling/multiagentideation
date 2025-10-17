# Multi-Agent System - Command Reference

Complete guide to all available commands and workflows.

---

## 🚀 1. Main Ideation System (`main.py`)

### Generate Ideas

```bash
python main.py generate [OPTIONS]
```

**Options:**
- `--domain DOMAIN` - Predefined domain
- `--prompt TEXT` - Custom prompt (overrides --domain)
- `--num-ideas N` - Number of ideas (default: 5)
- `--use-search` - Enable web search
- `--output FILE` - Custom output file

**Examples:**

```bash
# Generate 5 GRC ideas
python main.py generate --domain "GRC (Governance, Risk, Compliance)" --num-ideas 5

# Custom prompt with web search
python main.py generate --prompt "CRM product for GRC market" --num-ideas 10 --use-search

# SaaS ideas with web search
python main.py generate --prompt "SaaS product for FASSI" --num-ideas 5 --use-search
```

**Available Predefined Domains:**
- Sales & Marketing Automation
- Healthcare & Telemedicine
- FinTech & Digital Banking
- Education & EdTech
- GRC (Governance, Risk, Compliance)
- Supply Chain & Logistics
- Customer Support & Success
- HR & Talent Management
- Project Management
- Cybersecurity

---

### Creative Loop (Iterative Refinement)

```bash
python main.py creative-loop [OPTIONS]
```

**Options:**
- `--domain DOMAIN` - Predefined domain
- `--prompt TEXT` - Custom prompt
- `--num-ideas N` - Ideas per iteration (default: 3)
- `--max-iterations N` - Maximum iterations (default: 3)
- `--convergence-threshold N` - Stop threshold (default: 0.05)
- `--use-search` - Enable web search

**Examples:**

```bash
# Run creative loop for GRC
python main.py creative-loop --domain "GRC (Governance, Risk, Compliance)" \
  --num-ideas 3 --max-iterations 3

# Custom prompt with 5 iterations
python main.py creative-loop --prompt "Developer productivity tools" \
  --num-ideas 5 --max-iterations 5 --use-search
```

---

## 🔮 2. Deep Ideation (`deep_ideation.py`)

### Generate Novel Features (2-5 years ahead)

```bash
python deep_ideation.py DOMAIN [OPTIONS]
```

**Required:**
- `DOMAIN` - Domain or product to ideate for

**Options:**
- `--num-ideas N` - Number of features (default: 10)
- `--competitors A B C` - Competitor products
- `--time-horizon WHEN` - "2-3 years", "3-5 years", "5+ years"
- `--no-search` - Disable web search
- `--output FILE` - Custom output file

**Examples:**

```bash
# Basic novel feature generation
python deep_ideation.py "GRC software" --num-ideas 10

# With competitor analysis
python deep_ideation.py "GRC software" \
  --num-ideas 10 \
  --competitors "ServiceNow" "LogicGate" "OneTrust" \
  --time-horizon "2-3 years"

# Healthcare AI with 5-year horizon
python deep_ideation.py "Healthcare AI" \
  --num-ideas 15 \
  --competitors "Epic" "Cerner" \
  --time-horizon "3-5 years"

# FinTech features
python deep_ideation.py "FinTech payment platform" \
  --num-ideas 10 \
  --competitors "Stripe" "Square"

# Without web search (faster)
python deep_ideation.py "Developer Tools" --num-ideas 10 --no-search
```

---

## 📄 3. PRD Generator (`prd_generator.py`)

### Generate Product Requirements Document

```bash
python prd_generator.py [OPTIONS]
```

**Options:**
- `--idea-file FILE` - JSON file with ideas
- `--idea-index N` - Index of idea to expand (default: 0)
- `--idea-text TEXT` - Direct idea text
- `--output FILE` - Output file

**Examples:**

```bash
# Generate PRD from file (first idea)
python prd_generator.py \
  --idea-file "./reports/ideas_20241016.json" \
  --idea-index 0

# Generate PRD for second idea
python prd_generator.py \
  --idea-file "./reports/ideas_grc.json" \
  --idea-index 1 \
  --output "./reports/prd_grc_feature2.json"

# Generate PRD from direct text
python prd_generator.py \
  --idea-text "AI-powered compliance automation platform"
```

---

## 🎉 4. Event Ideator (`event_ideator.py`)

### Generate Event Concepts

```bash
python event_ideator.py concepts [OPTIONS]
```

**Options:**
- `--theme TEXT` - Event theme
- `--num-concepts N` - Number of concepts (default: 5)
- `--output FILE` - Output file

**Examples:**

```bash
# Generate event concepts
python event_ideator.py concepts --theme "re-ignite" --num-concepts 5

# Custom theme
python event_ideator.py concepts \
  --theme "AI and the future of work" \
  --num-concepts 8 \
  --output "./reports/ai_events.json"
```

---

### Generate Event Agenda

```bash
python event_ideator.py agenda [OPTIONS]
```

**Options:**
- `--concept-file FILE` - JSON file with concepts
- `--concept-index N` - Which concept to expand (default: 0)
- `--output FILE` - Output file

**Examples:**

```bash
# Generate agenda for first concept
python event_ideator.py agenda \
  --concept-file "./reports/reignite_event_concepts.json" \
  --concept-index 0

# Generate agenda for second concept
python event_ideator.py agenda \
  --concept-file "./reports/ai_events.json" \
  --concept-index 1 \
  --output "./reports/agenda_concept2.md"
```

---

## 🧪 5. Testing Tools

### Error Recovery Test

```bash
python error_recovery_test.py
```

Tests error detection and recovery system.

---

### Web Search Test

```bash
python web_search_test.py
```

Tests web search integration with examples.

---

## 💡 Common Workflows

### Workflow 1: Quick Ideation (5-10 minutes)

```bash
# Generate ideas
python main.py generate --prompt "YOUR IDEA" --num-ideas 5 --use-search
```

---

### Workflow 2: Deep Exploration (30-60 minutes)

```bash
# Step 1: Run creative loop
python main.py creative-loop --prompt "YOUR IDEA" \
  --num-ideas 5 --max-iterations 3 --use-search

# Step 2: Generate PRD for best idea
python prd_generator.py \
  --idea-file "./reports/creative_loop_*.json" \
  --idea-index 0
```

---

### Workflow 3: Strategic Planning (1-2 hours)

```bash
# Step 1: Deep ideation for novel features
python deep_ideation.py "YOUR DOMAIN" \
  --num-ideas 10 \
  --competitors "Competitor1" "Competitor2" \
  --time-horizon "2-3 years"

# Step 2: Generate PRD for highest impact feature
python prd_generator.py --idea-text "SELECTED NOVEL FEATURE"
```

---

### Workflow 4: Product Roadmap (Monthly)

```bash
# Step 1: Near-term features
python main.py generate --prompt "YOUR PRODUCT - Q1 2025" \
  --num-ideas 10 --use-search

# Step 2: Long-term vision
python deep_ideation.py "YOUR PRODUCT" \
  --num-ideas 15 \
  --competitors "Top 3 Competitors" \
  --time-horizon "3-5 years"

# Step 3: Generate PRDs for top 3-5 features
```

---

## 💰 Cost Estimation

### Per Command Costs (Approximate)

| Command | Cost |
|---------|------|
| `main.py generate` (5 ideas) | $0.10-$0.20 |
| `main.py generate` (10 ideas) | $0.20-$0.40 |
| `main.py creative-loop` (3 iter) | $0.40-$0.80 |
| `deep_ideation.py` (10 features) | $0.40-$0.60 |
| `prd_generator.py` (1 PRD) | $0.20-$0.40 |
| `event_ideator.py` (concepts) | $0.15-$0.30 |
| `event_ideator.py` (agenda) | $0.25-$0.50 |

### Web Search
- First 2,500 searches/month: **FREE**
- After that: $0.005 per search

### Typical Daily Usage
- 5 generations: $1.00
- 1 creative loop: $0.60
- 1 deep ideation: $0.50
- 2 PRDs: $0.60
- **Total per day: ~$2.70**

### Monthly Usage
- 20 working days: **~$54.00/month**

---

## 📊 Output Files

### Default Locations

```
reports/ideas_*.json                  Generated ideas (main.py)
reports/creative_loop_*.json          Creative loop results
reports/deep_ideation_*.json          Novel features + analysis
reports/prd_*.json                    Product Requirements Documents
reports/*_event_concepts.json         Event concepts
reports/*_agenda.md                   Event agendas
```

### Database

```
data/saas_ideas.db                    DuckDB database (all ideas)
data/ideas.db                         Legacy database
```

---

## 🔧 Environment Setup

### Required in `.env` file:

```bash
# AWS Bedrock (for Claude Sonnet 4.5)
USE_AWS_BEDROCK=true
AWS_PROFILE=diligent
AWS_REGION=us-east-1

# Web Search (optional but recommended)
SERPER_API_KEY=your_serper_key_here
```

### Conda Environment

```bash
conda activate awsproject
```

---

## 📚 Help & Documentation

### View Help for Any Command

```bash
python main.py --help
python main.py generate --help
python main.py creative-loop --help
python deep_ideation.py --help
python prd_generator.py --help
python event_ideator.py --help
```

### Documentation Files

- `docs/README.md` - Documentation index
- `docs/DEEP_IDEATION.md` - Deep ideation guide
- `docs/AGENTIC_PATTERNS.md` - System architecture
- `docs/WEB_SEARCH.md` - Web search integration
- `docs/ERROR_RECOVERY.md` - Error recovery system
- `docs/SYSTEM_EVALUATION.md` - Production readiness

---

## 🎯 Quick Start Examples

```bash
# 1. Generate 5 CRM ideas with web search
python main.py generate --prompt "CRM for GRC market" --num-ideas 5 --use-search

# 2. Generate 10 novel AI features (2-3 years ahead)
python deep_ideation.py "AI customer support" --num-ideas 10 --time-horizon "2-3 years"

# 3. Run creative loop with 3 iterations
python main.py creative-loop --prompt "Developer productivity tools" \
  --num-ideas 3 --max-iterations 3 --use-search

# 4. Generate PRD from best idea
python prd_generator.py --idea-file "./reports/ideas_*.json" --idea-index 0

# 5. Generate event concepts
python event_ideator.py concepts --theme "AI innovation summit" --num-concepts 5
```

---

## 🚀 Getting Started

1. **Activate conda environment:**
   ```bash
   conda activate awsproject
   ```

2. **Run your first generation:**
   ```bash
   python main.py generate --prompt "YOUR IDEA HERE" --num-ideas 5 --use-search
   ```

3. **Review output in `reports/` directory**

4. **Generate PRD for best idea:**
   ```bash
   python prd_generator.py --idea-file "./reports/ideas_*.json" --idea-index 0
   ```

---

**Last Updated:** October 16, 2024  
**System Version:** 1.0  
**Pattern Maturity:** 83% (10/12 patterns)

