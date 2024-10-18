from google.cloud import storage
import os
from dotenv import load_dotenv




# GCP local connection sucked so i needed to test it locally

def list_buckets():
    """Lists all buckets."""
    # Explicitly specify the project ID here
    project_id = "cs-crimsonchat"  # Replace with your actual project ID
    storage_client = storage.Client(project=project_id)
    buckets = storage_client.list_buckets()

    print("Buckets:")
    for bucket in buckets:
        print(bucket.name)

if __name__ == "__main__":
    list_buckets()
    # Load environment variables from .env file
    # Load environment variables from .env file
    load_dotenv('env.dev')
    print("blah blah")
    # Set up project details
    GCP_PROJECT = os.environ.get("GCP_PROJECT")
    LOCATION = os.environ.get("LOCATION")
    # Initialize Qdrant client
    QDRANT_URL = os.environ.get("QDRANT_URL")
    QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = "milestone_2"
    print(GCP_PROJECT, LOCATION, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME)