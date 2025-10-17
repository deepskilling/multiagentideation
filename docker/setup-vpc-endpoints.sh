#!/bin/bash
set -e

# Setup VPC Endpoints for ECS to access ECR without Internet Gateway
# This allows ECS tasks to pull Docker images from ECR in a private VPC

VPC_ID=${1:-vpc-e09d1e87}
REGION=${2:-us-east-1}
SG_ID=${3:-sg-01bf2f1572fa084d5}
SUBNET_IDS=${4:-"subnet-5425090c subnet-48341662"}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Setting up VPC Endpoints for ECS/ECR Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "VPC ID:      $VPC_ID"
echo "Region:      $REGION"
echo "Security:    $SG_ID"
echo "Subnets:     $SUBNET_IDS"
echo ""

# Convert space-separated subnet IDs to comma-separated for AWS CLI
SUBNET_ARRAY=$(echo $SUBNET_IDS | sed 's/ /,/g')

echo "📝 Step 1: Creating ECR Docker VPC Endpoint..."
ECR_DKR_ENDPOINT=$(aws ec2 create-vpc-endpoint \
  --vpc-id "$VPC_ID" \
  --service-name "com.amazonaws.${REGION}.ecr.dkr" \
  --vpc-endpoint-type Interface \
  --subnet-ids $(echo $SUBNET_IDS) \
  --security-group-ids "$SG_ID" \
  --private-dns-enabled \
  --region "$REGION" \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text 2>&1) || echo "Endpoint may already exist"

if [[ $ECR_DKR_ENDPOINT == vpc-* ]]; then
  echo "✅ ECR Docker endpoint created: $ECR_DKR_ENDPOINT"
else
  echo "⚠️  ECR Docker endpoint: $ECR_DKR_ENDPOINT"
fi

echo ""
echo "📝 Step 2: Creating ECR API VPC Endpoint..."
ECR_API_ENDPOINT=$(aws ec2 create-vpc-endpoint \
  --vpc-id "$VPC_ID" \
  --service-name "com.amazonaws.${REGION}.ecr.api" \
  --vpc-endpoint-type Interface \
  --subnet-ids $(echo $SUBNET_IDS) \
  --security-group-ids "$SG_ID" \
  --private-dns-enabled \
  --region "$REGION" \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text 2>&1) || echo "Endpoint may already exist"

if [[ $ECR_API_ENDPOINT == vpc-* ]]; then
  echo "✅ ECR API endpoint created: $ECR_API_ENDPOINT"
else
  echo "⚠️  ECR API endpoint: $ECR_API_ENDPOINT"
fi

echo ""
echo "📝 Step 3: Getting route table ID..."
ROUTE_TABLE_ID=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --region "$REGION" \
  --query 'RouteTables[0].RouteTableId' \
  --output text)

echo "Route Table: $ROUTE_TABLE_ID"

echo ""
echo "📝 Step 4: Creating S3 Gateway VPC Endpoint (for ECR layer storage)..."
S3_ENDPOINT=$(aws ec2 create-vpc-endpoint \
  --vpc-id "$VPC_ID" \
  --service-name "com.amazonaws.${REGION}.s3" \
  --vpc-endpoint-type Gateway \
  --route-table-ids "$ROUTE_TABLE_ID" \
  --region "$REGION" \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text 2>&1) || echo "Endpoint may already exist"

if [[ $S3_ENDPOINT == vpc-* ]]; then
  echo "✅ S3 Gateway endpoint created: $S3_ENDPOINT"
else
  echo "⚠️  S3 Gateway endpoint: $S3_ENDPOINT"
fi

echo ""
echo "📝 Step 5: Creating CloudWatch Logs VPC Endpoint (for ECS logs)..."
LOGS_ENDPOINT=$(aws ec2 create-vpc-endpoint \
  --vpc-id "$VPC_ID" \
  --service-name "com.amazonaws.${REGION}.logs" \
  --vpc-endpoint-type Interface \
  --subnet-ids $(echo $SUBNET_IDS) \
  --security-group-ids "$SG_ID" \
  --private-dns-enabled \
  --region "$REGION" \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text 2>&1) || echo "Endpoint may already exist"

if [[ $LOGS_ENDPOINT == vpc-* ]]; then
  echo "✅ CloudWatch Logs endpoint created: $LOGS_ENDPOINT"
else
  echo "⚠️  CloudWatch Logs endpoint: $LOGS_ENDPOINT"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ VPC Endpoints Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Created/Verified Endpoints:"
echo "   • ECR Docker (dkr):     $ECR_DKR_ENDPOINT"
echo "   • ECR API:              $ECR_API_ENDPOINT"
echo "   • S3 Gateway:           $S3_ENDPOINT"
echo "   • CloudWatch Logs:      $LOGS_ENDPOINT"
echo ""
echo "🔍 Verify endpoints:"
echo "   aws ec2 describe-vpc-endpoints --vpc-endpoint-ids $ECR_DKR_ENDPOINT --region $REGION"
echo ""
echo "🚀 Now you can run ECS tasks and they'll be able to pull from ECR!"
echo ""

