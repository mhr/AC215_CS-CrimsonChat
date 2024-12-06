#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
source ./env.dev

export IMAGE_NAME="model_training"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

if [[ "$1" == "--run-cli" ]]; then
  # Run the container and execute the Python CLI
  docker run --rm --name $IMAGE_NAME -ti \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e BUCKET_NAME=$BUCKET_NAME \
    -e LOCATION=$LOCATION \
    -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
    $IMAGE_NAME python /app/cli.py --train --train_config /app/train_config.json --dataset /app/kaggle_mental_dataset.json
else
  # Default: Drop into the container's shell
  docker run --rm --name $IMAGE_NAME -ti \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e BUCKET_NAME=$BUCKET_NAME \
    -e LOCATION=$LOCATION \
    -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
    $IMAGE_NAME
fi
