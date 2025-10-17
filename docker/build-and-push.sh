#!/bin/bash

# Build and Push Docker Image to AWS ECR
# Usage: ./build-and-push.sh [AWS_ACCOUNT_ID] [AWS_REGION] [IMAGE_TAG]

set -e

# Configuration
AWS_ACCOUNT_ID=${1:-"YOUR_ACCOUNT_ID"}
AWS_REGION=${2:-"us-east-1"}
IMAGE_TAG=${3:-"latest"}
REPOSITORY_NAME="multiagent-ideation"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:${IMAGE_TAG}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 Building and Pushing Multi-Agent Ideation System to ECR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region:     ${AWS_REGION}"
echo "Repository:     ${REPOSITORY_NAME}"
echo "Image Tag:      ${IMAGE_TAG}"
echo "Image URI:      ${IMAGE_URI}"
echo ""

# Step 1: Authenticate Docker to ECR
echo "📝 Step 1: Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

if [ $? -ne 0 ]; then
    echo "❌ Failed to authenticate to ECR"
    exit 1
fi
echo "✅ Successfully authenticated to ECR"
echo ""

# Step 2: Create ECR repository if it doesn't exist
echo "📝 Step 2: Checking ECR repository..."
aws ecr describe-repositories --repository-names ${REPOSITORY_NAME} --region ${AWS_REGION} 2>/dev/null || \
    (echo "Creating ECR repository..." && \
     aws ecr create-repository \
         --repository-name ${REPOSITORY_NAME} \
         --region ${AWS_REGION} \
         --image-scanning-configuration scanOnPush=true \
         --encryption-configuration encryptionType=AES256)

if [ $? -ne 0 ]; then
    echo "❌ Failed to verify/create ECR repository"
    exit 1
fi
echo "✅ ECR repository ready"
echo ""

# Step 3: Build Docker image
echo "📝 Step 3: Building Docker image..."
cd ..
docker build -f docker/Dockerfile -t ${REPOSITORY_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi
echo "✅ Successfully built Docker image"
echo ""

# Step 4: Tag image for ECR
echo "📝 Step 4: Tagging image for ECR..."
docker tag ${REPOSITORY_NAME}:${IMAGE_TAG} ${IMAGE_URI}

if [ $? -ne 0 ]; then
    echo "❌ Failed to tag Docker image"
    exit 1
fi
echo "✅ Successfully tagged image"
echo ""

# Step 5: Push image to ECR
echo "📝 Step 5: Pushing image to ECR..."
docker push ${IMAGE_URI}

if [ $? -ne 0 ]; then
    echo "❌ Failed to push Docker image to ECR"
    exit 1
fi
echo "✅ Successfully pushed image to ECR"
echo ""

# Step 6: Display image information
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Build and Push Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Image Information:"
echo "   URI:  ${IMAGE_URI}"
echo "   Tag:  ${IMAGE_TAG}"
echo ""
echo "🚀 Next Steps:"
echo "   1. Update ecs-task-definition.json with image URI:"
echo "      ${IMAGE_URI}"
echo ""
echo "   2. Deploy to ECS:"
echo "      ./deploy-to-ecs.sh ${AWS_ACCOUNT_ID} ${AWS_REGION}"
echo ""
echo "   3. Or run locally:"
echo "      docker run -it ${IMAGE_URI} /bin/bash"
echo ""

# Get image size
IMAGE_SIZE=$(docker images ${REPOSITORY_NAME}:${IMAGE_TAG} --format "{{.Size}}")
echo "📊 Image Size: ${IMAGE_SIZE}"
echo ""

