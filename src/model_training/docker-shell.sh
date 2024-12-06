#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
source ./env.dev

export IMAGE_NAME="model_training"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Detect if a TTY is available
if [ -t 1 ]; then
  DOCKER_FLAGS="-ti"
else
  DOCKER_FLAGS="-i"  # Use non-interactive mode when no TTY is present
fi

if [[ "$1" == "--run-cli" ]]; then
  # Run the container and execute the Python CLI
  docker run --rm --name $IMAGE_NAME $DOCKER_FLAGS \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e BUCKET_NAME=$BUCKET_NAME \
    -e LOCATION=$LOCATION \
    -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
    $IMAGE_NAME pipenv run python /app/cli.py --train --train_config /app/train_config.json --dataset /app/kaggle_mental_dataset.json
else
  # Default: Drop into the container's shell because we're local
  docker run --rm --name $IMAGE_NAME $DOCKER_FLAGS \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e BUCKET_NAME=$BUCKET_NAME \
    -e LOCATION=$LOCATION \
    -e MODEL_ENDPOINT=$MODEL_ENDPOINT \
    $IMAGE_NAME
fi
