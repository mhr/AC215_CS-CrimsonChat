""" TODO
- Implement RAG experiment and logging
- VerttexAi implement batch embedding
"""

import os
from langchain.schema import Document
from utils.qdrant_utils import qdrant_transform_and_upsert, qdrant_search, initialize_qdrant_client
from utils.embedding_utils import process_and_embed_documents, get_dense_embedding
from utils.chunker_utils import run_chunking
from utils.json_utils import load_json_to_documents
from utils.config_utils import get_configuration, print_config
from dotenv import load_dotenv
import datetime
import sys
import json
import vertexai
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel, GenerationConfig


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
        "temperature": 0.75,
        "max_output_tokens": 2000,
        "top_p": 0.95,
        "num_documents": 50,  # Number of documents to retrieve
        "num_documents_for_llm": 20,  # Number of documents to input into the LLM
        "max_history_tokens": 10000  # Maximum number of tokens for chat history
    }

def initialize_vertex_ai():
    """Returns: GenerativeModel: The initialized generative model instance."""
    return GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")

def initialize_qdrant():
    """Returns: QdrantClient: The initialized Qdrant client instance."""
    return initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

def get_prompts():
    """
    Reads the prompts from files located in the ./prompts directory and returns them as strings.
    Returns: dict: A dictionary containing the prompts with keys 'llm_output' and 'query_processing'.
    """
    prompts = {}
    prompt_files = {
        'llm_output': './prompts/llm_output.txt',
        'query_processing': './prompts/query_processing.txt'
    }
    
    for key, file_path in prompt_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                prompts[key] = file.read()
        else:
            print(f"Warning: {file_path} not found.")
            prompts[key] = ""
    return prompts

def estimate_tokens_from_words(text):
    # Estimate the number of tokens in a string or list of strings
    if isinstance(text, list):  # Join list elements if input is a list of strings
        text = " ".join(text)
    words = text.split()  # Split text into words to estimate token count
    return int(len(words) * 1.3)  # Estimate: 1 word ~ 1.3 tokens

def manage_session(query, chat_history):
    """
    Check if session should end based on user input or chat history limits.
    Args:
        query: The user's query
        chat_history: List of chat messages
    Returns:
        (bool, str): Tuple containing:
        - should_end: True if session should end, False if continuing
        - reason: Message explaining why session ended, empty if continuing
    """
    # Check if user wants to end
    if query.lower() == 'end':
        return True, "User requested to end the session."
    # Check chat history token limit
    combined_history = "\n".join(chat_history)
    token_count = estimate_tokens_from_words(combined_history)

    if token_count > get_rag_config()['max_history_tokens']:
        return True, "Chat history has exceeded the maximum token limit. Please start a new session."
    return False, ""

def get_llm_response(query, prompt, generative_model, config):
    """
    Get response from LLM using prompt and config.
    
    Args:
        query (str): The input query to be processed
        prompt (str): Prompt text to guide the model's response
        generative_model: The LLM model instance
        config (dict): Configuration parameters for generation
        
    Returns:
        str: Generated response from the LLM
    """
    input_prompt = f"{prompt}\n Text or user query to be processed: {query}"

    # Use only needed config parameters
    generation_config = {
        "temperature": config.get("temperature", 0.75),
        "max_output_tokens": config.get("max_output_tokens", 2000),
        "top_p": config.get("top_p", 0.95)
    }
    
    # Generate response
    try:
        response = generative_model.generate_content(
            [input_prompt],
            generation_config=generation_config,
            stream=False
        )
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I apologize, but I encountered an error generating a response. Please try again."

def process_user_query(query, generative_model, config):
    """
    Process user query to extract retrieval and LLM instruction components.
    
    Args:
        query (str): The user's original query
        generative_model: The LLM model instance
        config (dict): Configuration parameters for generation
        
    Returns:
        dict: Dictionary containing retrieval and LLM instruction components
    """
    def try_parse_response(response):
        """Try to parse and validate LLM response"""
        try:
            parsed = json.loads(response)
            # Ensure response is a dictionary and contains "retrieval_component"
            if not isinstance(parsed, dict) or "retrieval_component" not in parsed:
                print("Missing or invalid 'retrieval_component'")
                return None
            
            # Get llm_instruction_component or set defaults if missing keys
            llm_component = parsed.get("llm_instruction_component", {})
            
            # Define expected keys and their default values as per instruction example
            expected_structure = {
                "format": "None specified",
                "content_structure": "None specified",
                "additional_instructions": "None specified"
            }
            
            # Fill in missing keys with "None specified"
            for key, default_value in expected_structure.items():
                if key not in llm_component:
                    llm_component[key] = default_value
            
            # Validate final structure
            if all(key in llm_component for key in expected_structure):
                parsed["llm_instruction_component"] = llm_component  # Ensure defaults are added
                return parsed
            else:
                print("Failed structure validation.")
                return None
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        return None

    # Get prompt and try first attempt
    prompts = get_prompts()
    response = get_llm_response(
        query=query,
        prompt=prompts['query_processing'],
        generative_model=generative_model,
        config=config
    )
    # # Remove markdown code block indicators if present
    # if response.startswith("```json") and response.endswith("```"):
    #     response = response[7:-3].strip()
    # elif response.startswith("```") and response.endswith("```"):
    #     response = response[3:-3].strip()
        
    print("Debug First Response query process:, ", response, "\n\n")
    result = try_parse_response(response)
    if result:
        return result
    
    print("First Response query process FAILED, result:, ", result, "\n\n")
    # If failed, retry with format instructions
    retry_prompt = (
        f"{prompts['query_processing']}\n\n"
        "IMPORTANT: Return response ONLY in this JSON format:\n"
        '{"retrieval_component": "what to retrieve",\n'
        ' "llm_instruction_component": {\n'
        '    "format": "output format",\n'
        '    "content_structure": "content structure",\n'
        '    "additional_instructions": "other instructions"\n'
        '}}'
    )
    
    response = get_llm_response(
        query=query,
        prompt=retry_prompt,
        generative_model=generative_model,
        config=config
    )
    # # Remove markdown code block indicators if present
    # if response.startswith("```json") and response.endswith("```"):
    #     response = response[7:-3].strip()
    # elif response.startswith("```") and response.endswith("```"):
    #     response = response[3:-3].strip()

    print("Second Response query process, response:, ", response, "\n\n")
    result = try_parse_response(response)
    if result:
        return result
    print("Second Response query process FAILED, result:, ", result, "\n\n")
    # Return default if all attempts fail
    return {
        "retrieval_component": query,
        "llm_instruction_component": {
            "format": "bullet points",
            "content_structure": "brief list",
            "additional_instructions": "Keep response concise"
        }
    }

# Frontend Integration Notes:
    # 1. Replace get_query_fn with your frontend query handler, for example:
    #    async def get_frontend_query():
    #        # Get query from frontend (e.g., React state, form input, etc.)
    #        return await fetch_query_from_frontend()
    #
    # 2. For backend API implementation:
    #    @app.post("/chat")
    #    async def chat_endpoint(query: str):
    #        response = await handle_single_query(query, model, chat_history)
    #        return {"response": response}
def get_user_query(config=None):
    """
    Get query from config or command line input.
    Args: config: Optional configuration dictionary. If provided, attempts to get query from config first.
    Returns: Stripped query string from either config or user input
    """
    if config and config.get('query'):
        query = config['query']
        config['query'] = None  # Reset config query after using it
        return query.strip()
    return input("What is your query? (or type 'end' to exit): ").strip()

def get_documents_from_qdrant(query, config, qdrant_client):
    """
    Retrieve relevant documents from Qdrant based on the given query.
    Args:
        query (str): The search query.
        config (dict): Configuration settings.
        qdrant_client: The Qdrant client instance.
    Returns:
        list: A list of document texts retrieved from Qdrant.
    """
    search_results = qdrant_search(
        qdrant_client,
        config['qdrant_collection'],
        get_dense_embedding(query, config['embedding_model'], config['vector_dim']),
        get_rag_config()['num_documents']  # Retrieve number of documents from RAG config
    )
    return [result['payload']['text'] for result in search_results[:get_rag_config()['num_documents_for_llm']]]

def generate_llm_response(user_query, instruction_dict, knowledge_documents, chat_history, generative_model, config):
    """
    Generate LLM response combining user query, documents, and formatting instructions.
    Args:
        user_query (str): Original user query
        instruction_dict (dict): Dictionary containing format instructions
        knowledge_documents (list): Retrieved documents from Qdrant
        chat_history (list): Previous conversation history
        generative_model: The LLM model instance
        config (dict): Configuration parameters
    Returns:
        str: Formatted LLM response
    """
    # Format documents into a single string
    docs_text = "\n\n".join(str(doc) for doc in knowledge_documents)
    
    # Format chat history if exists
    history_text = ""
    if chat_history:
        history_text = "Previous conversation:\n" + "\n".join(chat_history) + "\n\n"
    
    # Simply convert instruction dictionary to string
    instruction_text = str(instruction_dict)
    
    # Get response prompt template
    prompts = get_prompts()
    llm_prompt = prompts.get('llm_output', "").strip()
    
    # Combine all components into final prompt
    final_prompt = (
        f"{llm_prompt}\n\n"
        f"{history_text}"
        f"User Query: {user_query}\n\n"
        f"Retrieved Information:\n{docs_text}\n\n"
        f"Response Instructions:\n{instruction_text}"
    )

    # Get LLM response
    response = get_llm_response(
        query=user_query,
        prompt=final_prompt,
        generative_model=generative_model,
        config=config
    )
    
    return response

def main():
    # Get the configuration, combining defaults, config file (if specified), and command-line arguments
    config = get_configuration()
    print_config(config)

    # Initialize the Vertex AI model and Qdrant client once
    generative_model = initialize_vertex_ai()
    qdrant_client = initialize_qdrant()

    # Print welcome message
    print("\n\n\n")
    print("Welcome to Harvard's CS-CrimsonChat! You can ask me any questions and I'll do my best to help you.")
    print("Type 'end' whenever you'd like to stop the chat.")

    # initialize chat history
    chat_history = []
        
    while True:
        # # Get query from config or user input
        # query = config.get('query') or input("What is your query? (or type 'end' to exit): ").strip()
        # Get query using the provided function
        user_query = get_user_query()

        # Check for end conditions
        should_end, end_reason = manage_session(user_query, chat_history)
        if should_end:
            print(f"Ending chat session. {end_reason}")
            break  # Use break instead of return None to exit the loop
        
        # get LLM to preprocess user query
        intruction_dict = process_user_query(user_query, generative_model, config)
        print("Debug: intruction_dict, ", intruction_dict, "\n\n")
        # perform Qdrant search
        knowledge_documents = get_documents_from_qdrant(intruction_dict["retrieval_component"], config, qdrant_client)
        
        # Generate LLM response
        llm_response = generate_llm_response(
            user_query=user_query,
            instruction_dict=intruction_dict["llm_instruction_component"],
            knowledge_documents=knowledge_documents,
            chat_history=chat_history,
            generative_model=generative_model,
            config=config
        )
        
        # Update chat history
        chat_history.append(f"User: {user_query}")
        chat_history.append(f"Response: {llm_response}")
        
        # Print the response
        print(f"Response: {llm_response}")

        # Reset query in config for next iteration
        config['query'] = None
    
    # Ensure any buffered output is written
    sys.stdout.flush()

if __name__ == "__main__":
    main()
    sys.stdout.flush()

