#!/bin/bash

# Global IQ Kubernetes Deployment Script
# This script builds, pushes, and deploys the Global IQ application to Kubernetes

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-YOUR_DOCKERHUB_USERNAME}"
APP_NAME="global-iq-app"
VERSION="${VERSION:-v1}"
IMAGE_NAME="${DOCKER_USERNAME}/${APP_NAME}:${VERSION}"
NAMESPACE="global-iq"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Global IQ Kubernetes Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

# Check if Kubernetes cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Step 2: Build Docker image
echo -e "${YELLOW}Step 2: Building Docker image...${NC}"
echo "Image: ${IMAGE_NAME}"

docker build -t ${IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}Error: Docker build failed${NC}"
    exit 1
fi
echo ""

# Step 3: Push to Docker Hub (optional, comment out if not needed)
echo -e "${YELLOW}Step 3: Push to Docker Hub? (y/n)${NC}"
read -r PUSH_RESPONSE

if [[ "$PUSH_RESPONSE" =~ ^[Yy]$ ]]; then
    echo "Pushing ${IMAGE_NAME} to Docker Hub..."

    if [ "${DOCKER_USERNAME}" = "YOUR_DOCKERHUB_USERNAME" ]; then
        echo -e "${RED}Error: Please set DOCKER_USERNAME environment variable${NC}"
        echo "Example: export DOCKER_USERNAME=yourname"
        exit 1
    fi

    docker push ${IMAGE_NAME}

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Image pushed successfully${NC}"
    else
        echo -e "${RED}Error: Docker push failed. Make sure you're logged in (docker login)${NC}"
        exit 1
    fi
else
    echo "Skipping Docker Hub push"
fi
echo ""

# Step 4: Create secret.yaml if it doesn't exist
echo -e "${YELLOW}Step 4: Checking Kubernetes secrets...${NC}"

if [ ! -f "k8s/secret.yaml" ]; then
    echo -e "${YELLOW}Warning: k8s/secret.yaml not found${NC}"
    echo "Creating from template..."

    echo -e "${YELLOW}Enter your OpenAI API key:${NC}"
    read -rs OPENAI_KEY

    echo -e "${YELLOW}Enter Chainlit auth secret (or press enter for 'password'):${NC}"
    read -rs CHAINLIT_SECRET
    CHAINLIT_SECRET=${CHAINLIT_SECRET:-password}

    # Base64 encode the secrets
    OPENAI_KEY_B64=$(echo -n "$OPENAI_KEY" | base64)
    CHAINLIT_SECRET_B64=$(echo -n "$CHAINLIT_SECRET" | base64)

    # Create secret.yaml from template
    cat k8s/secret.yaml.template | \
        sed "s|REPLACE_WITH_BASE64_ENCODED_OPENAI_KEY|$OPENAI_KEY_B64|g" | \
        sed "s|cGFzc3dvcmQ=|$CHAINLIT_SECRET_B64|g" > k8s/secret.yaml

    echo -e "${GREEN}✓ secret.yaml created${NC}"
else
    echo -e "${GREEN}✓ secret.yaml exists${NC}"
fi
echo ""

# Step 5: Update deployment image
echo -e "${YELLOW}Step 5: Updating deployment manifest...${NC}"

# Update the image in deployment.yaml
sed -i.bak "s|image: .*global-iq-app:.*|image: ${IMAGE_NAME}|g" k8s/deployment.yaml
rm k8s/deployment.yaml.bak 2>/dev/null || true

echo -e "${GREEN}✓ Deployment manifest updated${NC}"
echo ""

# Step 6: Deploy to Kubernetes
echo -e "${YELLOW}Step 6: Deploying to Kubernetes...${NC}"

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply all configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/deployment.yaml

echo -e "${GREEN}✓ Kubernetes resources deployed${NC}"
echo ""

# Step 7: Wait for deployment
echo -e "${YELLOW}Step 7: Waiting for deployment to be ready...${NC}"

kubectl wait --for=condition=available --timeout=300s \
    deployment/global-iq-deployment -n ${NAMESPACE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment is ready${NC}"
else
    echo -e "${RED}Warning: Deployment may not be ready yet${NC}"
    echo "Check status with: kubectl get pods -n ${NAMESPACE}"
fi
echo ""

# Step 8: Display status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Namespace: ${NAMESPACE}"
echo "Image: ${IMAGE_NAME}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods:      kubectl get pods -n ${NAMESPACE}"
echo "  View services:  kubectl get svc -n ${NAMESPACE}"
echo "  View logs:      kubectl logs -f deployment/global-iq-deployment -n ${NAMESPACE}"
echo "  Port forward:   kubectl port-forward svc/global-iq-service 8000:8000 -n ${NAMESPACE}"
echo "  Scale:          kubectl scale deployment/global-iq-deployment --replicas=3 -n ${NAMESPACE}"
echo "  Delete:         kubectl delete namespace ${NAMESPACE}"
echo ""

# Step 9: Offer to port-forward
echo -e "${YELLOW}Would you like to start port-forwarding now? (y/n)${NC}"
read -r PORT_FORWARD_RESPONSE

if [[ "$PORT_FORWARD_RESPONSE" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}Starting port-forward on http://localhost:8000${NC}"
    echo "Press Ctrl+C to stop"
    kubectl port-forward svc/global-iq-service 8000:8000 -n ${NAMESPACE}
else
    echo ""
    echo -e "${GREEN}Access your application by running:${NC}"
    echo "kubectl port-forward svc/global-iq-service 8000:8000 -n ${NAMESPACE}"
fi
