"""
vertex_ai_embedding_utils.py

This utility file contains functions for generating embeddings using Vertex AI and processing LangChain Document objects.

Input:
    - Google Cloud Project ID (string)
    - Google Cloud Location (string)
    - List of LangChain Document objects
    - Embedding model name (string)

Input LangChain Document schema:
    Document(
        page_content: str,  # The text content of the document
        metadata: {
            'id': str,      # Unique identifier for the document
            'url': str,     # URL source of the document
            'timestamp': str  # Timestamp of when the document was created or processed
        }
    )

Usage:
    from vertex_ai_embedding_utils import process_and_embed_documents
    embedded_documents = process_and_embed_documents(project_id, location, documents, model_name)

Output:
    List of LangChain Document objects with embeddings added to their metadata

Output LangChain Document schema:
    Document(
        page_content: str,  # The original text content of the document
        metadata: {
            'id': str,      # Original unique identifier for the document
            'url': str,     # Original URL source of the document
            'timestamp': str,  # Original timestamp of the document
            'embedding': List[float]  # The generated embedding for the document
        }
    )

Note: The Google Cloud Project ID and Location must be specified when calling the function.

Author: Artem Dinh
Date: 10/10/2024
"""

from typing import List
from google.cloud import aiplatform
from langchain.docstore.document import Document
from langchain.embeddings import VertexAIEmbeddings
import logging
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

def initialize_vertex_ai(project_id: str, location: str):
    """Initialize Vertex AI with the given project ID and location."""
    aiplatform.init(project=project_id, location=location)

def get_dense_embedding(text: str, model: TextEmbeddingModel, vector_dim: int = None) -> List[float]:
    """Generate an embedding for the given text using the Vertex AI model."""
    if type(model) != TextEmbeddingModel:
        model = TextEmbeddingModel.from_pretrained(model)
    try:
        inputs = [text]
        # Handle optional vector dimension argument
        kwargs = {"output_dimensionality": vector_dim} if vector_dim else {}
        # Generate the embeddings
        embeddings = model.get_embeddings(inputs, **kwargs)
        # Return the first embedding vector
        return embeddings[0].values  
    except Exception as e:
        logging.error(f"Error in embedding text: {e}")
        return []

def process_and_embed_documents(
    project_id: str,
    location: str,
    documents: List[Document],
    model_name: str = "text-embedding-004",
    vector_dim: int = None
) -> List[Document]:
    """
    Process and embed documents from the input list of LangChain Documents.
    
    Args:
        project_id (str): Google Cloud Project ID
        location (str): Google Cloud Location
        documents (List[Document]): List of LangChain Document objects
        model_name (str): Name of the embedding model to use
        vector_dim (int): Desired dimensionality of the output embeddings (optional)
    
    Returns:
        List[Document]: List of LangChain Document objects with embeddings added to their metadata
    """
    initialize_vertex_ai(project_id, location)
    model = TextEmbeddingModel.from_pretrained(model_name)

    embedded_documents = []
    for doc in documents:
        dense_embedding = get_dense_embedding(doc.page_content, model, vector_dim)
        if dense_embedding:
            embedded_doc = Document(
                page_content=doc.page_content,
                metadata={
                    **doc.metadata,
                    'embedding': dense_embedding
                }
            )
            embedded_documents.append(embedded_doc)
        else:
            logging.warning(f"Failed to generate embedding for document with ID: {doc.metadata.get('id', 'Unknown')}")

    return embedded_documents