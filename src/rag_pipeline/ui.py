import os
import logging
from utils.embedding_utils import get_dense_embedding
from dotenv import load_dotenv

import streamlit as st
from vertexai.generative_models import GenerativeModel
from utils.db_clients import QdrantDatabaseClient
from utils.history import History  # Import the History class

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv("env.dev")
# Set up project details
GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")

# Initialize Qdrant client
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")

if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
else:
    raise ValueError(
        "Missing path to service account key file. Please set the 'GOOGLE_APPLICATION_CREDENTIALS' environment variable."
    )


def chat(conversation_history, documents_llm):
    print("chat()")

    # Get the model endpoint from Vertex AI
    generative_model = GenerativeModel(
        f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}"
    )

    # Construct the input prompt by including the conversation history
    input_prompt = (
        f"{conversation_history}\n"
        f"Assistant: Answer the following query based on the provided documents.\n"
        f"Documents:\n{documents_llm}\nAssistant:"
    )
    print("Input Prompt:", input_prompt)

    generation_config = {
        "temperature": 0.75,
        "max_output_tokens": 2000, # response length limit
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
    st.title("Chatbot Interface")
    st.write("Welcome! Ask your question below.")

    # Initialize session state for conversation history
    if "history" not in st.session_state:
        st.session_state.history = History()
        # Optionally, add a system message
        st.session_state.history.add_message(
            role="system",
            content="I am an AI assistant to answer any question related to Harvard University's Computer Science department.",
        )

    # Initialize Qdrant client if not already initialized
    if "db_client" not in st.session_state:
        st.session_state.db_client = QdrantDatabaseClient(QDRANT_URL, QDRANT_API_KEY)
        logger.info("Initialized QdrantDatabaseClient")

    # Predefined questions
    st.subheader("Quick Questions:")
    predefined_questions = [
        "What are the requirements for a CS degree at Harvard?",
        "Who are the CS faculty at Harvard?",
        "What research areas are covered in Harvard's CS department?",
        "How do I apply for a graduate program in CS at Harvard?",
    ]

    predefined_prompt = None
    for question in predefined_questions:
        if st.button(question):
            predefined_prompt = question

    # User input
    prompt = st.chat_input("Ask a question about Harvard CS")
    if predefined_prompt is not None:
        prompt = predefined_prompt

    if prompt:
        # Append user message to history
        st.session_state.history.add_message(
            role="user",
            content=prompt,
        )

        # Search in Qdrant
        try:
            query_dict = {
                "collection_name": "ms3-production_v256_te004",
                "question_embedding": get_dense_embedding(
                    prompt, "text-embedding-004", 256
                ),
                "limit": 30,
            }
            response = st.session_state.db_client.query(query_dict)
            logger.info("Performed Qdrant search")

            retrieved_texts, links = st.session_state.db_client.parse(
                response, query_dict
            )
            logger.info("Parsed search results")
            logger.info(retrieved_texts)

            # Prepare documents for LLM
            documents_llm = "\n".join(retrieved_texts)
        except Exception as e:
            logger.exception("Error during Qdrant search")
            st.error("An error occurred during the search.")
            return

        # Prepare conversation history for the model using the helper function
        conversation_history = st.session_state.history.get_conversation()

        # Get response from LLM
        llm_response = chat(conversation_history, documents_llm)

        # Append assistant's response to history, including links
        st.session_state.history.add_message(
            role="assistant",
            content=llm_response,
            links=links,
        )

    # Display the conversation history
    messages = st.session_state.history.get_messages()
    if messages:
        for message in messages:
            role = message["role"]
            content = message["content"]
            links = message.get("links", [])
            with st.chat_message(role):
                st.markdown(content)
                if links:
                    st.markdown("> Reference Links:\n" + "\n".join(links))


if __name__ == "__main__":
    main()
