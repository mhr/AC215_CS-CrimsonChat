#!/bin/bash

set -e

export IMAGE_NAME="react-ui"
export IMAGE_TAG="latest"

# Set build-time arguments (update REACT_APP_API_URL as needed)
REACT_APP_API_URL="http://35.237.221.78:9000"

# Build the Docker image for amd64 architecture
docker build --platform linux/amd64 \
  --build-arg REACT_APP_API_URL=$REACT_APP_API_URL \
  -t $IMAGE_NAME:$IMAGE_TAG -f Dockerfile .

# Run the container locally
docker run --rm \
  --name $IMAGE_NAME \
  -e PORT=3000 \
  -p 3000:3000 \
  $IMAGE_NAME:$IMAGE_TAG
