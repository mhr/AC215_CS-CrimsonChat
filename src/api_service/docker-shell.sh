#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Disable path conversion for Windows
export MSYS_NO_PATHCONV=1

# Load the settings from the env.dev file. Change for production later
source ./env.dev


# export PERSISTENT_DIR=$(pwd)/../../../persistent-folder/
export IMAGE_NAME="api-service"

# export PORT="8000:8000"
export PORT="9000"



# Create the network if we don't have it yet
#connect a network to the container - inspect asking whether the network already exists
docker network inspect llm-crimsonchat >/dev/null 2>&1 || docker network create llm-crimsonchat

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
# docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

docker run --rm --name $IMAGE_NAME -i \
  -p 9000:$PORT \
  -e DEV=0 \
  -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
  -e GCP_PROJECT=$GCP_PROJECT \
  -e LOCATION=$LOCATION \
  -e QDRANT_URL=$QDRANT_URL \
  -e QDRANT_API_KEY=$QDRANT_API_KEY \
  -e QDRANT_COLLECTION_NAME=$QDRANT_COLLECTION_NAME \
  -e GCP_SERVICE_ACCOUNT=$GCP_SERVICE_ACCOUNT \
  -e BUCKET_NAME=$BUCKET_NAME \
  -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
  -v "$BASE_DIR":/app \
  -v "$SECRETS_DIR":/secrets \
  --network llm-crimsonchat \
  $IMAGE_NAME