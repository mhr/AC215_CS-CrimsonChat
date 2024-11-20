"""
test_chat_utils.py

This file contains unit tests for functions in chat_utils.py, which manage session states, estimate token usage, add context to queries, and handle responses from a language model (LLM).
The tests verify expected behavior, such as session management based on user input, token estimation for chat histories, and proper response structures from LLM.

Original Functions and Corresponding Test Functions:

1. manage_chat_session
    - Determines if the chat session should end based on user input or chat history token limits.
    - Test Functions:
      - test_manage_chat_session_end_request: Verifies ending the session when the user inputs "end".
      - test_manage_chat_session_token_limit_exceeded: Checks if the session ends when token limit is exceeded.
      - test_manage_chat_session_continue: Confirms session continues under normal conditions.

2. history_estimate_tokens_from_words
    - Estimates the number of tokens in a text or list of texts.
    - Test Functions:
      - test_history_estimate_tokens_from_words_single_string: Tests token estimation for a single string.
      - test_history_estimate_tokens_from_words_list: Tests token estimation for a list of strings.

3. add_context_to_query
    - Adds context from chat history and last instruction dictionary to the user query for enhanced relevance.
    - Test Function:
      - test_add_context_to_query: Verifies that context and prior instructions are correctly added to the query.

4. parse_and_validate_llm_response
    - Parses and validates an LLM response to ensure it meets the expected structure.
    - Test Functions:
      - test_parse_and_validate_llm_response_valid: Tests response parsing with a valid JSON response.
      - test_parse_and_validate_llm_response_invalid_json: Verifies handling of invalid JSON response.
      - test_parse_and_validate_llm_response_missing_keys: Ensures missing keys are handled by adding default values.

5. get_fallback_response
    - Provides a default structured response if parsing or retrieval attempts fail.
    - Test Function:
      - test_get_fallback_response: Verifies the fallback response structure and content.

Note:
- This file assumes the LLM response is structured as JSON. The tests for `parse_and_validate_llm_response` validate the JSON structure and handle fallback cases.
- Other functions such as `preprocess_user_query` and `retry_with_json_format_prompt` are not directly tested here, though they depend on functions covered in these tests.

"""

import json
from rag_pipeline.utils.chat_utils import (
    manage_chat_session,
    history_estimate_tokens_from_words,
    add_context_to_query,
    parse_and_validate_llm_response,
    get_fallback_response
    # preprocess_user_query,
    # get_llm_preprocess_user_prompt,
    # retry_with_json_format_prompt
)

# Function: manage_chat_session
# Description: Determines if the chat session should end based on user input or chat history token limits.
# Inputs:
# - query (str): User query, which can be "end" to terminate the session.
# - chat_history (list): List of chat messages.
# - rag_config (dict): Configuration dictionary containing 'max_history_tokens'.
# Outputs:
# - (bool, str): Tuple where the boolean indicates if the session should end and the string provides a reason if it should.


def test_manage_chat_session_end_request():
    result = manage_chat_session("end", ["Hello", "How are you?"], {'max_history_tokens': 100})
    assert result == (True, "User requested to end the session.")


def test_manage_chat_session_token_limit_exceeded():
    chat_history = ["This is a test message."] * 50  # Large enough to exceed token limit
    result = manage_chat_session("continue", chat_history, {'max_history_tokens': 10})
    assert result == (True, "Chat history has exceeded the maximum token limit. Please start a new session.")


def test_manage_chat_session_continue():
    chat_history = ["This is a test message."]
    result = manage_chat_session("continue", chat_history, {'max_history_tokens': 1000})
    assert result == (False, "")

# Function: history_estimate_tokens_from_words
# Description: Estimates the number of tokens based on the input text or list of texts.
# Inputs:
# - text (str or list): Input text or list of texts to be tokenized.
# Outputs:
# - int: Estimated token count.


def test_history_estimate_tokens_from_words_single_string():
    text = "This is a test string for token estimation."
    result = history_estimate_tokens_from_words(text)
    expected_token_count = int(len(text.split()) * 1.3)
    assert result == expected_token_count


def test_history_estimate_tokens_from_words_list():
    text_list = ["This is a test.", "Another test sentence."]
    result = history_estimate_tokens_from_words(text_list)
    total_words = sum(len(text.split()) for text in text_list)
    expected_token_count = int(total_words * 1.3)
    assert result == expected_token_count

# Function: add_context_to_query
# Description: Adds context from the chat history and last instruction dictionary to the user query.
# Inputs:
# - query (str): The original user query.
# - chat_history (list): List of previous chat messages.
# - last_instruction_dict (dict): Dictionary containing prior instructions.
# Outputs:
# - str: The modified query with context added if applicable.


def test_add_context_to_query():
    query = "What is the weather?"
    chat_history = ["Hello!", "How can I assist you?"]
    last_instruction_dict = {"llm_instruction_component": "additional instructions"}
    result = add_context_to_query(query, chat_history, last_instruction_dict)
    assert "Context: How can I assist you?" in result
    assert "User Query: What is the weather?" in result
    assert "prior instructions to keep consistency" in result

# Function: parse_and_validate_llm_response
# Description: Parses and validates an LLM response to ensure it meets expected structure.
# Inputs:
# - response (str): JSON string response from the LLM.
# Outputs:
# - dict or None: Parsed response dictionary if valid, None if parsing fails.


def test_parse_and_validate_llm_response_valid():
    response = json.dumps({
        "retrieval_component": "Sample retrieval data",
        "llm_instruction_component": {
            "format": "text",
            "content_structure": "structured",
            "additional_instructions": "none"
        }
    })
    parsed_response = parse_and_validate_llm_response(response)
    assert parsed_response is not None
    assert "retrieval_component" in parsed_response
    assert "llm_instruction_component" in parsed_response
    assert "format" in parsed_response["llm_instruction_component"]
    assert "content_structure" in parsed_response["llm_instruction_component"]
    assert "additional_instructions" in parsed_response["llm_instruction_component"]


def test_parse_and_validate_llm_response_invalid_json():
    response = "This is not JSON"
    parsed_response = parse_and_validate_llm_response(response)
    assert parsed_response is None  # Parsing should fail and return None


def test_parse_and_validate_llm_response_missing_keys():
    response = json.dumps({
        "retrieval_component": "Sample retrieval data"
    })
    parsed_response = parse_and_validate_llm_response(response)
    assert parsed_response is not None
    assert "llm_instruction_component" in parsed_response  # It should fill missing keys
    assert parsed_response["llm_instruction_component"]["format"] == "None specified"

# Function: get_fallback_response
# Description: Provides a default structured response if parsing or retrieval attempts fail.
# Inputs:
# - query (str): The original user query.
# Outputs:
# - dict: Dictionary containing fallback 'retrieval_component' and 'llm_instruction_component' defaults.


def test_get_fallback_response():
    query = "Test fallback query"
    result = get_fallback_response(query)
    expected_response = {
        "retrieval_component": query,
        "llm_instruction_component": {
            "format": "bullet points",
            "content_structure": "brief list",
            "additional_instructions": "Keep response concise"
        }
    }
    assert result == expected_response
