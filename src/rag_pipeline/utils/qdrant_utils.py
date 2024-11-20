"""
qdrant_utils.py

This utility file contains functions for interacting with Qdrant vector database using LangChain Document objects.

Input:
    - Qdrant URL (string)
    - Qdrant API Key (string)
    - List of LangChain Document objects
    - Collection name (string)

Usage:
    from qdrant_utils import qdrant_transform_and_upsert
    qdrant_transform_and_upsert(qdrant_url, qdrant_api_key, documents, collection_name)

Output:
    None (performs upsert operation to Qdrant)

Note: The collection_name must be manually specified when calling the function.

Author: Artem Dinh
Date: 10/10/2024
"""

<<<<<<< HEAD
import uuid
import logging
import time
from typing import List,  Optional, Dict, Any
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from qdrant_client import http as qhttp
from langchain.schema import Document
from utils.embedding_utils import get_dense_embedding
=======
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rag_pipeline.utils.embedding_utils import get_dense_embedding
>>>>>>> e547b8d919e196352063181e9b516ac65e39f639


def initialize_qdrant_client(qdrant_url: str, qdrant_api_key: str) -> QdrantClient:
    """
    Initialize and return a Qdrant client instance.
    """
    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )


def qdrant_search(
    client: QdrantClient,
    collection_name: str,
    query_vector: List[float],
    limit: int = 10,
    filter_field: Optional[str] = None,
    filter_value: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Perform a search in Qdrant collection.

    Args:
        client (QdrantClient): Initialized Qdrant client.
        collection_name (str): Name of the collection to search in.
        query_vector (List[float]): The query vector to search with.
        limit (int): Maximum number of results to return. Defaults to 30.
        filter_field (Optional[str]): Field name to filter on. Defaults to None.
        filter_value (Optional[Any]): Value to filter by. Defaults to None.

    Returns:
        List[Dict[str, Any]]: List of search results.
    """
    search_params = {
        "collection_name": collection_name,
        "query_vector": query_vector,
        "limit": limit
    }

    if filter_field and filter_value is not None:
        search_params["query_filter"] = Filter(
            must=[
                FieldCondition(
                    key=filter_field,
                    match=MatchValue(value=filter_value)
                )
            ]
        )

    search_results = client.search(**search_params)

    # Process and return the results
    return [
        {
            "id": result.id,
            "score": result.score,
            "payload": result.payload
        } for result in search_results
    ]


def get_documents_from_qdrant(query, config, rag_config, qdrant_client):
    """
    Retrieve relevant documents from Qdrant based on the given query.
    Args:
        query (str): The search query.
        config (dict): Configuration settings.
        rag_config (dict): RAG Configuration settings containing num_documents
        qdrant_client: The Qdrant client instance.
    Returns:
        list: A list of document texts retrieved from Qdrant.
    """
    search_results = qdrant_search(
        qdrant_client,
        config['qdrant_collection'],
        get_dense_embedding(query, config['embedding_model'], config['vector_dim']),
        rag_config['num_documents']  # Retrieve number of documents from RAG config
    )
    return [result['payload']['text'] + ", retrieved from: " + result['payload']['url'] for result in search_results]
