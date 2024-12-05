"""
test_qdrant_utils.py

Unit tests for Qdrant functionality using the `qdrant-client` library.
"""

from unittest.mock import patch, MagicMock
import pytest

# Patch paths
PATCH_QDRANT_CLIENT = "utils.qdrant_utils.QdrantClient"
PATCH_GET_EMBEDDING = "utils.embedding_utils.get_dense_embedding"

# Test constants
MOCK_QDRANT_URL = "http://mock-qdrant-url.com"
MOCK_QDRANT_API_KEY = "mock-api-key"
VECTOR_DIM = 256
QDRANT_COLLECTION = "test-collection"
EMBEDDING_MODEL = "test-embedding-model"


@pytest.fixture
def mocked_qdrant_client():
    """
    Fixture to mock QdrantClient.
    """
    with patch(PATCH_QDRANT_CLIENT) as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@patch(PATCH_QDRANT_CLIENT)
def test_initialize_qdrant_client(mock_client_class):
    """
    Tests initialization of QdrantClient.
    """
    from utils.qdrant_utils import initialize_qdrant_client

    # Call the function
    client = initialize_qdrant_client(MOCK_QDRANT_URL, MOCK_QDRANT_API_KEY)

    # Validate the mock call
    mock_client_class.assert_called_once_with(url=MOCK_QDRANT_URL, api_key=MOCK_QDRANT_API_KEY)
    assert client is mock_client_class(), "Expected mocked QdrantClient instance"


def test_qdrant_search(mocked_qdrant_client):
    """
    Tests the qdrant_search function.
    """
    from utils.qdrant_utils import qdrant_search
    from qdrant_client.http.models import ScoredPoint  # Import the model for consistency in mocking

    # Mock Qdrant search response with required fields
    mocked_qdrant_client.search.return_value = [
        ScoredPoint(
            id="1",
            payload={"key": "value"},
            score=0.95,
            vector=[0.1] * VECTOR_DIM,
            version=1  # Include the required `version` field
        ),
        ScoredPoint(
            id="2",
            payload={"key": "value"},
            score=0.85,
            vector=[0.1] * VECTOR_DIM,
            version=1  # Include the required `version` field
        ),
    ]

    # Example inputs
    query_vector = [0.1] * VECTOR_DIM
    limit = 5

    # Call the function
    results = qdrant_search(mocked_qdrant_client, QDRANT_COLLECTION, query_vector, limit)

    # Validate the results
    assert isinstance(results, list), "Expected a list of results"
    assert len(results) == 2, "Mismatch in result count"
    for result in results:
        assert "id" in result, "Missing 'id' in result"
        assert "score" in result, "Missing 'score' in result"
        assert "payload" in result, "Missing 'payload' in result"

    # Validate the mock call
    mocked_qdrant_client.search.assert_called_once_with(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=limit
    )
