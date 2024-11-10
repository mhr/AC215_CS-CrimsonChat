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

import uuid
import logging
import time
from typing import List,  Optional, Dict, Any
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from qdrant_client import http as qhttp
from langchain.schema import Document
from utils.embedding_utils import get_dense_embedding

def initialize_qdrant_client(qdrant_url: str, qdrant_api_key: str) -> QdrantClient:
    """
    Initialize and return a Qdrant client instance.
    """
    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )

def qdrant_transform_and_upsert(qdrant_url: str, qdrant_api_key: str, documents: List[Document], collection_name: str) -> None:
    print("qdrant_transform_and_upsert")
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(qdrant_url, qdrant_api_key)

    # Transform embedded documents and perform upsert operation to Qdrant with retry logic
    max_retries = 1
    retry_delay = 5  # seconds

    # Transform the documents
    points = []
    for doc in documents:
        # Ensure the document has an embedding
        embedding = doc.metadata.get('embedding')
        if not embedding:
            logging.warning(f"Document with content '{doc.page_content[:50]}...' has no embedding. Skipping.")
            continue

        # Construct Qdrant point
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            payload={
                "text": doc.page_content,
                **{k: v for k, v in doc.metadata.items() if k != 'embedding'}  # Include all metadata fields except 'embedding'
            },
            vector=embedding  # Ensure embedding is passed correctly
        )
        points.append(point)

    if not points:
        logging.warning("No valid documents with embeddings to upsert.")
        return

    # Perform upsert
    for attempt in range(max_retries):
        try:
            result = qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            logging.info(f"Qdrant upsert successful: {result}")
            return
        except qhttp.exceptions.UnexpectedResponse as e:
            logging.error(f"Unexpected response from Qdrant (Attempt {attempt + 1}/{max_retries}): {e}")
        except qhttp.exceptions.NetworkError as e:
            logging.error(f"Network error occurred while communicating with Qdrant (Attempt {attempt + 1}/{max_retries}): {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during Qdrant upsert (Attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            logging.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logging.error("Max retries reached. Qdrant upsert failed.")


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
    return [result['payload']['text']+", retrieved from: "+result['payload']['url'] for result in search_results]