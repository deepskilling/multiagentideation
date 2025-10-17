#!/bin/bash

# Setup AWS Infrastructure for Multi-Agent Ideation System
# Usage: ./setup-aws-infrastructure.sh [AWS_ACCOUNT_ID] [AWS_REGION]

set -e

# Configuration
AWS_ACCOUNT_ID=${1:-$(aws sts get-caller-identity --query Account --output text)}
AWS_REGION=${2:-"us-east-1"}

EXECUTION_ROLE_NAME="multiagent-ideation-execution-role"
TASK_ROLE_NAME="multiagent-ideation-task-role"
LOG_GROUP_NAME="/ecs/multiagent-ideation"
SECRET_NAME="multiagent/serper-api-key"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Setting up AWS Infrastructure for Multi-Agent Ideation System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region:     ${AWS_REGION}"
echo ""

# Step 1: Create CloudWatch Log Group
echo "📝 Step 1: Creating CloudWatch Log Group..."
aws logs create-log-group \
    --log-group-name ${LOG_GROUP_NAME} \
    --region ${AWS_REGION} 2>/dev/null || echo "Log group already exists"

aws logs put-retention-policy \
    --log-group-name ${LOG_GROUP_NAME} \
    --retention-in-days 7 \
    --region ${AWS_REGION} 2>/dev/null

echo "✅ CloudWatch Log Group ready: ${LOG_GROUP_NAME}"
echo ""

# Step 2: Create ECS Task Execution Role
echo "📝 Step 2: Creating ECS Task Execution Role..."

# Create trust policy file
cat > /tmp/trust-policy-execution.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
    --role-name ${EXECUTION_ROLE_NAME} \
    --assume-role-policy-document file:///tmp/trust-policy-execution.json \
    --region ${AWS_REGION} 2>/dev/null || echo "Execution role already exists"

# Attach policies
aws iam attach-role-policy \
    --role-name ${EXECUTION_ROLE_NAME} \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
    --region ${AWS_REGION} 2>/dev/null || true

# Create inline policy for Secrets Manager
cat > /tmp/secrets-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:multiagent/*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ${EXECUTION_ROLE_NAME} \
    --policy-name SecretsManagerAccess \
    --policy-document file:///tmp/secrets-policy.json \
    --region ${AWS_REGION} 2>/dev/null || true

echo "✅ ECS Task Execution Role ready: ${EXECUTION_ROLE_NAME}"
echo ""

# Step 3: Create ECS Task Role (for Bedrock access)
echo "📝 Step 3: Creating ECS Task Role..."

# Create trust policy file
cat > /tmp/trust-policy-task.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
    --role-name ${TASK_ROLE_NAME} \
    --assume-role-policy-document file:///tmp/trust-policy-task.json \
    --region ${AWS_REGION} 2>/dev/null || echo "Task role already exists"

# Create inline policy for Bedrock access
cat > /tmp/bedrock-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:*:${AWS_ACCOUNT_ID}:inference-profile/*"
      ]
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT_ID}:log-group:${LOG_GROUP_NAME}:*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ${TASK_ROLE_NAME} \
    --policy-name BedrockAndLogsAccess \
    --policy-document file:///tmp/bedrock-policy.json \
    --region ${AWS_REGION} 2>/dev/null || true

echo "✅ ECS Task Role ready: ${TASK_ROLE_NAME}"
echo ""

# Step 4: Create Secrets Manager secret for Serper API key
echo "📝 Step 4: Setting up Secrets Manager..."
echo ""
echo "⚠️  You need to manually create the Serper API key secret:"
echo ""
echo "aws secretsmanager create-secret \\"
echo "  --name ${SECRET_NAME} \\"
echo "  --description 'Serper API key for multi-agent ideation' \\"
echo "  --secret-string 'YOUR_SERPER_API_KEY_HERE' \\"
echo "  --region ${AWS_REGION}"
echo ""

# Cleanup temp files
rm -f /tmp/trust-policy-execution.json /tmp/trust-policy-task.json /tmp/secrets-policy.json /tmp/bedrock-policy.json

# Step 5: Display summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ AWS Infrastructure Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Created Resources:"
echo "   ✅ CloudWatch Log Group:        ${LOG_GROUP_NAME}"
echo "   ✅ ECS Task Execution Role:     ${EXECUTION_ROLE_NAME}"
echo "   ✅ ECS Task Role (Bedrock):     ${TASK_ROLE_NAME}"
echo ""
echo "🔑 IAM Role ARNs (update in ecs-task-definition.json):"
echo "   Execution Role: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${EXECUTION_ROLE_NAME}"
echo "   Task Role:      arn:aws:iam::${AWS_ACCOUNT_ID}:role/${TASK_ROLE_NAME}"
echo ""
echo "⚠️  Manual Steps Required:"
echo "   1. Create Serper API key secret (see command above)"
echo "   2. Update ecs-task-definition.json with:"
echo "      - executionRoleArn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${EXECUTION_ROLE_NAME}"
echo "      - taskRoleArn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${TASK_ROLE_NAME}"
echo "      - AWS Account ID: ${AWS_ACCOUNT_ID}"
echo ""
echo "🚀 Next Steps:"
echo "   1. Build and push Docker image:"
echo "      ./build-and-push.sh ${AWS_ACCOUNT_ID} ${AWS_REGION}"
echo ""
echo "   2. Deploy to ECS:"
echo "      ./deploy-to-ecs.sh ${AWS_ACCOUNT_ID} ${AWS_REGION}"
echo ""

