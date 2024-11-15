#!/bin/bash

set -e

export IMAGE_NAME="crimson-chat-ui"

# Build the image based on the Dockerfile
docker build -t crimson-chat-ui -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti -v "$(pwd)/:/app/" -p 3000:3000 $IMAGE_NAME