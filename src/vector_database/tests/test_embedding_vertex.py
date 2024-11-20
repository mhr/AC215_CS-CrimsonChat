import pytest
from unittest.mock import patch, MagicMock
from vector_database.utils.embedding_utils import (
    initialize_vertex_ai,
    get_dense_embedding,
    process_and_embed_documents,
)
from langchain.docstore.document import Document

# Define base patch path for mocking
BASE_PATCH_PATH = "vector_database.utils.embedding_utils"

# Master docstring
"""
Unit tests for embedding_utils.py.

Function Overview:
- Purpose: Provides utility functions for generating embeddings using Vertex AI and processing LangChain Document objects.
- Input:
  - Various inputs, including project_id, location, LangChain Documents, and embedding model names.
- Output:
  - Functions initialize the Vertex AI environment, generate embeddings, and return processed documents with embeddings.
- Errors:
  - Functions handle input validation and log errors appropriately.
"""

# --- Tests for initialize_vertex_ai ---

@patch(f"{BASE_PATCH_PATH}.aiplatform.init")
def test_initialize_vertex_ai_valid(mock_init):
    """
    Test case: Valid input for initializing Vertex AI.
    Input: project_id="my-project", location="us-central1"
    Expected Behavior: Calls aiplatform.init with correct arguments.
    Why: Ensures proper integration with the aiplatform library.
    """
    initialize_vertex_ai("my-project", "us-central1")
    mock_init.assert_called_once_with(project="my-project", location="us-central1")

# --- Tests for get_dense_embedding ---
@patch(f"{BASE_PATCH_PATH}.TextEmbeddingModel.from_pretrained")
def test_get_dense_embedding_invalid_model(mock_from_pretrained):
    """
    Test case: Invalid model input (not TextEmbeddingModel).
    Input: text="sample text", model="invalid_model"
    Expected Output: Exception raised as 'Invalid model'.
    Why: Ensures that the exception is triggered for invalid models.
    """
    # Simulate the exception when attempting to load an invalid model
    mock_from_pretrained.side_effect = Exception("Invalid model")

    with pytest.raises(Exception, match="Invalid model"):
        get_dense_embedding("sample text", "invalid_model")

    # Ensure the mock was called
    mock_from_pretrained.assert_called_once_with("invalid_model")



# --- Tests for process_and_embed_documents ---

@patch(f"{BASE_PATCH_PATH}.get_dense_embedding", return_value=[0.1, 0.2, 0.3])
@patch(f"{BASE_PATCH_PATH}.initialize_vertex_ai")
@patch(f"{BASE_PATCH_PATH}.TextEmbeddingModel")
def test_process_and_embed_documents_valid(mock_model, mock_init, mock_embed):
    """
    Test case: Valid documents for embedding.
    Input: 
        project_id="my-project", location="us-central1",
        documents=[Document(page_content="sample", metadata={"id": "1"})]
    Expected Output: List of documents with embeddings added to metadata.
    Why: Ensures documents are processed and embeddings are correctly added.
    """
    mock_instance = MagicMock()
    mock_model.from_pretrained.return_value = mock_instance
    documents = [Document(page_content="sample", metadata={"id": "1"})]

    result = process_and_embed_documents("my-project", "us-central1", documents, "model-001")
    assert len(result) == 1
    assert result[0].metadata["embedding"] == [0.1, 0.2, 0.3]
    mock_init.assert_called_once_with("my-project", "us-central1")
    mock_embed.assert_called_once_with("sample", mock_instance, None)

@patch(f"{BASE_PATCH_PATH}.get_dense_embedding", return_value=[])
@patch(f"{BASE_PATCH_PATH}.initialize_vertex_ai")
@patch(f"{BASE_PATCH_PATH}.TextEmbeddingModel")
def test_process_and_embed_documents_empty_embedding(mock_model, mock_init, mock_embed):
    """
    Test case: Document embedding fails.
    Input: 
        project_id="my-project", location="us-central1",
        documents=[Document(page_content="sample", metadata={"id": "1"})]
    Expected Output: Empty list (embedding failure logged).
    Why: Verifies behavior when embedding generation fails.
    """
    mock_instance = MagicMock()
    mock_model.from_pretrained.return_value = mock_instance
    documents = [Document(page_content="sample", metadata={"id": "1"})]

    result = process_and_embed_documents("my-project", "us-central1", documents, "model-001")
    assert len(result) == 0
    mock_embed.assert_called_once_with("sample", mock_instance, None)
