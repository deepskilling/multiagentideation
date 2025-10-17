# Docker & AWS ECS Deployment Guide

Complete guide to containerizing and deploying the Multi-Agent Ideation System.

---

## 📦 What's Included

This directory contains everything needed to containerize and deploy the multi-agent system:

```
docker/
├── Dockerfile                      # Docker image definition
├── .dockerignore                   # Files to exclude from build
├── docker-compose.yml              # Local development with Docker Compose
├── ecs-task-definition.json        # AWS ECS Fargate task definition
├── iam-policies.json               # IAM policies for ECS tasks
├── build-and-push.sh               # Build and push to ECR
├── deploy-to-ecs.sh                # Deploy to ECS
├── setup-aws-infrastructure.sh     # Setup AWS resources
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Option 1: Local Development (Docker Compose)

```bash
# 1. Navigate to docker directory
cd docker

# 2. Build and start
docker-compose up --build

# 3. In another terminal, run commands:
docker-compose exec multiagent-ideation python main.py generate \
  --prompt "AI-powered SaaS" --num-ideas 5 --use-search

# 4. Stop
docker-compose down
```

### Option 2: AWS ECS Deployment

```bash
# 1. Setup AWS infrastructure
./setup-aws-infrastructure.sh YOUR_ACCOUNT_ID us-east-1

# 2. Build and push to ECR
./build-and-push.sh YOUR_ACCOUNT_ID us-east-1 latest

# 3. Update ecs-task-definition.json with your account ID and resources

# 4. Deploy to ECS
./deploy-to-ecs.sh YOUR_ACCOUNT_ID us-east-1
```

---

## 📋 Prerequisites

### For Local Development

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- AWS credentials configured (for Bedrock access)
- Serper API key (optional, for web search)

### For ECS Deployment

- AWS CLI (version 2.0+)
- AWS account with permissions for:
  - ECR (Elastic Container Registry)
  - ECS (Elastic Container Service)
  - IAM (Identity and Access Management)
  - CloudWatch Logs
  - Secrets Manager
  - Bedrock
- Configured AWS credentials with `diligent` profile

---

## 🏗️ Architecture

### Docker Image

```
Base Image: python:3.10-slim
Size: ~1.5 GB (estimated)
Layers:
  - System dependencies (gcc, g++, curl)
  - Python dependencies (from requirements.txt)
  - Application code
  - Data directories
```

### ECS Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS ECS Fargate                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Task Definition: multiagent-ideation-task          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  Container: multiagent-ideation                      │   │
│  │  • Image from ECR                                    │   │
│  │  • CPU: 2 vCPU                                       │   │
│  │  • Memory: 4 GB                                      │   │
│  │  • Environment variables                             │   │
│  │  • Secrets from Secrets Manager                      │   │
│  │                                                       │   │
│  │  IAM Roles:                                          │   │
│  │  • Task Execution Role (ECR, Logs, Secrets)         │   │
│  │  • Task Role (Bedrock, CloudWatch)                  │   │
│  │                                                       │   │
│  │  Storage:                                            │   │
│  │  • EFS for /data (DuckDB, FAISS)                    │   │
│  │  • EFS for /reports (outputs)                       │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
        │                    │                    │
        ↓                    ↓                    ↓
   AWS Bedrock      Serper API (web)    CloudWatch Logs
   (Claude 4.5)
```

---

## 🔧 Detailed Setup

### Step 1: AWS Infrastructure Setup

Run the infrastructure setup script:

```bash
./setup-aws-infrastructure.sh YOUR_ACCOUNT_ID us-east-1
```

This creates:
- ✅ CloudWatch Log Group `/ecs/multiagent-ideation`
- ✅ IAM Task Execution Role (for ECR, logs, secrets)
- ✅ IAM Task Role (for Bedrock access)

### Step 2: Create Secrets in AWS Secrets Manager

```bash
# Create Serper API key secret
aws secretsmanager create-secret \
  --name multiagent/serper-api-key \
  --description "Serper API key for multi-agent ideation" \
  --secret-string "YOUR_SERPER_API_KEY_HERE" \
  --region us-east-1
```

### Step 3: Update ECS Task Definition

Edit `ecs-task-definition.json`:

1. Replace `YOUR_ACCOUNT_ID` with your AWS account ID
2. Update `executionRoleArn` with your execution role ARN
3. Update `taskRoleArn` with your task role ARN
4. (Optional) Add EFS file system ID if using persistent storage

### Step 4: Build and Push Docker Image

```bash
./build-and-push.sh YOUR_ACCOUNT_ID us-east-1 latest
```

This will:
1. Authenticate Docker to ECR
2. Create ECR repository (if it doesn't exist)
3. Build Docker image
4. Tag image
5. Push to ECR

### Step 5: Deploy to ECS

```bash
./deploy-to-ecs.sh YOUR_ACCOUNT_ID us-east-1
```

For first-time deployment, you'll need to manually create the ECS service with VPC configuration:

```bash
aws ecs create-service \
  --cluster multiagent-ideation-cluster \
  --service-name multiagent-ideation-service \
  --task-definition multiagent-ideation-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXX,subnet-YYYYY],securityGroups=[sg-ZZZZZ],assignPublicIp=ENABLED}" \
  --region us-east-1
```

---

## 💻 Local Development with Docker

### Build and Run Locally

```bash
# Build image
docker build -f docker/Dockerfile -t multiagent-ideation:local .

# Run interactively
docker run -it \
  -v ~/.aws:/root/.aws:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -e USE_AWS_BEDROCK=true \
  -e AWS_REGION=us-east-1 \
  -e AWS_PROFILE=diligent \
  multiagent-ideation:local \
  /bin/bash

# Inside container, run commands:
python main.py generate --prompt "AI-powered CRM" --num-ideas 5 --use-search
python deep_ideation.py "Healthcare AI" --num-ideas 10
```

### Using Docker Compose

```bash
# Start in detached mode
docker-compose up -d

# Execute commands
docker-compose exec multiagent-ideation \
  python main.py generate --prompt "YOUR IDEA" --num-ideas 5

docker-compose exec multiagent-ideation \
  python deep_ideation.py "YOUR DOMAIN" --num-ideas 10

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🎯 Running Different Commands

### 1. Generate Ideas

```bash
# Via Docker
docker run multiagent-ideation:latest \
  python main.py generate --prompt "AI agents" --num-ideas 5 --use-search

# Via ECS (update task definition command)
"command": ["python", "main.py", "generate", "--prompt", "AI agents", "--num-ideas", "5", "--use-search"]
```

### 2. Deep Ideation

```bash
# Via Docker
docker run multiagent-ideation:latest \
  python deep_ideation.py "Healthcare AI" --num-ideas 10 \
  --competitors "Epic" "Cerner" --time-horizon "2-3 years"

# Via ECS
"command": ["python", "deep_ideation.py", "Healthcare AI", "--num-ideas", "10"]
```

### 3. Generate PRD

```bash
# Via Docker (requires mounted volumes for input/output)
docker run \
  -v $(pwd)/reports:/app/reports \
  multiagent-ideation:latest \
  python prd_generator.py --idea-file /app/reports/ideas.json --idea-index 0
```

### 4. Creative Loop

```bash
# Via Docker
docker run multiagent-ideation:latest \
  python main.py creative-loop --prompt "Developer tools" \
  --num-ideas 3 --max-iterations 3 --use-search
```

---

## 📊 Monitoring & Logs

### View CloudWatch Logs

```bash
# Tail logs in real-time
aws logs tail /ecs/multiagent-ideation --follow --region us-east-1

# View specific log stream
aws logs get-log-events \
  --log-group-name /ecs/multiagent-ideation \
  --log-stream-name ecs/multiagent-ideation/TASK_ID \
  --region us-east-1
```

### Check ECS Service Status

```bash
# Describe service
aws ecs describe-services \
  --cluster multiagent-ideation-cluster \
  --services multiagent-ideation-service \
  --region us-east-1

# List running tasks
aws ecs list-tasks \
  --cluster multiagent-ideation-cluster \
  --service-name multiagent-ideation-service \
  --region us-east-1

# Describe task
aws ecs describe-tasks \
  --cluster multiagent-ideation-cluster \
  --tasks TASK_ARN \
  --region us-east-1
```

---

## 💰 Cost Estimation

### ECS Fargate Costs (us-east-1)

**Configuration:**
- CPU: 2 vCPU
- Memory: 4 GB
- Storage: EFS (optional)

**Pricing:**
- vCPU: $0.04048 per vCPU per hour
- Memory: $0.004445 per GB per hour

**Calculation:**
- vCPU: 2 × $0.04048 = $0.08096/hour
- Memory: 4 × $0.004445 = $0.01778/hour
- **Total: $0.09874/hour ≈ $0.10/hour**

**Monthly cost (if running 24/7):**
- 730 hours × $0.10 = **$73/month**

**Recommended: Run on-demand**
- 1 hour session: $0.10
- 10 sessions/day × 20 days = $20/month

### Additional Costs

| Service | Usage | Cost |
|---------|-------|------|
| **Bedrock (Claude 4.5)** | Per token | $0.003/1K input, $0.015/1K output |
| **ECR Storage** | Per GB-month | $0.10/GB-month |
| **EFS Storage** | Per GB-month | $0.30/GB-month (standard) |
| **CloudWatch Logs** | Per GB ingested | $0.50/GB |
| **Data Transfer** | Per GB out | $0.09/GB (first 10 TB) |

---

## 🔐 Security Best Practices

### 1. IAM Roles (Not Access Keys)

✅ **Use IAM roles** for ECS tasks (already configured)  
❌ **Don't** hardcode AWS credentials

### 2. Secrets Management

✅ **Use AWS Secrets Manager** for API keys  
❌ **Don't** put secrets in environment variables or code

### 3. Network Security

- Use private subnets for ECS tasks
- Use security groups to restrict access
- Use VPC endpoints for AWS services (avoid public internet)

### 4. Image Security

```bash
# Scan image for vulnerabilities
aws ecr start-image-scan \
  --repository-name multiagent-ideation \
  --image-id imageTag=latest \
  --region us-east-1

# View scan results
aws ecr describe-image-scan-findings \
  --repository-name multiagent-ideation \
  --image-id imageTag=latest \
  --region us-east-1
```

### 5. Least Privilege

- Task execution role: Only ECR, logs, secrets
- Task role: Only Bedrock, CloudWatch

---

## 🐛 Troubleshooting

### Issue: Container fails to start

**Check logs:**
```bash
aws logs tail /ecs/multiagent-ideation --follow --region us-east-1
```

**Common causes:**
- Missing environment variables
- IAM permissions issues
- AWS Bedrock access not enabled
- Serper API key not set

### Issue: "Permission denied" for Bedrock

**Solution:**
- Ensure task role has `bedrock:InvokeModel` permission
- Check that Bedrock is enabled in your AWS account
- Verify model access is granted in Bedrock console

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker daemon
sudo systemctl start docker

# Or on Mac
open -a Docker
```

### Issue: ECS task keeps restarting

**Check:**
1. Health check configuration
2. Application logs for errors
3. Resource limits (CPU/memory)
4. Network connectivity

---

## 📚 Additional Resources

### Docker Documentation
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose reference](https://docs.docker.com/compose/compose-file/)

### AWS Documentation
- [ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)

### Multi-Agent System Documentation
- [Main README](../README.md)
- [Command Reference](../COMMAND_REFERENCE.md)
- [Deep Ideation Guide](../docs/DEEP_IDEATION.md)
- [Agentic Patterns](../docs/AGENTIC_PATTERNS.md)

---

## 🎉 Summary

You now have a fully containerized multi-agent ideation system ready for:
- ✅ Local development with Docker/Docker Compose
- ✅ Production deployment on AWS ECS Fargate
- ✅ Scalable, secure, and cost-effective

**Quick commands:**
```bash
# Local
docker-compose up -d && docker-compose exec multiagent-ideation python main.py generate --prompt "YOUR IDEA" --num-ideas 5

# AWS ECS
./setup-aws-infrastructure.sh YOUR_ACCOUNT_ID
./build-and-push.sh YOUR_ACCOUNT_ID us-east-1
./deploy-to-ecs.sh YOUR_ACCOUNT_ID us-east-1
```

---

**Created:** October 16, 2024  
**Last Updated:** October 16, 2024  
**Version:** 1.0

