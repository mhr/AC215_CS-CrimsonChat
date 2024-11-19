import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json
from langchain.schema import Document
from vector_database.utils.json_utils import (
    load_and_validate_json_from_bucket,
    load_all_documents_in_json
)

BASE_PATCH_PATH = "google.cloud.storage.Client"

# Master docstring
"""
Unit tests for functions in vector_database.utils.json_utils.

Functions Overview:
1. load_and_validate_json_from_bucket:
   - Purpose: Downloads and validates JSON from Google Cloud Storage, returning data as a list of Document objects.
   - Input:
     - bucket_name: GCS bucket name.
     - source_blob_name: Name of the blob to fetch.
   - Output:
     - List of Document objects or None on failure.
   - Errors:
     - Raises ValueError for invalid JSON structure, missing fields, or incorrect metadata formats.

2. load_all_documents_in_json:
   - Purpose: Loads all documents from a JSON file in GCS.
   - Input:
     - config: Dictionary containing bucket_name and file path.
   - Output:
     - List of Document objects or None on failure.
"""

@pytest.fixture
def mock_gcs_blob():
    """
    Fixture to create a mock GCS blob.
    """
    blob = MagicMock()
    blob.download_as_text.return_value = json.dumps({
        "https://example.com": {
            "text_content": "Sample content",
            "metadata": {
                "last_modified": "2023-01-01T00:00:00Z",
                "scraped_at": "2023-01-02T00:00:00Z",
                "word_count": 100
            }
        }
    })
    return blob


# Tests for load_and_validate_json_from_bucket
def test_load_and_validate_json_from_bucket_valid(mock_gcs_blob):
    """
    Test case: Valid JSON structure and data.
    Input: Mock GCS blob with valid JSON.
    Expected Output: List containing one Document object with correct data.
    Why: Ensures proper parsing, validation, and conversion to Document.
    """
    bucket_mock = MagicMock()
    bucket_mock.get_blob.return_value = mock_gcs_blob

    with patch(BASE_PATCH_PATH) as mock_client:
        mock_client.return_value.bucket.return_value = bucket_mock
        documents = load_and_validate_json_from_bucket("test-bucket", "test-blob")
        assert len(documents) == 1
        doc = documents[0]
        assert doc.page_content == "Sample content"
        assert doc.metadata['url'] == "https://example.com"
        assert doc.metadata['word_count'] == 100


def test_load_and_validate_json_from_bucket_blob_not_found():
    """
    Test case: Blob not found in GCS bucket.
    Input: None (simulating missing blob).
    Expected Output: None.
    Why: Ensures function returns None for missing blob.
    """
    bucket_mock = MagicMock()
    bucket_mock.get_blob.return_value = None

    with patch(BASE_PATCH_PATH) as mock_client:
        mock_client.return_value.bucket.return_value = bucket_mock
        documents = load_and_validate_json_from_bucket("test-bucket", "test-blob")
        assert documents is None


def test_load_and_validate_json_from_bucket_invalid_json(mock_gcs_blob):
    """
    Test case: Invalid JSON format.
    Input: Malformed JSON in the blob.
    Expected Output: None.
    Why: Ensures function handles JSONDecodeError gracefully.
    """
    mock_gcs_blob.download_as_text.return_value = "{invalid_json}"

    bucket_mock = MagicMock()
    bucket_mock.get_blob.return_value = mock_gcs_blob

    with patch(BASE_PATCH_PATH) as mock_client:
        mock_client.return_value.bucket.return_value = bucket_mock
        documents = load_and_validate_json_from_bucket("test-bucket", "test-blob")
        assert documents is None


def test_load_and_validate_json_from_bucket_missing_metadata_fields(mock_gcs_blob):
    """
    Test case: Missing required metadata fields.
    Input: JSON with missing 'last_modified' field.
    Expected Output: None.
    Why: Ensures function raises ValueError for invalid metadata structure.
    """
    mock_gcs_blob.download_as_text.return_value = json.dumps({
        "https://example.com": {
            "text_content": "Sample content",
            "metadata": {
                "scraped_at": "2023-01-02T00:00:00Z"
                # Missing 'last_modified' and 'word_count'
            }
        }
    })

    bucket_mock = MagicMock()
    bucket_mock.get_blob.return_value = mock_gcs_blob

    with patch(BASE_PATCH_PATH) as mock_client:
        mock_client.return_value.bucket.return_value = bucket_mock
        documents = load_and_validate_json_from_bucket("test-bucket", "test-blob")
        assert documents is None


def test_load_and_validate_json_from_bucket_invalid_date_format(mock_gcs_blob):
    """
    Test case: Invalid ISO 8601 date format in metadata.
    Input: JSON with invalid date format for 'scraped_at'.
    Expected Output: None.
    Why: Ensures function validates date formats strictly.
    """
    mock_gcs_blob.download_as_text.return_value = json.dumps({
        "https://example.com": {
            "text_content": "Sample content",
            "metadata": {
                "last_modified": "2023-01-01T00:00:00Z",
                "scraped_at": "not-a-date",
                "word_count": 100
            }
        }
    })

    bucket_mock = MagicMock()
    bucket_mock.get_blob.return_value = mock_gcs_blob

    with patch(BASE_PATCH_PATH) as mock_client:
        mock_client.return_value.bucket.return_value = bucket_mock
        documents = load_and_validate_json_from_bucket("test-bucket", "test-blob")
        assert documents is None


# Tests for load_all_documents_in_json
def test_load_all_documents_in_json_default_path(mock_gcs_blob):
    """
    Test case: Default bucket file path is used.
    Input: Config with no 'bucket_file_path'.
    Expected Output: List of Document objects.
    Why: Ensures default path handling works correctly.
    """
    with patch("vector_database.utils.json_utils.load_and_validate_json_from_bucket") as mock_load:
        mock_load.return_value = [Document(page_content="content", metadata={"url": "test-url"})]
        config = {}
        documents = load_all_documents_in_json(config)
        assert len(documents) == 1
        assert documents[0].metadata['url'] == "test-url"


def test_load_all_documents_in_json_custom_path(mock_gcs_blob):
    """
    Test case: Custom bucket file path is provided.
    Input: Config with 'bucket_name' and 'bucket_file_path'.
    Expected Output: List of Document objects.
    Why: Ensures custom path is handled correctly.
    """
    with patch("vector_database.utils.json_utils.load_and_validate_json_from_bucket") as mock_load:
        mock_load.return_value = [Document(page_content="content", metadata={"url": "test-url"})]
        config = {"bucket_name": "custom-bucket", "bucket_file_path": "custom-path"}
        documents = load_all_documents_in_json(config)
        assert len(documents) == 1
        assert documents[0].metadata['url'] == "test-url"