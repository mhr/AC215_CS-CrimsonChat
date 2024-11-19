"""
test_chat_utils.py

This file contains unit tests for functions in chat_utils.py, which manage chat sessions and preprocess user queries using LLM and Qdrant functionalities.
The tests cover various functionalities, such as session management, token estimation, LLM prompt preprocessing, and handling fallback responses.

Original Functions and Corresponding Test Functions:

1. manage_chat_session
    - Checks if a chat session should end based on user input or token limits.
    - Test Function: None (no test function provided for session management in this file)

2. history_estimate_tokens_from_words
    - Estimates the number of tokens in a given text, assuming each word maps to roughly 1.3 tokens.
    - Test Function: None (no test function provided for token estimation in this file)

3. preprocess_user_query
    - Preprocesses a user query to extract components relevant for retrieval and LLM instructions.
    - Test Function: test_preprocess_user_query (verifies response structure and fallback handling)

4. add_context_to_query
    - Appends relevant chat history and prior instructions to the user query for contextual continuity.
    - Test Function: None (no test function provided for query context addition in this file)

5. get_llm_preprocess_user_prompt
    - Retrieves the LLM response using a structured prompt for query preprocessing.
    - Test Functions:
      - test_get_llm_preprocess_user_prompt_valid_response: Verifies successful response with correct JSON format.
      - test_get_llm_preprocess_user_prompt_fallback_response: Verifies fallback handling when JSON format is invalid.

6. parse_and_validate_llm_response
    - Parses and validates the LLM response, ensuring the response includes required fields.
    - Test Function: None (tested indirectly within get_llm_preprocess_user_prompt and preprocess_user_query tests)

7. retry_with_json_format_prompt
    - Retries an LLM response with a structured JSON prompt to enforce format consistency.
    - Test Function: test_retry_with_json_format_prompt

8. get_fallback_response
    - Provides a default response structure when parsing or retrieval attempts fail.
    - Test Function: None (tested indirectly in test_get_llm_preprocess_user_prompt_fallback_response and test_preprocess_user_query)

Additional Notes:
- The test file assumes configuration from `env.dev` and initializes a GenerativeModel using the Vertex AI API with specific RAG and model parameters.
- Tests ensure JSON structures are parsed correctly and validate fallback handling for invalid or missing JSON fields.

"""

import json
import os
import json
from dotenv import load_dotenv
from utils.chat_utils import (
    manage_chat_session,
    history_estimate_tokens_from_words,
    add_context_to_query,
    parse_and_validate_llm_response,
    get_fallback_response,
    preprocess_user_query,
    get_llm_preprocess_user_prompt,
    retry_with_json_format_prompt
)
from utils.config_utils import get_configuration
from vertexai.generative_models import GenerativeModel

# Load environment variables
load_dotenv('env.dev')

# Set up project details
GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")

def get_rag_config():
    """
    Returns the default configuration dictionary for the Retrieval-Augmented Generation (RAG) settings.
    """
    return {
        "temperature": 0.75,
        "max_output_tokens": 2000,
        "top_p": 0.95,
        "num_documents": 20,
        "max_history_tokens": 8000
    }

def initialize_llm():
    """
    Initializes and returns the generative model instance using Vertex AI.
    Returns:
        GenerativeModel: The initialized Vertex AI model.
    """
    return GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")

# Initialize global config and model for testing
rag_config = get_rag_config()
generative_model = initialize_llm()
config = get_configuration()
prompts = {
    "query_processing": "Process the user query to identify key information for retrieval.",
    "final_prompt": "Create a response based on the user's question and the retrieved context."
}

# Function: retry_with_json_format_prompt
# Description: Retries the LLM response with a specific prompt enforcing a structured JSON response format.
# Inputs:
# - query (str): The user's query.
# - instruction_prompt (str): A guiding prompt to ensure the LLM structures the output as JSON.
# - generative_model: The LLM model instance.
# - config (dict): Configuration for the LLM interaction.
# Outputs:
# - dict or None: Parsed response dictionary if valid, otherwise the fallback response.
def test_retry_with_json_format_prompt():
    """
    Tests the retry_with_json_format_prompt function from chat_utils.
    
    This function tests:
    - Whether the function returns a valid structured JSON response with required fields.
    - Fallback response handling if the JSON response is invalid.
    """
    query = "Tell me about machine learning."
    instruction_prompt = "Identify key information from the query and structure output as JSON."

    # Run function
    result = retry_with_json_format_prompt(query, instruction_prompt, generative_model, config)

    # Ensure result is a valid JSON structure
    assert result is not None, "Expected a valid JSON response or fallback response"
    assert "retrieval_component" in result, "Missing 'retrieval_component' in response"
    assert "llm_instruction_component" in result, "Missing 'llm_instruction_component' in response"
    llm_component = result["llm_instruction_component"]
    assert "format" in llm_component, "Missing 'format' in 'llm_instruction_component'"
    assert "content_structure" in llm_component, "Missing 'content_structure' in 'llm_instruction_component'"
    assert "additional_instructions" in llm_component, "Missing 'additional_instructions' in 'llm_instruction_component'"

    # Additional test for fallback handling if JSON parsing fails
    query_invalid = "Invalid JSON format test."
    invalid_result = retry_with_json_format_prompt(query_invalid, instruction_prompt, generative_model, config)
    fallback = get_fallback_response(query_invalid)
    assert invalid_result == fallback, "Fallback response should be returned for an invalid format"

# Function: get_llm_preprocess_user_prompt
# Description: Retrieves the LLM response with a specific prompt to preprocess the user query.
# Inputs:
# - query (str): The original user query.
# - instruction_prompt (str): The guiding prompt that directs LLM to preprocess the query.
# - generative_model: The LLM model instance.
# - config (dict): Configuration parameters for the LLM interaction.
# Outputs:
# - dict: JSON-like response structured as:
#     - "retrieval_component": relevant information
#     - "llm_instruction_component": { "format": ..., "content_structure": ..., "additional_instructions": ... }
def test_get_llm_preprocess_user_prompt_valid_response():
    """
    Tests get_llm_preprocess_user_prompt function from chat_utils for a valid model response.
    
    This function tests:
    - Whether the function returns a structured JSON response with required keys.
    - The presence of "retrieval_component" and "llm_instruction_component" fields in the JSON response.
    """
    query = "Explain the concept of quantum computing."
    instruction_prompt = "Summarize the query and structure response as JSON."

    # Run function
    result = get_llm_preprocess_user_prompt(query, instruction_prompt, generative_model, config)

    # Verify JSON structure of a valid response
    assert "retrieval_component" in result, "Expected 'retrieval_component' in response"
    assert "llm_instruction_component" in result, "Expected 'llm_instruction_component' in response"
    llm_component = result["llm_instruction_component"]
    assert "format" in llm_component, "Missing 'format' in 'llm_instruction_component'"
    assert "content_structure" in llm_component, "Missing 'content_structure' in 'llm_instruction_component'"
    assert "additional_instructions" in llm_component, "Missing 'additional_instructions' in 'llm_instruction_component'"

# Function: get_llm_preprocess_user_prompt
# Description: Retrieves the LLM response with a specific prompt to preprocess the user query.
# This test verifies the fallback behavior when the LLM returns an invalid response.
# Inputs:
# - query (str): The original user query.
# - instruction_prompt (str): The guiding prompt directing LLM to structure the response.
# - generative_model: The LLM model instance.
# - config (dict): Configuration for the LLM interaction.
# Outputs:
# - dict: Fallback response structure when the LLM response is invalid.
def test_get_llm_preprocess_user_prompt_fallback_response():
    """
    Tests get_llm_preprocess_user_prompt function from chat_utils for scenarios where fallback is needed.
    
    This function tests:
    - The handling of invalid responses by checking if the fallback response is returned.
    - The structure and content of the fallback response to ensure it meets expected format.
    """
    query = "Invalid JSON scenario"
    instruction_prompt = "This prompt will produce an invalid JSON format."

    # Run function
    result = get_llm_preprocess_user_prompt(query, instruction_prompt, generative_model, config)

    # Verify if fallback response is returned
    fallback_response = get_fallback_response(query)
    assert result == fallback_response, "Fallback response expected due to invalid format"
    assert "retrieval_component" in fallback_response
    assert "llm_instruction_component" in fallback_response
    llm_component = fallback_response["llm_instruction_component"]
    assert llm_component["format"] == "bullet points"
    assert llm_component["content_structure"] == "brief list"
    assert llm_component["additional_instructions"] == "Keep response concise"

# Function: get_llm_preprocess_user_prompt
# Description: Retrieves the LLM response with a specific prompt to preprocess the user query.
# This test verifies that missing fields in the response are filled with default values.
# Inputs:
# - query (str): The original user query.
# - instruction_prompt (str): The guiding prompt directing the LLM response.
# - generative_model: The LLM model instance.
# - config (dict): Configuration for the LLM interaction.
# Outputs:
# - dict: JSON-like response where missing fields are supplemented with defaults.
import json

def test_get_llm_preprocess_user_prompt_valid_response():
    """
    Tests get_llm_preprocess_user_prompt function from chat_utils for a valid model response.
    
    This function tests:
    - Whether the function returns a structured JSON response with required keys.
    - The presence of "retrieval_component" and "llm_instruction_component" fields in the JSON response.
    """
    query = "Explain the concept of quantum computing."
    instruction_prompt = "Summarize the query and structure response as JSON."

    # Run function
    result = get_llm_preprocess_user_prompt(query, instruction_prompt, generative_model, config)

    # Attempt to parse the result as JSON if it is a string
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            assert False, f"Expected a JSON response but got an invalid JSON string: {result}"

    # Verify if the parsed result is a dictionary
    assert isinstance(result, dict), f"Expected a dictionary response, but got {type(result)}: {result}"

    # Check for required fields in the response
    assert "retrieval_component" in result, "Expected 'retrieval_component' in response"
    assert "llm_instruction_component" in result, "Expected 'llm_instruction_component' in response"
    llm_component = result["llm_instruction_component"]
    assert isinstance(llm_component, dict), f"Expected 'llm_instruction_component' to be a dictionary, but got {type(llm_component)}"

    # Further check keys within 'llm_instruction_component'
    assert "format" in llm_component, "Expected 'format' in 'llm_instruction_component'"
    assert "content_structure" in llm_component, "Expected 'content_structure' in 'llm_instruction_component'"
    assert "additional_instructions" in llm_component, "Expected 'additional_instructions' in 'llm_instruction_component'"

# Function: preprocess_user_query
# Description: Preprocesses the user query to extract retrieval and LLM instruction components.
# Inputs:
# - query (str): The original user query.
# - generative_model: The LLM model instance.
# - config (dict): Configuration for generation.
# - chat_history (list): List of previous chat messages.
# - last_instruction_dict (dict): Dictionary of prior instructions.
# - prompts (dict): Dictionary containing the LLM prompts.
# Outputs:
# - dict: A dictionary containing structured components for retrieval and LLM instruction formatting.
def test_preprocess_user_query():
    """
    Tests the preprocess_user_query function from chat_utils.

    This function tests:
    - Whether the function returns a structured dictionary with the required keys.
    - If fallback handling occurs when the LLM returns an invalid format.
    """
    # Example inputs
    query = "Tell me about AI applications in healthcare."
    chat_history = ["Hello!", "What are some AI use cases?"]
    last_instruction_dict = {"llm_instruction_component": {"format": "list"}}
    prompts = {
        "query_processing": "Extract information for the query and provide structured instructions."
    }

    # Run function with valid inputs
    result = preprocess_user_query(query, generative_model, config, chat_history, last_instruction_dict, prompts)

    # Verify that the result is a dictionary and contains the required keys
    assert isinstance(result, dict), "Expected a dictionary response."
    assert "retrieval_component" in result, "Missing 'retrieval_component' in the result."
    assert "llm_instruction_component" in result, "Missing 'llm_instruction_component' in the result."
    
    llm_component = result["llm_instruction_component"]
    assert isinstance(llm_component, dict), "Expected 'llm_instruction_component' to be a dictionary."

    # Check for specific keys within 'llm_instruction_component'
    assert "format" in llm_component, "Missing 'format' in 'llm_instruction_component'."
    assert "content_structure" in llm_component, "Missing 'content_structure' in 'llm_instruction_component'."
    assert "additional_instructions" in llm_component, "Missing 'additional_instructions' in 'llm_instruction_component'."

    # Run function with inputs expected to trigger fallback
    invalid_query = "This will trigger a fallback response."
    fallback_result = preprocess_user_query(invalid_query, generative_model, config, [], {}, prompts)
    fallback_response = get_fallback_response(invalid_query)

    # Validate fallback handling by checking if it matches the expected fallback structure
    assert fallback_result == fallback_response, "Expected fallback response due to invalid LLM response format."
