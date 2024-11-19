import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
from langchain.schema import Document
from rag_pipeline.utils.llm_utils import get_prompts, create_final_prompt



def test_get_prompts_empty_files():
    """
    Test case: All prompt files exist but are empty.
    """
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="")):
            prompts = get_prompts()
            assert prompts['llm_output'] == ''
            assert prompts['query_processing'] == ''

# Tests for create_final_prompt
def test_create_final_prompt_valid_input():
    """
    Test case: All inputs are valid.
    """
    user_query = "What is AI?"
    instruction_dict = {"format": "concise"}
    knowledge_documents = ["AI is artificial intelligence.", "AI is used in many fields."]
    chat_history = ["What is AI?", "AI is technology that mimics human intelligence."]
    prompts = {"llm_output": "Respond with concise, factual information."}
    
    final_prompt = create_final_prompt(user_query, instruction_dict, knowledge_documents, chat_history, prompts)
    assert "Respond with concise, factual information." in final_prompt
    assert "User Query: What is AI?" in final_prompt
    assert "AI is artificial intelligence.\n\nAI is used in many fields." in final_prompt
    assert "Previous conversation:\nWhat is AI?" in final_prompt
    assert str(instruction_dict) in final_prompt

def test_create_final_prompt_empty_chat_history():
    """
    Test case: Chat history is empty.
    """
    user_query = "What is AI?"
    instruction_dict = {"format": "concise"}
    knowledge_documents = ["AI is artificial intelligence."]
    chat_history = []
    prompts = {"llm_output": "Respond with concise, factual information."}
    
    final_prompt = create_final_prompt(user_query, instruction_dict, knowledge_documents, chat_history, prompts)
    assert "Previous conversation:" not in final_prompt
    assert "AI is artificial intelligence." in final_prompt

def test_create_final_prompt_empty_knowledge_documents():
    """
    Test case: Knowledge documents are empty.
    """
    user_query = "What is AI?"
    instruction_dict = {"format": "concise"}
    knowledge_documents = []
    chat_history = ["What is AI?"]
    prompts = {"llm_output": "Respond with concise, factual information."}
    
    final_prompt = create_final_prompt(user_query, instruction_dict, knowledge_documents, chat_history, prompts)
    assert "Retrieved Context Knowledge:" in final_prompt
    assert "AI is artificial intelligence." not in final_prompt

def test_create_final_prompt_missing_prompt_key():
    """
    Test case: Prompts dictionary does not contain 'llm_output' key.
    """
    user_query = "What is AI?"
    instruction_dict = {"format": "concise"}
    knowledge_documents = ["AI is artificial intelligence."]
    chat_history = ["What is AI?"]
    prompts = {}  # Missing 'llm_output'
    
    with pytest.raises(KeyError, match="'llm_output'"):
        create_final_prompt(user_query, instruction_dict, knowledge_documents, chat_history, prompts)
