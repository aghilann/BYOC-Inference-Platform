#!/bin/bash

# Define your Docker Hub username and image name
DOCKER_USERNAME="aghilann"
IMAGE_NAME="model-router"
IMAGE_TAG="latest"

# Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME .

# Tag the Docker image with Docker Hub username and repository name
docker tag $IMAGE_NAME $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG

# Log in to Docker Hub (you may need sudo depending on your Docker setup)
echo "Logging in to Docker Hub..."
docker login

# Push the Docker image to Docker Hub
echo "Pushing the Docker image to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG

# Update Kubernetes Deployment to use the new image
echo "Updating Kubernetes Deployment..."
kubectl set image deployment/model-router-deployment model-router=$DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG --record

# Check the rollout status
kubectl rollout status deployment/model-router-deployment

echo "Deployment successfully updated with the new image."
