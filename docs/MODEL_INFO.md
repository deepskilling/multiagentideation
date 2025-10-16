# LLM Model Configuration

## Current Configuration: Claude Sonnet 4.5

All agents in the Multi-Agent Creativity System are now configured to use **Claude Sonnet 4.5** by default.

### Model Details

**Model Name:** `claude-sonnet-4.5-20250514`  
**Provider:** Anthropic  
**API Key Required:** `ANTHROPIC_API_KEY`

### Why Claude Sonnet 4.5?

- **High Performance:** Latest Claude model with improved reasoning
- **Cost Effective:** Good balance of quality and cost
- **Consistency:** All agents use the same model for predictable behavior
- **Long Context:** Handles large prompts with detailed information
- **Strong JSON Output:** Reliable structured output parsing

### Agent Model Assignments

All five agents use the same model:

| Agent | Model | Temperature |
|-------|-------|-------------|
| **Generator** | claude-sonnet-4.5-20250514 | 0.8 (high creativity) |
| **Critic** | claude-sonnet-4.5-20250514 | 0.3 (consistent evaluation) |
| **Synthesizer** | claude-sonnet-4.5-20250514 | 0.7 (balanced) |
| **Disruptor** | claude-sonnet-4.5-20250514 | 0.9 (very creative) |
| **Strategist** | claude-sonnet-4.5-20250514 | 0.5 (balanced assessment) |

### Setting Up Your API Key

1. Get your Anthropic API key from: https://console.anthropic.com/settings/keys

2. Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

3. The system will automatically use Claude Sonnet 4.5 for all agents.

### Changing Models (Optional)

You can override the default model for specific agents in your `.env` file:

```bash
# Use different models for different agents
GENERATOR_MODEL=claude-sonnet-4.5-20250514
CRITIC_MODEL=claude-opus-4-20250514
SYNTHESIZER_MODEL=gpt-4-turbo-preview
DISRUPTOR_MODEL=claude-sonnet-4.5-20250514
STRATEGIST_MODEL=claude-sonnet-4.5-20250514
```

### Model Name Format

**Anthropic Models:**
- Claude Sonnet 4.5: `claude-sonnet-4.5-20250514`
- Claude Opus 4: `claude-opus-4-20250514`
- Claude 3.5 Sonnet: `claude-3-5-sonnet-20241022`
- Claude 3 Opus: `claude-3-opus-20240229`

**OpenAI Models (if you prefer):**
- GPT-4 Turbo: `gpt-4-turbo-preview`
- GPT-4: `gpt-4`
- GPT-3.5 Turbo: `gpt-3.5-turbo`

### Verifying Your Setup

Test your configuration:

```bash
python -c "from config import config; print(f'Generator Model: {config.GENERATOR_MODEL}')"
```

Expected output:
```
Generator Model: claude-sonnet-4.5-20250514
```

### Cost Estimation

**Claude Sonnet 4.5 Pricing (approximate):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Typical Usage per Idea:**
- Input tokens: ~1,500 (prompts + context)
- Output tokens: ~500 (generated content)
- Cost per idea: ~$0.01 - $0.02

**Full Creative Loop (5 iterations, 5 ideas each):**
- Total ideas: ~25-30 (with synthesis and disruption)
- Estimated cost: $0.30 - $0.60

### Troubleshooting

**Error: "Model not found"**
- Check if model name is correct: `claude-sonnet-4.5-20250514`
- Verify with Anthropic's latest API documentation
- Try: `claude-3-5-sonnet-20241022` if 4.5 not available yet

**Error: "Invalid API key"**
- Verify your `ANTHROPIC_API_KEY` in `.env`
- Check key format: starts with `sk-ant-`
- Ensure key has not expired

**Error: "Rate limit exceeded"**
- Add delays between API calls
- Reduce `--num-ideas` parameter
- Consider upgrading your Anthropic API plan

### Alternative: Mixed Model Setup

For optimal performance, you might want to use different models for different tasks:

```bash
# High creativity for generation
GENERATOR_MODEL=claude-sonnet-4.5-20250514

# Strong reasoning for evaluation  
CRITIC_MODEL=claude-opus-4-20250514

# Balanced for synthesis
SYNTHESIZER_MODEL=claude-sonnet-4.5-20250514

# Maximum creativity for disruption
DISRUPTOR_MODEL=claude-sonnet-4.5-20250514

# Strategic thinking
STRATEGIST_MODEL=claude-opus-4-20250514
```

### Performance Notes

**Claude Sonnet 4.5 Characteristics:**
- ✅ Excellent at structured JSON output
- ✅ Strong reasoning and analysis
- ✅ Good at creative ideation
- ✅ Reliable consistency across calls
- ✅ Handles long prompts well
- ⚡ Fast response times
- 💰 Cost-effective for production use

### Support

For model-related issues:
- Anthropic Documentation: https://docs.anthropic.com/
- Model Capabilities: https://www.anthropic.com/claude
- API Status: https://status.anthropic.com/

---

*Last Updated: October 2025*  
*Note: Model names and availability may change. Check Anthropic's latest documentation.*

