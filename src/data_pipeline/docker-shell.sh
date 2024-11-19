#!/bin/bash

# Name of the Docker image
IMAGE_NAME="data-pipeline"

# Source the .env.dev file to set environment variables
source .env.dev

# Build the Docker image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container with volume mounting for data and secrets
docker run --rm --name $IMAGE_NAME -ti \
--privileged \
--cap-add SYS_ADMIN \
--device /dev/fuse \
-v "$BASE_DIR":/app \
-v "$(pwd)/data:/app/data" \
-v "$SECRETS_DIR":/secrets \
-v ~/.gitconfig:/etc/gitconfig \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
$IMAGE_NAME
