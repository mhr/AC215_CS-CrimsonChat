import json
from routers.utils.llm_utils import get_llm_response


def manage_chat_session(query, chat_history, rag_config):
    """
    Check if session should end based on user input or chat history limits.
    Args:
        query: The user's query
        chat_history: List of chat messages
        rag_config: dict of config containing max_history_tokens
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
    token_count = history_estimate_tokens_from_words(combined_history)

    if token_count > rag_config['max_history_tokens']:
        return True, "Chat history has exceeded the maximum token limit. Please start a new session."
    return False, ""


def history_estimate_tokens_from_words(text):
    # Estimate the number of tokens in a string or list of strings
    if isinstance(text, list):  # Join list elements if input is a list of strings
        text = " ".join(text)
    words = text.split()  # Split text into words to estimate token count
    return int(len(words) * 1.3)  # Estimate: 1 word ~ 1.3 tokens


def preprocess_user_query(query, generative_model, config, chat_history, last_instruction_dict, prompts):
    """
    Preprocess the user query to extract retrieval and LLM instruction components.

    Args:
        query (str): The user's original query
        generative_model: The LLM model instance
        config (dict): Configuration parameters for generation
        chat_history (list): List of chat history
        last_instruction_dict (dict): Past instructions

    Returns:
        dict: Dictionary containing structured components:
            - retrieval_component (str): Extracted context-specific information for retrieval
            - llm_instruction_component (dict): Instructions for the LLM output format with keys:
                - format (str): Expected output format
                - content_structure (str): Structure of content in the output
                - additional_instructions (str): Any extra guidance for the LLM
    """
    instruction_prompt = prompts['query_processing']
    query = add_context_to_query(query, chat_history, last_instruction_dict)

    # First attempt to get a response
    response = get_llm_preprocess_user_prompt(query, instruction_prompt, generative_model, config)
    result = parse_and_validate_llm_response(response)

    # Debug only if the first response parsing fails
    if not result:
        print("Debug: First response parsing failed. Response:", response)
        result = retry_with_json_format_prompt(query, instruction_prompt, generative_model, config)
    return result or get_fallback_response(query)


def add_context_to_query(query, chat_history, last_instruction_dict):
    """
    Append relevant context from chat history and last instructions to the user query.
    """
    if chat_history and len(chat_history) % 2 == 0:
        last_message = chat_history[-1]
        query = f"Context: {last_message}\nUser Query: {query}"

    if last_instruction_dict and last_instruction_dict.get("llm_instruction_component"):
        query += f", prior instructions to keep consistency: {str(last_instruction_dict['llm_instruction_component'])}"
    return query


def get_llm_preprocess_user_prompt(query, prompt, generative_model, config):
    """
    Retrieve the LLM response with a specific prompt to preprocess the user query.
    """
    full_prompt = (
        f"Query might contain history/context, extract what seems helpful for current query, ignore irrelevant, and combine with latest query\n"
        f"query: {query} \n"
        f"{prompt}\n\n"
        "IMPORTANT: Return response ONLY in this JSON format, do not wrap in ``` or 'json':\n"
        '{"retrieval_component": "what to retrieve",\n'
        ' "llm_instruction_component": {\n'
        '    "format": "output format",\n'
        '    "content_structure": "content structure",\n'
        '    "additional_instructions": "other instructions"\n'
        '}}'
    )
    return get_llm_response(
        prompt=full_prompt,
        generative_model=generative_model,
        rag_config=config
    )


def parse_and_validate_llm_response(response):
    """
    Attempt to parse the LLM response as JSON and validate it for required fields.

    Ensures that the response includes:
        - A 'retrieval_component' key for context-specific information.
        - An 'llm_instruction_component' with specific formatting instructions.
    """
    try:
        parsed = json.loads(response)
        if "retrieval_component" not in parsed:
            print("Missing or invalid 'retrieval_component'")
            return None

        llm_component = parsed.get("llm_instruction_component", {})
        expected_structure = {
            "format": "None specified",
            "content_structure": "None specified",
            "additional_instructions": "None specified"
        }

        for key, default_value in expected_structure.items():
            if key not in llm_component:
                llm_component[key] = default_value

        if all(key in llm_component for key in expected_structure):
            parsed["llm_instruction_component"] = llm_component
            return parsed
        else:
            print("Failed structure validation.")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None


def retry_with_json_format_prompt(query, prompt, generative_model, config):
    """
    Retry the LLM response with a prompt enforcing a specific JSON response format.
    """
    retry_prompt = (
        f"Query: {query}, Instruction Prompt: {prompt}\n\n"
        "IMPORTANT: Return response ONLY in this JSON format, do not wrap in ``` or 'json':\n"
        '{"retrieval_component": "what to retrieve",\n'
        ' "llm_instruction_component": {\n'
        '    "format": "output format",\n'
        '    "content_structure": "content structure",\n'
        '    "additional_instructions": "other instructions"\n'
        '}}'
    )
    response = get_llm_response(
        prompt=retry_prompt,
        generative_model=generative_model,
        rag_config=config
    )
    return parse_and_validate_llm_response(response)


def get_fallback_response(query):
    """
    Return a default response structure when parsing or retrieval attempts fail.
    """
    return {
        "retrieval_component": query,
        "llm_instruction_component": {
            "format": "bullet points",
            "content_structure": "brief list",
            "additional_instructions": "Keep response concise"
        }
    }