# Docker & ECS Quick Start

**5-minute guide** to get your multi-agent system running in containers.

---

## 🎯 Choose Your Path

### Path 1: Local Development (Docker Compose) - 2 minutes

```bash
# 1. Navigate to docker directory
cd docker

# 2. Start the system
docker-compose up -d

# 3. Run your first command
docker-compose exec multiagent-ideation \
  python main.py generate --prompt "AI-powered CRM" --num-ideas 5 --use-search

# 4. View output
docker-compose exec multiagent-ideation ls -l reports/

# 5. Stop
docker-compose down
```

**✅ Done!** Your multi-agent system is running in Docker.

---

### Path 2: AWS ECS Deployment - 15 minutes

```bash
# Prerequisites: AWS CLI configured, account ID handy

# 1. Setup AWS infrastructure
./setup-aws-infrastructure.sh YOUR_ACCOUNT_ID us-east-1

# 2. Create Serper API secret (if using web search)
aws secretsmanager create-secret \
  --name multiagent/serper-api-key \
  --secret-string "YOUR_SERPER_KEY" \
  --region us-east-1

# 3. Update ecs-task-definition.json
# Replace YOUR_ACCOUNT_ID with your AWS account ID

# 4. Build and push image
./build-and-push.sh YOUR_ACCOUNT_ID us-east-1 latest

# 5. Deploy to ECS
./deploy-to-ecs.sh YOUR_ACCOUNT_ID us-east-1

# 6. Create ECS service (first time only)
aws ecs create-service \
  --cluster multiagent-ideation-cluster \
  --service-name multiagent-ideation-service \
  --task-definition multiagent-ideation-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXX],securityGroups=[sg-XXX],assignPublicIp=ENABLED}" \
  --region us-east-1
```

**✅ Done!** Your system is deployed to AWS ECS Fargate.

---

## 📋 What You Get

### Docker Image Includes:
- ✅ All Python dependencies
- ✅ Multi-agent system (9 agents)
- ✅ Deep ideation capabilities
- ✅ PRD generator
- ✅ Event ideator
- ✅ Web search integration
- ✅ Error recovery system
- ✅ Cost tracking

### ECS Deployment Includes:
- ✅ Fargate task (2 vCPU, 4 GB)
- ✅ IAM roles for Bedrock access
- ✅ CloudWatch logging
- ✅ Secrets Manager integration
- ✅ Optional EFS persistence

---

## 🎨 Usage Examples

### Example 1: Generate Ideas

```bash
# Docker
docker run multiagent-ideation:latest \
  python main.py generate --prompt "Healthcare AI" --num-ideas 5 --use-search

# Docker Compose
docker-compose exec multiagent-ideation \
  python main.py generate --prompt "Healthcare AI" --num-ideas 5 --use-search

# ECS (update task definition command)
"command": ["python", "main.py", "generate", "--prompt", "Healthcare AI", "--num-ideas", "5", "--use-search"]
```

### Example 2: Deep Ideation

```bash
# Docker
docker run multiagent-ideation:latest \
  python deep_ideation.py "GRC software" --num-ideas 10 \
  --competitors "ServiceNow" "LogicGate"

# Docker Compose
docker-compose exec multiagent-ideation \
  python deep_ideation.py "GRC software" --num-ideas 10 \
  --competitors "ServiceNow" "LogicGate"
```

### Example 3: Generate PRD

```bash
# Docker (with volume mounts)
docker run \
  -v $(pwd)/reports:/app/reports \
  multiagent-ideation:latest \
  python prd_generator.py --idea-file /app/reports/ideas.json --idea-index 0
```

---

## 🔍 Monitoring

### View Logs (Docker Compose)

```bash
# Follow logs
docker-compose logs -f multiagent-ideation

# View last 100 lines
docker-compose logs --tail=100 multiagent-ideation
```

### View Logs (ECS)

```bash
# Real-time logs
aws logs tail /ecs/multiagent-ideation --follow --region us-east-1

# Last 100 lines
aws logs tail /ecs/multiagent-ideation --since 1h --region us-east-1
```

### Check Status (ECS)

```bash
# Service status
aws ecs describe-services \
  --cluster multiagent-ideation-cluster \
  --services multiagent-ideation-service \
  --region us-east-1 \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'

# Running tasks
aws ecs list-tasks \
  --cluster multiagent-ideation-cluster \
  --service-name multiagent-ideation-service \
  --region us-east-1
```

---

## 💰 Quick Cost Reference

### Local Development (Docker)
- **Cost**: $0 (uses your machine)
- **LLM**: ~$0.50/session (Bedrock charges)

### ECS Fargate
- **Fargate**: $0.10/hour (~$2/day if running 24/7)
- **Recommended**: Run on-demand = $0.10/session
- **LLM**: ~$0.50/session (Bedrock charges)
- **Storage**: ~$1/month (if using EFS)

**Total per session: ~$0.60** (on-demand ECS + LLM)

---

## 🛠️ Troubleshooting

### Issue: "Cannot connect to Docker daemon"

```bash
# Start Docker
sudo systemctl start docker  # Linux
open -a Docker              # Mac
```

### Issue: "Permission denied" accessing AWS

```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure if needed
aws configure --profile diligent
```

### Issue: Container exits immediately

```bash
# Check logs
docker logs CONTAINER_ID

# Or for compose
docker-compose logs multiagent-ideation

# Common causes:
# - Missing .env file
# - Invalid AWS credentials
# - Serper API key not set
```

### Issue: "Task failed to start" in ECS

```bash
# View stopped task reason
aws ecs describe-tasks \
  --cluster multiagent-ideation-cluster \
  --tasks TASK_ARN \
  --region us-east-1 \
  --query 'tasks[0].stopCode'

# Common causes:
# - IAM role permissions
# - ECR image not found
# - Invalid task definition
# - Resource limits exceeded
```

---

## 📚 Next Steps

1. **Read full documentation**: `README.md`
2. **Understand architecture**: `../docs/AGENTIC_PATTERNS.md`
3. **Learn commands**: `../COMMAND_REFERENCE.md`
4. **Explore deep ideation**: `../docs/DEEP_IDEATION.md`

---

## 🎉 You're Ready!

Choose your deployment method and start generating novel ideas! 🚀

**Local development:**
```bash
docker-compose up -d
```

**AWS ECS:**
```bash
./setup-aws-infrastructure.sh && ./build-and-push.sh && ./deploy-to-ecs.sh
```

**Questions?** Check `README.md` for detailed documentation.

---

**Created:** October 16, 2024  
**Quick Start Version:** 1.0

