# AWS Bedrock Inference Profiles - Claude Sonnet 4.5 Setup Guide

## Understanding Inference Profiles

AWS Bedrock introduced **Inference Profiles** for newer models (v2 and later) to provide better cost management and regional routing. Claude Sonnet 4.5 requires an inference profile and cannot be invoked directly with on-demand throughput.

### Why Inference Profiles?

1. **Cross-Region Routing** - Automatically route requests across regions for better availability
2. **Cost Control** - Manage throughput and pricing tiers
3. **Performance** - Optimize latency by routing to nearest available region
4. **Capacity Management** - Better handle of provisioned throughput

---

## Current Error Explanation

```
ValidationException: Invocation of model ID anthropic.claude-sonnet-4-5-20250929-v1:0 
with on-demand throughput isn't supported. Retry your request with the ID or ARN of 
an inference profile that contains this model.
```

**What this means:**
- Claude Sonnet 4.5 cannot be invoked using the direct model ID
- You need to use an **inference profile ARN** instead
- Inference profiles provide cross-region capabilities

---

## Option 1: Use Cross-Region Inference Profile (Recommended)

AWS provides pre-configured cross-region inference profiles for Claude models.

### Cross-Region Inference Profile IDs

For Claude Sonnet 4.5, use:
```
us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

This is the **US cross-region inference profile** that:
- Routes requests across US regions (us-east-1, us-west-2)
- Provides automatic failover
- No setup required - it's pre-configured by AWS

### Code Implementation

```python
# In base_agent.py
def _get_bedrock_model_id(self, model: str) -> str:
    model_mapping = {
        "claude-sonnet-4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # US cross-region
        "claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # US cross-region
    }
    return model_mapping.get(model, "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
```

**This is already implemented in the current code!**

---

## Option 2: Create Custom Inference Profile

If you need more control, create a custom inference profile.

### Using AWS CLI

#### Step 1: Check Available Models
```bash
aws bedrock list-foundation-models \
    --by-provider anthropic \
    --profile diligent \
    --region us-east-1
```

#### Step 2: Create Inference Profile
```bash
aws bedrock create-inference-profile \
    --inference-profile-name my-claude-sonnet-45-profile \
    --description "Custom profile for Claude Sonnet 4.5" \
    --model-source '{
        "copyFrom": "anthropic.claude-sonnet-4-5-20250929-v1:0"
    }' \
    --profile diligent \
    --region us-east-1
```

#### Step 3: List Your Inference Profiles
```bash
aws bedrock list-inference-profiles \
    --profile diligent \
    --region us-east-1
```

#### Step 4: Get Profile ARN
The output will include an ARN like:
```
arn:aws:bedrock:us-east-1:123456789012:inference-profile/abc123def456
```

### Use Custom Profile in Code

```python
# In .env file
CLAUDE_45_INFERENCE_PROFILE=arn:aws:bedrock:us-east-1:123456789012:inference-profile/abc123def456

# In config.py
CLAUDE_45_PROFILE = os.getenv("CLAUDE_45_INFERENCE_PROFILE")

# In base_agent.py
def _get_bedrock_model_id(self, model: str) -> str:
    if model == "claude-sonnet-4.5" and config.CLAUDE_45_PROFILE:
        return config.CLAUDE_45_PROFILE
    # ... rest of mapping
```

---

## Option 3: Use Provisioned Throughput

For production workloads with predictable traffic, use provisioned throughput.

### Create Provisioned Model

```bash
# Step 1: Create provisioned throughput
aws bedrock create-provisioned-model-throughput \
    --model-id anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --model-units 1 \
    --provisioned-model-name claude-45-provisioned \
    --commitment-duration OneMonth \
    --profile diligent \
    --region us-east-1

# Step 2: Wait for provisioning (takes ~10-15 minutes)
aws bedrock get-provisioned-model-throughput \
    --provisioned-model-id <id-from-step-1> \
    --profile diligent \
    --region us-east-1

# Step 3: Use the provisioned throughput ARN
# arn:aws:bedrock:us-east-1:123456789012:provisioned-model/<id>
```

**Cost:** Provisioned throughput has hourly charges regardless of usage.

---

## Option 4: Check Model Access

Ensure your AWS account has access to Claude Sonnet 4.5.

### Grant Model Access via AWS Console

1. Go to **AWS Bedrock Console**
2. Navigate to **Model access** (left sidebar)
3. Click **Manage model access**
4. Find **Anthropic** section
5. Enable **Claude Sonnet 4.5**
6. Accept terms and conditions
7. Wait for access approval (~5 minutes)

### Check Access via CLI

```bash
aws bedrock get-foundation-model \
    --model-identifier anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --profile diligent \
    --region us-east-1
```

If access is granted, you'll see model details. If not:
```
AccessDeniedException: You don't have access to this model
```

---

## Recommended Solution for Your Setup

Based on your current implementation, I recommend **Option 1** (already done!):

### Current Implementation Status

✅ **Already implemented in `base_agent.py`:**
```python
"claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### To Enable Claude Sonnet 4.5

1. **Verify Model Access** (most important!)
```bash
aws bedrock list-foundation-models \
    --by-provider anthropic \
    --profile diligent \
    --region us-east-1 \
    | grep "claude-sonnet-4"
```

2. **Check if inference profile exists:**
```bash
aws bedrock list-inference-profiles \
    --profile diligent \
    --region us-east-1
```

3. **Update `.env` to use Claude 4.5:**
```bash
GENERATOR_MODEL=claude-sonnet-4.5
CRITIC_MODEL=claude-sonnet-4.5
```

4. **The code already maps it:**
```python
"claude-sonnet-4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

---

## Troubleshooting

### Error: "You don't have access to this model"

**Solution:** Request model access in AWS Bedrock Console
1. AWS Console → Bedrock → Model access
2. Enable Claude Sonnet 4.5
3. Wait 5-10 minutes for approval

### Error: "Inference profile not found"

**Solution:** The cross-region profile might not be available in your region
- Try different regions: us-west-2, us-east-1
- Or create a custom inference profile (Option 2)

### Error: "Invalid model identifier"

**Solution:** Check the exact model ID
```bash
aws bedrock list-foundation-models \
    --by-provider anthropic \
    --profile diligent \
    --region us-east-1 \
    --query 'modelSummaries[?contains(modelId, `claude-sonnet`)].modelId'
```

---

## Cost Comparison

| Method | Cost Model | Best For |
|--------|-----------|----------|
| **Cross-Region Profile** | Pay per token (on-demand) | Development, variable workloads |
| **Custom Profile** | Pay per token (on-demand) | Specific region requirements |
| **Provisioned Throughput** | Hourly + per token | Production, predictable traffic |

**Current Setup (Cross-Region):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- No base charges

---

## Testing Commands

### Test with Claude 3.5 Sonnet (works now)
```bash
python main.py generate --domain "GRC" --num-ideas 3
```

### Test with Claude Sonnet 4.5 (after setup)
```bash
# Update .env first
echo "GENERATOR_MODEL=claude-sonnet-4.5" >> .env

# Then test
python main.py generate --domain "GRC" --num-ideas 3
```

### Debug AWS Bedrock Access
```bash
# List all available models
aws bedrock list-foundation-models \
    --profile diligent \
    --region us-east-1

# Check specific model
aws bedrock get-foundation-model \
    --model-identifier anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --profile diligent \
    --region us-east-1
```

---

## Next Steps

1. **Verify Model Access** - Most likely the issue
   ```bash
   aws bedrock list-foundation-models --by-provider anthropic --profile diligent --region us-east-1
   ```

2. **Check Inference Profiles**
   ```bash
   aws bedrock list-inference-profiles --profile diligent --region us-east-1
   ```

3. **Request Access** (if needed)
   - AWS Console → Bedrock → Model access → Enable Claude Sonnet 4.5

4. **Test the Setup**
   ```bash
   python main.py generate --domain "GRC" --num-ideas 3
   ```

---

## Additional Resources

- **AWS Bedrock Documentation:** https://docs.aws.amazon.com/bedrock/
- **Inference Profiles Guide:** https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html
- **Anthropic Models in Bedrock:** https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html
- **Pricing:** https://aws.amazon.com/bedrock/pricing/

---

*Last Updated: October 2025*

