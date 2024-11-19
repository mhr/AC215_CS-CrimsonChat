import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from routers.utils.qdrant_utils import get_documents_from_qdrant, initialize_qdrant_client
from routers.utils.llm_utils import get_prompts, generate_llm_response, create_final_prompt
from routers.utils.config_utils import get_configuration
from routers.utils.chat_utils import manage_chat_session, preprocess_user_query
from vertexai.generative_models import GenerativeModel

# Define Router
router = APIRouter()

# Load environment variables
GCP_PROJECT = os.getenv("GCP_PROJECT")
LOCATION = os.getenv("LOCATION")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")

# Initialize global dependencies
generative_model = GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")
qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
prompts = get_prompts()
rag_config = {
    "temperature": 0.75,
    "max_output_tokens": 2000,
    "top_p": 0.95,
    "num_documents": 20,
    "max_history_tokens": 8000,
}


class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[str]] = []


class ChatResponse(BaseModel):
    response: str
    updated_history: List[str]


@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Handles chat queries by the user.
    """
    user_query = request.query.strip()
    chat_history = request.chat_history or []

    # Check if the session should end
    should_end, end_reason = manage_chat_session(user_query, chat_history, rag_config)
    if should_end:
        raise HTTPException(status_code=400, detail=end_reason)

    # Preprocess user query
    instruction_dict = preprocess_user_query(
        user_query, generative_model, get_configuration(), chat_history, {}, prompts
    )

    # Perform Qdrant search
    knowledge_documents = get_documents_from_qdrant(
        instruction_dict["retrieval_component"], get_configuration(), rag_config, qdrant_client
    )

    # Create final structured prompt
    final_prompt = create_final_prompt(
        user_query=user_query,
        instruction_dict=instruction_dict["llm_instruction_component"],
        knowledge_documents=knowledge_documents,
        chat_history=chat_history,
        prompts=prompts,
    )

    # Generate response
    llm_response = generate_llm_response(
        final_prompt=final_prompt, generative_model=generative_model, rag_config=rag_config
    )

    # Update chat history
    chat_history.append(f"User: {user_query}")
    chat_history.append(f"Response: {llm_response}")

    return ChatResponse(response=llm_response, updated_history=chat_history)


@router.get("/")
async def welcome():
    """
    Returns a welcome message.
    """
    return {"message": "Welcome to the Crimson Chat API"}
