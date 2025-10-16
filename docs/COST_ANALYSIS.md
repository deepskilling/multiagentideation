# Cost Analysis - Multi-Agent Creativity System

## Recent Generation Cost Breakdown

### Latest Run: 3 Ideas with Claude Sonnet 4.5

**Date:** October 16, 2025  
**Model:** Claude Sonnet 4.5 (via AWS Bedrock)  
**Region:** us-east-1  
**Profile:** Cross-region inference profile

---

## AWS Bedrock Pricing for Claude Sonnet 4.5

| Item | Price |
|------|-------|
| **Input tokens** | $3.00 per million tokens |
| **Output tokens** | $15.00 per million tokens |

---

## Token Usage Estimation

### Per Idea Generation:

**Generator Agent (creates ideas):**
- Input (prompt + context): ~1,500 tokens
- Output (5 ideas in JSON): ~2,500 tokens
- Cost: (1,500 × $3/1M) + (2,500 × $15/1M) = $0.0045 + $0.0375 = **$0.042**

**Critic Agent (evaluates each idea):**
- Input per idea: ~800 tokens × 5 ideas = 4,000 tokens
- Output per idea: ~300 tokens × 5 ideas = 1,500 tokens
- Cost: (4,000 × $3/1M) + (1,500 × $15/1M) = $0.012 + $0.0225 = **$0.0345**

**Scoring Engine:**
- Uses local embeddings (sentence-transformers)
- No API cost

**Total per 5-idea batch:**
- Generator: $0.042
- Critic: $0.0345
- **Total: ~$0.077** (approximately **7.7 cents**)

---

## Actual Cost Estimate for Your Runs

### Run 1: 5 Ideas with Claude 3.5 Sonnet
**Estimated Cost:** $0.05 - $0.08

Breakdown:
- Generator: 1 API call (~2,500 input, ~2,500 output)
- Critic: 5 API calls (~800 input each, ~300 output each)
- **Total: ~$0.065** (6.5 cents)

Claude 3.5 Sonnet pricing (AWS Bedrock):
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

### Run 2: 3 Ideas with Claude Sonnet 4.5
**Estimated Cost:** $0.04 - $0.06

Breakdown:
- Generator: 1 API call (~1,500 input, ~1,500 output)
- Critic: 3 API calls (~800 input each, ~300 output each)
- **Total: ~$0.046** (4.6 cents)

Claude Sonnet 4.5 pricing (AWS Bedrock):
- Input: $3.00 per million tokens  
- Output: $15.00 per million tokens

---

## Cost Comparison: Full Creative Loop

### Single Batch (5 ideas)
- **Cost:** ~$0.08

### Creative Loop (5 iterations, 5 ideas each)
Including synthesis and disruption:

**Per Iteration:**
1. Generator: $0.042 (5 new ideas)
2. Critic: $0.0345 (evaluate 5 ideas)
3. Synthesizer: $0.025 (merge 2-3 pairs)
4. Disruptor: $0.020 (2 variations)
5. Strategist: $0.010 (assessment)

**Total per iteration:** ~$0.13

**5 iterations:** 5 × $0.13 = **$0.65**

**Grand total for full loop:** ~$0.60-0.70

---

## Cost Breakdown by Agent

| Agent | API Calls | Cost per Call | Total (5 ideas) |
|-------|-----------|---------------|-----------------|
| Generator | 1 | $0.042 | $0.042 |
| Critic | 5 | $0.007 | $0.035 |
| Synthesizer | 2-3 | $0.012 | $0.025 |
| Disruptor | 2 | $0.010 | $0.020 |
| Strategist | 1 | $0.010 | $0.010 |
| **Total** | **~11** | - | **$0.132** |

---

## Token Usage Details

### Typical Token Counts:

**Generator Agent:**
```
Input:  
- System message: ~200 tokens
- Prompt template: ~400 tokens
- Domain context: ~100 tokens
- Instructions: ~300 tokens
Total input: ~1,500 tokens

Output:
- 5 ideas in JSON format
- ~500 tokens per idea
Total output: ~2,500 tokens
```

**Critic Agent (per idea):**
```
Input:
- System message: ~150 tokens
- Evaluation criteria: ~200 tokens
- Idea details: ~300 tokens
- Instructions: ~150 tokens
Total input: ~800 tokens

Output:
- Scores + justification
Total output: ~300 tokens
```

---

## Cost Projections

### Daily Usage Scenarios:

**Light Usage** (5 ideas/day):
- Daily: $0.08
- Monthly: $2.40
- Annual: $29.20

**Medium Usage** (50 ideas/day):
- Daily: $0.80
- Monthly: $24.00
- Annual: $292.00

**Heavy Usage** (500 ideas/day):
- Daily: $8.00
- Monthly: $240.00
- Annual: $2,920.00

**Enterprise** (5,000 ideas/day):
- Daily: $80.00
- Monthly: $2,400.00
- Annual: $29,200.00

---

## Cost Optimization Tips

### 1. Batch Processing
Generate multiple ideas in one API call instead of one at a time:
- **Current:** 1 call for 5 ideas = $0.042
- **If separate:** 5 calls for 1 idea each = $0.21 (5x more!)
- **Savings:** 80%

### 2. Reduce Iterations
- Start with fewer iterations (3 instead of 10)
- Use strategist to stop early when quality is good
- Savings: Up to 70%

### 3. Use Faster Models for Some Agents
- Generator & Critic: Keep Claude Sonnet 4.5 (quality matters)
- Strategist: Use Claude Haiku 4.5 (faster, cheaper)
- Potential savings: 20-30%

### 4. Cache System Prompts
Claude has prompt caching that can reduce costs:
- Cache system messages and templates
- Savings: Up to 50% on repeated calls

### 5. Filter Before Evaluation
- Use embeddings to filter obvious duplicates first
- Only evaluate unique ideas with Critic
- Savings: 10-20%

---

## AWS Bedrock Cost Monitoring

### View Your Actual Costs:

```bash
# Get AWS billing info
aws ce get-cost-and-usage \
    --time-period Start=2025-10-01,End=2025-10-31 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --filter file://bedrock-filter.json \
    --profile diligent

# Create filter file (bedrock-filter.json):
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Bedrock"]
  }
}
```

### CloudWatch Metrics:
- Monitor token usage
- Track API calls
- Set up billing alarms

---

## Comparison with Direct Anthropic API

| Provider | Input (per 1M) | Output (per 1M) | Notes |
|----------|----------------|-----------------|-------|
| **AWS Bedrock** | $3.00 | $15.00 | Uses your AWS account |
| **Anthropic Direct** | $3.00 | $15.00 | Same pricing |

**Advantage of AWS Bedrock:**
- Integrated with AWS services
- No separate billing
- Better monitoring
- Cross-region routing
- Same cost!

---

## Summary: Your Actual Costs

### What You've Generated:

**Run 1:** 5 ideas with Claude 3.5 Sonnet
- **Cost:** ~$0.065 (6.5 cents)

**Run 2:** 3 ideas with Claude Sonnet 4.5  
- **Cost:** ~$0.046 (4.6 cents)

**Total spent so far:** ~$0.11 (11 cents)

---

## Cost per Idea

| Metric | Value |
|--------|-------|
| **Per idea (generation + evaluation)** | $0.015-0.020 |
| **Per 100 ideas** | $1.50-2.00 |
| **Per 1,000 ideas** | $15-20 |

---

## Is This Expensive?

**Context:**
- **Human ideation session (1 hour):** $50-200+ (labor cost)
- **Consulting firm for 10 ideas:** $5,000-20,000
- **Internal workshop (10 people, 2 hours):** $500-1,500
- **AI system (100 ideas):** $1.50-2.00

**ROI:** 🚀 **Extremely cost-effective!**

---

## Next Steps

### To Track Costs:

1. **Set up AWS Cost Explorer**
   - Filter by Amazon Bedrock
   - Set budget alerts

2. **Enable detailed logging**
   ```python
   # Add to your code
   import logging
   logging.basicConfig(level=logging.INFO)
   # Log token counts for each call
   ```

3. **Monitor usage**
   ```bash
   # Check monthly Bedrock costs
   aws ce get-cost-and-usage --time-period Start=2025-10-01,End=2025-10-31 \
       --granularity MONTHLY --metrics "UnblendedCost" \
       --filter file://bedrock-filter.json --profile diligent
   ```

---

*Last Updated: October 2025*
*Pricing based on AWS Bedrock rates as of October 2025*

