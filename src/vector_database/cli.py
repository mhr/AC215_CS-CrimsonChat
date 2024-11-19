""" TODO
- Implement RAG experiment and logging
- VerttexAi implement batch embedding
"""

import os
from vector_database.utils.qdrant_upsert_utils import qdrant_transform_and_upsert
from utils.embedding_utils import process_and_embed_documents, get_dense_embedding
from utils.chunker_utils import run_chunking
from utils.json_utils import load_all_documents_in_json
from utils.config_utils import get_configuration, print_config
from dotenv import load_dotenv
import sys
import math
from typing import List, Dict, Any

# Arguments explanation (see config.txt or config_utils.py for more details):
# --query: Query string to search for (default: None)
# --config: Path to a configuration file (optional)
# --embedding_model: Model name for Vertex AI embedder, consistent with target Qdrant collection's embeddings (default: textembedding-gecko@001)
# --chunking_method: Chunking method, either "simple" or "semantic" (default: none)
# --qdrant_collection: Name of the Qdrant collection (default: default_collection)
# --vector_dim: size of vector embedding (dimenstions) (default: 768)
# --bucket_file_path: Path for json file in bucket (default: None)
# For semantic chunking:
# --breakpoint_threshold_type: Type of threshold for semantic chunking
# --buffer_size: Buffer size for semantic chunking
# --breakpoint_threshold_amount: Threshold amount for semantic chunking
# For simple chunking:
# --chunk_size: Size of each chunk for simple chunking
# --chunk_overlap: Overlap between chunks for simple chunking

# Load environment variables from .env file
load_dotenv('env.dev')
# Set up project details
GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")
BUCKET_NAME = os.environ["BUCKET_NAME"]
# Initialize Qdrant client
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") # not really used, Vertex AI library looks for global env automatically

def process_batch(batch: List[Dict[str, Any]], config: Dict[str, Any], gcp_project: str, location: str, qdrant_url: str, qdrant_api_key: str):
    # Chunk the documents
    chunked_batch = run_chunking(batch, config, get_dense_embedding)
    print(f"Batch chunked: {len(chunked_batch)} chunks")
    # Embed chunks
    embedded_batch = process_and_embed_documents(gcp_project, location, chunked_batch, config['embedding_model'], config['vector_dim'])
    print(f"Batch embedded: {len(embedded_batch)} embeddings")
    # Upsert the data to Qdrant Cloud
    qdrant_transform_and_upsert(qdrant_url, qdrant_api_key, embedded_batch, config['qdrant_collection'])
    print(f"Batch upserted to Qdrant")

def batch_process_documents(documents: List[Dict[str, Any]], config: Dict[str, Any], gcp_project: str, location: str, qdrant_url: str, qdrant_api_key: str, batch_size: int = 10):
    # process documents in batches: chunk, embed, upsert
    total_documents = len(documents)
    num_batches = math.ceil(total_documents / batch_size)
    print(f"===Total documents: {total_documents}===")
    print(f"Processing in {num_batches} batches of {batch_size} documents each")

    for i in range(0, total_documents, batch_size):
        batch = documents[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{num_batches}")
        process_batch(batch, config, gcp_project, location, qdrant_url, qdrant_api_key)
    print("RAG TESTING COMPLETED, V2, 10/16/2024")

def main():
    # Get the configuration, combining defaults, config file (if specified), and command-line arguments
    config = get_configuration()
    print_config(config)
    # add bucket info to config
    config['bucket_name'] = BUCKET_NAME
    # Load the documents from the GCP Bucket
    documents = load_all_documents_in_json(config)
    print(f"Documents loaded: {len(documents)}")

    batch_process_documents(documents, config, GCP_PROJECT, LOCATION, QDRANT_URL, QDRANT_API_KEY)

if __name__ == "__main__":
    main()
    sys.stdout.flush()