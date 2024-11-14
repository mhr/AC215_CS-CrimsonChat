import os
from fastapi import APIRouter, Header, Query, Body, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import uuid
import time
from datetime import datetime
import mimetypes
from pathlib import Path
from utils.qdrant_utils import get_documents_from_qdrant, initialize_qdrant_client
from utils.llm_utils import get_prompts, generate_llm_response, create_final_prompt
from utils.config_utils import get_configuration
from utils.chat_utils import manage_chat_session, preprocess_user_query
from dotenv import load_dotenv
import sys
from vertexai.generative_models import GenerativeModel

# Define Router
router = APIRouter()

# Load environment variables from .env file
load_dotenv('env.dev')
# Set up project details
GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")
# Initialize Qdrant client
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")


def get_rag_config():
    """
    Returns the default configuration dictionary for the Retrieval-Augmented Generation (RAG) settings.
    """
    return {
        "temperature": 0.75, # vertexai
        "max_output_tokens": 2000, # vertexai
        "top_p": 0.95, # vertexai
        "num_documents": 20,  # Number of documents to retrieve
        "max_history_tokens": 8000  # Maximum number of tokens for chat history
    }


def initialize_llm():
    """Returns: GenerativeModel: The initialized generative model instance."""
    return GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")


def initialize_qdrant():
    """Returns: QdrantClient: The initialized Qdrant client instance."""
    return initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)


# Frontend Integration Notes:
    # Replace get_user_query with your frontend query handler, for example:
    #    async def get_frontend_query():
    #        # Get query from frontend (e.g., React state, form input, etc.)
    #        return await fetch_query_from_frontend()
    #
    
def get_user_query():
    """
    Get query from command line input.
    Returns: Stripped query string from user input
    """
    return input("What is your query? (or type 'end' to exit): ").strip()


def main():
    # Get the configuration, combining defaults, config file (if specified), and command-line arguments
    config = get_configuration()
    rag_config = get_rag_config()
    # Initialize the Vertex AI model and Qdrant client once
    generative_model = initialize_llm()
    qdrant_client = initialize_qdrant()
    prompts = get_prompts()

    # Print welcome message
    print("\n\n\n")
    print("Welcome to Harvard's CS-CrimsonChat! You can ask me any questions and I'll do my best to help you.")
    print("Type 'end' whenever you'd like to stop the chat.")

    # initialize chat history
    chat_history = []
    last_instruction_dict = {}

    while True:
        # Get query using the provided function
        user_query = get_user_query()

        # Check for end conditions
        should_end, end_reason = manage_chat_session(user_query, chat_history, rag_config)
        if should_end:
            print(f"Ending chat session. {end_reason}")
            break  # Use break instead of return None to exit the loop
        
        # get LLM to preprocess user query
        instruction_dict = preprocess_user_query(user_query, generative_model, config, chat_history, last_instruction_dict, prompts)
        
        print("\n Debug: intruction_dict, ", instruction_dict, "\n\n")
        # perform Qdrant search
        knowledge_documents = get_documents_from_qdrant(instruction_dict["retrieval_component"], config, rag_config, qdrant_client)
        
        # create final structure LLM prompt with user query, user instruction, knowledge text, and generative instructions
        final_prompt = create_final_prompt(
            user_query=user_query,
            instruction_dict=instruction_dict["llm_instruction_component"],
            knowledge_documents=knowledge_documents,
            chat_history=chat_history,
            prompts=prompts
        )

        # Generate LLM response with the final prompt
        llm_response = generate_llm_response(
            final_prompt=final_prompt,
            generative_model=generative_model,
            rag_config=rag_config
        )
        
        # Update chat history
        chat_history.append(f"User: {user_query}")
        chat_history.append(f"Response: {llm_response}")
        last_instruction_dict = instruction_dict
        
        # Print the response
        print(f"Response: {llm_response}")
    
    # Ensure any buffered output is written
    sys.stdout.flush()

if __name__ == "__main__":
    main()
    sys.stdout.flush()
