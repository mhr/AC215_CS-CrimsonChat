#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load the settings from the env.dev file
source ./env.dev

# Set the image name
export IMAGE_NAME="rag_pipeline"

# Build the image based on the Dockerfile
docker build -t "$IMAGE_NAME" -f Dockerfile .

# Run the container with /bin/sh instead of /bin/bash
docker run --rm --name "$IMAGE_NAME" -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS" \
-e GCP_PROJECT="$GCP_PROJECT" \
-e GCS_BUCKET_NAME="$GCS_BUCKET_NAME" \
-p 8501:8501 \
$IMAGE_NAME