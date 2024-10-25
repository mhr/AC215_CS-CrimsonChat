#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
source ./env.dev

export IMAGE_NAME="vector_database"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS="/secrets/crimsonchat.json" \
-e GCP_PROJECT=$GCP_PROJECT \
-e BUCKET_NAME=$BUCKET_NAME \
-e LOCATION=$LOCATION \
-e QDRANT_URL=$QDRANT_URL \
-e QDRANT_API_KEY=$QDRANT_API_KEY \
$IMAGE_NAME