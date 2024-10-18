#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Source the .env.dev file to get the environment variables
if [ -f .env.dev ]; then
  source .env.dev
else
  echo ".env.dev file not found. Please ensure it's available."
  exit 1
fi

echo "Container is running!!!"

# Authenticate with GCP using the service account credentials
echo "Authenticating with Google Cloud..."
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Create the necessary directories for mounting the GCS bucket
echo "Creating mount directories..."
mkdir -p /mnt/gcs_bucket
mkdir -p /app/gcp_static_data

# Mount the GCS bucket to /mnt/gcs_bucket using gcsfuse
echo "Mounting GCS bucket $GCS_BUCKET_NAME/$GCS_BUCKET_FOLDER..."
gcsfuse --key-file=$GOOGLE_APPLICATION_CREDENTIALS $GCS_BUCKET_NAME /mnt/gcs_bucket

# Check if the GCS bucket folder exists and is mounted successfully
if [ -d "/mnt/gcs_bucket/$GCS_BUCKET_FOLDER" ]; then
  echo "GCS bucket mounted at /mnt/gcs_bucket/$GCS_BUCKET_FOLDER"
else
  echo "Error: GCS bucket folder /mnt/gcs_bucket/$GCS_BUCKET_FOLDER does not exist."
  exit 1
fi

# Bind the folder from the GCS bucket to /app/gcp_static_data
echo "Binding /mnt/gcs_bucket/$GCS_BUCKET_FOLDER to /app/gcp_static_data"
mount --bind /mnt/gcs_bucket/$GCS_BUCKET_FOLDER /app/gcp_static_data

# Check if the GCS folder contains files before copying
if [ "$(ls -A /mnt/gcs_bucket/$GCS_BUCKET_FOLDER)" ]; then
  echo "Copying files from GCS bucket to /app/data for local review..."
  cp -r /mnt/gcs_bucket/$GCS_BUCKET_FOLDER/* /app/data/
else
  echo "Warning: No files found in GCS bucket folder /mnt/gcs_bucket/$GCS_BUCKET_FOLDER."
fi

# Start a bash shell to keep the container running interactively
exec /bin/bash
