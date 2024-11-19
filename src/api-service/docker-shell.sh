#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e


# export PERSISTENT_DIR=$(pwd)/../../../persistent-folder/
# Define some environment variables
export IMAGE_NAME="api-service-test"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
# export GCP_PROJECT="ac2215-project"
export GCP_PROJECT="upbeat-cargo-434717-p9"
export LOCATION="us-central1"
export QDRANT_URL="https://1494f517-c19c-490b-8a4e-43ff3b02bbb7.europe-west3-0.gcp.cloud.qdrant.io:6333"
export QDRANT_API_KEY="5qJBIKdEycPYlWfaDiAwd-1Hz2z88qaBsSV_UAa4AljpqWpWGzmRTg"
export QDRANT_COLLECTION_NAME="ms3-production_v256_te004"
export GOOGLE_APPLICATION_CREDENTIALS="../secrets/llm-service-account.json"
export MODEL_ENDPOINT="4516847642973569024"

# export PORT="8000:8000"
export PORT="8000"


# Create the network if we don't have it yet
#connect a network to the container - inspect asking whether the network already exists
docker network inspect llm-crimsonchat >/dev/null 2>&1 || docker network create llm-crimsonchat

# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run the container
# docker run --rm --name $IMAGE_NAME -ti \
# -v "$BASE_DIR":/app \
# -v "$SECRETS_DIR":/secrets \
# -p 9000:9000 \
# -e DEV=1 \
# -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
# -e GCP_PROJECT=$GCP_PROJECT \
# -e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
# --network llm-crimsonchat \
# $IMAGE_NAME

docker run -ti \
  -p 8000:$PORT \
  -e DEV=0 \
  -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
  -e GCP_PROJECT=$GCP_PROJECT \
  -e LOCATION=$LOCATION \
  -e QDRANT_URL=$QDRANT_URL \
  -e QDRANT_API_KEY=$QDRANT_API_KEY \
  -e QDRANT_COLLECTION_NAME=$QDRANT_COLLECTION_NAME \
  -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
  -v "$BASE_DIR":/app \
  -v "$SECRETS_DIR":/secrets \
  --network llm-crimsonchat \
  $IMAGE_NAME