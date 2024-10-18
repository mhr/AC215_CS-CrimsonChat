# Use the official Debian-hosted Python image
FROM python:3.11-slim-buster

# Set environment variable for pipenv shell
ENV PYENV_SHELL=/bin/bash

# Install system dependencies and pipenv
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git ffmpeg && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock into the container
# COPY Pipfile Pipfile.lock /app/
COPY Pipfile /app/

# Install dependencies; this will also generate the Pipfile.lock if it doesn't exist
RUN pipenv install

# Copy the rest of the application code into the container
COPY . /app

# Entry point
ENTRYPOINT ["/bin/bash"]

# Start pipenv shell
CMD ["-c", "pipenv shell"]
