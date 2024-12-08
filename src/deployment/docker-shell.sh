#!/bin/bash

# exit immediately if a command exits with a non-zero status
#set -e

# Define some environment variables
export IMAGE_NAME="crimsonchat-deployment"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT="cs-crimsonchat" # CHANGE TO YOUR PROJECT ID
export GCP_ZONE="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/deployment.json

export GOOGLE_APPLICATION_CREDENTIALS="/secrets/crimsonchat.json"

#using secret - embedding goes to this account (grabbing the model)
#the following works when testing locally
# export GOOGLE_APPLICATION_CREDENTIALS="../../../secrets/llm-service-account.json"
export GCP_SERVICE_ACCOUNT="crimsonchat@cs-crimsonchat.iam.gserviceaccount.com"
export BUCKET_NAME="cs-crimsonchat"
export MODEL_ENDPOINT="1654493420430819328"


# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/docker.sock \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$HOME/.ssh":/home/app/.ssh \
-v "$BASE_DIR/../api-service":/api-service \
-v "$BASE_DIR/../frontend-react":/frontend-react \
-v "$BASE_DIR/../vector-db":/vector-db \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e USE_GKE_GCLOUD_AUTH_PLUGIN=True \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
$IMAGE_NAME

