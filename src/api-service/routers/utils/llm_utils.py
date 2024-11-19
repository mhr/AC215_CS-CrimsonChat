import os  # To check file existence and read files
import time


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


def create_final_prompt(user_query, instruction_dict, knowledge_documents, chat_history, prompts):
    """
    Create the final prompt for the LLM response.
    Args:
        user_query (str): Original user query
        instruction_dict (dict): Dictionary containing format instructions
        knowledge_documents (list): Retrieved documents from Qdrant
        chat_history (list): Previous conversation history
        prompts (dict): dictionary with key-value pairs of llm prompts, must contain llm_output key
    Returns:
        str: Formatted prompt for LLM
    """
    # Format documents into a single string
    docs_text = "\n\n".join(str(doc) for doc in knowledge_documents)
    
    # Format chat history if it exists
    history_text = ""
    if chat_history:
        history_text = "Previous conversation:\n" + "\n".join(chat_history) + "\n\n"
    
    # Simply convert instruction dictionary to string
    instruction_text = str(instruction_dict)
    
    # Get response prompt template
    llm_prompt = prompts['llm_output']
    
    # Combine all components into final prompt
    final_prompt = (
        f"{llm_prompt}\n\n"
        f"{history_text}"
        f"User Query: {user_query}\n\n"
        f"Retrieved Context Knowledge:\n{docs_text}\n\n"
        f"Response & Format Instructions:\n{instruction_text}"
    )
    return final_prompt


def get_llm_response(prompt, generative_model, rag_config):
    """
    Get response from LLM using prompt and config.
    
    Args:
        query (str): The input query to be processed
        prompt (str): Prompt text to guide the model's response
        generative_model: The LLM model instance
        rag_config (dict): Configuration parameters for generation
        
    Returns:
        str: Generated response from the LLM
    """
    input_prompt = f"Following prompt has question to be answered, context knowledge, and instructions, respond strictly using provided knowledge and guidelines: {prompt}"

    # Use only needed config parameters
    generation_config = {
        "temperature": rag_config.get("temperature", 0.75),
        "max_output_tokens": rag_config.get("max_output_tokens", 2000),
        "top_p": rag_config.get("top_p", 0.95)
    }
    time.sleep(1)
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
    

def generate_llm_response(final_prompt, generative_model, rag_config):
    """
    Generate LLM response based on the prepared final prompt.
    Args:
        final_prompt (str): Formatted prompt for LLM containing user query, knowledge, and instructions
        generative_model: The LLM model instance
        rag_config (dict): RAG Configuration parameters
    Returns:
        str: Formatted LLM response
    """
    # Get LLM response
    
    response = get_llm_response(
        prompt=final_prompt,
        generative_model=generative_model,
        rag_config=rag_config
    )
    time.sleep(1)
    return response
