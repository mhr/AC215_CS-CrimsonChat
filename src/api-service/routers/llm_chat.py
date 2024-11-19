import os
from fastapi import APIRouter, Header, HTTPException, Body
from typing import Dict, Any, Optional
import uuid
import time
from dotenv import load_dotenv
import sys
from routers.utils.qdrant_utils import get_documents_from_qdrant, initialize_qdrant_client
from routers.utils.llm_utils import get_prompts, generate_llm_response, create_final_prompt
from routers.utils.config_utils import get_configuration
from routers.utils.chat_utils import manage_chat_session, preprocess_user_query
from vertexai.generative_models import GenerativeModel

# Define Router
router = APIRouter()


# def get_configuration():
#     return {
#         "temperature": 0.75,
#         "max_output_tokens": 2000,
#         "top_p": 0.95,
#         "num_documents": 20,
#         "max_history_tokens": 8000,
#         "qdrant_url": os.getenv("QDRANT_URL"),
#         "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
#         "model_endpoint": os.getenv("MODEL_ENDPOINT"),
#     }



@router.get("/chat")
async def chat():
    return {"message": "Welcome to AC215"}

# Load environment variables
# load_dotenv('env.dev')

# # Set up project details
# GCP_PROJECT = os.getenv("GCP_PROJECT")
# LOCATION = os.getenv("LOCATION")
# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")

# # Initialize configuration, model, and Qdrant client
# config = get_configuration()
# rag_config = {
#     "temperature": 0.75,
#     "max_output_tokens": 2000,
#     "top_p": 0.95,
#     "num_documents": 20,
#     "max_history_tokens": 8000
# }
# generative_model = GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")
# qdrant_client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
# prompts = get_prompts()

# @router.post("/sendMessageToAI")
# async def send_message_to_ai(request: Request):
#     """
#     Endpoint to process user queries via the RAG pipeline and LLM inference.
#     """
#     try:
#         body = await request.json()
#         auth_key = body.get("authKey")
#         user_message = body.get("userMessage")

#         # Validate authKey (mock validation for now)
#         if auth_key != "dummy_auth_key_12345":
#             raise HTTPException(status_code=403, detail="Invalid auth key")

#         # Manage chat history
#         chat_history = []  # Fetch chat history if stored elsewhere
#         prompts = {}  # Load or define prompt templates
#         should_end, end_reason = manage_chat_session(user_message, chat_history, config)

#         if should_end:
#             return {"response": f"Chat session ended: {end_reason}"}

#         # Preprocess query and retrieve relevant documents
#         instruction_dict = preprocess_user_query(user_message, generative_model, config, chat_history, {}, prompts)
#         knowledge_documents = get_documents_from_qdrant(instruction_dict["retrieval_component"], config, config["rag_config"], qdrant_client)

#         # Generate final response
#         final_prompt = create_final_prompt(
#             user_query=user_message,
#             instruction_dict=instruction_dict["llm_instruction_component"],
#             knowledge_documents=knowledge_documents,
#             chat_history=chat_history,
#             prompts=prompts
#         )
#         llm_response = generate_llm_response(final_prompt, generative_model, config["rag_config"])
#         return {"response": llm_response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))





    
# @router.post("/chat")
# async def chat_with_llm(
#     user_query: str = Body(..., embed=True),
#     chat_history: Optional[List[str]] = Body([], embed=True),
#     last_instruction_dict: Optional[Dict[str, Any]] = Body({}, embed=True)
# ):
#     """
#     Handle chat requests, manage chat session, process user query, retrieve relevant documents, and generate LLM response.
#     """
#     try:
#         # Manage the chat session, checking if it should end
#         should_end, end_reason = manage_chat_session(user_query, chat_history, rag_config)
#         if should_end:
#             return {"message": f"Chat session ended. {end_reason}"}

#         # Preprocess user query with LLM
#         instruction_dict = preprocess_user_query(user_query, generative_model, config, chat_history, last_instruction_dict, prompts)

#         # Retrieve documents from Qdrant
#         knowledge_documents = get_documents_from_qdrant(
#             instruction_dict["retrieval_component"],
#             config,
#             rag_config,
#             qdrant_client
#         )

#         # Create the final prompt to be sent to the LLM
#         final_prompt = create_final_prompt(
#             user_query=user_query,
#             instruction_dict=instruction_dict["llm_instruction_component"],
#             knowledge_documents=knowledge_documents,
#             chat_history=chat_history,
#             prompts=prompts
#         )

#         # Generate LLM response
#         llm_response = generate_llm_response(
#             final_prompt=final_prompt,
#             generative_model=generative_model,
#             rag_config=rag_config
#         )

#         # Update chat history
#         chat_history.append(f"User: {user_query}")
#         chat_history.append(f"Response: {llm_response}")
#         last_instruction_dict = instruction_dict

#         # Return the response
#         return {
#             "response": llm_response,
#             "chat_history": chat_history,
#             "last_instruction_dict": last_instruction_dict
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")