# Use the official Python 3.9.13 slim-buster image from Debian
FROM python:3.9.13-slim-buster

# Define required Debian packages as a build argument
ARG DEBIAN_PACKAGES="build-essential git curl wget unzip gzip"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies and other dependencies for Google Cloud SDK
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get install -y lsb-release && \
    apt-get install -y --no-install-recommends software-properties-common apt-transport-https ca-certificates gnupg2 gnupg-agent curl openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install gcsfuse manually
RUN echo "deb http://packages.cloud.google.com/apt gcsfuse-focal main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y gcsfuse && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install Google Cloud SDK manually (for ARM64 compatible setup)
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-436.0.0-linux-x86_64.tar.gz && \
    tar -xf google-cloud-sdk-436.0.0-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh -q && \
    ./google-cloud-sdk/bin/gcloud components install gsutil -q && \
    rm google-cloud-sdk-436.0.0-linux-x86_64.tar.gz

# Add Google Cloud SDK to PATH
ENV PATH="/google-cloud-sdk/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install pipenv

# Add user
RUN useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

# Create mount point directories
RUN mkdir -p /mnt/gcs_data /app/data && chown app:app /mnt/gcs_data /app/data

# Set working directory to /app
WORKDIR /app

# Copy Pipfile and Pipfile.lock and install dependencies
ADD --chown=app:app Pipfile Pipfile.lock /app/
RUN pipenv sync

# Copy source code to the working directory
ADD --chown=app:app . /app

# Copy the docker-entrypoint.sh script and make it executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint to docker-entrypoint.sh
ENTRYPOINT ["pipenv", "run", "/bin/bash", "./docker-entrypoint.sh"]
