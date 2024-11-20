import json
# from typing import List
from langchain.schema import Document
from google.cloud import storage
from datetime import datetime


def load_and_validate_json_from_bucket(bucket_name, source_blob_name):
    """
    Downloads a JSON file from the specified GCS bucket,
    validates its format, and returns the data as a list of Document objects.
    """
    print("Downloading JSON file from bucket...", bucket_name, source_blob_name)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(source_blob_name)  # source_blob_name
    if blob:
        json_content = blob.download_as_text()
    else:
        print("Blob not found")
        return None
    # Download the file content
    json_content = blob.download_as_text()
    print(f"File {source_blob_name} downloaded from bucket {bucket_name}.")
    try:
        # Parse the JSON content
        data = json.loads(json_content)
        # Validate the JSON structure
        if not isinstance(data, dict):
            raise ValueError("JSON must be a dictionary")
        documents = []
        for url, content in data.items():
            print("processing", url)
            if not isinstance(content, dict) or 'text_content' not in content or 'metadata' not in content:
                raise ValueError("Each URL entry must have 'text_content' and 'metadata' fields")
            metadata = content['metadata']
            print("metadata", metadata)
            required_fields = ['last_modified', 'scraped_at', 'word_count']
            if not all(field in metadata for field in required_fields):
                raise ValueError("Metadata must include 'last_modified', 'scraped_at', and 'word_count' fields")

            # Handle None values for datetime fields
            scraped_at = metadata['scraped_at']
            last_modified = metadata['last_modified']
            if scraped_at is not None:
                try:
                    datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("'scraped_at' must be a valid ISO 8601 format")
            if last_modified is not None:
                try:
                    datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("'last_modified' must be a valid ISO 8601 format")

            # Handle None value for word_count
            word_count = metadata['word_count']
            if word_count is not None and not isinstance(word_count, int):
                raise ValueError("'word_count' must be an integer")

            # Set text_content to empty string if it's None
            text_content = "" if content['text_content'] is None else content['text_content']

            doc = Document(
                page_content=text_content,
                metadata={
                    'id': url,
                    'url': url,
                    'timestamp': scraped_at,
                    'last_modified': last_modified,
                    'word_count': word_count
                }
            )
            documents.append(doc)
        print("JSON file has the correct format.")
        return documents
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return None
    except ValueError as e:
        print(f"Error: {str(e)}")
        return None


def load_all_documents_in_json(config):
    # only loading from bucket, no support for local json file anymore
    default_bucket_name = "cs-crimsonchat"
    default_blob_name = "/rag_knowledge/sample.json"
    if not config.get('bucket_file_path'):
        print(f"No bucket file path provided, using default: {default_bucket_name}/{default_blob_name}")
        bucket_name = default_bucket_name
        source_blob_name = default_blob_name
    else:
        bucket_name = config['bucket_name']
        source_blob_name = config['bucket_file_path']
        print(f"Bucket file path provided, using: {bucket_name}/{source_blob_name}")
    documents = load_and_validate_json_from_bucket(bucket_name, source_blob_name)
    return documents
