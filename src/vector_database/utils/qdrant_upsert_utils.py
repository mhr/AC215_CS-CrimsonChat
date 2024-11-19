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
from typing import List
from qdrant_client import QdrantClient, models
from qdrant_client import http as qhttp
from langchain.schema import Document

def initialize_qdrant_client(qdrant_url: str, qdrant_api_key: str) -> QdrantClient:
    """
    Initialize and return a Qdrant client instance.
    """
    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )

def ensure_collection_exists(qdrant_client: QdrantClient, collection_name: str, vector_size: int) -> None:
    """
    Check if the collection exists, and create it if it doesn't.
    """
    collections = qdrant_client.get_collections().collections
    if not any(collection.name == collection_name for collection in collections):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        logging.info(f"Created new collection: {collection_name}")
    else:
        logging.info(f"Collection {collection_name} already exists")

def qdrant_transform_and_upsert(qdrant_url: str, qdrant_api_key: str, documents: List[Document], collection_name: str) -> None:
    print("qdrant_transform_and_upsert")
    # Initialize Qdrant client
    qdrant_client = initialize_qdrant_client(qdrant_url, qdrant_api_key)
    max_retries = 1
    retry_delay = 5  # seconds

    # Transform the documents
    points = []
    vector_size = None
    for doc in documents:
        # Ensure the document has an embedding
        embedding = doc.metadata.get('embedding')
        if not embedding:
            logging.warning(f"Document with content '{doc.page_content[:50]}...' has no embedding. Skipping.")
            continue

        if vector_size is None:
            vector_size = len(embedding)
        elif len(embedding) != vector_size:
            logging.warning(f"Inconsistent embedding size. Expected {vector_size}, got {len(embedding)}. Skipping document.")
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

    # Ensure the collection exists
    ensure_collection_exists(qdrant_client, collection_name, vector_size)

    # Perform upsert
    for attempt in range(max_retries):
        try:
            result = qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            logging.info(f"Qdrant upsert successful: {result}")
            return
        except Exception as e:
            logging.error(f"An unexpected error occurred during Qdrant upsert (Attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            logging.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logging.error("Max retries reached. Qdrant upsert failed.")



            