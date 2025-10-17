#!/bin/bash

# Deploy Multi-Agent Ideation System to AWS ECS
# Usage: ./deploy-to-ecs.sh [AWS_ACCOUNT_ID] [AWS_REGION] [CLUSTER_NAME] [SERVICE_NAME]

set -e

# Configuration
AWS_ACCOUNT_ID=${1:-"YOUR_ACCOUNT_ID"}
AWS_REGION=${2:-"us-east-1"}
CLUSTER_NAME=${3:-"multiagent-ideation-cluster"}
SERVICE_NAME=${4:-"multiagent-ideation-service"}
TASK_DEFINITION_FILE="ecs-task-definition.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Deploying Multi-Agent Ideation System to ECS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region:     ${AWS_REGION}"
echo "Cluster:        ${CLUSTER_NAME}"
echo "Service:        ${SERVICE_NAME}"
echo ""

# Step 1: Register task definition
echo "📝 Step 1: Registering ECS task definition..."

# Replace placeholders in task definition
TEMP_TASK_DEF=$(mktemp)
sed -e "s/YOUR_ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" \
    -e "s/us-east-1/${AWS_REGION}/g" \
    ${TASK_DEFINITION_FILE} > ${TEMP_TASK_DEF}

TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://${TEMP_TASK_DEF} \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

if [ $? -ne 0 ]; then
    echo "❌ Failed to register task definition"
    rm ${TEMP_TASK_DEF}
    exit 1
fi

rm ${TEMP_TASK_DEF}
echo "✅ Task definition registered: ${TASK_DEFINITION_ARN}"
echo ""

# Step 2: Check if ECS cluster exists
echo "📝 Step 2: Checking ECS cluster..."
aws ecs describe-clusters --clusters ${CLUSTER_NAME} --region ${AWS_REGION} | \
    grep -q "ACTIVE" 2>/dev/null || \
    (echo "Creating ECS cluster..." && \
     aws ecs create-cluster --cluster-name ${CLUSTER_NAME} --region ${AWS_REGION})

if [ $? -ne 0 ]; then
    echo "❌ Failed to verify/create ECS cluster"
    exit 1
fi
echo "✅ ECS cluster ready: ${CLUSTER_NAME}"
echo ""

# Step 3: Check if service exists
echo "📝 Step 3: Checking if ECS service exists..."
SERVICE_EXISTS=$(aws ecs describe-services \
    --cluster ${CLUSTER_NAME} \
    --services ${SERVICE_NAME} \
    --region ${AWS_REGION} \
    --query 'services[0].status' \
    --output text 2>/dev/null)

if [ "${SERVICE_EXISTS}" == "ACTIVE" ]; then
    # Update existing service
    echo "📝 Updating existing ECS service..."
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --task-definition ${TASK_DEFINITION_ARN} \
        --force-new-deployment \
        --region ${AWS_REGION}
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to update ECS service"
        exit 1
    fi
    echo "✅ ECS service updated successfully"
else
    # Create new service
    echo "📝 Creating new ECS service..."
    echo ""
    echo "⚠️  IMPORTANT: You need to provide VPC and subnet information!"
    echo ""
    echo "Please run the following command manually with your VPC settings:"
    echo ""
    echo "aws ecs create-service \\"
    echo "  --cluster ${CLUSTER_NAME} \\"
    echo "  --service-name ${SERVICE_NAME} \\"
    echo "  --task-definition ${TASK_DEFINITION_ARN} \\"
    echo "  --desired-count 1 \\"
    echo "  --launch-type FARGATE \\"
    echo "  --network-configuration \"awsvpcConfiguration={subnets=[subnet-XXXXX,subnet-YYYYY],securityGroups=[sg-ZZZZZ],assignPublicIp=ENABLED}\" \\"
    echo "  --region ${AWS_REGION}"
    echo ""
    echo "Or use the AWS Console to create the service with your VPC configuration."
fi
echo ""

# Step 4: Display service status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Service Information:"
echo "   Cluster:  ${CLUSTER_NAME}"
echo "   Service:  ${SERVICE_NAME}"
echo "   Task Def: ${TASK_DEFINITION_ARN}"
echo ""
echo "🔍 View service status:"
echo "   aws ecs describe-services --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME} --region ${AWS_REGION}"
echo ""
echo "📋 View running tasks:"
echo "   aws ecs list-tasks --cluster ${CLUSTER_NAME} --service-name ${SERVICE_NAME} --region ${AWS_REGION}"
echo ""
echo "📜 View logs:"
echo "   aws logs tail /ecs/multiagent-ideation --follow --region ${AWS_REGION}"
echo ""
echo "🛑 Stop service:"
echo "   aws ecs update-service --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --desired-count 0 --region ${AWS_REGION}"
echo ""

