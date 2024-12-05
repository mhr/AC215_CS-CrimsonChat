# import pytest
from unittest.mock import MagicMock, patch
from qdrant_client import models
from langchain.schema import Document
from qdrant_utils import ensure_collection_exists, qdrant_transform_and_upsert

# Define base path for patching
BASE_PATCH_PATH = 'qdrant_upsert_utils'

"""
Unit Tests for `qdrant_upsert_utils.py`

Overview:
These tests validate the functionality of utility functions designed to interact with the Qdrant vector database.
The primary functions under test include:
- `ensure_collection_exists`: Ensures the specified collection exists in the Qdrant database, creating it if necessary.
- `qdrant_transform_and_upsert`: Processes LangChain documents, transforms them into Qdrant-compatible points, and upserts them into the specified collection.

Tested Scenarios:
1. Collection Management:
   - Creating a collection if it does not exist.
   - Avoiding redundant creation when the collection already exists.
2. Document Transformation and Upsert:
   - Handling documents with valid embeddings, transforming and upserting them.
   - Skipping documents with missing or invalid embeddings.

External Dependencies:
- `qdrant_client`: Provides the client and related models for interacting with Qdrant.
- `langchain.schema.Document`: Defines the document schema used for transformation.

Mocking Strategy:
- `qdrant_client.QdrantClient`: Mocked to simulate Qdrant API interactions.
- `qdrant_client.models.VectorParams`: Mocked to validate the correct construction of vector parameters.
- LangChain Document objects are mocked to test edge cases in document handling.

Expected Behavior:
- Proper API calls to `create_collection` and `upsert` in the respective scenarios.
- Skipping invalid documents and logging appropriate warnings.

"""


@patch('qdrant_client.models.VectorParams')
@patch('qdrant_client.QdrantClient')
def test_ensure_collection_exists_collection_does_not_exist(mock_qdrant_client, mock_vector_params):
    """
    Test case: Creates a collection if it does not exist.
    Input: Mock Qdrant client, collection_name, vector_size.
    Expected Output: New collection is created.
    Why: Ensures that missing collections are created.
    """
    mock_client = MagicMock()
    mock_qdrant_client.return_value = mock_client

    # Simulate no existing collections
    mock_client.get_collections.return_value.collections = []

    # Mock the behavior of VectorParams
    mock_vector_params.return_value = MagicMock()

    # Call the function
    ensure_collection_exists(mock_client, "test_collection", 128)

    # Assert VectorParams was called with correct arguments
    mock_vector_params.assert_called_once_with(size=128, distance=models.Distance.COSINE)
    mock_client.create_collection.assert_called_once_with(
        collection_name="test_collection",
        vectors_config=mock_vector_params()
    )


@patch('qdrant_client.QdrantClient')  # Mock the Qdrant client
def test_ensure_collection_exists_collection_exists(mock_qdrant_client):
    """
    Test case: Collection already exists.
    Input: Mock Qdrant client, collection_name, vector_size.
    Expected Output: Collection creation is skipped.
    Why: Ensures that existing collections are not recreated.
    """
    mock_client = MagicMock()
    mock_qdrant_client.return_value = mock_client

    # Simulate an existing collection
    existing_collection = MagicMock()
    existing_collection.name = "test_collection"
    mock_client.get_collections.return_value.collections = [existing_collection]

    ensure_collection_exists(mock_client, "test_collection", 128)

    mock_client.create_collection.assert_not_called()


@patch(f'{BASE_PATCH_PATH}.initialize_qdrant_client')  # Refactored path
@patch(f'{BASE_PATCH_PATH}.ensure_collection_exists')  # Refactored path
def test_qdrant_transform_and_upsert(mock_ensure, mock_initialize):
    """
    Test case: Transforms documents and upserts into Qdrant.
    Input: Mock QdrantClient, documents, collection_name.
    Expected Output: Upsert operation is called.
    Why: Verifies correct transformation and upsertion of documents.
    """
    mock_client = MagicMock()
    mock_initialize.return_value = mock_client

    documents = [
        Document(page_content="Test content", metadata={"embedding": [0.1, 0.2, 0.3]}),
        Document(page_content="Another content", metadata={"embedding": [0.4, 0.5, 0.6]}),
    ]

    qdrant_transform_and_upsert("http://test-url", "test-key", documents, "test_collection")

    mock_initialize.assert_called_once_with("http://test-url", "test-key")
    mock_ensure.assert_called_once_with(mock_client, "test_collection", 3)
    mock_client.upsert.assert_called_once()


@patch(f'{BASE_PATCH_PATH}.initialize_qdrant_client')  # Refactored path
@patch(f'{BASE_PATCH_PATH}.ensure_collection_exists')  # Refactored path
def test_qdrant_transform_and_upsert_no_embeddings(mock_ensure, mock_initialize):
    """
    Test case: Handles documents without embeddings.
    Input: Documents without embeddings.
    Expected Output: Logs warning and skips documents.
    Why: Ensures function handles cases where embeddings are missing.
    """
    mock_client = MagicMock()
    mock_initialize.return_value = mock_client

    documents = [
        Document(page_content="Test content", metadata={}),
    ]

    qdrant_transform_and_upsert("http://test-url", "test-key", documents, "test_collection")

    mock_initialize.assert_called_once_with("http://test-url", "test-key")
    mock_ensure.assert_not_called()
    mock_client.upsert.assert_not_called()
