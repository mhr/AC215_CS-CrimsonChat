""" TODO
- Implement RAG experiment and logging
- VerttexAi implement batch embedding
"""

import os
import logging
from langchain.schema import Document
from utils.qdrant_utils import qdrant_transform_and_upsert, qdrant_search, initialize_qdrant_client
from utils.embedding_utils import process_and_embed_documents, get_dense_embedding
from utils.chunker_utils import run_chunking
from utils.json_utils import load_json_to_documents
from utils.config_utils import get_configuration, print_config
from dotenv import load_dotenv
import datetime
import sys

import vertexai
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv('env.dev')
# Set up project details
GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")
# Initialize Qdrant client
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../secrets/crimsonchat.json"

def chat(query, documents_llm, chat_history):
    print("chat()")

    #get the model endpoint from Vertex AI
    generative_model = GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")

    # Include previous chat history in the prompt
    history = "\n".join(chat_history)

    input_prompt = f"Chat History: {history}\n\n \
                    Query: {query}\n \
                    Documents: {documents_llm}"
    
    # print(input_prompt)

    generation_config = {
        "temperature": 0.75,
        "max_output_tokens": 150,
        "top_p": 0.95,
    }

    # Generate content from the LLM
    response = generative_model.generate_content(
        [input_prompt], 
        generation_config=generation_config,
        stream=False,
    )

    generated_text = response.text
    print("LLM Response:", generated_text)
    return generated_text


def main():
    logger.info("Starting the script")
    # Get the configuration, combining defaults, config file (if specified), and command-line arguments
    config = get_configuration()
    print_config(config)
    # Arguments explanation:
    # --query: Query string to search for (default: None)
    # --config: Path to a configuration file (optional)
    # --testing_json: Path to the JSON file for testing (default: None)
    # --embedding_model: Model name for Vertex AI embedder, consistent with target Qdrant collection's embeddings (default: textembedding-gecko@001)
    # --chunking_method: Chunking method, either "simple" or "semantic" (default: none)
    # --qdrant_collection: Name of the Qdrant collection (default: default_collection)
    # --vector_dim: size of vector embedding (dimenstions) (default: 768)
    # For semantic chunking:
    # --breakpoint_threshold_type: Type of threshold for semantic chunking
    # --buffer_size: Buffer size for semantic chunking
    # --breakpoint_threshold_amount: Threshold amount for semantic chunking
    # For simple chunking:
    # --chunk_size: Size of each chunk for simple chunking
    # --chunk_overlap: Overlap between chunks for simple chunking
    
    
    # if not config['query']:
    #     print("No query provided, using default")
    #     config['query'] = "How does a good loving relationship looking like?" #, "are capybaras worst animals ever?", "why did dinosaurs die"]
    if not config['testing_json']:
        print("No JSON testing file provided, assuming server mode, executing FastAPI server at port 8000")
        # Add your FastAPI routes and logic here

    # query processing+embedding - terminal argument

    curr_qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
    print("RAG TESTING COMPLETED, V2, 10/15/2024", curr_qdrant_client)

    # Giving some space to more easily see where the chat starts
    print("\n")
    print("\n")
    print("\n")

    # perform search
    # query_results = []
    # for query in config["query"]:
        # Perform search

    chat_history = []

    print("Welcome to Harvard's CS-CrimsonChat! You can ask me any questions and I'll do my best to help you.")
    print("Type 'end' whenever you'd like to stop the chat.")


    while True:
        # Prompt the user for their query
        if not config['query']:
            config['query'] = input("What is your query? (or type 'end' to exit): ").strip()
        query = config['query']
        
        if query.lower() == 'end':
            print("Ending chat session. Thank you for using CS CrimsonChat!")
            break

        # get the documents using Qdrant
        search_results = qdrant_search(
            curr_qdrant_client,
            config['qdrant_collection'],
            get_dense_embedding(query, config['embedding_model'], config['vector_dim']),
            50
        )
        
        #setting documents inputting into the model as 5 temporarily - this can change
        results = []
        for result in search_results[:20]:
            results.append(result['payload']['text'])

        documents_llm = str(results)

        llm_response = chat(query, documents_llm, chat_history)

        chat_history.append(f"User: {query}")
        chat_history.append(f"Response: {llm_response}")

        # Prompt user for the next query
        config['query'] = None  # Reset to initialize the next query input

    # query = config['query']
    # search_results = qdrant_search(curr_qdrant_client, config['qdrant_collection'], get_dense_embedding(query, config['embedding_model'], config['vector_dim']), 5)
    # query_results = {"query": query, "results": search_results}

    
    # # print(query_results)

    # # prompt engineering: huge prompt

    # # print(query_results['results'])

    # results = []
    # for result in query_results['results'][:5]:
    #     results.append(result['payload']['text'])

    # # print(results)

    # documents_llm = str(results)

    # # input_for_llm = f"Answer the following query based on the provided documents: \
    # #                 Query: {query} \
    # #                 Documents: {documents_llm}"
    
    # # print(input_for_llm)

    # # LLM inference

    # # print/write LLM's response.

    # llm_response = chat(query, documents_llm)

    # # print(f"Final LLM Response: {llm_response}")



if __name__ == "__main__":
    main()
    sys.stdout.flush()
