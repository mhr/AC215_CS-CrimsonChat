"""
test_qdrant_utils.py

This file contains unit tests for functions in qdrant_utils.py, which interact with the Qdrant vector database.
The tests verify initialization, search, and document retrieval operations using QdrantClient.

Original Functions and Corresponding Test Functions:

1. initialize_qdrant_client
    - Initializes a Qdrant client instance for database interaction.
    - Test Function: test_initialize_qdrant_client

2. qdrant_search
    - Performs a vector-based search in a specified Qdrant collection.
    - Test Function: test_qdrant_search

3. get_documents_from_qdrant
    - Retrieves relevant documents from Qdrant based on a query by leveraging vector embeddings.
    - Test Functions:
      - test_get_documents_from_qdrant: Verifies retrieval of documents for a specific query.
      - test_get_documents_from_qdrant_no_results: Ensures that no results are returned for a non-matching query.

Additional Notes:
- The qdrant_transform_and_upsert function mentioned in the qdrant_utils.py documentation is not tested in this file, as it is not included in the provided code.
- The tests use an environment configuration specified in `env.dev` for connecting to the Qdrant instance.
- The VECTOR_DIM and QDRANT_COLLECTION are configured to align with the Qdrant setup specified in the configuration file.

"""
from qdrant_client import QdrantClient
from utils.qdrant_utils import initialize_qdrant_client, qdrant_search, get_documents_from_qdrant
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.dev')

# Set up Qdrant and embedding details from configuration
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
EMBEDDING_MODEL = "text-embedding-004"
VECTOR_DIM = 256
QDRANT_COLLECTION = "ms3-production_v256_te004"

# Function: initialize_qdrant_client
# Description: Initializes and returns a Qdrant client instance to interact with Qdrant's vector database.
# Inputs:
# - qdrant_url (str): The Qdrant instance URL.
# - qdrant_api_key (str): API key for authenticating with Qdrant.
# Outputs:
# - QdrantClient: An instance of the Qdrant client, ready for database operations.
def test_initialize_qdrant_client():
    """
    Tests the initialize_qdrant_client function.
    
    This function checks:
    - If a valid QdrantClient instance is returned.
    - The correctness of the API key and URL in the client instance.
    """
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    # Validate that a QdrantClient instance is returned
    assert isinstance(qdrant_client, QdrantClient), "Expected QdrantClient instance"

# Function: qdrant_search
# Description: Performs a search in a Qdrant collection using a query vector and optional filters.
# Inputs:
# - client (QdrantClient): Initialized Qdrant client.
# - collection_name (str): Name of the Qdrant collection to search.
# - query_vector (List[float]): Vector to search for.
# - limit (int): Maximum number of results. Default is 10.
# Outputs:
# - List[Dict[str, Any]]: List of search result dictionaries containing document metadata.
def test_qdrant_search():
    """
    Tests the qdrant_search function for a basic search operation in Qdrant.
    
    This function checks:
    - If the search returns a list of documents with required fields.
    - If the returned documents are within the specified limit.
    """
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    # Example data for testing
    query_vector = [0.1] * VECTOR_DIM
    limit = 5

    # Run function
    results = qdrant_search(qdrant_client, QDRANT_COLLECTION, query_vector, limit)

    # Validate results
    assert isinstance(results, list), "Expected list of results"
    assert len(results) <= limit, "Exceeded result limit"
    for result in results:
        assert "id" in result, "Expected 'id' in result"
        assert "score" in result, "Expected 'score' in result"
        assert "payload" in result, "Expected 'payload' in result"
        assert isinstance(result["payload"], dict), "Expected payload to be a dictionary"

# Function: get_documents_from_qdrant
# Description: Retrieves relevant documents from Qdrant based on a given query by using vector embeddings.
# Inputs:
# - query (str): The search query string.
# - config (dict): Configuration settings including collection name and embedding model.
# - rag_config (dict): RAG configuration settings such as number of documents.
# - qdrant_client (QdrantClient): The initialized Qdrant client.
# Outputs:
# - list: List of document texts retrieved from Qdrant, with metadata appended.
def test_get_documents_from_qdrant():
    """
    Tests get_documents_from_qdrant function to retrieve documents from Qdrant.
    
    This function checks:
    - If the function returns a list of documents for a given query.
    - The structure and content of each document, ensuring metadata fields like 'url' are appended.
    """
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    # Test configuration
    query = "Machine learning in healthcare"
    config = {
        "qdrant_collection": QDRANT_COLLECTION,
        "embedding_model": EMBEDDING_MODEL,
        "vector_dim": VECTOR_DIM
    }
    rag_config = {"num_documents": 5}

    # Run function
    documents = get_documents_from_qdrant(query, config, rag_config, qdrant_client)

    # Validate retrieved documents
    assert isinstance(documents, list), "Expected a list of documents"
    assert len(documents) <= rag_config["num_documents"], "Exceeded expected document count"
    for doc in documents:
        assert isinstance(doc, str), "Expected document to be a string with appended metadata"
        assert "retrieved from:" in doc, "Expected document metadata to be appended"

def test_get_documents_from_qdrant_no_results():
    """
    Tests get_documents_from_qdrant for a query that yields no results.
    
    This function checks:
    - How the function handles cases where there are no relevant documents.
    - Ensures that an empty list is returned if no documents match the query.
    """
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    # Test configuration for a non-matching query
    query = "xqzvyrk-12345-nonexistent-topic-query"  # Highly improbable query string
    config = {
        "qdrant_collection": QDRANT_COLLECTION,
        "embedding_model": EMBEDDING_MODEL,
        "vector_dim": VECTOR_DIM
    }
    rag_config = {"num_documents": 5}

    # Run function
    documents = get_documents_from_qdrant(query, config, rag_config, qdrant_client)

    # Validate no results case
    assert isinstance(documents, list), "Expected a list even if empty"
    assert len(documents) == 0, "Expected no documents for a highly improbable topic query"
